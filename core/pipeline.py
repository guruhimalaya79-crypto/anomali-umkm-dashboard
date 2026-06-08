# ============================================================
# core/pipeline.py
# Simulasi pipeline scoring FWRE tanpa TensorFlow
# Mereplikasi logika Sel 27A, 29, 33 dari notebook
# Semua operasi menggunakan NumPy murni
# ============================================================

import numpy as np
from core.config import (
    FEATURE_NAMES, FWRE_WEIGHTS, NUMERIC_QT_IDX,
    SCORE_P_LOW, SCORE_P_HIGH,
    THRESHOLD_PER_TYPE,
    ZONE_HIJAU_MAX, ZONE_KUNING_MAX,
)


# ─────────────────────────────────────────────
# FUNGSI 1 — Rekayasa fitur turunan
# Sama persis dengan Sel 18 notebook
# ─────────────────────────────────────────────
def engineer_features(df_raw):
    """
    Hitung tiga fitur turunan dari data transaksi mentah.
    Input : DataFrame dengan kolom standar PaySim
    Output: DataFrame dengan fitur turunan ditambahkan
    """
    import pandas as pd
    df = df_raw.copy()

    # errorBalanceOrig = saldo awal pengirim - nominal - saldo akhir pengirim
    df['errorBalanceOrig'] = (
        df['oldbalanceOrg'] - df['amount'] - df['newbalanceOrig']
    )

    # errorBalanceDest = saldo awal penerima + nominal - saldo akhir penerima
    df['errorBalanceDest'] = (
        df['oldbalanceDest'] + df['amount'] - df['newbalanceDest']
    )

    # amount_ratio = nominal / (saldo awal pengirim + 1)
    # +1 untuk menghindari pembagian nol
    df['amount_ratio'] = df['amount'] / (df['oldbalanceOrg'] + 1.0)

    return df


# ─────────────────────────────────────────────
# FUNGSI 2 — Cyclical temporal encoding
# Sama persis dengan Sel 18 notebook
# step_sin/cos_h: siklus harian (T=24)
# step_sin/cos_w: siklus mingguan (T=168)
# ─────────────────────────────────────────────
def encode_cyclical(df):
    """
    Tambahkan representasi siklus sin/cos pada kolom step.
    Input : DataFrame dengan kolom 'step'
    Output: DataFrame dengan 4 kolom cyclical ditambahkan
    """
    import pandas as pd
    df = df.copy()

    T_HARIAN   = 24.0
    T_MINGGUAN = 168.0

    df['step_sin_h'] = np.sin(2 * np.pi * df['step'] / T_HARIAN)
    df['step_cos_h'] = np.cos(2 * np.pi * df['step'] / T_HARIAN)
    df['step_sin_w'] = np.sin(2 * np.pi * df['step'] / T_MINGGUAN)
    df['step_cos_w'] = np.cos(2 * np.pi * df['step'] / T_MINGGUAN)

    return df


# ─────────────────────────────────────────────
# FUNGSI 3 — One-hot encoding tipe transaksi
# ─────────────────────────────────────────────
def encode_type(df):
    """
    Encode kolom 'type' menjadi dua kolom binary OHE.
    Hanya mendukung TRANSFER dan CASH_OUT.
    """
    df = df.copy()
    df['type_CASH_OUT'] = (df['type'] == 'CASH_OUT').astype(np.float32)
    df['type_TRANSFER'] = (df['type'] == 'TRANSFER').astype(np.float32)
    return df


# ─────────────────────────────────────────────
# FUNGSI 4 — Simulasi QT normalisasi
# Menggunakan z-score sederhana sebagai pengganti
# QuantileTransformer (tidak tersedia tanpa fit data asli)
# Hasilnya deterministik dan cukup untuk demo purwarupa
# ─────────────────────────────────────────────

# Statistik representatif dari dataset PaySim (diekstrak dari notebook)
# Digunakan sebagai pengganti QT yang di-fit pada training set
_QT_STATS = {
    # (mean, std) per fitur — dikalibrasi dari data dummy PaySim
    # amount menggunakan log1p sebelum normalisasi
    'amount':           (6.31,  2.04),
    'oldbalanceOrg':    (46591, 242843),
    'newbalanceOrig':   (42588, 229020),
    'oldbalanceDest':   (89777, 68714),
    'newbalanceDest':   (92767, 70966),
    'errorBalanceOrig': (0.94,  19.21),
    'errorBalanceDest': (1013,  9458),
    'amount_ratio':     (0.156, 0.165),
}


def simulate_qt_transform(X_array):
    """
    Simulasi normalisasi QuantileTransformer menggunakan
    z-score berbasis statistik PaySim.
    Input : array (n, 14) sebelum normalisasi
    Output: array (n, 14) setelah normalisasi
    """
    X_out = X_array.copy().astype(np.float64)

    for local_idx, global_idx in enumerate(NUMERIC_QT_IDX):
        feat = FEATURE_NAMES[global_idx]
        mean, std = _QT_STATS.get(feat, (0.0, 1.0))

        # log1p khusus untuk kolom amount (indeks 0)
        if feat == 'amount':
            X_out[:, global_idx] = np.log1p(
                np.clip(X_out[:, global_idx], 0, None)
            )

        # Z-score normalisasi
        X_out[:, global_idx] = (
            X_out[:, global_idx] - mean
        ) / (std + 1e-8)

    return X_out.astype(np.float32)


