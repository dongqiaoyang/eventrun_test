 ## Create firewall rule to allow traffics for serverless spark jobs
``` bash
gcloud compute firewall-rules create allow-internal-ingress --network=spark --source-ranges=10.0.0.0/8 --direction="ingress" --action="allow" --rules="all"
```

## Sample command to execute the job
``` bash
gcloud beta dataproc batches submit pyspark --region northamerica-northeast1 --subnet projects/dse-cicd-test-lab-4c0841/regions/northamerica-northeast1/subnetworks/sspark --service-account spark-serverless@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com gs://dse-cicd-test-lab-4c0841-spark-scripts/sample.py
```

## Build image
```bash
gcloud builds submit --tag gcr.io/dse-cicd-test-lab-4c0841/sspark
```

## Deploy the image to Cloud Run 
```bash
gcloud beta run deploy sspark --image gcr.io/dse-cicd-test-lab-4c0841/sspark --region northamerica-northeast1 --service-account spark-serverless@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com --timeout 600 --execution-environment gen2
```

# Create pubsub topic

```bash
gcloud pubsub topics create sspark
```

# Create the pubsub subscription  
```bash
gcloud pubsub subscriptions create cloud-run --topic sspark \
   --push-endpoint=https://hellopubsub-tqjcrev3ga-nn.a.run.app/ \
   --push-auth-service-account=scheduler-test@cio-exegol-lab-3dabae.iam.gserviceaccount.com --ack-deadline=600
```

