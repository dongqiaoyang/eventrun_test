#!/usr/bin/env bash
# [START cloudrun_fuse_script]
#!/usr/bin/env bash
set -eo pipefail

# Create mount directory for service
mkdir -p /mnt/gcs

echo "Mounting GCS Fuse."
gcsfuse --debug_gcs --debug_fuse --implicit-dirs $BUCKET $MNT_DIR 
echo "Mounting completed."

# cp -rf e2e_test.py /mnt/gcs/

# ls
echo check mounting points
ls $MNT_DIR 

# ls /mnt/gcs/vertex-dse-cicd-test-lab-4c0841

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app &

exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 main:app
# Exit immediately when one of the background processes terminate.
wait -n
# [END cloudrun_fuse_script]