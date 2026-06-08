# ============================================================
# pages/03_Riwayat_Transaksi.py
# Tabel interaktif riwayat transaksi + upload CSV + ekspor
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import io
from core.config import ZONE_COLORS, ZONE_LABELS, SUPPORTED_TYPES
from core.pipeline import run_scoring_pipeline
from core.dummy_data import (
    generate_demo_dataset,
    generate_batch_upload_sample
)

st.set_page_config(
    page_title="Riwayat Transaksi | EARS-UMKM",
    page_icon="📋",
    layout="wide",
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 📋 Riwayat Transaksi")
st.caption(
    "Tabel lengkap seluruh transaksi yang telah di-*scoring*. "
    "Gunakan filter untuk menelusuri zona risiko tertentu."
)
st.divider()

# ─────────────────────────────────────────────
# TAB — Demo vs Upload
# ─────────────────────────────────────────────
tab_demo, tab_upload = st.tabs([
    "📂 Data Demo",
    "⬆️ Upload CSV"
])

# ══════════════════════════════════════════════
# TAB 1 — Data Demo
# ══════════════════════════════════════════════
with tab_demo:
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        n_demo = st.selectbox(
            "Jumlah Transaksi",
            [50, 100, 200, 300, 500],
            index=1
        )
    with col_ctrl2:
        fraud_pct = st.selectbox(
            "Proporsi Fraud Demo",
            ["5%", "10%", "15%", "20%"],
            index=1
        )
    with col_ctrl3:
        seed_demo = st.number_input(
            "Seed", value=42, min_value=1, key="seed_demo"
        )

    if st.button("▶️ Load Data Demo", key="btn_demo",
                 use_container_width=True, type="primary"):
        with st.spinner("Memuat data..."):
            df_raw = generate_demo_dataset(
                n_total=n_demo,
                fraud_rate=int(fraud_pct.replace("%", "")) / 100.0,
                seed=int(seed_demo)
            )
            df_result = run_scoring_pipeline(df_raw)
        st.session_state['df_riwayat'] = df_result
        st.success(
            f"✅ {len(df_result)} transaksi berhasil di-scoring."
        )

# ══════════════════════════════════════════════
# TAB 2 — Upload CSV
# ══════════════════════════════════════════════
with tab_upload:
    st.markdown("**Format CSV yang diperlukan:**")

    # Template download
    df_template = generate_batch_upload_sample(n=10)
    csv_template = df_template.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Template CSV",
        data=csv_template,
        file_name="template_transaksi_umkm.csv",
        mime="text/csv",
    )

    st.caption(
        "Kolom wajib: `transaction_id`, `step`, `type`, `amount`, "
        "`oldbalanceOrg`, `newbalanceOrig`, "
        "`oldbalanceDest`, `newbalanceDest`"
    )

    uploaded = st.file_uploader(
        "Upload file CSV transaksi",
        type=["csv"],
        key="uploader_csv"
    )

    if uploaded is not None:
        try:
            df_up = pd.read_csv(uploaded)
            required_cols = [
                'step', 'type', 'amount',
                'oldbalanceOrg', 'newbalanceOrig',
                'oldbalanceDest', 'newbalanceDest'
            ]
            missing = [
                c for c in required_cols
                if c not in df_up.columns
            ]
            if missing:
                st.error(
                    f"Kolom tidak lengkap: {missing}"
                )
            else:
                # Filter hanya tipe yang didukung
                df_up = df_up[
                    df_up['type'].isin(SUPPORTED_TYPES)
                ].copy()

                if len(df_up) == 0:
                    st.error(
                        "Tidak ada transaksi TRANSFER atau "
                        "CASH_OUT dalam file."
                    )
                else:
                    # Tambah isFraud dummy jika tidak ada
                    if 'isFraud' not in df_up.columns:
                        df_up['isFraud'] = 0

                    with st.spinner("Men-scoring transaksi..."):
                        df_result_up = run_scoring_pipeline(df_up)

                    st.session_state['df_riwayat'] = df_result_up
                    st.success(
                        f"✅ {len(df_result_up)} transaksi "
                        "berhasil di-scoring."
                    )
        except Exception as e:
            st.error(f"Error membaca file: {e}")

# ─────────────────────────────────────────────
# TABEL RIWAYAT
# ─────────────────────────────────────────────
st.divider()

