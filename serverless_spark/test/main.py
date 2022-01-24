from urllib import response
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from base64 import b64decode
from datetime import datetime
import subprocess


app = FastAPI()

"""
data model:
{
    "project_id": "cio-exegol-lab",
    "dataset_id": "ge_test",
    "bucket_id": "cio-exegol-lab-test",
    "bigquery_dataset": "ge_test",
    "query": "select * from this.table",
    "properties": {
        "column1": {"type": "integer"},
        "column2": {"enum": [1, 2, 4]},
    },
}
"""

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
    # cp=subprocess.run(["ls", "-la"],text=True,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # print(cp.stdout)
    # print(cp.stderr)
    # print(cp.returncode)
    print('process starts')
    p=subprocess.run(['/bin/bash','gcloud_run.sh'], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p.stdout)
    print(p.stderr)
    print(p.returncode)
    
    return p

@app.post("/",  status_code=201)
def create_item(model: PubsubModel, background_tasks: BackgroundTasks):
    print(b64decode(model.message.data).decode("utf-8"))
    message = {'text': b64decode(model.message.data).decode("utf-8")}
    background_tasks.add_task(gcloud_run, message)
    return "", 201
