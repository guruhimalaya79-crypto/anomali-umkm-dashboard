# ============================================================
# pages/01_Scoring_Transaksi.py
# Input transaksi manual + scoring real-time
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.config import (
    ZONE_COLORS, ZONE_LABELS, THRESHOLD_PER_TYPE,
    SUPPORTED_TYPES, RESEARCH_INFO
)
from core.pipeline import score_single_transaction

st.set_page_config(
    page_title="Scoring Transaksi | EARS-UMKM",
    page_icon="📝",
    layout="wide",
)

# ─────────────────────────────────────────────
# CSS inline
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .result-box {
        border-radius: 12px; padding: 1.5rem;
        text-align: center; margin-top: 1rem;
    }
    .score-big { font-size: 4rem; font-weight: 800; }
    .zone-label { font-size: 1.3rem; font-weight: 600;
                  margin-top: 0.3rem; }
    .detail-row { display:flex; justify-content:space-between;
                  padding: 6px 0;
                  border-bottom: 1px solid rgba(0,0,0,0.08); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 📝 Scoring Transaksi Manual")
st.caption(
    "Masukkan data transaksi untuk mendapatkan "
    "*early anomaly risk score* secara real-time."
)
st.divider()

# ─────────────────────────────────────────────
# FORM INPUT
# ─────────────────────────────────────────────
with st.form("form_transaksi", clear_on_submit=False):
    st.subheader("Data Transaksi")

    col1, col2 = st.columns(2)

    with col1:
        tipe = st.selectbox(
            "Tipe Transaksi *",
            options=SUPPORTED_TYPES,
            help="Sistem mendukung TRANSFER dan CASH_OUT "
                 "(domain transaksi UMKM digital)"
        )
        amount = st.number_input(
            "Nominal Transaksi (Rp) *",
            min_value=1.0,
            max_value=100_000_000.0,
            value=500_000.0,
            step=1000.0,
            format="%.2f",
            help="Nominal transaksi dalam Rupiah"
        )
        step = st.number_input(
            "Step (Jam ke-) *",
            min_value=1,
            max_value=743,
            value=100,
            help="Waktu transaksi dalam satuan jam (1–743, setara ~30 hari)"
        )

    with col2:
        old_balance_orig = st.number_input(
            "Saldo Awal Pengirim (Rp) *",
            min_value=0.0,
            max_value=500_000_000.0,
            value=2_000_000.0,
            step=1000.0,
            format="%.2f"
        )
        new_balance_orig = st.number_input(
            "Saldo Akhir Pengirim (Rp) *",
            min_value=0.0,
            max_value=500_000_000.0,
            value=1_500_000.0,
            step=1000.0,
            format="%.2f"
        )
        old_balance_dest = st.number_input(
            "Saldo Awal Penerima (Rp) *",
            min_value=0.0,
            max_value=500_000_000.0,
            value=1_000_000.0,
            step=1000.0,
            format="%.2f"
        )
        new_balance_dest = st.number_input(
            "Saldo Akhir Penerima (Rp) *",
            min_value=0.0,
            max_value=500_000_000.0,
            value=1_500_000.0,
            step=1000.0,
            format="%.2f"
        )

    submitted = st.form_submit_button(
        "🔍 Analisis Sekarang",
        use_container_width=True,
        type="primary"
    )

# ─────────────────────────────────────────────
# HASIL SCORING
# ─────────────────────────────────────────────
if submitted:
    with st.spinner("Menghitung anomaly risk score..."):
        result = score_single_transaction(
            step=step,
            transaction_type=tipe,
            amount=amount,
            old_balance_orig=old_balance_orig,
            new_balance_orig=new_balance_orig,
            old_balance_dest=old_balance_dest,
            new_balance_dest=new_balance_dest,
        )

    score  = result['risk_score']
    zone   = result['risk_zone']
    color  = ZONE_COLORS[zone]
    label  = ZONE_LABELS[zone]
    is_ano = result['is_anomaly']
    thr    = result['threshold_used']

    st.divider()
    st.subheader("Hasil Analisis")

    col_score, col_detail, col_gauge = st.columns([1, 1.5, 1.5])

    # ── Kotak skor utama
    with col_score:
        bg_light = color + "22"
        st.markdown(f"""
        <div class="result-box" style="background:{bg_light};
             border: 2px solid {color};">
            <div class="score-big" style="color:{color};">
                {score:.1f}
            </div>
            <div class="zone-label" style="color:{color};">
                {label}
            </div>
            <div style="font-size:0.85rem; color:#555;
                        margin-top:0.5rem;">
                Threshold {tipe}: {thr:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if is_ano:
            st.error("⚠️ Transaksi ini terdeteksi sebagai **ANOMALI**")
        else:
            st.success("✅ Transaksi ini terdeteksi sebagai **NORMAL**")

    # ── Detail fitur turunan
    with col_detail:
        st.markdown("**Fitur Turunan yang Dihitung**")

        err_orig  = result['error_balance_orig']
        err_dest  = result['error_balance_dest']
        amt_ratio = result['amount_ratio']

        st.markdown(f"""
        <div style="background:#F8F9FA; border-radius:8px;
                    padding:1rem; font-size:0.88rem;">
            <div class="detail-row">
                <span>errorBalanceOrig</span>
                <strong>{err_orig:,.2f}</strong>
            </div>
            <div class="detail-row">
                <span>errorBalanceDest</span>
                <strong>{err_dest:,.2f}</strong>
            </div>
            <div class="detail-row">
                <span>amount_ratio</span>
                <strong>{amt_ratio:.4f}</strong>
            </div>
            <div class="detail-row">
                <span>Tipe Transaksi</span>
                <strong>{tipe}</strong>
            </div>
            <div class="detail-row">
                <span>Nominal</span>
                <strong>Rp {amount:,.2f}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Interpretasi fitur turunan
        if abs(err_orig) > amount * 0.1:
            st.warning(
                "⚠️ *errorBalanceOrig* tinggi — "
                "saldo pengirim tidak konsisten dengan nominal transaksi.",
                icon="🔎"
            )

    # ── Gauge chart
    with col_gauge:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Risk Score [0–100]", "font": {"size": 14}},
            number={"font": {"size": 48, "color": color}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar":  {"color": color, "thickness": 0.25},
                "steps": [
                    {"range": [0,  40], "color": "#E8F5E9"},
                    {"range": [40, 70], "color": "#FFFDE7"},
                    {"range": [70, 100], "color": "#FFEBEE"},
                ],
                "threshold": {
                    "line": {"color": "#333", "width": 3},
                    "thickness": 0.75,
                    "value": thr,
                },
            }
        ))
        fig.update_layout(
            height=250,
            margin=dict(t=40, b=10, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            f"Garis vertikal menunjukkan threshold {tipe} = {thr:.2f}"
        )

    # ── Tombol skenario cepat
    st.divider()
    st.subheader("💡 Coba Skenario Ujicoba")
    st.caption("Klik untuk mengisi form dengan data skenario tipikal.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(
            "**Skenario Normal — TRANSFER**\n\n"
            "Nominal: Rp 500.000 | Saldo pengirim cukup | "
            "Saldo konsisten\n\n"
            "_Ekspektasi: Zona Hijau_"
        )
    with c2:
        st.warning(
            "**Skenario Waspada — CASH_OUT**\n\n"
            "Nominal mendekati batas saldo | "
            "Saldo akhir penerima tidak wajar\n\n"
            "_Ekspektasi: Zona Kuning_"
        )
    with c3:
        st.error(
            "**Skenario Fraud — TRANSFER**\n\n"
            "Nominal = saldo pengirim | "
            "Saldo akhir pengirim = 0 | Pola PaySim fraud\n\n"
            "_Ekspektasi: Zona Merah_"
        )
