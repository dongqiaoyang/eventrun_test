from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from base64 import b64decode
from datetime import datetime
from typing import Dict, Any

import subprocess
import ast
import os
import json
import requests
import time
import warnings


app = FastAPI()


class Message(BaseModel):
    data: str
    messageId: str
    message_id: str
    publishTime: str
    publish_time: str


class PubsubModel(BaseModel):
    message: Message
    subscription: str


def gcloud_run(message):
    print('gcloud - subprocess starting ...')
    p = subprocess.run(
        ['/bin/bash', 'gcloud_run.sh', 'test_arg'],
        stdin=None,
        stdout=None,
        stderr=None)


@app.post("/", status_code=201)
async def create_item(model: PubsubModel, background_tasks: BackgroundTasks):
    print(b64decode(model.message.data).decode("utf-8"))
    message = {'text': b64decode(model.message.data).decode("utf-8")}
    background_tasks.add_task(gcloud_run, message)
    return