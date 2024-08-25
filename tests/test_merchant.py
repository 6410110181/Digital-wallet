from httpx import AsyncClient
from wallet_app import models
import pytest


@pytest.mark.asyncio
async def test_create_merchants(client: AsyncClient, user1: models.DBUser):
    payload = {"name": "merchants", "user_id": user1.id}
    response = await client.post("/merchants", json=payload)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_merchants(client: AsyncClient):
    response = await client.get("/merchants")

    assert response.status_code == 200
