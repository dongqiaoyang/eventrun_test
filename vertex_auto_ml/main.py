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
    # p=subprocess.run(['/bin/bash','gcloud_run.sh',project, job_file], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(p.stdout)
    # print(p.stderr)
    # print(p.returncode)
    # execute the pipeline
    
    # from google.cloud import storage
    # storage_client = storage.Client(project=PROJECT_ID)
    # print(storage_client)
    # bucket = storage_client.bucket("vertex-dse-cicd-test-lab-4c0841")
    # print(bucket)
    # blob = bucket.blob("pipelines/autoML_tabular.py")
    # blob.download_to_filename("pipeline_ref.py")
    
    p=subprocess.run(['/bin/bash','gcloud_run.sh'], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p.stdout)
    print(p.stderr)
    print(p.returncode)
    
    from os import listdir
    print(listdir())
    
    import autoML_tabular
    from datetime import datetime
    import google.cloud.aiplatform as aip
    from kfp.v2 import compiler  # noqa: F811

    REGION="northamerica-northeast1"
    PROJECT_ID = "dse-cicd-test-lab-4c0841" 
    BUCKET_NAME = "gs://vertex-dse-cicd-test-lab-4c0841"
    PIPELINE_ROOT = "{}".format(BUCKET_NAME)
    TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
    aip.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)

    pipeline_ref.main()

    print(pipeline_ref.main())

    compiler.Compiler().compile(
        pipeline_func=pipeline_ref.main(),
        package_path="tabular regression_pipeline.json".replace(" ", "_"),
    )

    DISPLAY_NAME = "cal_housing_" + TIMESTAMP

    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="tabular regression_pipeline.json".replace(" ", "_"),
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
