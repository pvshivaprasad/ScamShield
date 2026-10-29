# ScamShield

**Explainable AI for suspicious SMS, WhatsApp and UPI messages.**

ScamShield combines a TF-IDF + Logistic Regression text classifier with explainable, India-focused pattern rules. It returns a risk assessment, shows the warning signs that contributed to the result, and suggests safer next steps.

> **Research prototype:** ScamShield is a decision aid, not a guarantee that a message is safe or fraudulent. Its India-specific evaluation includes synthetic examples and has not been independently validated on a representative real-world Indian scam dataset. Do not use the displayed scores as proof of production accuracy.

## Capabilities

- Single-message analysis with risk level, evidence, and practical advice.
- Explainable signals for common patterns such as fake KYC, UPI PIN tricks, urgency, impersonation, and suspicious links.
- Bulk CSV analysis (up to 2,000 messages per upload).
- REST API and interactive API documentation.
- Responsive light/dark interface.
- Privacy-conscious request handling; submitted messages are not intentionally persisted by the API. Hosting providers may have their own logging/retention policies.

## Run locally (Windows)

1. Install Python 3.12.
2. Download/clone this repository and open its root folder.
3. Run `START_SCAMSHIELD.bat`.
4. Open http://127.0.0.1:8000.

For CLI setup:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Run automated tests with:

```bash
python -m pytest -q
```

## API

- `GET /api/health` — service health
- `POST /api/check` — analyse a message, JSON body: `{"message":"..."}`
- `POST /api/batch` — upload a CSV containing a `text` or `message` column
- `GET /api/metrics` — evaluation metrics
- `GET /docs` — interactive API documentation

## Deploy to Render

The repository includes `render.yaml`. In Render, choose **New + → Blueprint**, connect this repository, and follow the deployment flow. After deployment, verify `/api/health` and `/docs` on the hosted URL. Check the deployment build logs; do not share a public URL until the live service has been smoke-tested.

## Evaluation and limitations

- The rule-based component was designed for common India-specific scam patterns.
- The India-style transfer evaluation is synthetic and partly aligned with the rules, so it can overstate generalisation.
- The hand-written sample is small and not a representative benchmark.
- English-only at present; Hindi, Telugu and Hinglish are not yet supported.
- False positives and false negatives remain possible. Always verify financial requests in the bank's official app or website.

## Safer next steps

Never share OTPs, passwords, UPI PINs, or banking details. If money has been lost to cyber fraud in India, call **1930** and report at https://cybercrime.gov.in.

## Project documents

- `PITCH.md` — Zeta Innovate pitch and demo guidance
- `DEMO_SCRIPT.md` — three-minute demo flow
