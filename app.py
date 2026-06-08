# ============================================================
# app.py — Landing Page Dashboard
# Early Anomaly Risk Scoring UMKM | TKT Level 5
# Politeknik Negeri Bali, 2026
# ============================================================

import streamlit as st
from core.config import RESEARCH_INFO, ZONE_COLORS

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
# CSS kustom — tema profesional penelitian
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Header utama */
    .main-header {
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    .main-header p {
        font-size: 0.95rem;
        opacity: 0.9;
        margin: 0.3rem 0 0 0;
        color: white;
    }
    /* Kartu metrik */
    .metric-card {
        background: white;
        border: 1px solid #E3EAF8;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(21,101,192,0.08);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1565C0;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.3rem;
    }
    .metric-status {
        font-size: 0.75rem;
        color: #43A047;
        font-weight: 600;
        margin-top: 0.2rem;
    }
    /* Kartu fitur navigasi */
    .nav-card {
        background: white;
        border: 1px solid #E3EAF8;
        border-left: 4px solid #1565C0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 4px rgba(21,101,192,0.06);
    }
    .nav-card h4 { margin: 0 0 0.3rem 0; color: #1565C0; }
    .nav-card p  { margin: 0; font-size: 0.85rem; color: #555; }
    /* Badge zona */
    .badge-hijau  { background:#E8F5E9; color:#2E7D32;
                    padding:3px 10px; border-radius:12px;
                    font-size:0.8rem; font-weight:600; }
    .badge-kuning { background:#FFFDE7; color:#F57F17;
                    padding:3px 10px; border-radius:12px;
                    font-size:0.8rem; font-weight:600; }
    .badge-merah  { background:#FFEBEE; color:#C62828;
                    padding:3px 10px; border-radius:12px;
                    font-size:0.8rem; font-weight:600; }
    /* Footer */
    .footer-info {
        background: #F0F4FF;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        font-size: 0.8rem;
        color: #555;
        margin-top: 1.5rem;
    }
    /* Sembunyikan menu bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER UTAMA
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1>🔍 Early Anomaly Risk Scoring UMKM</h1>
    <p>
        Purwarupa Deteksi Anomali Transaksi Keuangan Digital &nbsp;|&nbsp;
        TKT Level 5 &nbsp;|&nbsp; {RESEARCH_INFO['institution']} &nbsp;|&nbsp;
        {RESEARCH_INFO['year']}
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# METRIK KINERJA MODEL — baris pertama
# ─────────────────────────────────────────────
st.subheader("📊 Kinerja Model Tervalidasi")
st.caption(
    "Model Deep Autoencoder Strictly Undercomplete "
    "— divalidasi pada dataset PaySim (~2,77 juta transaksi, "
    "10-fold StratifiedKFold + Wilcoxon Signed-Rank Test)"
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

metrics = [
    (col1, f"{RESEARCH_INFO['auc']:.4f}", "AUC",        "Target ≥ 0.85 ✅"),
    (col2, f"{RESEARCH_INFO['recall']*100:.2f}%","Recall","Target ≥ 70% ✅"),
    (col3, f"{RESEARCH_INFO['fpr']*100:.2f}%",  "FPR",   "Target ≤ 5% ✅"),
    (col4, RESEARCH_INFO['pr_auc_delta'],        "ΔPR-AUC vs IF","Target ≥+10% ✅"),
    (col5, f"{RESEARCH_INFO['std_auc']:.4f}",   "Std AUC K-Fold","Target ≤ 0.03 ✅"),
    (col6, f"{RESEARCH_INFO['wilcoxon_p']:.6f}","Wilcoxon p-value","Target < 0.05 ✅"),
]

for col, val, label, status in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-status">{status}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NAVIGASI HALAMAN
# ─────────────────────────────────────────────
col_nav, col_info = st.columns([3, 2])

with col_nav:
    st.subheader("🗂 Fitur Dashboard")
    st.markdown("""
    <div class="nav-card">
        <h4>📝 Scoring Transaksi</h4>
        <p>Input data transaksi secara manual satu per satu.
        Sistem menghitung <i>early anomaly risk score</i> [0–100]
        dan zona risiko secara real-time.</p>
    </div>
    <div class="nav-card">
        <h4>📊 Monitoring Dashboard</h4>
        <p>Visualisasi distribusi <i>risk score</i>,
        komposisi zona risiko, dan tren anomali
        pada batch transaksi.</p>
    </div>
    <div class="nav-card">
        <h4>📋 Riwayat Transaksi</h4>
        <p>Tabel interaktif seluruh transaksi yang telah di-<i>scoring</i>.
        Tersedia filter zona risiko dan ekspor ke CSV.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info(
        "💡 Gunakan menu di panel kiri untuk berpindah antar halaman.",
        icon="ℹ️"
    )

with col_info:
    st.subheader("🎯 Sistem Zona Risiko")
    st.markdown("""
    <table style="width:100%; border-collapse:collapse;
                  font-size:0.9rem;">
      <tr style="background:#F0F4FF;">
        <th style="padding:8px; text-align:left;">Zona</th>
        <th style="padding:8px; text-align:center;">Skor</th>
        <th style="padding:8px; text-align:left;">Interpretasi</th>
      </tr>
      <tr>
        <td style="padding:8px;">
          <span class="badge-hijau">🟢 Normal</span>
        </td>
        <td style="padding:8px; text-align:center;">0 – 39</td>
        <td style="padding:8px; font-size:0.8rem;">
          Pola transaksi konsisten dengan profil normal UMKM
        </td>
      </tr>
      <tr style="background:#FAFAFA;">
        <td style="padding:8px;">
          <span class="badge-kuning">🟡 Waspada</span>
        </td>
        <td style="padding:8px; text-align:center;">40 – 69</td>
        <td style="padding:8px; font-size:0.8rem;">
          Deviasi sebagian dari pola normal — perlu investigasi
        </td>
      </tr>
      <tr>
        <td style="padding:8px;">
          <span class="badge-merah">🔴 Anomali</span>
        </td>
        <td style="padding:8px; text-align:center;">70 – 100</td>
        <td style="padding:8px; font-size:0.8rem;">
          Pola menyimpang signifikan — indikasi kuat fraud
        </td>
      </tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏗 Arsitektur Model")
    st.code(
        "D=14 → 12 → BN → 8 → BN → 6 → 8 → BN → 12 → BN → 14\n"
        "Loss    : Huber (δ=1.0)\n"
        "RE      : FWRE (data-driven weights)\n"
        "Threshold: Per tipe transaksi (consensus voting)",
        language=None
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="footer-info">
    <strong>Peneliti:</strong> {RESEARCH_INFO['researcher']} &nbsp;|&nbsp;
    <strong>Institusi:</strong> {RESEARCH_INFO['institution']} &nbsp;|&nbsp;
    <strong>Skema:</strong> DIPA Unggulan &nbsp;|&nbsp;
    <strong>Dataset:</strong> PaySim (~6,3 juta transaksi) &nbsp;|&nbsp;
    <strong>Target Luaran:</strong> Jurnal SINTA 2 + HKI Program Komputer
</div>
""", unsafe_allow_html=True)
