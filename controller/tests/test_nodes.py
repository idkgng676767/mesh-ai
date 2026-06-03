def test_register_and_list_nodes(client):
    payload = {
        "host": "localhost",
        "port": 9000,
        "ram_gb": 8,
        "cpu_freq_ghz": 3.5,
        "gpu_vram_gb": 0,
        "current_utilization": 0.8,
    }
    response = client.post("/nodes/register", json=payload)
    assert response.status_code == 200

    node_id = response.json()["id"]
    response = client.get(f"/nodes/{node_id}")
    assert response.status_code == 200

    list_response = client.get("/nodes")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
