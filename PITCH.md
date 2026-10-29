# Zeta Innovate submission: ScamShield

**Title:** ScamShield: Explainable AI to Detect UPI and SMS Scams  
**Category:** AI-powered solution  
**One-liner:** A privacy-conscious prototype that estimates message risk, highlights evidence and explains scam patterns in plain language.

## Problem
Fake KYC alerts, UPI “refund” tricks, impersonation and task scams exploit urgency and trust. A user may click a convincing link or share sensitive information before checking whether a message is genuine.

## Solution
ScamShield combines a TF-IDF + Logistic Regression classifier with explainable, India-focused pattern rules. It provides a risk score, a verdict, highlighted warning signs, and practical next steps. The prototype includes a responsive web interface, bulk CSV scanning, and a REST API.

## What is different
1. **Explainability:** shows why a message looks suspicious rather than only providing a label.
2. **Hybrid approach:** combines statistical text features with rule signals for common local fraud patterns.
3. **Safety context:** distinguishes certain legitimate safety warnings from requests for secrets.
4. **Privacy-conscious design:** the API does not intentionally persist message submissions; hosting logs and retention require separate review.

## Evidence and limitations
- Automated test suite covers pattern rules, API behaviour, and security-related responses.
- The Indian-style examples in current evaluation are synthetic and partly aligned with the handcrafted rules; improvements on them may overstate generalisation.
- The hand-written sample is small and not representative of real-world traffic.
- False positives and false negatives remain possible; the model has not been independently validated on a representative, labelled Indian scam dataset.
- English only at present; Hindi, Telugu and Hinglish are future work.

## Demo flow
1. Select the Fake KYC example; explain the highlighted evidence.
2. Select a legitimate bank OTP safety warning and compare.
3. Demonstrate batch CSV scanning and export.
4. Open the accuracy page and openly describe the synthetic-data limitations.
5. Close with safe next steps: verify in the official banking app; if money was lost in India, call 1930 and report at cybercrime.gov.in.

## Claims to make—and avoid
- **Say:** “ScamShield gives an explainable risk assessment and highlights patterns worth checking.”
- **Say:** “The current prototype combines TF-IDF + Logistic Regression with explainable rules.”
- **Say:** “Current metrics are early internal evaluations; independent real-world validation is still needed.”
- **Avoid:** “It detects every scam,” “guaranteed safe,” or “production-grade accuracy.”

## Final checks
Confirm the official submission deadline, rubric, eligibility and required file formats. Run the test suite and smoke-test the live deployment before presenting. Use synthetic messages only.
