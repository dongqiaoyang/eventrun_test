import kfp
from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip
import google.cloud.aiplatform as aip
from typing import NamedTuple

from kfp import dsl
from kfp.v2 import compiler
from kfp.v2.dsl import component

from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
# REGION="northamerica-northeast1"
REGION="us-central1"
PROJECT_ID = "acn-mtl-data-studio-sandbox"
BUCKET_NAME = "gs://ai-files-acn-mtl-data-studio-sandbox"
# PIPELINE_ROOT = "{}/pipeline_root/intro".format(BUCKET_NAME)

aip.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)

# gcs_csv_path = f"{PIPELINE_ROOT}/data/california_housing_train.csv"

# @pipeline(name="automl-beans-custom",
                  # pipeline_root=PIPELINE_ROOT)
                  
@kfp.dsl.pipeline(name="cust-tab-training-v2")
def pipeline(
    bq_source: str = "bq://sara-vertex-demos.beans_demo.large_dataset",
    bucket: str = BUCKET_NAME, project: str = PROJECT_ID,
    gcp_region: str = REGION,
    bq_dest: str = "",
    container_uri: str = "",
    batch_destination: str = ""
):
    dataset_create_op = gcc_aip.TabularDatasetCreateOp(
        display_name="tabular-beans-dataset",
        bq_source=bq_source,
        # gcs_source=gcs_csv_path,
        project=project,
        location=gcp_region
    )

    training_op = gcc_aip.CustomContainerTrainingJobRunOp(
        display_name="pipeline-beans-custom-train",
        container_uri=container_uri,
        project=project,
        location=gcp_region,
        dataset=dataset_create_op.outputs["dataset"],
        staging_bucket=bucket,
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        bigquery_destination=bq_dest,
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest",
        model_display_name="scikit-beans-model-pipeline",
        machine_type="n1-standard-4",
    )
    batch_predict_op = gcc_aip.ModelBatchPredictOp(
        project=project,
        location=gcp_region,
        job_display_name="beans-batch-predict",
        model=training_op.outputs["model"],
        gcs_source_uris=["{0}/batch_examples.csv".format(BUCKET_NAME)],
        instances_format="csv",
        gcs_destination_output_uri_prefix=batch_destination,
        machine_type="n1-standard-4"
    )
    
compiler.Compiler().compile(
    pipeline_func=pipeline, package_path="custom_train_pipeline.json"
)

pipeline_job = aiplatform.PipelineJob(
    display_name="custom-train-pipeline",
    template_path="custom_train_pipeline.json",
    job_id="custom-train-pipeline-{0}".format(TIMESTAMP),
    location= REGION,
    parameter_values={
        "project": PROJECT_ID,
        "bucket": BUCKET_NAME,
        "bq_dest": "bq://{0}".format(PROJECT_ID),
        "container_uri": "gcr.io/{0}/cpred".format(PROJECT_ID),
        "batch_destination": "{0}/batchpredresults".format(BUCKET_NAME)
    },
    enable_caching=True,
)

pipeline_job.submit()