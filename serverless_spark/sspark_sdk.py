import re


from google.cloud import dataproc_v1 as dataproc
from google.cloud import storage

# client= dataproc.JobControllerClient()
client=dataproc.services.batch_controller.BatchControllerAsyncClient()

# dataproc
    
# def submit_job(project_id, region):
    # # Create the job client.
    # print('start')
    # job_client = dataproc.JobControllerClient(
        # # client_options={"api_endpoint": "northamerica-northeast1-dataproc.googleapis.com:443"}
    # )
    
    # print(job_client)
    # # Create the job config. 'main_jar_file_uri' can also be a
    # # Google Cloud Storage URL.
    # job = {
        # # "placement": {"cluster_name": cluster_name},
        # "pyspark_job": {
            # "main_python_file_uri": ["gs://dse-cicd-test-lab-4c0841-spark-scripts/sample.py"]
            # # "main_class": "org.apache.spark.examples.SparkPi",
            # # "jar_file_uris": ["file:///usr/lib/spark/examples/jars/spark-examples.jar"],
            # # "args": ["1000"],
        # },
    # }

    # operation = job_client.submit_job_as_operation(
        # request={"project_id": project_id, "region": region, "job": job}
    # )
    # response = operation.result()

    # # Dataproc job output gets saved to the Google Cloud Storage bucket
    # # allocated to the job. Use a regex to obtain the bucket and blob info.
    # matches = re.match("gs://(.*?)/(.*)", response.driver_output_resource_uri)

    # output = (
        # storage.Client()
        # .get_bucket(matches.group(1))
        # .blob(f"{matches.group(2)}.000000000")
        # .download_as_string()
    # )

    # print(f"Job finished successfully: {output}")

# submit_job('dse-cicd-test-lab-4c0841','northamerica-northeast1')