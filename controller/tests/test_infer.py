def test_infer_without_model(client):
    response = client.post("/infer", json={"prompt": "hello"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
