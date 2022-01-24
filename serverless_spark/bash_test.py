# import subprocess

# def bash_command(cmd):
    # subprocess.Popen(cmd, shell=True, executable='/bin/sh')

# bash_command('a="Apples and oranges" && echo "${a/oranges/grapes}"')

import subprocess

def bash_command(cmd):
    # subprocess.Popen(['/bin/bash', '-c', cmd],shell=True)
    subprocess.Popen(['C:\\Users\\dong.qiao.yang\\AppData\\Local\\Programs\\Git\\bin\\bash', '-c', cmd])
    

# bash_command('a="Apples and oranges" && echo "${a/oranges/grapes}"')

bash_command('gcloud config list')

################

import os
import subprocess

from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.post("/",  status_code=201)
def get_files(path: str = "./"):
    if os.path.exists(path):
        content = subprocess.run(
            ["ls", "-la"],
            stdout=subprocess.PIPE,
            shell=True,
            text=True,
            cwd=path,
            check=True,
        ).stdout.splitlines()
        return content
    else:
        raise HTTPException(status_code=400, detail="Path does not exist")

################

# !/usr/bin/env bash
set -eo pipefail

echo "call gcloud"
gcloud ... <blah>
echo "gcloud call completed."

##############

FROM python:3.10-buster

RUN set -e; \
    apt-get update -y && apt-get install -y \
    tini && apt-get clean

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt
RUN chmod +x /app/gcloud_run.sh

ENTRYPOINT ["/usr/bin/tini", "--"] 
CMD ["/app/startup.sh"]

##################

#!/usr/bin/env bash
set -eo pipefail

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 main:app &

# Exit immediately when one of the background processes terminate.
wait -n


####################

# requirements 

fastapi gunicorn uvicorn uvloop httptools

#################

#Script 

import subprocess

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from base64 import b64decode

app = FastAPI()

class MessageModel(BaseModel):
    data: str,
    messageId: str,
    message_id: str,
    publishTime: str,
    publish_time: str


class PubsubModel(BaseModel):
    message: MessageModel,
    substription: str


def gcloud_run(path: str = "./"):
    if os.path.exists(path):
        content = subprocess.run(
            ["sh", "run_gcloud.sh"],
            stdout-subprocess.PIPE,
            shell=True,
            text=True,
            cwd=path,
            check=True
        ).stdout.splitlines()
        return content
    else:
        raise HTTPException(status_code=400, detail="Path does not exist")


@app.post("/",  status_code=201)
def get_item(model: PubSubModel, background_tasks: BackgroundTasks):
    print(b64decode(model.message.data).decode("utf-8"))
    background_tasks.add_task(gcloud_run, <input args to gcloud as dict>)
    return