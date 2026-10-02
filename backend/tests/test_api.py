import os
os.environ["MOCK_MODE"]="true"
os.environ["DATABASE_URL"]="sqlite:///./test_opspilot.db"
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'
def test_agent_run():
    r=client.post('/api/runs',json={'message':'Investigate the payments API latency incident.'})
    assert r.status_code==200; b=r.json(); assert b['thread_id']; assert b['response']['title']=='Investigation complete'; assert len(b['plan'])>=3
