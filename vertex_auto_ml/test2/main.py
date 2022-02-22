from urllib import response
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from base64 import b64decode
from datetime import datetime
import subprocess
import ast
import os
from os import listdir
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
    # Fetch the input parameters
    ref_file_path=parameter['ref_file_path']
    PROJECT_ID=parameter['PROJECT_ID']
    BUCKET_NAME=parameter['BUCKET_NAME']
    base=os.path.basename(ref_file_path)
    ref_name=os.path.splitext(base)[0]
    # Copy the ref file to the instance

    # print(listdir())
    # p=subprocess.run(['/bin/bash','gcloud_run.sh',ref_file_path, ref_name], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(p.stdout)
    # print(p.stderr)
    # print(p.returncode)
    
    print(listdir())
    import sys
    import importlib
    
    sys.path.insert(1, '/mnt/gcs/pipelines/')
    ref = importlib.import_module("autoML_tabular")
    
    from datetime import datetime
    import google.cloud.aiplatform as aip
    from kfp.v2 import compiler  # noqa: F811

    # PROJECT_ID = "dse-cicd-test-lab-4c0841" 
    # BUCKET_NAME = "gs://vertex-dse-cicd-test-lab-4c0841"
    PIPELINE_ROOT = "{}".format(BUCKET_NAME)
    TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
    aip.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)

    # pipeline_ref.main()

    # print(pipeline_ref.main())

    compiler.Compiler().compile(
        pipeline_func=ref.main(),
        package_path="{}.json".format(ref_name),
    )

    DISPLAY_NAME = str(ref_name) + TIMESTAMP

    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="{}.json".format(ref_name),
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
        location= "northamerica-northeast1"
    )

    result = job.run()
    return result

@app.post("/",  status_code=201)
def create_item(model: PubsubModel, background_tasks: BackgroundTasks):
    print(b64decode(model.message.data).decode("utf-8"))
    message = b64decode(model.message.data).decode("utf-8")
    background_tasks.add_task(gcloud_run, message)
    return "", 201
