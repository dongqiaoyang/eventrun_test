## Create firewall rule to allow traffics for serverless spark jobs
``` bash
gcloud compute firewall-rules create allow-internal-ingress --network=spark --source-ranges=10.0.0.0/8 --direction="ingress" --action="allow" --rules="all"
```

## Sample command to execute the job
``` bash
gcloud beta dataproc batches submit pyspark --region northamerica-northeast1 --subnet projects/dse-cicd-test-lab-4c0841/regions/northamerica-northeast1/subnetworks/spark --service-account spark-serverless@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com gs://dse-cicd-test-lab-4c0841-spark-scripts/sample.py
```

