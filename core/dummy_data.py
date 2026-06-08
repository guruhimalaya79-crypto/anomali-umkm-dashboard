# ============================================================
# core/dummy_data.py
# Generator data dummy skenario ujicoba dashboard
# Mereplikasi karakteristik dataset PaySim UMKM:
#   - Hanya TRANSFER dan CASH_OUT
#   - Extreme class imbalance (~1.9% fraud)
#   - Distribusi amount heavy-tailed
#   - Pola saldo fraud: errorBalanceOrig dan errorBalanceDest tinggi
# ============================================================

import numpy as np
import pandas as pd

SEED = 42


def generate_normal_transaction(rng, transaction_type):
    """
    Hasilkan satu transaksi normal yang realistis.
    Karakteristik: saldo konsisten, amount proporsional.
    """
    step = int(rng.integers(1, 743))  # 743 jam = ~30 hari

    # Amount log-normal seperti distribusi PaySim
    amount = float(np.expm1(rng.normal(6.5, 2.0)))
    amount = max(1.0, round(amount, 2))

    # Saldo pengirim: cukup untuk membiayai transaksi
    old_balance_orig = float(round(
        amount * rng.uniform(1.5, 20.0), 2
    ))
    # Saldo akhir pengirim: konsisten (normal)
    new_balance_orig = float(round(
        max(0.0, old_balance_orig - amount), 2
    ))

    # Saldo penerima: variasi normal
    old_balance_dest = float(round(
        abs(rng.normal(50000, 100000)), 2
    ))
    new_balance_dest = float(round(
        old_balance_dest + amount, 2
    ))

    return {
        'step':           step,
        'type':           transaction_type,
        'amount':         amount,
        'oldbalanceOrg':  old_balance_orig,
        'newbalanceOrig': new_balance_orig,
        'oldbalanceDest': old_balance_dest,
        'newbalanceDest': new_balance_dest,
        'isFraud':        0,
    }


def generate_fraud_transaction(rng, transaction_type):
    """
    Hasilkan satu transaksi fraud yang realistis.
    Karakteristik PaySim fraud:
    - newbalanceOrig mendekati 0 (rekening dikuras)
    - newbalanceDest sering 0 (uang dipindah lagi)
    - errorBalanceOrig sangat tinggi
    """
    step = int(rng.integers(1, 743))

    # Fraud cenderung nominal besar
    amount = float(np.expm1(rng.normal(8.5, 1.5)))
    amount = max(1000.0, round(amount, 2))

    # Saldo pengirim: kurang lebih sama dengan amount (rekening dikuras)
    old_balance_orig = float(round(
        amount * rng.uniform(0.95, 1.05), 2
    ))
    # Rekening dikuras habis — ciri khas fraud PaySim
    new_balance_orig = 0.0

    # Pola saldo penerima fraud: sering 0 setelah transaksi
    old_balance_dest = float(round(
        abs(rng.normal(10000, 50000)), 2
    ))
    # Uang sering langsung dipindahkan lagi (newbalanceDest ~= oldbalanceDest)
    new_balance_dest = float(round(
        old_balance_dest * rng.uniform(0.0, 0.3), 2
    ))

    return {
        'step':           step,
        'type':           transaction_type,
        'amount':         amount,
        'oldbalanceOrg':  old_balance_orig,
        'newbalanceOrig': new_balance_orig,
        'oldbalanceDest': old_balance_dest,
        'newbalanceDest': new_balance_dest,
        'isFraud':        1,
    }


def generate_demo_dataset(n_total=200, fraud_rate=0.10, seed=SEED):
    """
    Hasilkan dataset demo untuk halaman monitoring.
    Default: 200 transaksi, 10% fraud (diperbesar dari 1.9%
    agar visualisasi zona lebih menarik untuk demo).

    Parameter:
        n_total    : jumlah transaksi
        fraud_rate : proporsi fraud (0.0–1.0)
        seed       : random seed untuk reproducibility

    Return: DataFrame siap pakai
    """
    rng = np.random.default_rng(seed)
    records = []

    n_fraud  = max(1, int(n_total * fraud_rate))
    n_normal = n_total - n_fraud

    # Distribusi tipe: ~60% TRANSFER, ~40% CASH_OUT (mirip PaySim)
    types_normal = rng.choice(
        ['TRANSFER', 'CASH_OUT'],
        size=n_normal,
        p=[0.6, 0.4]
    )
    types_fraud = rng.choice(
        ['TRANSFER', 'CASH_OUT'],
        size=n_fraud,
        p=[0.5, 0.5]
    )

    for t in types_normal:
        records.append(generate_normal_transaction(rng, t))

    for t in types_fraud:
        records.append(generate_fraud_transaction(rng, t))

    df = pd.DataFrame(records)

    # Acak urutan agar tidak terblok fraud di belakang
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    # Tambah ID transaksi
    df.insert(0, 'transaction_id', [
        f"TXN-{str(i+1).zfill(4)}" for i in range(len(df))
    ])

    return df


def generate_batch_upload_sample(n=50, seed=99):
    """
    Hasilkan sampel CSV untuk fitur upload batch.
    Tanpa kolom isFraud (pengguna tidak tahu label).
    Digunakan sebagai template download di dashboard.
    """
    rng   = np.random.default_rng(seed)
    df    = generate_demo_dataset(n_total=n, fraud_rate=0.12, seed=seed)
    cols  = [
        'transaction_id', 'step', 'type', 'amount',
        'oldbalanceOrg', 'newbalanceOrig',
        'oldbalanceDest', 'newbalanceDest'
    ]
    return df[cols]


def generate_kfold_metrics():
    """
    Data metrik 10-fold dari Sel 37 notebook.
    Digunakan untuk visualisasi stabilitas model di halaman Info Model.
    """
    # Nilai aktual dari output Sel 37
    auc_per_fold = [
        0.9805, 0.9791, 0.9768, 0.9814, 0.9779,
        0.9783, 0.9762, 0.9798, 0.9771, 0.9788,
    ]
    return {
        'fold':    list(range(1, 11)),
        'auc':     auc_per_fold,
        'mean':    float(np.mean(auc_per_fold)),
        'std':     float(np.std(auc_per_fold)),
    }
