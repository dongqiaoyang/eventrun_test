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

# from google.cloud import storage
# storage_client = storage.Client(project=PROJECT_ID)
# print(storage_client)
# bucket = storage_client.bucket("vertex-dse-cicd-test-lab-4c0841")
# print(bucket)
# blob = bucket.blob("pipelines/autoML_tabular.py")
# blob.download_to_filename("pipeline_ref.py")
    
autoML_tabular.main()

print(autoML_tabular.main())

compiler.Compiler().compile(
	pipeline_func=autoML_tabular.main(),
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