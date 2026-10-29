"""ScamShield web app + REST API. Run: python run.py (docs at /docs)."""
import collections
import io
import json
import time
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from scamshield.model import MODEL_PATH, ScamShield

ROOT=Path(__file__).resolve().parent
STATIC=ROOT/"static"
MAX_CHARS,MAX_ROWS,MAX_UPLOAD=2000,2000,2_000_000
RATE_LIMIT,RATE_WINDOW=120,60
app=FastAPI(title="ScamShield API",version="1.0.0",description="Explainable scam-risk assessment for SMS and UPI messages.")
_model=None
_hits=collections.defaultdict(collections.deque)

def model():
    global _model
    if _model is None:
        try:
            _model=ScamShield.load()
        except Exception:
            from train import main
            main()
            _model=ScamShield.load()
    return _model

@app.middleware("http")
async def guard(request: Request,call_next):
    if request.url.path.startswith("/api/"):
        now=time.time()
        key=request.client.host if request.client else "unknown"
        q=_hits[key]
        while q and now-q[0]>RATE_WINDOW: q.popleft()
        if len(q)>=RATE_LIMIT:
            return JSONResponse({"detail":"Too many requests. Please wait a minute and try again."},status_code=429)
        q.append(now)
    response=await call_next(request)
    response.headers.update({"X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"no-referrer",
        "Content-Security-Policy":"default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'"})
    if request.url.path.startswith("/api/"): response.headers["Cache-Control"]="no-store"
    return response

class Check(BaseModel):
    message:str=Field(...,max_length=MAX_CHARS,description="SMS / WhatsApp / UPI message to analyse")

@app.get("/api/health")
def health(): return {"status":"ok","model_loaded":_model is not None}

@app.post("/api/check")
def check(body:Check):
    text=body.message.strip()
    if not text: raise HTTPException(422,"Paste a message to check.")
    return model().explain(text)

@app.post("/api/batch")
async def batch(file:UploadFile=File(...)):
    raw=await file.read(MAX_UPLOAD+1)
    if len(raw)>MAX_UPLOAD: raise HTTPException(413,"File is larger than 2 MB.")
    try: df=pd.read_csv(io.BytesIO(raw))
    except Exception: raise HTTPException(422,"Could not read this file as CSV.")
    cols={str(c).lower().strip():c for c in df.columns}
    col=cols.get("text") or cols.get("message") or (df.columns[0] if len(df.columns)==1 else None)
    if col is None: raise HTTPException(422,"The CSV needs a column named 'text'.")
    texts=df[col].dropna().astype(str).str.slice(0,MAX_CHARS).tolist()[:MAX_ROWS]
    if not texts: raise HTTPException(422,"No messages found in the file.")
    rows=[{"text":t,**r} for t,r in zip(texts,model().score_batch(texts))]
    summary=collections.Counter(r["label"] for r in rows)
    return {"count":len(rows),"truncated":len(df)>MAX_ROWS,"summary":summary,"rows":rows}

@app.get("/api/metrics")
def metrics():
    path=ROOT/"models"/"metrics.json"
    if not path.exists(): model()
    return json.loads(path.read_text())

@app.get("/",include_in_schema=False)
def index(): return FileResponse(STATIC/"index.html")

app.mount("/static",StaticFiles(directory=STATIC),name="static")
