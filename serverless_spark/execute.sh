# ls -la
gcloud config list | gcloud beta dataproc batches submit pyspark --region northamerica-northeast1 --subnet projects/dse-cicd-test-lab-4c0841/regions/northamerica-northeast1/subnetworks/spark --service-account spark-serverless@dse-cicd-test-lab-4c0841.iam.gserviceaccount.com gs://dse-cicd-test-lab-4c0841-spark-scripts/sample.py