from fastapi import FastAPI
from app.routers import ubigeo_v1 


def create_app():
    app = FastAPI()

    app.include_router(ubigeo_v1.router, prefix="/v1")

    return app


app = create_app()