# ============================================================
# app.py — Landing Page Dashboard
# Early Anomaly Risk Scoring UMKM | TKT Level 5
# Politeknik Negeri Bali, 2026
# ============================================================

import streamlit as st
from core.config import RESEARCH_INFO

# ─────────────────────────────────────────────
# Konfigurasi halaman — wajib baris pertama
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EARS-UMKM | PNB",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS minimal — hanya untuk elemen yang perlu
# ─────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🔍 Early Anomaly Risk Scoring UMKM")
st.caption(
    f"Purwarupa Deteksi Anomali Transaksi Keuangan Digital  |  "
    f"TKT Level 5  |  {RESEARCH_INFO['institution']}  |  "
    f"{RESEARCH_INFO['year']}"
)
st.divider()

# ─────────────────────────────────────────────
# METRIK KINERJA MODEL — pakai st.metric native
# ─────────────────────────────────────────────
st.subheader("📊 Kinerja Model Tervalidasi")
st.caption(
    "Deep Autoencoder Strictly Undercomplete — divalidasi pada "
    "dataset PaySim (~2,77 juta transaksi), "
    "10-fold StratifiedKFold + Wilcoxon Signed-Rank Test"
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        label="AUC",
        value=f"{RESEARCH_INFO['auc']:.4f}",
        delta="Target ≥ 0.85 ✅"
    )
with col2:
    st.metric(
        label="Recall",
        value=f"{RESEARCH_INFO['recall']*100:.2f}%",
        delta="Target ≥ 70% ✅"
    )
with col3:
    st.metric(
        label="FPR",
        value=f"{RESEARCH_INFO['fpr']*100:.2f}%",
        delta="Target ≤ 5% ✅"
    )
with col4:
    st.metric(
        label="ΔPR-AUC vs IF",
        value=RESEARCH_INFO['pr_auc_delta'],
        delta="Target ≥ +10% ✅"
    )
with col5:
    st.metric(
        label="Std AUC K-Fold",
        value=f"{RESEARCH_INFO['std_auc']:.4f}",
        delta="Target ≤ 0.03 ✅"
    )
with col6:
    st.metric(
        label="Wilcoxon p-value",
        value=f"{RESEARCH_INFO['wilcoxon_p']:.6f}",
        delta="Target < 0.05 ✅"
    )

st.divider()

# ─────────────────────────────────────────────
# NAVIGASI DAN INFO
# ─────────────────────────────────────────────
col_nav, col_zona, col_arch = st.columns(3)

with col_nav:
    st.subheader("🗂 Fitur Dashboard")

    st.info(
        "**📝 Scoring Transaksi**\n\n"
        "Input data transaksi secara manual. "
        "Sistem menghitung *early anomaly risk score* "
        "[0–100] dan zona risiko secara real-time."
    )
    st.success(
        "**📊 Monitoring Dashboard**\n\n"
        "Visualisasi distribusi *risk score*, "
        "komposisi zona risiko, tren anomali, "
        "dan stabilitas model K-Fold."
    )
    st.warning(
        "**📋 Riwayat Transaksi**\n\n"
        "Tabel interaktif dengan filter zona risiko, "
        "upload CSV batch, dan ekspor hasil ke "
        "CSV atau Excel."
    )
    st.caption("💡 Gunakan menu di panel kiri untuk berpindah halaman.")

with col_zona:
    st.subheader("🎯 Sistem Zona Risiko")

    st.success("🟢 **Normal — Skor 0 sampai 39**")
    st.write(
        "Pola transaksi konsisten dengan profil "
        "transaksi normal UMKM digital."
    )

    st.warning("🟡 **Waspada — Skor 40 sampai 69**")
    st.write(
        "Deviasi sebagian dari pola normal. "
        "Perlu investigasi lebih lanjut."
    )

    st.error("🔴 **Anomali — Skor 70 sampai 100**")
    st.write(
        "Pola menyimpang signifikan dari distribusi normal. "
        "Indikasi kuat fraud — tindakan segera diperlukan."
    )

with col_arch:
    st.subheader("🏗 Arsitektur Model")
    st.code(
        "D=14 → 12 → BN → 8 → BN → 6\n"
        "     → 8 → BN → 12 → BN → 14\n\n"
        "Loss      : Huber (δ=1.0)\n"
        "RE        : FWRE data-driven\n"
        "Threshold : Per tipe (consensus)",
        language=None
    )

    st.subheader("📋 Detail Konfigurasi")
    st.write(f"**Loss function:** Huber (δ=1.0)")
    st.write(f"**Bottleneck k:** 6")
    st.write(f"**Input D:** 14 fitur")
    st.write(f"**Threshold TRANSFER:** 96.32")
    st.write(f"**Threshold CASH_OUT:** 69.68")
    st.write(f"**Strategi:** Consensus voting")
    st.write(f"**k_optimal:** 5.0")

st.divider()

# ─────────────────────────────────────────────
# FOOTER INFO
# ─────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.write(f"**Peneliti:** {RESEARCH_INFO['researcher']}")
    st.write(f"**Institusi:** {RESEARCH_INFO['institution']}")
with col_f2:
    st.write("**Skema:** DIPA Unggulan PNB")
    st.write("**Dataset:** PaySim (~6,3 juta transaksi)")
with col_f3:
    st.write("**Target Luaran:** Jurnal SINTA 2")
    st.write("**HKI:** Program Komputer")