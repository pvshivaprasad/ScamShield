from scamshield.rules import analyze, rule_score

def test_kyc_threat_signal():
    signals=analyze("URGENT your SBI account will be blocked today. Complete KYC immediately at https://example.test")
    assert any(s.key=="kyc_block" for s in signals)
    assert rule_score(signals)>0.4

def test_legitimate_otp_warning_not_otp_request():
    signals=analyze("Never share your OTP or UPI PIN with anyone. Your bank will never ask for it.")
    assert not any(s.key=="otp_request" for s in signals)

def test_upi_trick_signal():
    signals=analyze("To receive a refund, enter your UPI PIN and OTP")
    assert any(s.key=="upi_pin" for s in signals)

def test_digital_arrest_signal():
    signals=analyze("Digital arrest notice: pay immediately or face arrest")
    assert any(s.key=="digital_arrest" for s in signals)

def test_link_detected():
    signals=analyze("Verify details at https://example.test")
    assert any(s.key=="link" for s in signals)
