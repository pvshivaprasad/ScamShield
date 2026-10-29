"""Hybrid detector: TF-IDF + Logistic Regression blended with explainable rules."""
import re
from pathlib import Path
import joblib
import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from .rules import URL_RE, analyze, rule_score

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "scamshield.joblib"
ML_WEIGHT = 0.6
LEVELS = [(0.70, "HIGH RISK", "Do not click, reply or pay. Verify through your bank's official app. If money was lost in India, report at cybercrime.gov.in or call 1930."),
          (0.45, "SUSPICIOUS", "Verify through the official app or website, or call the number printed on your card."),
          (0.0, "LOOKS SAFE", "No strong scam signals found. This is not a guarantee; never share an OTP or PIN.")]

def combine(ml, rl):
    score = ML_WEIGHT * ml + (1 - ML_WEIGHT) * rl
    if rl >= 0.6:
        score = max(score, rl)
    if rl >= 0.4:
        score = max(score, 0.5)
    return score

def level(score):
    return next((label, advice) for threshold, label, advice in LEVELS if score >= threshold)

class ScamShield:
    def __init__(self):
        self.word = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True)
        self.char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True, max_features=60000)
        self.clf = LogisticRegression(C=8, max_iter=2000, class_weight="balanced")

    def _x(self, texts, fit=False):
        if fit:
            return hstack([self.word.fit_transform(texts), self.char.fit_transform(texts)]).tocsr()
        return hstack([self.word.transform(texts), self.char.transform(texts)]).tocsr()

    def fit(self, texts, y):
        self.clf.fit(self._x(texts, fit=True), y)
        return self

    def ml_proba(self, texts):
        return self.clf.predict_proba(self._x(texts))[:, 1]

    def predict_proba(self, texts):
        ml = self.ml_proba(texts)
        return np.array([combine(float(m), rule_score(analyze(t))) for m, t in zip(ml, texts)])

    def top_words(self, text, k=6):
        coefs = self.clf.coef_[0][:len(self.word.vocabulary_)]
        vec = self.word.transform([text])
        names = self.word.get_feature_names_out()
        contrib = sorted(((names[i], float(vec[0, i] * coefs[i])) for i in vec.indices), key=lambda x: -x[1])
        return [(w, c) for w, c in contrib if c > 0 and not all(t in ENGLISH_STOP_WORDS for t in w.split())][:k]

    def explain(self, text):
        ml = float(self.ml_proba([text])[0])
        sigs = analyze(text)
        rl = rule_score(sigs)
        score = combine(ml, rl)
        label, advice = level(score)
        words = self.top_words(text) if score >= 0.45 else []
        urls = [u.span() for u in URL_RE.finditer(text)]
        word_spans = sorted({m.span() for w, _ in words for m in re.finditer(rf"\b{re.escape(w)}\b", text, re.I)
                             if not any(a <= m.start() and m.end() <= b for a, b in urls)})
        return {"score": round(score, 4), "ml_score": round(ml, 4), "rule_score": round(rl, 4),
                "label": label, "advice": advice, "signals": [s.to_dict() for s in sigs],
                "top_words": [w for w, _ in words], "word_spans": [list(s) for s in word_spans]}

    def score_batch(self, texts):
        ml = self.ml_proba(texts)
        rows = []
        for text, probability in zip(texts, ml):
            sigs = analyze(text)
            score = combine(float(probability), rule_score(sigs))
            rows.append({"score": round(score, 4), "label": level(score)[0], "reason": sigs[0].name if sigs else ""})
        return rows

    def save(self, path=MODEL_PATH):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path=MODEL_PATH):
        # Refit at startup if the model was saved by another sklearn version.
        model = joblib.load(path)
        required = ("word", "char", "clf")
        if any(not hasattr(model, name) for name in required):
            raise ValueError("Saved model is missing required components")
        if not hasattr(model.clf, "multi_class"):
            raise ValueError("Saved LogisticRegression is incompatible; retrain with installed scikit-learn")
        return model
