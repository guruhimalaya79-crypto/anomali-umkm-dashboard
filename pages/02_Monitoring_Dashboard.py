# ============================================================
# pages/02_Monitoring_Dashboard.py
# Monitoring batch transaksi + visualisasi distribusi
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.config import ZONE_COLORS, ZONE_LABELS, RESEARCH_INFO
from core.pipeline import run_scoring_pipeline
from core.dummy_data import generate_demo_dataset, generate_kfold_metrics

st.set_page_config(
    page_title="Monitoring Dashboard | EARS-UMKM",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .kpi-card {
        background:white; border:1px solid #E3EAF8;
        border-radius:10px; padding:1rem;
        text-align:center;
        box-shadow:0 2px 6px rgba(21,101,192,0.07);
    }
    .kpi-val  { font-size:2.2rem; font-weight:700; }
    .kpi-lbl  { font-size:0.8rem; color:#666; margin-top:3px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 📊 Monitoring Dashboard")
st.caption(
    "Analisis distribusi *risk score* dan zona risiko "
    "pada batch transaksi."
)
st.divider()

# ─────────────────────────────────────────────
# PANEL KONTROL — sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Pengaturan Demo")
    n_transaksi = st.slider(
        "Jumlah Transaksi", 50, 500, 200, step=50
    )
    fraud_rate = st.slider(
        "Proporsi Fraud Demo (%)", 5, 30, 10, step=5
    )
    seed_val = st.number_input(
        "Random Seed", value=42, min_value=1
    )
    refresh = st.button(
        "🔄 Generate Ulang Data", use_container_width=True
    )

# ─────────────────────────────────────────────
# GENERATE DAN SCORING DATA DEMO
# ─────────────────────────────────────────────
cache_key = f"{n_transaksi}_{fraud_rate}_{seed_val}"

if 'last_key' not in st.session_state or \
   st.session_state.last_key != cache_key or refresh:

    with st.spinner("Memuat dan men-scoring data transaksi..."):
        df_raw = generate_demo_dataset(
            n_total=n_transaksi,
            fraud_rate=fraud_rate / 100.0,
            seed=int(seed_val)
        )
        df = run_scoring_pipeline(df_raw)

    st.session_state.df_scored  = df
    st.session_state.last_key   = cache_key

df = st.session_state.df_scored

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
n_total   = len(df)
n_anomali = int(df['is_anomaly'].sum())
n_waspada = int((df['risk_zone'] == 'Kuning').sum())
n_normal  = int((df['risk_zone'] == 'Hijau').sum())
avg_score = float(df['risk_score'].mean())
max_score = float(df['risk_score'].max())

cols = st.columns(6)
kpis = [
    (cols[0], str(n_total),            "Total Transaksi",    "#1565C0"),
    (cols[1], str(n_normal),           "🟢 Normal",           "#43A047"),
    (cols[2], str(n_waspada),          "🟡 Waspada",          "#F9A825"),
    (cols[3], str(n_anomali),          "🔴 Anomali",          "#D32F2F"),
    (cols[4], f"{avg_score:.1f}",      "Rata-rata Score",    "#1565C0"),
    (cols[5], f"{max_score:.1f}",      "Score Tertinggi",    "#D32F2F"),
]
for col, val, lbl, clr in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val" style="color:{clr};">{val}</div>
            <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BARIS VISUALISASI 1 — Distribusi + Donut
# ─────────────────────────────────────────────
col_hist, col_donut = st.columns([3, 2])

with col_hist:
    st.subheader("Distribusi Risk Score")

    # Pisahkan normal vs fraud (berdasarkan isFraud dari data dummy)
    df_normal = df[df['isFraud'] == 0]
    df_fraud  = df[df['isFraud'] == 1]

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df_normal['risk_score'],
        name="Normal",
        marker_color=ZONE_COLORS['Hijau'],
        opacity=0.7,
        nbinsx=30,
    ))
    fig_hist.add_trace(go.Histogram(
        x=df_fraud['risk_score'],
        name="Fraud (ground truth)",
        marker_color=ZONE_COLORS['Merah'],
        opacity=0.7,
        nbinsx=30,
    ))
    # Garis threshold
    fig_hist.add_vline(
        x=40, line_dash="dash",
        line_color=ZONE_COLORS['Kuning'],
        annotation_text="Batas Waspada (40)",
        annotation_position="top"
    )
    fig_hist.add_vline(
        x=70, line_dash="dash",
        line_color=ZONE_COLORS['Merah'],
        annotation_text="Batas Anomali (70)",
        annotation_position="top"
    )
    fig_hist.update_layout(
        barmode="overlay",
        height=320,
        xaxis_title="Risk Score [0–100]",
        yaxis_title="Jumlah Transaksi",
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=40, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_donut:
    st.subheader("Komposisi Zona Risiko")

    zone_counts = df['risk_zone'].value_counts()
    labels = []
    values = []
    colors = []
    for z in ['Hijau', 'Kuning', 'Merah']:
        labels.append(ZONE_LABELS[z])
        values.append(int(zone_counts.get(z, 0)))
        colors.append(ZONE_COLORS[z])

    fig_donut = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker_colors=colors,
        textinfo="label+percent",
        textfont_size=12,
    ))
    fig_donut.update_layout(
        height=320,
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{n_total}</b><br>Transaksi",
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False
        )]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ─────────────────────────────────────────────
