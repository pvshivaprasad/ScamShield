"""Train and evaluate the hybrid detector."""
import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from scamshield.data_gen import build, synthetic, load_real
from scamshield.model import ScamShield

OUT = Path(__file__).parent / "models"


def metrics(y, p, th=0.45):
    pred = (p >= th).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    return {
        "precision": round(precision_score(y, pred, zero_division=0), 4),
        "recall": round(recall_score(y, pred, zero_division=0), 4),
        "f1": round(f1_score(y, pred, zero_division=0), 4),
        "false_positive_rate": round(fp / (fp + tn), 4),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "n": int(len(y)),
    }


def main():
    real_df = load_real(required=False)
    df = build()
    print(
        f"Dataset: {len(df)} messages | real={int((df.source == 'real').sum())} "
        f"synthetic={int((df.source == 'synthetic').sum())} | scam={int(df.label.sum())}"
    )

    tr, te = train_test_split(
        df, test_size=0.25, stratify=df.label, random_state=42
    )
    m = ScamShield().fit(tr.text.tolist(), tr.label.values)
    res = {
        "overall_hybrid": metrics(te.label.values, m.predict_proba(te.text.tolist())),
        "overall_ml_only": metrics(te.label.values, m.ml_proba(te.text.tolist())),
    }

    # Only publish real-data and real-to-synthetic transfer metrics when the
    # real SMS dataset is available. Synthetic-only metrics are not a real-world benchmark.
    real_test = te[te.source == "real"]
    if not real_test.empty:
        res["real_sms_only_hybrid"] = metrics(
            real_test.label.values, m.predict_proba(real_test.text.tolist())
        )

    if not real_df.empty:
        m_real = ScamShield().fit(real_df.text.tolist(), real_df.label.values)
        syn = synthetic(n_each=300, seed=999)
        res["transfer_real_to_indian_hybrid"] = metrics(
            syn.label.values, m_real.predict_proba(syn.text.tolist())
        )
        res["transfer_real_to_indian_ml_only"] = metrics(
            syn.label.values, m_real.ml_proba(syn.text.tolist())
        )

    final = ScamShield().fit(df.text.tolist(), df.label.values)
    final.save()

    manual_path = Path(__file__).parent / "data" / "manual_eval.csv"
    if manual_path.exists():
        import pandas as pd

        manual = pd.read_csv(manual_path)
        res["manual30_ml_only"] = metrics(
            manual.label.values, final.ml_proba(manual.text.tolist())
        )
        res["manual30_hybrid"] = metrics(
            manual.label.values, final.predict_proba(manual.text.tolist())
        )

    OUT.mkdir(exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=2))
    for key, value in res.items():
        if isinstance(value, dict) and "f1" in value:
            print(
                f"{key:34s} P={value['precision']:.3f} R={value['recall']:.3f} "
                f"F1={value['f1']:.3f} FPR={value['false_positive_rate']:.3f} "
                f"(n={value['n']})"
            )


if __name__ == "__main__":
    main()
