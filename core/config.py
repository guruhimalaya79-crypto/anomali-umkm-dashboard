# ============================================================
# core/config.py
# Parameter model diekstrak dari Sel 32 notebook
# (sel32_freeze_config — timestamp: 2026-04-16 01:50:38)
# ============================================================

# ─────────────────────────────────────────────
# IDENTITAS PENELITIAN
# ─────────────────────────────────────────────
RESEARCH_INFO = {
    "title":        "Deteksi Anomali Transaksi Keuangan Digital UMKM",
    "subtitle":     "Purwarupa Early Anomaly Risk Scoring — TKT Level 5",
    "model":        "Deep Autoencoder Strictly Undercomplete + FWRE",
    "arch":         "D=14 → 12→BN→8→BN→6→8→BN→12→BN→14",
    "institution":  "Politeknik Negeri Bali",
    "researcher":   "I Made Dwi Jendra Sulastra, S.Kom., M.T.",
    "year":         "2026",
    "auc":          0.9782,
    "recall":       0.8086,
    "fpr":          0.0086,
    "pr_auc_delta": "+21.27%",
    "std_auc":      0.0056,
    "wilcoxon_p":   0.000977,
}

# ─────────────────────────────────────────────
# NAMA FITUR — urutan wajib konsisten dengan model
# [00–07] numerik QT | [08–09] binary OHE | [10–13] cyclical
# ─────────────────────────────────────────────
FEATURE_NAMES = [
    'amount',           # [00] numerik-QT (log1p dulu)
    'oldbalanceOrg',    # [01] numerik-QT
    'newbalanceOrig',   # [02] numerik-QT
    'oldbalanceDest',   # [03] numerik-QT
    'newbalanceDest',   # [04] numerik-QT
    'errorBalanceOrig', # [05] numerik-QT (fitur turunan)
    'errorBalanceDest', # [06] numerik-QT (fitur turunan)
    'amount_ratio',     # [07] numerik-QT (fitur turunan)
    'type_CASH_OUT',    # [08] binary OHE
    'type_TRANSFER',    # [09] binary OHE
    'step_sin_h',       # [10] cyclical harian sin
    'step_cos_h',       # [11] cyclical harian cos
    'step_sin_w',       # [12] cyclical mingguan sin
    'step_cos_w',       # [13] cyclical mingguan cos
]

NUMERIC_QT_IDX = [0, 1, 2, 3, 4, 5, 6, 7]

# ─────────────────────────────────────────────
# BOBOT FWRE — diekstrak dari Sel 27A notebook
# disc_ratio = RE_fraud / RE_normal per fitur
# weight = disc_ratio / sum(disc_ratio) * D
# ─────────────────────────────────────────────
FWRE_WEIGHTS = {
    'amount':           1.6705,
    'oldbalanceOrg':    1.8851,
    'newbalanceOrig':   1.5314,
    'oldbalanceDest':   0.4115,
    'newbalanceDest':   1.1811,
    'errorBalanceOrig': 1.5779,
    'errorBalanceDest': 1.3799,
    'amount_ratio':     0.7587,
    'type_CASH_OUT':    0.8321,
    'type_TRANSFER':    0.8539,
    'step_sin_h':       0.4564,
    'step_cos_h':       0.7045,
    'step_sin_w':       0.4242,
    'step_cos_w':       0.3327,
}

# ─────────────────────────────────────────────
# PARAMETER NORMALISASI SCORE [0–100]
# Mode simulasi: anchor P5–P99 dari RE simulasi
# (Model asli: P_LOW=0.08933, P_HIGH=0.55280)
# Anchor simulasi dikalibrasi dari 1000 sampel normal dummy
# ─────────────────────────────────────────────
SCORE_P_LOW  = 0.00017937   # P5 RE simulasi val normal
SCORE_P_HIGH = 0.00391000   # P75 RE simulasi fraud (kalibrasi zona)

# Anchor model asli (untuk referensi jurnal)
SCORE_P_LOW_ORIGINAL  = 0.08933351933956146
SCORE_P_HIGH_ORIGINAL = 0.5528032779693604

# ─────────────────────────────────────────────
# THRESHOLD PER TIPE TRANSAKSI
# Sumber: freeze_config Sel 32 | consensus voting
# ─────────────────────────────────────────────
THRESHOLD_PER_TYPE = {
    'CASH_OUT': 69.6813735961914,
    'TRANSFER': 96.31692504882812,
}
THRESHOLD_GLOBAL = 100.0

# ─────────────────────────────────────────────
# ZONA RISIKO (Sel 33, T14)
# ─────────────────────────────────────────────
ZONE_HIJAU_MAX  = 40.0
ZONE_KUNING_MAX = 70.0

ZONE_COLORS = {
    'Hijau':  '#43A047',
    'Kuning': '#F9A825',
    'Merah':  '#D32F2F',
}

ZONE_LABELS = {
    'Hijau':  '🟢 Normal',
    'Kuning': '🟡 Waspada',
    'Merah':  '🔴 Anomali',
}

SUPPORTED_TYPES = ['TRANSFER', 'CASH_OUT']
