from pathlib import Path

import uvicorn as uvicorn
from fastapi import FastAPI
from ms_core import setup_app

from app.settings import db_url

application = FastAPI(
    title="ploshtadka-users-ms",
)

tortoise_conf = setup_app(application, db_url, Path("app") / "routers", ["app.models"])
