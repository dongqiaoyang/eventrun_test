
# FROM python:3.10
FROM gcr.io/google.com/cloudsdktool/cloud-sdk:latest

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Download and install required tools.
RUN pip3 install --upgrade google-cloud-bigquery
RUN pip3 install --upgrade google-auth

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install -r requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

CMD exec gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:app

# Exit immediately when one of the background processes terminate.
# wait -n

# [END run_pubsub_dockerfile]
# [END cloudrun_pubsub_dockerfile]