if 'df_riwayat' not in st.session_state:
    st.info(
        "Belum ada data. Gunakan tab **Data Demo** "
        "atau **Upload CSV** di atas untuk memulai.",
        icon="ℹ️"
    )
else:
    df_tbl = st.session_state['df_riwayat'].copy()

    # ── Filter panel
    st.subheader("Filter & Pencarian")
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)

    with fcol1:
        filter_zona = st.multiselect(
            "Zona Risiko",
            options=['Hijau', 'Kuning', 'Merah'],
            default=['Hijau', 'Kuning', 'Merah'],
            format_func=lambda z: ZONE_LABELS[z]
        )
    with fcol2:
        filter_tipe = st.multiselect(
            "Tipe Transaksi",
            options=SUPPORTED_TYPES,
            default=SUPPORTED_TYPES
        )
    with fcol3:
        score_min, score_max = st.slider(
            "Rentang Risk Score",
            0.0, 100.0,
            (0.0, 100.0),
            step=1.0
        )
    with fcol4:
        filter_anomali = st.selectbox(
            "Status Deteksi",
            ["Semua", "Anomali Saja", "Normal Saja"]
        )

    # Terapkan filter
    mask = (
        df_tbl['risk_zone'].isin(filter_zona) &
        df_tbl['type'].isin(filter_tipe) &
        (df_tbl['risk_score'] >= score_min) &
        (df_tbl['risk_score'] <= score_max)
    )
    if filter_anomali == "Anomali Saja":
        mask &= (df_tbl['is_anomaly'] == 1)
    elif filter_anomali == "Normal Saja":
        mask &= (df_tbl['is_anomaly'] == 0)

    df_filtered = df_tbl[mask].copy()

    # Ringkasan hasil filter
    n_filt = len(df_filtered)
    n_ano  = int(df_filtered['is_anomaly'].sum())
    st.caption(
        f"Menampilkan **{n_filt}** dari {len(df_tbl)} transaksi "
        f"| Anomali terdeteksi: **{n_ano}**"
    )

    # Kolom yang ditampilkan
    display_cols = {
        'transaction_id':   'ID Transaksi',
        'step':             'Step',
        'type':             'Tipe',
        'amount':           'Nominal (Rp)',
        'oldbalanceOrg':    'Saldo Awal Pengirim',
        'newbalanceOrig':   'Saldo Akhir Pengirim',
        'errorBalanceOrig': 'Error Saldo Pengirim',
        'amount_ratio':     'Amount Ratio',
        'risk_score':       'Risk Score',
        'risk_zone':        'Zona Risiko',
        'is_anomaly':       'Anomali',
        'threshold_used':   'Threshold',
    }

    df_display = df_filtered[
        [c for c in display_cols.keys() if c in df_filtered.columns]
    ].rename(columns=display_cols).copy()

    # Format kolom
    if 'Nominal (Rp)' in df_display.columns:
        df_display['Nominal (Rp)'] = df_display[
            'Nominal (Rp)'
        ].apply(lambda x: f"Rp {x:,.0f}")

    if 'Risk Score' in df_display.columns:
        df_display['Risk Score'] = df_display[
            'Risk Score'
        ].apply(lambda x: f"{x:.1f}")

    if 'Anomali' in df_display.columns:
        df_display['Anomali'] = df_display['Anomali'].map(
            {1: "⚠️ Anomali", 0: "✅ Normal"}
        )

    if 'Zona Risiko' in df_display.columns:
        df_display['Zona Risiko'] = df_display['Zona Risiko'].map(
            ZONE_LABELS
        )

    # Tampilkan tabel
    st.dataframe(
        df_display,
        use_container_width=True,
        height=min(600, 40 + n_filt * 35),
        hide_index=True,
    )

    # ── Ekspor
    st.divider()
    col_exp1, col_exp2, _ = st.columns([1, 1, 2])

    with col_exp1:
        csv_out = df_filtered.to_csv(index=False)
        st.download_button(
            label="⬇️ Ekspor CSV",
            data=csv_out,
            file_name="hasil_scoring_umkm.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_exp2:
        # Ekspor Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtered.to_excel(
                writer,
                sheet_name='Hasil Scoring',
                index=False
            )
        st.download_button(
            label="⬇️ Ekspor Excel",
            data=buffer.getvalue(),
            file_name="hasil_scoring_umkm.xlsx",
            mime="application/vnd.openxmlformats-"
                 "officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
