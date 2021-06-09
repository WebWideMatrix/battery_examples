from bldg_utils import get_flr
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import BaseSettings
import requests
import json


class Settings(BaseSettings):
    bldg_server_url: str = "https://api.w2m.site"
    bldg_address: str = "g-b(17,24)-l0-b(12,2)"
    battery_type: str = "sample-clock"
    battery_vendor: str = "w2m"
    battery_version: str = "0.0.1"
    callback_url: str = "http://localhost:3000/v1/on_message"

    class Config:
        env_file = ".env"
    

class Message(BaseModel):
    flr: str
    message: str
    sender: str
    sender_name: str



app = FastAPI()
settings = Settings()


@app.on_event("startup")
async def startup_event():
    # attach to bldg-server
    battery_config = {
        "battery_type": settings.battery_type,
        "battery_vendor": settings.battery_vendor,
        "battery_version": settings.battery_version,
        "bldg_address": settings.bldg_address,
        "callback_url": settings.callback_url,
        "flr": get_flr(settings.bldg_address)
    }
    data = {"battery": battery_config}
    url = f'{settings.bldg_server_url}/v1/batteries/attach'
    print(f'Connecting to bldg-server {url}...')
    r = requests.post(url, json=data)
    if r.status_code == 422:
        raise RuntimeError(f'Failed to start battery - another battery is already attached at {settings.bldg_address}')
    elif r.status_code != 201:
        raise RuntimeError(f'Failed to start battery - got {r.status_code} error from bldg server: {r.text}')
    print(f'Battery attached to bldg {settings.bldg_address}')

@app.post("/v1/on_message")
def process_message(msg: Message):
    return {"sender": msg.sender, "message": msg.message}
