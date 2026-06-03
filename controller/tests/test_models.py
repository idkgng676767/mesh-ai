def test_model_activation(client):
    model_payload = {
        "id": "qwen-72b",
        "tier": "72b",
        "parameters": 72000000000,
        "size_gb": 144,
        "layers": 80,
        "url": "https://example.com/qwen",
    }
    response = client.post("/models", json=model_payload)
    assert response.status_code == 200

    response = client.post("/models/activate", json={"model_id": "qwen-72b"})
    assert response.status_code == 200

    response = client.get("/current-model")
    assert response.status_code == 200
    assert response.json()["id"] == "qwen-72b"
