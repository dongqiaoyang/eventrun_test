FROM python:3.10

ENV PYTHONUNBUFFERED True
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdir -p /usr/local/gcloud \
    && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
    && /usr/local/gcloud/google-cloud-sdk/install.sh

RUN gcloud components install beta

ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 main:app