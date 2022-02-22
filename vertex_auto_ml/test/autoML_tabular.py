def main(): 
    import kfp
    from google.cloud import aiplatform
    from google_cloud_pipeline_components import aiplatform as gcc_aip
    # from kfp import dsl
    # from kfp.v2.dsl import component
    from datetime import datetime

    TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
    REGION="northamerica-northeast1"
    PROJECT_ID = "dse-cicd-test-lab-4c0841" 
    BUCKET_NAME = "gs://vertex-dse-cicd-test-lab-4c0841"
    PIPELINE_ROOT = "{}".format(BUCKET_NAME)

    # Define AutoML tabular regression model pipeline that uses components from google_cloud_pipeline_components

    TRAIN_FILE_NAME = "california_housing_train.csv"

    gcs_csv_path = f"{PIPELINE_ROOT}/data/{TRAIN_FILE_NAME}"

    @kfp.dsl.pipeline(name="automl-tab-training-v2")
    def pipeline(project: str = PROJECT_ID, region: str = REGION):
        from google_cloud_pipeline_components import aiplatform as gcc_aip
        from google_cloud_pipeline_components.v1.endpoint import (EndpointCreateOp,
                                                                  ModelDeployOp)

        dataset_create_op = gcc_aip.TabularDatasetCreateOp(
            project=project, display_name="housing", gcs_source=gcs_csv_path,location= REGION
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
            location= REGION
        )

        endpoint_op = EndpointCreateOp(
            project=project,
            location=region,
            display_name="train-automl-flowers",
        )

        ModelDeployOp(
            model=training_op.outputs["model"],
            endpoint=endpoint_op.outputs["endpoint"],
            dedicated_resources_machine_type="n1-standard-4",
            dedicated_resources_min_replica_count=1,
            dedicated_resources_max_replica_count=1,
        )
    return pipeline
    
# import google.cloud.aiplatform as aip
# from kfp.v2 import compiler  # noqa: F811
# aip.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)

# compiler.Compiler().compile(
    # pipeline_func=pipeline,
    # package_path="tabular regression_pipeline.json".replace(" ", "_"),
# )

# DISPLAY_NAME = "cal_housing_" + TIMESTAMP

# job = aip.PipelineJob(
    # display_name=DISPLAY_NAME,
    # template_path="tabular regression_pipeline.json".replace(" ", "_"),
    # pipeline_root=PIPELINE_ROOT,
    # enable_caching=False,
    # location= "northamerica-northeast1"
# )

# job.run()