# BARIS VISUALISASI 2 — Bar 30 sampel + Box plot
# ─────────────────────────────────────────────
col_bar, col_box = st.columns([3, 2])

with col_bar:
    st.subheader("30 Transaksi Terakhir")

    df_show = df.tail(30).copy()
    bar_colors = [
        ZONE_COLORS[z] for z in df_show['risk_zone']
    ]
    # Tandai fraud dengan simbol bintang
    fraud_marks = [
        "★" if f == 1 else ""
        for f in df_show['isFraud']
    ]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=list(range(len(df_show))),
        y=df_show['risk_score'],
        marker_color=bar_colors,
        text=fraud_marks,
        textposition="outside",
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Tipe: %{customdata[1]}<br>"
            "Score: %{y:.1f}<br>"
            "Zona: %{customdata[2]}<br>"
            "<extra></extra>"
        ),
        customdata=df_show[
            ['transaction_id', 'type', 'risk_zone']
        ].values,
    ))
    fig_bar.add_hline(
        y=40, line_dash="dot",
        line_color=ZONE_COLORS['Kuning'], line_width=1.5
    )
    fig_bar.add_hline(
        y=70, line_dash="dot",
        line_color=ZONE_COLORS['Merah'], line_width=1.5
    )
    fig_bar.update_layout(
        height=320,
        xaxis_title="Indeks Transaksi",
        yaxis_title="Risk Score",
        yaxis_range=[0, 110],
        margin=dict(t=20, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption("★ = Fraud berdasarkan label data demo")

with col_box:
    st.subheader("Sebaran Score per Tipe")

    fig_box = go.Figure()
    for tipe in ['TRANSFER', 'CASH_OUT']:
        df_t = df[df['type'] == tipe]
        if len(df_t) > 0:
            fig_box.add_trace(go.Box(
                y=df_t['risk_score'],
                name=tipe,
                boxmean='sd',
                marker_color=(
                    "#1565C0" if tipe == 'TRANSFER'
                    else "#F57F17"
                ),
            ))
    fig_box.add_hline(
        y=70, line_dash="dash",
        line_color=ZONE_COLORS['Merah'],
        annotation_text="Batas Anomali"
    )
    fig_box.update_layout(
        height=320,
        yaxis_title="Risk Score [0–100]",
        margin=dict(t=20, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ─────────────────────────────────────────────
# BARIS VISUALISASI 3 — Stabilitas K-Fold AUC
# ─────────────────────────────────────────────
st.divider()
st.subheader("📈 Stabilitas Model — 10-Fold StratifiedKFold")
st.caption(
    "AUC per fold dari validasi silang 10-fold "
    "(Sel 37 notebook). Std AUC = 0.0056 ≤ 0.03 ✅"
)

kfold = generate_kfold_metrics()

fig_kfold = go.Figure()
fig_kfold.add_trace(go.Bar(
    x=[f"Fold {i}" for i in kfold['fold']],
    y=kfold['auc'],
    marker_color=[
        "#1565C0" if v >= 0.97 else "#42A5F5"
        for v in kfold['auc']
    ],
    text=[f"{v:.4f}" for v in kfold['auc']],
    textposition="outside",
))
fig_kfold.add_hline(
    y=kfold['mean'],
    line_dash="dash",
    line_color="#D32F2F",
    annotation_text=f"Mean AUC = {kfold['mean']:.4f}",
    annotation_position="right",
)
fig_kfold.add_hline(
    y=0.85,
    line_dash="dot",
    line_color="#F9A825",
    annotation_text="Target ≥ 0.85",
    annotation_position="right",
)
fig_kfold.update_layout(
    height=300,
    yaxis_title="AUC",
    yaxis_range=[0.95, 0.99],
    margin=dict(t=20, b=40, l=40, r=100),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_kfold, use_container_width=True)

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Mean AUC", f"{kfold['mean']:.4f}", "Target ≥ 0.85 ✅")
with col_m2:
    st.metric("Std AUC",  f"{kfold['std']:.4f}",  "Target ≤ 0.03 ✅")
with col_m3:
    st.metric("Wilcoxon p", f"{RESEARCH_INFO['wilcoxon_p']:.6f}",
              "Target < 0.05 ✅")
