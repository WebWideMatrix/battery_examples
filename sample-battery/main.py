from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import BaseSettings

app = FastAPI()


class Settings(BaseSettings):
    bldg_server_url: str = "Awesome API"
    battery_type: str = "Awesome API"
    battery_vendor: str = "Awesome API"
    battery_version: str = "Awesome API"
    

class Message(BaseModel):
    flr: str
    message: str
    sender: str
    sender_name: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/v1/on_message")
def process_message(msg: Message):
    return {"sender": msg.sender, "message": msg.message}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}
