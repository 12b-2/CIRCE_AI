from __future__ import annotations

import pytest

import circe_app.auth.database as database
from circe_app.auth.auth_service import AuthError, AuthService
from circe_app.auth.progress_store import ProgressStore
from circe_app.orchestrator import CIRCEOrchestrator


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "circe_test.db")


def test_register_and_login_success() -> None:
    auth = AuthService()
    registered = auth.register("carla", "clave123")
    logged_in = auth.login("carla", "clave123")
    assert registered.id == logged_in.id
    assert logged_in.username == "carla"


def test_register_duplicate_username_rejected() -> None:
    auth = AuthService()
    auth.register("duplicado", "clave123")
    with pytest.raises(AuthError):
        auth.register("duplicado", "otraclave")


def test_login_wrong_password_rejected() -> None:
    auth = AuthService()
    auth.register("pedro", "clave123")
    with pytest.raises(AuthError):
        auth.login("pedro", "clave-equivocada")


def test_login_unknown_user_rejected() -> None:
    auth = AuthService()
    with pytest.raises(AuthError):
        auth.login("inexistente", "cualquiera")


def test_register_rejects_short_password_and_invalid_username() -> None:
    auth = AuthService()
    with pytest.raises(AuthError):
        auth.register("ok", "clave123")  # usuario muy corto
    with pytest.raises(AuthError):
        auth.register("usuariovalido", "123")  # contraseña muy corta


def test_progress_save_and_load_roundtrip() -> None:
    auth = AuthService()
    store = ProgressStore()
    user = auth.register("ana", "clave123")

    orchestrator = CIRCEOrchestrator(level_id="level_1")
    orchestrator.session.score = 42.0
    orchestrator.session.xp = 30
    orchestrator.session.active_node = "node_3"
    store.save_progress(user.id, orchestrator.session)

    loaded = store.load_progress(user.id, "level_1")
    assert loaded is not None
    assert loaded.score == 42.0
    assert loaded.xp == 30
    assert loaded.active_node == "node_3"

    orchestrator_2 = CIRCEOrchestrator(level_id="level_1")
    orchestrator_2.load_session(loaded)
    assert orchestrator_2.current_node == "node_3"


def test_completed_levels_tracking() -> None:
    auth = AuthService()
    store = ProgressStore()
    user = auth.register("luis", "clave123")

    orchestrator = CIRCEOrchestrator(level_id="level_1")
    orchestrator.session.scenario_completed = True
    orchestrator.session.score = 90.0
    store.save_progress(user.id, orchestrator.session)

    completed = store.get_completed_levels(user.id)
    assert completed == {"level_1": 90.0}


def test_load_progress_missing_returns_none() -> None:
    auth = AuthService()
    store = ProgressStore()
    user = auth.register("sin_progreso", "clave123")
    assert store.load_progress(user.id, "level_1") is None
