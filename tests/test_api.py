from fastapi.testclient import TestClient
import api

client=TestClient(api.app)

def test_health():
    r=client.get("/api/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_home_served():
    r=client.get("/")
    assert r.status_code==200
    assert "ScamShield" in r.text

def test_empty_message_rejected():
    r=client.post("/api/check",json={"message":"   "})
    assert r.status_code==422

def test_message_length_validation():
    r=client.post("/api/check",json={"message":"x"*2001})
    assert r.status_code==422

def test_security_headers():
    r=client.get("/")
    assert r.headers.get("X-Frame-Options")=="DENY"
    assert "nosniff" in r.headers.get("X-Content-Type-Options","")

def test_metrics_endpoint_exists():
    r=client.get("/api/metrics")
    assert r.status_code in (200,500)
