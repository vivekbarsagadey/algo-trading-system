import json
from typing import Generator

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.core.database import Base, get_db
from app.main import app
from app.models.strategy import Strategy as StrategyModel
from app.models.user import User as UserModel


@pytest.fixture(scope="session")
def engine(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("db")
    db_file = tmp_dir / "test_db.sqlite"
    url = f"sqlite:///{db_file}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="session")
def db_session(engine) -> Generator:
    """Create a temporary in-memory DB and return a session factory"""
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    yield SessionLocal
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        db = db_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_create_and_list_strategy(client, db_session):
    # create a user API level (in-memory) AND create DB-level user
    payload = {"email": "utest@example.com", "password": "secret", "full_name": "UTest"}
    # patch get_password_hash in auth module to avoid passlib/bcrypt issues in tests
    with patch("app.api.auth.get_password_hash", side_effect=lambda p: f"hashed-{p}"):
        r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 200

    # Insert a DB user directly so Strategy.user_id=1 exists in the DB for constraints
    db = db_session()
    user = UserModel(email="utest@example.com", hashed_password="hashed-secret", full_name="UTest")
    db.add(user)
    db.commit()
    db.close()

    # Create strategy
    create_payload = {
        "name": "test-strategy",
        "strategy_type": "momentum",
        "symbol": "SBIN",
        "parameters": {"lookback": 10},
        "user_id": 1,
    }
    r = client.post("/api/v1/strategies/", json=create_payload)
    assert r.status_code == 200
    strategy = r.json()
    assert strategy["name"] == "test-strategy"

    # List strategies
    r = client.get("/api/v1/strategies/")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list) and len(items) == 1
