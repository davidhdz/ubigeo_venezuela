# docstring this module
"""Module to create the FastAPI application"""

from fastapi import FastAPI
from app.routers import ubigeo_v1


def create_app():
    """
    Create the FastAPI application, attach the UBIGEO VENEZUELA v1 endpoints and return it.

    Returns:
        FastAPI: The FastAPI application.
    """
    ubi_api = FastAPI(
        title="UbiGeo Venezuela API",
        description="## API for ubigeo venezuelan entities",
        version="1.0.0",
        contact={
            "name": "by David Hernández Aponte",
            "url": "https://github.com/davidhdz/ubigeo_venezuela",
        },
        redoc_url=None,
    )
    ubi_api.include_router(ubigeo_v1.router, prefix="/v1")
    return ubi_api


app = create_app()
