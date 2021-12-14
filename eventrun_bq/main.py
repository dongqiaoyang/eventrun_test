# from google.cloud import bigquery
# from google.oauth2 import service_account
# import os
# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
    # key_path='sa.json'

    # credentials = service_account.Credentials.from_service_account_file(
        # key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    # )

    # bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

    # job_config = bigquery.QueryJobConfig(labels={'job': 'cloudrun'})

    # query='INSERT test_dataset.data (run_id) VALUES("iam")'  

    # job = bq_client.query(query, job_config=job_config)

    # job.result()  # Waits for the job to complete.
    # name = os.environ.get("NAME", "World")
    # print('hello')
    # return "Hello {}!".format(name)

# if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# Copyright 2021 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# [START eventarc_gcs_server]
import os
from flask import Flask, request
import json
from google.cloud import bigquery
from google.oauth2 import service_account

app = Flask(__name__)


# [END eventarc_gcs_server]


# [START eventarc_gcs_handler]
@app.route('/', methods=['POST'])
def index():
    # Gets the Payload data from the Audit Log
    content = request.json
    try:
        print(content)
        ds = content['resource']['labels']['dataset_id']
        proj = content['resource']['labels']['project_id']
        tbl = content['protoPayload']['resourceName']
        rows = int(content['protoPayload']['metadata']['tableDataChange']['insertedRowsCount'])
        if ds == 'test_dataset' and tbl.endswith('tables/new_data') and rows > 0:
            query = create_agg()
            return "table created", 200
    except:
        # if these fields are not in the JSON, ignore
        pass
    return "ok", 200


# [END eventarc_gcs_handler]

def create_agg():
    # key_path='sa.json'
    # credentials = service_account.Credentials.from_service_account_file(key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    # client = bigquery.Client(credentials=credentials, project=credentials.project_id,)
    client=bigquery.Client()
    query = """
# INSERT test_dataset.data (run_id) VALUES("call_success")
INSERT `cto-datahub-bi-staging-pr-3437.source_data.data` (run_id, run_ts) VALUES("ios", CURRENT_DATE())
    """
    client.query(query)
    return query


# [START eventarc_gcs_server]
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
# [END eventarc_gcs_server]    
    