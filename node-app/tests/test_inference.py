import pytest

from agent import inference


@pytest.mark.asyncio
async def test_process_layers(tmp_path, monkeypatch):
    async def fake_download(client, model_id, layer_id):
        path = tmp_path / model_id / f"layer-{layer_id}.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"data")
        return str(path)

    monkeypatch.setattr(inference, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(inference, "download_layer", fake_download)

    result = await inference.process_layers("model", 1, 2, None, object())
    assert "L1" in result
    assert "L2" in result
