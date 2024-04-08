#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI
import json
from unidecode import unidecode
from fastapi import APIRouter

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

DATA_FILE = "/code/app/data/ubigeo_ven.json"

import json


def read_json_file(file_path):
    """
    Read the content of a JSON file and return the loaded data.

    **Args**:
        **file_path (str)**: The path to the JSON file.

    **Returns**:
        **dict**: The loaded JSON data, or None if the file is not found.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
        return None


@router.get("/all", tags=["all data"])
async def getAll():
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


@router.get("/by_id/state/{id}", tags=["states"])
async def get_item_state_by_id(id: str):
    """
    An asynchronous function to retrieve the state by ID from the specified JSON file.

    **Args**:
    - **id (str)**: The ID of the state to retrieve.

    **Returns**:
    - **dict**: The state information if found, otherwise False.
    """
    if json_data := read_json_file(DATA_FILE):
        for state in json_data["estados"]:
            if state["codigo"] == id:
                return state
    return False


@router.get("/by_name/{state}", tags=["states"])
async def get_item_state_by_name(state: str):
    """
    An asynchronous function to retrieve the state item by name from the JSON data.

    **Parameters**:
    - **state (str)**: The name of the state to retrieve.

    **Returns**:
    - **dict**: The state item corresponding to the given state name, or False if not found.
    """
    if json_data := read_json_file(DATA_FILE):
        for state_item in json_data["estados"]:
            if unidecode(state_item["nombre"].lower()) == unidecode(state.lower()):
                return state_item
    return False


@router.get("/by_id/municipality/{id}", tags=["municipalities"])
async def get_item_municipality_by_id(id: str):
    """
    Asynchronous function to retrieve a municipality by its ID.

    **Args**:
    - **id (str)**: The ID of the municipality.

    **Returns**:
    - **dict**: The municipality data including its state code.
    - **bool**: False if the municipality data is not found.
    """
    state_code = id[0:2]
    if state := await get_item_state_by_id(id=state_code):
        data = {}
        for municipality in state["municipios"]:
            if municipality["codigo"] == id:
                data = municipality
                data["codigo_estado"] = state_code
                return data
    return False


@router.get("/by_name/{state}/{municipality}", tags=["municipalities"])
async def get_item_municipality_by_name(state: str, municipality: str):
    """
    Asynchronous function to retrieve municipality data by name and state.

    **Args**:
    - **state (str)**: The state name.
    - **municipality (str)**: The municipality name.

    **Returns**:
    - **dict**: The municipality data including its state code.
    - **bool**: False if the municipality data is not found.
    """
    if state_data := await get_item_state_by_name(state=state):
        data = {}
        for municipality_item in state_data["municipios"]:
            if unidecode(municipality_item["nombre"].lower()) == unidecode(
                municipality.lower()
            ):
                data = municipality_item
                data["codigo_estado"] = municipality_item["codigo"][0:2]
                return municipality_item
            else:
                for nombres_alternos in municipality_item["nombres_alternos"]:
                    if unidecode(nombres_alternos.lower()) == unidecode(
                        municipality.lower()
                    ):
                        data = municipality_item
                        data["codigo_estado"] = municipality_item["codigo"][0:2]
                        return municipality_item
    return False


@router.get("/by_id/parish/{id}", tags=["parish"])
async def get_item_parish_by_id(id: str):
    """
    Asynchronous function to retrieve parish data by ID from the specified municipality.

    **Args**:
    - **id (str)**: The ID of the parish to retrieve.

    **Returns**:
    - **dict**: The data of the parish including its municipality and state codes.
    - **bool**: False if the parish data is not found.
    """
    municipality_code = id[0:4] + "00"
    if municipality := await get_item_municipality_by_id(id=municipality_code):
        data = {}
        for parish in municipality["parroquias"]:
            if parish["codigo"] == id:
                data = parish
                data["codigo_municipio"] = municipality_code
                data["codigo_estado"] = municipality["codigo_estado"]
                return data
    return False


@router.get("/by_name/{state}/{municipality}/{parish}", tags=["parish"])
async def get_item_parish(state: str, municipality: str, parish: str):
    """
    Asynchronous function to retrieve parish data based on the state, municipality, and parish names.

    **Args**:
    - **state (str)**: The name of the state.
    - **municipality (str)**: The name of the municipality.
    - **parish (str)**: The name of the parish.

    **Returns**:
    - **dict**: The data of the specified parish including its municipality and state codes.
    - **bool**: False if the parish data is not found.
    """
    if municipality_data := await get_item_municipality_by_name(
        state=state, municipality=municipality
    ):
        data = {}
        for parish_item in municipality_data["parroquias"]:
            if unidecode(parish_item["nombre"].lower()) == unidecode(parish.lower()):
                data = parish_item
                data["codigo_municipio"] = municipality_data["codigo"]
                data["codigo_estado"] = municipality_data["codigo_estado"]
                return data
            else:
                for nombres_alternos in parish_item["nombres_alternos"]:
                    if unidecode(nombres_alternos.lower()) == unidecode(parish.lower()):
                        data = parish_item
                        data["codigo_municipio"] = municipality_data["codigo"]
                        data["codigo_estado"] = municipality_data["codigo_estado"]
                        return data
    return False
