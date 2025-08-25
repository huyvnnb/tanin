import uuid

import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from tanin.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_welcome(client):
    resp = await client.get("/")
    data = resp.json()
    expected_fields = {"message"}
    assert resp.status_code == 200

    assert expected_fields.issubset(data.keys())


@pytest.mark.asyncio
async def test_session(client):
    resp = await client.post("/sessions/anonymous")
    data = resp.json()
    expected_fields = {"client_id"}
    client_id = data["client_id"]

    assert resp.status_code == 200
    assert expected_fields.issubset(data.keys())
    assert isinstance(client_id, str)
    assert uuid.UUID(client_id)