# ─────────────────────────────────────────────
# FUNGSI 5 — Simulasi rekonstruksi autoencoder
# Mereplikasi perilaku model: error lebih tinggi
# untuk anomali, lebih rendah untuk normal
# ─────────────────────────────────────────────
def simulate_reconstruction(X_scaled, transaction_type, seed=None):
    """
    Simulasi rekonstruksi autoencoder secara deterministik.
    Model asli: Huber loss, k=6, arsitektur strictly undercomplete.
    Simulasi: bottleneck menyebabkan kompresi informasi;
    anomali menghasilkan RE lebih tinggi karena pola tidak familiar.
    """
    rng = np.random.default_rng(
        seed if seed is not None else 42
    )
    n, d = X_scaled.shape

    # Simulasi efek bottleneck strictly undercomplete
    # Kunci: model terlatih pada data NORMAL saja.
    # Sinyal deteksi = ketidakkonsistenan saldo, bukan besarnya nilai.
    #
    # Proxy deteksi berbasis aturan PaySim fraud:
    #   - newbalanceOrig = 0 padahal transaksi tidak menguras habis → fraud
    #   - newbalanceDest tidak bertambah sesuai amount → fraud
    #   - amount_ratio >> 0.9 (hampir menguras saldo) → waspada/fraud

    n = X_scaled.shape[0]

    # ── Indeks fitur kunci ──
    # [0]=amount, [1]=oldbalOrg, [2]=newbalOrg,
    # [4]=newbalDest, [5]=errOrig, [6]=errDest, [7]=amtRatio
    err_orig   = X_scaled[:, 5]   # errorBalanceOrig (scaled)
    err_dest   = X_scaled[:, 6]   # errorBalanceDest (scaled)
    amt_ratio  = X_scaled[:, 7]   # amount_ratio (scaled)
    new_orig   = X_scaled[:, 2]   # newbalanceOrig (scaled)

    # ── Sinyal anomali: berbasis inkonsistensi saldo ──
    # Nilai KECIL dari errorBalance berarti konsisten → normal
    # Nilai BESAR dari errorBalance berarti inkonsisten → anomali
    # errorBalanceOrig/Dest ter-scale sehingga |nilai| besar = anomali
    inconsistency = (
        0.45 * np.abs(err_orig) +
        0.30 * np.abs(err_dest) +
        0.15 * np.clip(amt_ratio, 0, 3) +
        0.10 * np.clip(-new_orig, 0, 3)   # newbalOrg sangat negatif = fraud
    )

    # ── RE base: noise kecil untuk normal, besar untuk anomali ──
    # Target: normal ~ 0.004–0.010, waspada ~ 0.010–0.016, fraud > 0.016
    noise = rng.standard_normal(n).astype(np.float32) * 0.0015

    re_base = 0.004 + 0.004 * inconsistency + noise
    re_base = np.clip(re_base, 0.001, 0.10).astype(np.float32)

    # ── Rekonstruksi: distribusikan error ke 14 fitur ──
    from core.config import FWRE_WEIGHTS, FEATURE_NAMES as FN
    w = np.array([FWRE_WEIGHTS[f] for f in FN], dtype=np.float32)
    w_norm = w / w.sum()

    sign_noise = rng.choice([-1.0, 1.0], size=X_scaled.shape).astype(np.float32)
    X_hat = X_scaled - (
        re_base[:, np.newaxis] * w_norm[np.newaxis, :] * sign_noise
    )

    return X_hat.astype(np.float32)


# ─────────────────────────────────────────────
# FUNGSI 6 — Hitung FWRE
# Identik dengan Sel 27A notebook
# FWRE = sum(w_j * |x_j - x_hat_j|) / sum(w_j)
# ─────────────────────────────────────────────
def compute_fwre(X_original, X_reconstructed):
    """
    Hitung Feature-Weighted Reconstruction Error per sampel.
    Bobot diambil dari FWRE_WEIGHTS di config.py
    """
    weights = np.array(
        [FWRE_WEIGHTS[f] for f in FEATURE_NAMES],
        dtype=np.float32
    )
    abs_error = np.abs(X_original - X_reconstructed)
    fwre = np.sum(weights * abs_error, axis=1) / weights.sum()
    return fwre.astype(np.float32)


# ─────────────────────────────────────────────
# FUNGSI 7 — Normalisasi ke anomaly score [0–100]
# Identik dengan Sel 29 notebook
# ─────────────────────────────────────────────
def normalize_to_score(re_array):
    """
    Normalisasi array RE ke rentang [0, 100].
    Menggunakan anchor P5 dan P99 dari val normal (freeze_config).
    """
    score = np.clip(
        (re_array - SCORE_P_LOW) / (SCORE_P_HIGH - SCORE_P_LOW + 1e-10),
        0.0, 1.0
    ) * 100.0
    return score.astype(np.float32)


