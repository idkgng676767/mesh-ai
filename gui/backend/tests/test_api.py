from fastapi.testclient import TestClient

import main


def test_login_and_status(monkeypatch):
    async def fake_get_nodes():
        return [{"ram_gb": 8, "current_utilization": 0.5}]

    async def fake_get_current_model():
        return {"id": "qwen-72b", "tier": "72b", "layers": 80}

    monkeypatch.setattr(main, "get_nodes", fake_get_nodes)
    monkeypatch.setattr(main, "get_current_model", fake_get_current_model)

    client = TestClient(main.app)
    login = client.post("/auth/login", json={"username": "alice"})
    assert login.status_code == 200
    token = login.json()["token"]

    status = client.get("/status", headers={"Authorization": f"******"})
    assert status.status_code == 200
    assert status.json()["nodes"] == 1

    model = client.get("/models/current", headers={"Authorization": f"******"})
    assert model.status_code == 200
