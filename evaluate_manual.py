"""Evaluate the current model on the small hand-written sanity set."""
from pathlib import Path
import pandas as pd
from sklearn.metrics import classification_report,confusion_matrix
from scamshield.model import ScamShield
root=Path(__file__).resolve().parent
data=pd.read_csv(root/"data"/"manual_eval.csv")
model=ScamShield.load()
pred=(model.predict_proba(data.text.astype(str).tolist())>=0.45).astype(int)
print(classification_report(data.label,pred,zero_division=0))
print(confusion_matrix(data.label,pred))
