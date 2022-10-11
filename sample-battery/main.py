from enum import Enum
from datetime import datetime
from time import time

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import BaseSettings
import requests

from bldg_utils import get_flr


class Settings(BaseSettings):
    bldg_server_url: str = "http://localhost:4000"
    bldg_address: str = "g/b(16,92)/l0/b(18,18)"
    bldg_url: str = "g/fromTeal/l0/test-decision"
    battery_type: str = "sample-clock"
    battery_vendor: str = "w2m"
    battery_version: str = "0.0.1"
    battery_owner: str = "dibaunaumh@gmail.com"
    callback_url: str = "http://localhost:8000/v1/on_message"

    class Config:
        env_file = ".env"
    

class Message(BaseModel):
    action_type: str
    resident_email: str
    say_flr: str
    say_flr_url: str
    say_location: str
    say_mimetype: str
    say_recipient: str
    say_speaker: str
    say_text: str
    say_time: int



app = FastAPI()
settings = Settings()



#
#   WEBHOOKS
#

@app.post("/v1/on_message")
def process_message(msg: Message):
    print(f'🔋 handling msg from {msg.say_speaker}: {msg.say_text}')
    intent = classify_intent(msg.say_text)
    if intent == Intent.ASK_FOR_TIME:
        time = get_current_time()
        say(f'The time is {time}', msg.say_speaker)
    return {"say_speaker": msg.say_speaker, "message": msg.say_text}



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


def say(msg: str, recipient: str):
    message = {
        "action_type": "SAY",
        "resident_email": settings.battery_owner,
        "bldg_url": settings.bldg_url,
        "say_flr": get_flr(settings.bldg_address),
        "say_flr_url": get_flr(settings.bldg_url),
        "say_location": settings.bldg_address,
        "say_mimetype": "text/plain",
        "say_recipient": recipient,
        "say_speaker": settings.battery_type,
        "say_text": msg
    }
    url = f'{settings.bldg_server_url}/v1/batteries/act'
    r = requests.post(url, json=message)
    if r.status_code != 200 and r.status_code != 201:
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
    "what time is it?",
    "what's the time",
    "what's the time?",
    "/what time is it",
    "/what time is it?",
    "/what's the time",
    "/what's the time?"
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
