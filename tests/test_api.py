"""
Unit & Integration tests for the SentinelEye Local REST API.
Verifies all FastAPI endpoints for search, change detection, briefing, audit, and mode toggling.
"""

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["air_gap_compliant"] is True
    assert "SentinelEye" in data["service"]


def test_api_scenarios():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 3


def test_api_search():
    payload = {
        "query": "road development along northern ridge",
        "scenario_id": "demo_pair_01_pangong",
        "top_k": 2,
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query_content"] == payload["query"]
    assert len(data["results"]) > 0


def test_api_detect_changes():
    payload = {
        "scenario_id": "demo_pair_01_pangong",
        "use_cva_fallback": False,
    }
    response = client.post("/api/detect-changes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert len(data["records"]) > 0
    assert data["confidence"] > 0.0


def test_api_generate_briefing():
    # Detect changes first to get real change records
    det_resp = client.post("/api/detect-changes", json={"scenario_id": "demo_pair_01_pangong"})
    records = det_resp.json()["records"]

    payload = {
        "facts": records,
        "scenario_id": "demo_pair_01_pangong",
    }
    response = client.post("/api/generate-briefing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "briefing_text" in data
    assert "TACTICAL SATELLITE INTELLIGENCE BRIEF" in data["briefing_text"]


def test_api_audit_commit():
    payload = {
        "change_record_id": "CHG-2026-0042",
        "analyst_id": "ANALYST-DEF-712",
        "decision": "CONFIRMED",
        "priority": "CRITICAL",
        "notes": "Verified against optical baseline.",
    }
    response = client.post("/api/audit/commit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "CONFIRMED"
    assert data["audit_crypto"]["block_index"] >= 1
    assert len(data["audit_crypto"]["signature"]) > 0


def test_api_mode_toggle():
    # Toggle to true
    res1 = client.post("/api/mode/toggle", json={"replay_mode": True})
    assert res1.status_code == 200
    assert res1.json()["replay_mode"] is True

    # Toggle back to false
    res2 = client.post("/api/mode/toggle", json={"replay_mode": False})
    assert res2.status_code == 200
    assert res2.json()["replay_mode"] is False
