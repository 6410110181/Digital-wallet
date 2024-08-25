from fastapi import FastAPI

from . import config
from . import models

from . import routers


def create_app():
    settings = config.get_settings()
    app = FastAPI()

    models.init_db(settings)

    routers.init_router(app)

    @app.on_event("startup")
    async def on_startup():
        await models.create_all()

    return app
