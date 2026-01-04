import os
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

# Ensure a default DB URL for tests before importing app modules.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.main import app
from app.core.database import get_session


@pytest.fixture
def engine():
    # StaticPool keeps the same in-memory DB across connections.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_post_buy_success(client):
    payload = {
        "asset_id": "ETF123",
        "operation_type": "BUY",
        "quantity": 10,
        "price": 100,
        "currency": "USD",
        "trade_date": "2024-01-10",
    }
    resp = client.post("/transactions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["asset_id"] == "ETF123"
    assert data["operation_type"] == "BUY"
    assert "id" in data


def test_post_future_date_rejected(client):
    future_date = (date.today() + timedelta(days=1)).isoformat()
    payload = {
        "asset_id": "ETF123",
        "operation_type": "BUY",
        "quantity": 1,
        "price": 10,
        "currency": "USD",
        "trade_date": future_date,
    }
    resp = client.post("/transactions", json=payload)
    assert resp.status_code == 400
    assert resp.json()["code"] == "domain_error"


def test_sell_over_position_rejected(client):
    buy_payload = {
        "asset_id": "ETF123",
        "operation_type": "BUY",
        "quantity": 5,
        "price": 10,
        "currency": "USD",
        "trade_date": "2024-01-10",
    }
    client.post("/transactions", json=buy_payload)

    sell_payload = {
        "asset_id": "ETF123",
        "operation_type": "SELL",
        "quantity": 10,
        "price": 10,
        "currency": "USD",
        "trade_date": "2024-01-11",
    }
    resp = client.post("/transactions", json=sell_payload)
    assert resp.status_code == 400
    assert resp.json()["code"] == "domain_error"


def test_get_returns_inserted(client):
    payload = {
        "asset_id": "ETF999",
        "operation_type": "BUY",
        "quantity": 2,
        "price": 50,
        "currency": "USD",
        "trade_date": "2024-01-10",
    }
    client.post("/transactions", json=payload)
    resp = client.get("/transactions", params={"skip": 0, "limit": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert any(item["asset_id"] == "ETF999" for item in data)


def test_delete_transaction_success(client):
    payload = {
        "asset_id": "ETFDEL",
        "operation_type": "BUY",
        "quantity": 1,
        "price": 10,
        "currency": "USD",
        "trade_date": "2024-01-10",
    }
    created = client.post("/transactions", json=payload).json()
    tx_id = created["id"]

    resp_delete = client.delete(f"/transactions/{tx_id}")
    assert resp_delete.status_code == 204

    resp_list = client.get("/transactions").json()
    assert all(item["id"] != tx_id for item in resp_list)


def test_delete_transaction_not_found(client):
    resp = client.delete("/transactions/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == "not_found"


def test_events_published_in_memory(client, monkeypatch):
    # Clear in-memory bus
    from app.core import events
    events.event_bus.clear()

    payload = {
        "asset_id": "EVT1",
        "operation_type": "BUY",
        "quantity": 1,
        "price": 1,
        "currency": "USD",
        "trade_date": "2024-01-10",
    }
    created = client.post("/transactions", json=payload).json()
    tx_id = created["id"]

    client.delete(f"/transactions/{tx_id}")

    evts = events.event_bus.list_events()
    names = [e.name for e in evts]
    assert "TransactionCreated" in names
    assert "TransactionDeleted" in names


def test_idempotency_key_returns_same_transaction(client):
    payload = {
        "asset_id": "ETF777",
        "operation_type": "BUY",
        "quantity": 1,
        "price": 10,
        "currency": "USD",
        "trade_date": "2024-01-10",
    }
    headers = {"Idempotency-Key": "demo-key"}
    resp1 = client.post("/transactions", json=payload, headers=headers)
    resp2 = client.post("/transactions", json=payload, headers=headers)

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["id"] == resp2.json()["id"]
