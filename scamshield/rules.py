"""Explainable pattern rules for common SMS/UPI scam indicators."""
from dataclasses import dataclass
import re

URL_RE = re.compile(r"""(?:https?://|www\.)[^\s<>"']+""", re.I)

@dataclass
class Signal:
    key: str
    name: str
    detail: str
    strength: str
    spans: list
    def to_dict(self):
        return {"key": self.key, "name": self.name, "detail": self.detail, "strength": self.strength,
                "spans": [list(s) for s in self.spans]}

def _spans(text, patterns):
    found=[]
    for p in patterns:
        found.extend(m.span() for m in re.finditer(p, text, re.I))
    return sorted(set(found))

def analyze(text):
    signals=[]
    def add(key,name,detail,strength,patterns):
        spans=_spans(text,patterns)
        if spans: signals.append(Signal(key,name,detail,strength,spans))
    sharing = not re.search(r"\b(?:do not|don't|never|never ever|not)\s+(?:share|reveal|tell|send|provide|disclose)\b", text, re.I)
    add("kyc_block","Fake KYC / account-block threat","KYC update used as a threat to block your account","strong",[r"\bKYC\b",r"\b(?:account|card|SIM)\s+(?:will be|has been|is)\s+(?:blocked|suspended|deactivated)\b"])
    add("otp_request","OTP or verification-code request","Requests a one-time code or verification code","strong",[r"\b(?:share|send|tell|provide|enter|submit)\s+(?:your\s+)?(?:OTP|one[- ]time password|verification code)\b"] if sharing else [])
    add("upi_pin","UPI PIN trick","A UPI PIN is requested to receive money or release a refund","strong",[r"\bUPI PIN\b",r"\b(?:receive|get|claim)\s+(?:money|payment|refund).{0,60}\b(?:PIN|OTP)\b"] if sharing else [r"\bUPI PIN\b"] if re.search(r"\b(?:receive|get|claim)\b",text,re.I) else [])
    add("digital_arrest","Digital-arrest / authority threat","Uses arrest or police threats to pressure the recipient","strong",[r"\bdigital arrest\b",r"\b(?:face arrest|arrest warrant|police case|cyber crime department)\b"])
    add("advance_fee","Advance-fee demand","Requests an advance fee for a prize, job, loan or reward","strong",[r"\b(?:registration|processing|release|refundable) fee\b",r"\bpay\s+(?:now|immediately|first)\b"])
    add("urgency","Urgency pressure","Pressure phrases encourage rushed action","moderate",[r"\bURGENT\b",r"\bimmediately\b",r"\bact now\b",r"\bwithin (?:\d+|\w+) hours?\b",r"\bexpires? today\b"])
    add("brand_fake_link","Brand + unofficial link","Mentions a financial brand alongside a link that needs checking","strong",[r"\b(?:SBI|HDFC|ICICI|Axis|Paytm|PhonePe|Google Pay|Airtel|Jio)\b",r"https?://[^\s]+"])
    add("link","Contains a link","A link is present; check its domain independently","weak",[r"""(?:https?://|www\.)[^\s<>"']+"""])
    add("prize","Unsolicited prize or guaranteed reward","Promises an unexpected prize or guaranteed return","moderate",[r"\b(?:you have won|congratulations.{0,30}won|lucky draw|guaranteed returns?)\b"])
    add("remote_access","Remote-access request","Requests an app or remote-access action that could expose your device","moderate",[r"\b(?:install|download)\s+(?:anydesk|teamviewer|remote access)\b",r"\bshare your screen\b"])
    add("task_scam","Task / work-from-home offer","Unsolicited work promises paired with fees or guaranteed income","moderate",[r"\bwork from home\b",r"\b(?:daily income|easy money|task job)\b"])
    return signals

def rule_score(signals):
    if not signals: return 0.0
    weights={"strong":0.68,"moderate":0.35,"weak":0.12}
    remaining=1.0
    for s in signals:
        remaining *= 1.0-weights.get(s.strength,0.1)
    score=1.0-remaining
    if len([s for s in signals if s.strength=="strong"])>=2: score=max(score,0.67)
    return min(1.0,score)
