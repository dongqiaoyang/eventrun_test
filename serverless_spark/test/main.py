from urllib import response
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from base64 import b64decode
from datetime import datetime
import subprocess
import ast


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


class Item(BaseModel):
    name: Message
    price: float
    is_offer: bool = None


def gcloud_run(message):
    print('process starts')
    parameter=ast.literal_eval(str(message))
    print(parameter)
    # parameter=ast.literal_eval(str(parameter['text']))
    # print(parameter)
    project=parameter['project']
    job_file=parameter['job_file']
    p=subprocess.run(['/bin/bash','gcloud_run.sh',project, job_file], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p.stdout)
    print(p.stderr)
    print(p.returncode)
    
    return p

@app.post("/",  status_code=201)
def create_item(model: PubsubModel, background_tasks: BackgroundTasks):
    print(b64decode(model.message.data).decode("utf-8"))
    message = b64decode(model.message.data).decode("utf-8")
    background_tasks.add_task(gcloud_run, message)
    return "", 201
