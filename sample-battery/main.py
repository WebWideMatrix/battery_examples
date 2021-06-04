from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import BaseSettings


class Settings(BaseSettings):
    bldg_server_url: str = "https://api.w2m.site"
    bldg_address: str = "g-b(17,24)-l0-b(12,2)"
    battery_type: str = "sample-clock"
    battery_vendor: str = "w2m"
    battery_version: str = "0.0.1"

    class Config:
        env_file = ".env"
    

class Message(BaseModel):
    flr: str
    message: str
    sender: str
    sender_name: str



app = FastAPI()
settings = Settings()


@app.post("/v1/on_message")
def process_message(msg: Message):
    return {"sender": msg.sender, "message": msg.message}
