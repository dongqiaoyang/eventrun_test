# def main(): 
import kfp
from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip
from kfp import dsl
from kfp.v2.dsl import component
from datetime import datetime



TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
REGION="northamerica-northeast1"
# PROJECT_ID = "dse-cicd-test-lab-4c0841" 
PROJECT_ID = 'acn-mtl-data-studio-sandbox'
# BUCKET_NAME = "gs://dse-cicd-test-lab-4c0841_bucket_1"
BUCKET_NAME='gs://vertex_pipelines_acn-mtl-data-studio-sandbox'
PIPELINE_ROOT = "{}".format(BUCKET_NAME)

import google.cloud.aiplatform as aip
from kfp.v2 import compiler  # noqa: F811
aip.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)


# Define AutoML tabular regression model pipeline that uses components from google_cloud_pipeline_components

TRAIN_FILE_NAME = "california_housing_train.csv"

gcs_csv_path = f"{PIPELINE_ROOT}/data/{TRAIN_FILE_NAME}"

@kfp.dsl.pipeline(name="automl-tab-training-v2-a")
def pipeline(project: str = PROJECT_ID, region: str = REGION):
    from google_cloud_pipeline_components import aiplatform as gcc_aip
    from google_cloud_pipeline_components.v1.endpoint import (EndpointCreateOp,
                                                              ModelDeployOp)

    dataset_create_op = gcc_aip.TabularDatasetCreateOp(
        project=project, display_name="housing", gcs_source=gcs_csv_path, location= "northamerica-northeast1",
    )

    training_op = gcc_aip.AutoMLTabularTrainingJobRunOp(
        project=project,
        display_name="train-automl-cal_housing",
        optimization_prediction_type="regression",
        optimization_objective="minimize-rmse",
        column_transformations=[
            {"numeric": {"column_name": "longitude"}},
            {"numeric": {"column_name": "latitude"}},
            {"numeric": {"column_name": "housing_median_age"}},
            {"numeric": {"column_name": "total_rooms"}},
            {"numeric": {"column_name": "total_bedrooms"}},
            {"numeric": {"column_name": "population"}},
            {"numeric": {"column_name": "households"}},
            {"numeric": {"column_name": "median_income"}},
            {"numeric": {"column_name": "median_house_value"}},
        ],
        dataset=dataset_create_op.outputs["dataset"],
        target_column="median_house_value",
        location= "northamerica-northeast1",
    )

    endpoint_op = EndpointCreateOp(
        project=project,
        display_name="train-automl-flowers",
        location= "northamerica-northeast1",
    )

    ModelDeployOp(
        model=training_op.outputs["model"],
        endpoint=endpoint_op.outputs["endpoint"],
        dedicated_resources_machine_type="n1-standard-4",
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1,
    )
    



compiler.Compiler().compile(
    pipeline_func=pipeline,
    package_path="tabular regression_pipeline.json".replace(" ", "_"),
)

DISPLAY_NAME = "cal_housing_" + TIMESTAMP

job = aip.PipelineJob(
    display_name=DISPLAY_NAME,
    template_path="tabular regression_pipeline.json".replace(" ", "_"),
    location= "northamerica-northeast1",
    pipeline_root=PIPELINE_ROOT,
    enable_caching=False,
)

job.run()