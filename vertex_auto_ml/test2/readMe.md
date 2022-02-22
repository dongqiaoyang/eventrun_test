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


```
gcloud beta run deploy filesystem-app --source . --region northamerica-northeast1 --execution-environment gen2 --service-account vertex-pipeline-user --update-env-vars BUCKET=vertex-dse-cicd-test-lab-4c0841
gcloud builds submit --tag gcr.io/dse-cicd-test-lab-4c0841/fuse
gcloud beta run deploy fuse --image gcr.io/dse-cicd-test-lab-4c0841/fuse --region northamerica-northeast1 --service-account vertex-pipeline-user@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com --timeout 600 --execution-environment gen2 --update-env-vars BUCKET=vertex-dse-cicd-test-lab-4c0841
```