import os
import sys
import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}/test.db"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import app.settings  # noqa: WPS433
    import app.db  # noqa: WPS433
    import app.main  # noqa: WPS433

    importlib.reload(app.settings)
    importlib.reload(app.db)
    importlib.reload(app.main)

    return TestClient(app.main.app)