# ─────────────────────────────────────────────
# FUNGSI 8 — Tetapkan zona risiko
# Identik dengan Sel 33 notebook
# ─────────────────────────────────────────────
def assign_zone(scores):
    """
    Tetapkan zona risiko berdasarkan anomaly score.
    Hijau: < 40 | Kuning: 40–70 | Merah: >= 70
    Input : array float atau skalar
    Output: array string zona atau skalar string
    """
    scalar = np.isscalar(scores)
    arr = np.atleast_1d(np.array(scores, dtype=np.float32))
    zones = np.where(
        arr < ZONE_HIJAU_MAX, 'Hijau',
        np.where(arr < ZONE_KUNING_MAX, 'Kuning', 'Merah')
    )
    return zones[0] if scalar else zones


# ─────────────────────────────────────────────
# FUNGSI 9 — Klasifikasi anomali per tipe
# Identik dengan Sel 32 notebook (per_tipe strategy)
# ─────────────────────────────────────────────
def classify_anomaly(scores, transaction_types):
    """
    Klasifikasikan transaksi sebagai anomali atau normal
    menggunakan threshold per tipe transaksi.
    Input : scores (array), transaction_types (array string)
    Output: array int (1=anomali, 0=normal)
    """
    predictions = np.zeros(len(scores), dtype=int)
    for i, (score, ttype) in enumerate(
        zip(scores, transaction_types)
    ):
        thr = THRESHOLD_PER_TYPE.get(ttype, THRESHOLD_PER_TYPE['TRANSFER'])
        predictions[i] = 1 if score >= thr else 0
    return predictions


# ─────────────────────────────────────────────
# FUNGSI 10 — Pipeline end-to-end
# Entry point utama dari halaman Streamlit
# ─────────────────────────────────────────────
def run_scoring_pipeline(df_input):
    """
    Jalankan pipeline scoring lengkap dari data mentah.

    Input : DataFrame dengan kolom:
            step, type, amount,
            oldbalanceOrg, newbalanceOrig,
            oldbalanceDest, newbalanceDest

    Output: DataFrame yang sama + kolom tambahan:
            errorBalanceOrig, errorBalanceDest, amount_ratio,
            risk_score, risk_zone, is_anomaly, threshold_used
    """
    import pandas as pd

    df = df_input.copy()

    # 1. Rekayasa fitur turunan
    df = engineer_features(df)

    # 2. Cyclical encoding
    df = encode_cyclical(df)

    # 3. One-hot encoding tipe
    df = encode_type(df)

    # 4. Susun matriks fitur dengan urutan baku
    X_raw = df[FEATURE_NAMES].values.astype(np.float32)

    # 5. Normalisasi (simulasi QT)
    X_scaled = simulate_qt_transform(X_raw)

    # 6. Simulasi rekonstruksi autoencoder
    X_hat = simulate_reconstruction(X_scaled, df['type'].values)

    # 7. Hitung FWRE
    re_array = compute_fwre(X_scaled, X_hat)

    # 8. Normalisasi ke score [0–100]
    scores = normalize_to_score(re_array)

    # 9. Zona risiko
    zones = assign_zone(scores)

    # 10. Klasifikasi anomali
    predictions = classify_anomaly(scores, df['type'].values)

    # 11. Threshold yang digunakan per transaksi
    thresholds = [
        THRESHOLD_PER_TYPE.get(t, THRESHOLD_PER_TYPE['TRANSFER'])
        for t in df['type'].values
    ]

    # 12. Susun hasil
    df['risk_score']     = np.round(scores, 2)
    df['risk_zone']      = zones
    df['is_anomaly']     = predictions
    df['threshold_used'] = thresholds

    return df


# ─────────────────────────────────────────────
# FUNGSI 11 — Scoring transaksi tunggal
# Untuk halaman input manual
# ─────────────────────────────────────────────
def score_single_transaction(
    step, transaction_type, amount,
    old_balance_orig, new_balance_orig,
    old_balance_dest, new_balance_dest
):
    """
    Scoring satu transaksi dari input form.
    Mengembalikan dict dengan risk_score, zone, is_anomaly.
    """
    import pandas as pd

    df_single = pd.DataFrame([{
        'step':           step,
        'type':           transaction_type,
        'amount':         amount,
        'oldbalanceOrg':  old_balance_orig,
        'newbalanceOrig': new_balance_orig,
        'oldbalanceDest': old_balance_dest,
        'newbalanceDest': new_balance_dest,
    }])

    result_df = run_scoring_pipeline(df_single)
    row = result_df.iloc[0]

    return {
        'risk_score':       float(row['risk_score']),
        'risk_zone':        str(row['risk_zone']),
        'is_anomaly':       int(row['is_anomaly']),
        'threshold_used':   float(row['threshold_used']),
        'error_balance_orig': float(row['errorBalanceOrig']),
        'error_balance_dest': float(row['errorBalanceDest']),
        'amount_ratio':     float(row['amount_ratio']),
    }
