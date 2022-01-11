
# [START cloudrun_pubsub_server_setup]
# [START run_pubsub_server_setup]
import base64
import os

from flask import Flask, request
from google.cloud import bigquery
from google.oauth2 import service_account

app = Flask(__name__)
# [END run_pubsub_server_setup]
# [END cloudrun_pubsub_server_setup]


# [START cloudrun_pubsub_handler]
# [START run_pubsub_handler]
@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    name = "World"
    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        name = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()

    print(f"Hello {name}!")
    query = create_agg()
    ge=ge_run()
    
    return "table created", 204
    
    # return ("", 204)

def create_agg():
    client=bigquery.Client()
    query = """
INSERT test_dataset.data_2 (run_id, run_ts) VALUES("call_success", current_timestamp())
# INSERT test_dataset.data (run_id, run_ts) VALUES("call_success", current_date())
# INSERT `cto-datahub-bi-staging-pr-3437.source_data.data` (run_id, run_ts) VALUES("ios", CURRENT_DATE())
    """
    print(query)
    client.query(query)
    return query
    
    
# [END run_pubsub_handler]
# [END cloudrun_pubsub_handler]


def ge_run():
    from google.cloud import storage
    import ruamel.yaml as yaml
    from typing import Any
    import logging
    import os
    from typing import Any, Dict

    import great_expectations as ge
    from great_expectations.checkpoint import SimpleCheckpoint
    from great_expectations.checkpoint.types.checkpoint_result import CheckpointResult
    from great_expectations.core.batch import RuntimeBatchRequest
    from great_expectations.data_context import BaseDataContext
    from great_expectations.data_context.types.base import DataContextConfig


    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)


    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    # project_id = 'vertex-test-335204'
    project_id='cio-exegol-lab-3dabae'

    dataset_id = 'ge_test'
    bucket_id = 'cio-exegol-lab-3dabae-ge-test'
    connection_str = f'bigquery://{project_id}/{dataset_id}'
    datasource_name = 'ge-test_datasource'
    data_asset_name = 'test-ge'

    gcp_project = project_id
    bigquery_dataset = 'ge_test'

    connection_str = f"bigquery://{gcp_project}/{bigquery_dataset}"

    context = ge.get_context()
    datasource_yaml = f"""
    name: {datasource_name}
    class_name: Datasource
    execution_engine:
      class_name: SqlAlchemyExecutionEngine
      connection_string: {connection_str}
    data_connectors:
       default_runtime_data_connector_name:
           class_name: RuntimeDataConnector
           batch_identifiers:
               - default_identifier_name
    """


    context.test_yaml_config(datasource_yaml)
    context.add_datasource(**yaml.safe_load(datasource_yaml))


    store_yaml = f"""
    stores:
      expectations_gcs_store:
        class_name: ExpectationsStore
        store_backend:
          class_name: TupleGCSStoreBackend
          project: {project_id}
          bucket: {bucket_id}
          prefix: "expect"
    expectations_store_name: expectations_gcs_store
    """
    store_yaml = yaml.safe_load(store_yaml)
    context.add_store(
        store_name=store_yaml["expectations_store_name"],
        store_config=store_yaml["stores"]["expectations_gcs_store"],
    )


    val_yaml = f"""
    stores:
      validations_gcs_store:
        class_name: ValidationsStore
        store_backend:
          class_name: TupleGCSStoreBackend
          project: {project_id}
          bucket: {bucket_id}
          prefix: "validate"

    validations_store_name: validations_gcs_store
    """

    val_yaml = yaml.safe_load(val_yaml)
    context.add_store(
        store_name=val_yaml["validations_store_name"],
        store_config=val_yaml["stores"]["validations_gcs_store"],
    )


    batch_request = RuntimeBatchRequest(
        datasource_name=datasource_name,
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name=data_asset_name,
        runtime_parameters={
            "query": "SELECT * FROM ge_test.test_table1"},
        batch_identifiers={"default_identifier_name": "default_identifier"},
        batch_spec_passthrough={
            "bigquery_temp_table": "ge_temp"
        },
    )

    expectation_suite_name = "ge-test-suite"
    context.create_expectation_suite(
        expectation_suite_name=expectation_suite_name,
        overwrite_existing=True
    )

    batch = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name="ge-test-suite"
    )

    batch.expect_column_values_to_not_be_null(column="first_name")
    batch.save_expectation_suite(discard_failed_expectations=False)

    checkpoint_name = 'test-check'
    checkpoint_config = {
        "config_version": 1.0,
        "class_name": "Checkpoint",
        "run_name_template": f"%Y%m%d-%H%M%S-{checkpoint_name}",
        "validations": [
            {
                "batch_request": batch_request.to_json_dict(),
                "expectation_suite_name": expectation_suite_name
            },
        ],
    }

    checkpoint = SimpleCheckpoint(
        name=checkpoint_name,
        data_context=context,
        **checkpoint_config
    )
    checkpoint_result = checkpoint.run()

    
    
    
    
    

if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)
