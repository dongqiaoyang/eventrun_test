	## Build image
```bash
gcloud builds submit --tag gcr.io/dse-cicd-test-lab-4c0841/automl
```

## Deploy the image to Cloud Run 
```bash
gcloud beta run deploy vertex --image gcr.io/dse-cicd-test-lab-4c0841/automl --region northamerica-northeast1 --service-account vertex-pipeline-user@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com --timeout 600 --execution-environment gen2
```

# Create pubsub topic

```bash
gcloud pubsub topics create vertex
```

# Create the pubsub subscription  
```bash
gcloud pubsub subscriptions create cloud-run --topic vertex \
   --push-endpoint=https://vertex-pw3d6qrcha-nn.a.run.app/ \
   --push-auth-service-account=vertex-pipeline-user@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com --ack-deadline=600
```

# Sample command
```
gcloud beta run deploy vertex-pipelines --source . --region northamerica-northeast1 --execution-environment gen2 --service-account vertex-pipeline-user --update-env-vars BUCKET=vertex-dse-cicd-test-lab-4c0841
gcloud builds submit --tag gcr.io/dse-cicd-test-lab-4c0841/vertex_pipelines
gcloud beta run deploy vertex-pipelines --image gcr.io/dse-cicd-test-lab-4c0841/vertex_pipelines --region northamerica-northeast1 --service-account vertex-pipeline-user@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com --timeout 600 --execution-environment gen2 --update-env-vars BUCKET=vertex-dse-cicd-test-lab-4c0841
```

# Sample pubsub payload
```
{"ref_file_path": "job_1/autoML_tabular.py", "PROJECT_ID": "dse-cicd-test-lab-4c0841", "BUCKET_NAME": "gs://vertex-dse-cicd-test-lab-4c0841", "mapping": "{'a': 5, 'c': 3, 'd': 9}"}
{"ref_file_path": "job_1/autoML_tabular.py", "PROJECT_ID": "dse-cicd-test-lab-4c0841", "BUCKET_NAME": "gs://vertex-dse-cicd-test-lab-4c0841", "mapping": "{'PROJECT_ID': 'dse-cicd-test-lab-4c0841', 'BUCKET_NAME': 'gs://vertex-dse-cicd-test-lab-4c0841', 'gcs_csv_path': 'gs://vertex-dse-cicd-test-lab-4c0841/data/california_housing_train.csv'}"}
```





