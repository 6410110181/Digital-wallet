import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient


from typing import Any, Dict, Optional
from pydantic_settings import SettingsConfigDict

from wallet_app import models, config, main
import pytest
import pytest_asyncio

import pathlib


SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)


@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)

    asyncio.run(models.recreate_table())

    yield app


@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:

    # client = TestClient(app)
    # yield client
    # app.dependency_overrides.clear()
    return AsyncClient(app=app, base_url="http://localhost")


@pytest.fixture(name="session", scope="session")
def get_session() -> models.AsyncSession:
    settings = SettingsTesting()
    models.init_db(settings)
    return models.get_session()


@pytest_asyncio.fixture(name="user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "123456"
    user = models.DBUser(
        username="user1",
        password=password,
        email="test@test.com",
        first_name="Firstname",
        last_name="lastname",
    )
    local_session = await anext(session)

    user.set_password(password)
    local_session.add(user)
    await local_session.commit()
    await local_session.refresh(user)
    return user
