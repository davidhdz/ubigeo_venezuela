#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides a FastAPI router for retrieving data from a JSON file 
containing Venezuelan's administrative divisions (UBIGEO).

It includes the following endpoints:

- `/all`: Returns all the data in the JSON file.
- `/states`: Returns a list of all the state names.
- `/by_id/state/{id}`: Returns the state data by its ID.
- `/by_name/{state}`: Returns the state data by its name.
- `/by_id/municipality/{id}`: Returns the municipality data by its ID.
- `/by_id/parish/{id}`: Returns the parish data by its ID.

The JSON file is located at `/code/app/data/ubigeo_ven.json`.

This module requires the following dependencies:
- fastapi
- unidecode

Example usage:

from fastapi import FastAPI
from app.routers.ubigeo_v1 import ubigeo_v1_router

app = FastAPI()
app.include_router(ubigeo_v1_router, prefix="/v1")
"""

import json

from fastapi import APIRouter
from unidecode import unidecode

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

DATA_FILE = "/code/app/data/ubigeo_ven.json"


def read_json_file(file_path):
    """
    Read the content of a JSON file and return the loaded data.

    **Args**:
        **file_path (str)**: The path to the JSON file.

    **Returns**:
        **dict**: The loaded JSON data, or None if the file is not found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"File not found: {file_path}")
        return None


@router.get("/all", tags=["all data"])
async def get_all():
    """
    A function to retrieve all data.
    """
    return read_json_file(DATA_FILE)


@router.get("/states/", tags=["states"])
async def get_list_states():
    """
    Asynchronous function to retrieve a list of states.

    No parameters.

    **Returns**:
    - **list**: A list of state names.
    """
    states = []
    if json_data := read_json_file(DATA_FILE):
        for item in json_data["estados"]:
            states.append(item["nombre"])
    return states


@router.get("/by_id/state/{state_id}", tags=["states"])
async def get_item_state_by_id(state_id: str):
    """
    An asynchronous function to retrieve the state by ID from the specified JSON file.

    **Args**:
    - **state_id (str)**: The ID of the state to retrieve.

    **Returns**:
    - **dict**: The state information if found, otherwise False.
    """
    if json_data := read_json_file(DATA_FILE):
        for state in json_data["estados"]:
            if state["codigo"] == state_id:
                return state
    return False


@router.get("/by_name/{state_name}", tags=["states"])
async def get_item_state_by_name(state_name: str):
    """
    An asynchronous function to retrieve the state item by name from the JSON data.

    **Parameters**:
    - **state_name (str)**: The name of the state to retrieve.

    **Returns**:
    - **dict**: The state item corresponding to the given state name, or False if not found.
    """
    if json_data := read_json_file(DATA_FILE):
        for state_item in json_data["estados"]:
            if unidecode(state_item["nombre"].lower()) == unidecode(state_name.lower()):
                return state_item
    return False


@router.get("/by_id/municipality/{municipality_id}", tags=["municipalities"])
async def get_item_municipality_by_id(municipality_id: str):
    """
    Asynchronous function to retrieve a municipality by its ID.

    **Args**:
    - **municipality_id (str)**: The ID of the municipality.

    **Returns**:
    - **dict**: The municipality data including its state code.
    - **bool**: False if the municipality data is not found.
    """
    state_code = municipality_id[0:2]
    if state := await get_item_state_by_id(state_id=state_code):
        data = {}
        for municipality in state["municipios"]:
            if municipality["codigo"] == municipality_id:
                data = municipality
                data["codigo_estado"] = state_code
                return data
    return False


@router.get("/by_name/{state_name}/{municipality_name}", tags=["municipalities"])
async def get_item_municipality_by_name(state_name: str, municipality_name: str):
    """
    Asynchronous function to retrieve municipality data by name and state.

    **Args**:
    - **state_name (str)**: The state name.
    - **municipality_name (str)**: The municipality name.

    **Returns**:
    - **dict**: The municipality data including its state code.
    - **bool**: False if the municipality data is not found.
    """
    if state_data := await get_item_state_by_name(state_name=state_name):
        data = {}
        for municipality_item in state_data["municipios"]:
            if unidecode(municipality_item["nombre"].lower()) == unidecode(
                municipality_name.lower()
            ):
                data = municipality_item
                data["codigo_estado"] = municipality_item["codigo"][0:2]
                return municipality_item
            for nombres_alternos in municipality_item["nombres_alternos"]:
                if unidecode(nombres_alternos.lower()) == unidecode(
                    municipality_name.lower()
                ):
                    data = municipality_item
                    data["codigo_estado"] = municipality_item["codigo"][0:2]
                    return municipality_item
    return False


@router.get("/by_id/parish/{parish_id}", tags=["parish"])
async def get_item_parish_by_id(parish_id: str):
    """
    Asynchronous function to retrieve parish data by ID from the specified municipality.

    **Args**:
    - **parish_id (str)**: The ID of the parish to retrieve.

    **Returns**:
    - **dict**: The data of the parish including its municipality and state codes.
    - **bool**: False if the parish data is not found.
    """
    municipality_code = parish_id[0:4] + "00"
    if municipality := await get_item_municipality_by_id(
        municipality_id=municipality_code
    ):
        data = {}
        for parish in municipality["parroquias"]:
            if parish["codigo"] == parish_id:
                data = parish
                data["codigo_municipio"] = municipality_code
                data["codigo_estado"] = municipality["codigo_estado"]
                return data
    return False


@router.get("/by_name/{state_name}/{municipality_name}/{parish_name}", tags=["parish"])
async def get_item_parish(state_name: str, municipality_name: str, parish_name: str):
    """
    Asynchronous function to retrieve parish data based on the state,
    municipality, and parish names.

    **Args**:
    - **state_name (str)**: The name of the state.
    - **municipality_name (str)**: The name of the municipality.
    - **parish_name (str)**: The name of the parish.

    **Returns**:
    - **dict**: The data of the specified parish including its municipality and state codes.
    - **bool**: False if the parish data is not found.
    """
    if municipality_data := await get_item_municipality_by_name(
        state_name=state_name, municipality_name=municipality_name
    ):
        data = {}
        for parish_item in municipality_data["parroquias"]:
            if unidecode(parish_item["nombre"].lower()) == unidecode(
                parish_name.lower()
            ):
                data = parish_item
                data["codigo_municipio"] = municipality_data["codigo"]
                data["codigo_estado"] = municipality_data["codigo_estado"]
                return data
            for nombres_alternos in parish_item["nombres_alternos"]:
                if unidecode(nombres_alternos.lower()) == unidecode(
                    parish_name.lower()
                ):
                    data = parish_item
                    data["codigo_municipio"] = municipality_data["codigo"]
                    data["codigo_estado"] = municipality_data["codigo_estado"]
                    return data
    return False
