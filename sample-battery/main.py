from enum import Enum
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import BaseSettings
import requests

from bldg_utils import get_flr


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



#
#   WEBHOOKS
#

@app.post("/v1/on_message")
def process_message(msg: Message):
    print(f'🔋 handling msg from {msg.sender}: {msg.message}')
    intent = classify_intent(msg.message)
    if intent == Intent.ASK_FOR_TIME:
        time = get_current_time()
        say(f'The time is {time}')
    return {"sender": msg.sender, "message": msg.message}



#
#   LIFECYCLE EVENTS
#

@app.on_event("startup")
async def startup_event():
    # attach to bldg-server
    attach()


@app.on_event("shutdown")
def shutdown_event():
    detach()



#
#   BLDG SERVER ACTIONS
#

def attach():
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
    print(f'🔋 attached to bldg {settings.bldg_address}')


def detach():
    data = {"bldg_address": settings.bldg_address}
    url = f'{settings.bldg_server_url}/v1/batteries/detach'
    r = requests.post(url, json=data)
    if r.status_code == 404:
        raise RuntimeError(f'Failed to detach battery - there is no active battery attached to {settings.bldg_address}')
    elif r.status_code != 204:
        raise RuntimeError(f'Failed to detach battery - got {r.status_code} error from bldg server: {r.text}')
    print(f'🔋 detached from bldg {settings.bldg_address}')


def say(msg: str):
    message = {
        "sender": settings.battery_type,
        "sender_name": settings.battery_type,
        "message": msg,
        "flr": get_flr(settings.bldg_address)
    }
    data = {"message": message}
    url = f'{settings.bldg_server_url}/v1/messages/say'
    r = requests.post(url, json=data)
    if r.status_code != 201:
        raise RuntimeError(f'Failed to say - got {r.status_code} error from bldg server: {r.text}')
    print(f'🔋 said: {msg}')


#
#   protocol parsing
#

class Intent(Enum):
    UNKNOWN = -1
    ASK_FOR_TIME = 1


ASK_FOR_TIME_SAMPLES = [
    "what time is it",
    "what's the time"
]

def classify_intent(msg: str) -> Intent:
    msg = msg.lower()
    if similar_to_samples(msg, ASK_FOR_TIME_SAMPLES):
        return Intent.ASK_FOR_TIME
    else:
        return Intent.UNKNOWN

def similar_to_samples(msg, samples) -> bool:
    return any(sample in msg for sample in samples)


#
#   protocol
#

def get_current_time() -> str:
    return datetime.now().strftime("%H:%M")
