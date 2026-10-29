"""Build training data from the public SMS spam TSV plus synthetic India-style examples."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent.parent

def load_real():
    path=ROOT/"data"/"sms_spam_raw.tsv"
    if not path.exists():
        raise FileNotFoundError(f"Required training data not found: {path}")
    df=pd.read_csv(path,sep="\t",header=None,names=["label","text"],encoding="latin-1",on_bad_lines="skip")
    df=df.dropna(subset=["text"])
    df["label"]=(df["label"].astype(str).str.strip().str.lower().isin(["spam","1","scam"])).astype(int)
    df["source"]="real"
    return df[["text","label","source"]]

def synthetic(n_each=600,seed=42):
    import random
    r=random.Random(seed)
    scams=[
      "URGENT your SBI account will be blocked today complete KYC at {url}",
      "To receive your UPI refund share OTP and UPI PIN now",
      "Digital arrest notice pay penalty immediately or police will arrest you",
      "Congratulations you won {money} in lottery pay processing fee to claim prize",
      "Work from home job guaranteed daily income pay registration fee {money}",
      "Your bank account is suspended verify password and OTP at {url}",
      "Your electricity connection will be disconnected today pay immediately at {url}",
      "Loan approved instantly pay advance release charge {money}",
      "Customer support needs remote access install AnyDesk and share screen",
      "Your parcel is held pay small customs fee at {url}",
    ]
    safe=[
      "Dear customer your account ending {digits} was debited by {money}. If this was not you contact the bank using the official app.",
      "Never share your OTP or UPI PIN with anyone. Your bank will never ask for it.",
      "Dear students the project review begins tomorrow at 10 AM in the computer science department.",
      "Your order has shipped. Open the official shopping application to track delivery.",
      "Your interview is scheduled for Friday. Please check the official email for details.",
      "Your bill is due soon. Please use the official electricity board app or website to pay.",
      "You paid {money} to the merchant through UPI. Check your banking app for transaction details.",
      "Your appointment is confirmed. Reply to the clinic using its official contact number if you need help.",
      "Your salary has been credited. Open your bank application to view the balance.",
      "Do not share your password, PIN or OTP with anyone, even if they claim to be from the bank.",
    ]
    urls=["http://verify-account.example.test","https://claim-prize.example.test","http://kyc-update.example.test"]
    money=["Rs 499","Rs 2500","Rs 15000","Rs 750"]
    rows=[]
    for i in range(n_each):
      rows.append((r.choice(scams).format(url=r.choice(urls),money=r.choice(money),digits=r.randint(1000,9999)),1,"synthetic"))
      rows.append((r.choice(safe).format(url=r.choice(urls),money=r.choice(money),digits=r.randint(1000,9999)),0,"synthetic"))
    return pd.DataFrame(rows,columns=["text","label","source"])

def build():
    df=pd.concat([load_real(),synthetic()],ignore_index=True)
    df["text"]=df["text"].astype(str).str.strip()
    return df.drop_duplicates(subset=["text"]).reset_index(drop=True)
