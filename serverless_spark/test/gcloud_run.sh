echo "All args: $0"
echo "First arg: $1"
echo "Second arg: $2"
gcloud beta dataproc batches submit pyspark --region northamerica-northeast1 --subnet projects/dse-cicd-test-lab-4c0841/regions/northamerica-northeast1/subnetworks/spark --service-account spark-serverless@$1.iam.gserviceaccount.com gs://$1-jobs-scripts/pyspark_jobs/$2