import datetime

import pandas as pd
from ruamel import yaml
import great_expectations as ge
import great_expectations.jupyter_ux
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.data_context.types.resource_identifiers import ExpectationSuiteIdentifier
from great_expectations.exceptions import DataContextError

from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest

# Add bq connection 

gcp_project = 'acn-montreal-ai-hackathon'
bigquery_dataset = 'GCPQuickStart'

CONNECTION_STRING = f"bigquery://{gcp_project}/{bigquery_dataset}"

# CONNECTION_STRING = f"bigquery://{gcp_project}"

context = ge.get_context()
datasource_config = {
    "name": "my_bigquery_datasource",
    "class_name": "Datasource",
    "execution_engine": {
        "class_name": "SqlAlchemyExecutionEngine",
        "connection_string": "{}".format(CONNECTION_STRING),
    },
    "data_connectors": {
        "default_runtime_data_connector_name": {
            "class_name": "RuntimeDataConnector",
            "batch_identifiers": ["default_identifier_name"],
        },
        "default_inferred_data_connector_name": {
            "class_name": "InferredAssetSqlDataConnector",
            "name": "whole_table",
        },
    },
}

datasource_config["execution_engine"]["connection_string"] = CONNECTION_STRING

context.test_yaml_config(yaml.dump(datasource_config))

context.add_datasource(**datasource_config)

# Create the expectation suites

context = ge.data_context.DataContext()


# Feel free to change the name of your suite here. Renaming this will not remove the other one.
expectation_suite_name = "test_try"
try:
    suite = context.get_expectation_suite(expectation_suite_name=expectation_suite_name)
    print(f'Loaded ExpectationSuite "{suite.expectation_suite_name}" containing {len(suite.expectations)} expectations.')
except DataContextError:
    suite = context.create_expectation_suite(expectation_suite_name=expectation_suite_name)
    print(f'Created ExpectationSuite "{suite.expectation_suite_name}".')
	

# create expectation 

expectation_configuration = ExpectationConfiguration(
   expectation_type="expect_column_values_to_be_in_set",
   kwargs={
      "column": "payment_type",
      "value_set": [1,2,3]
   },
    meta={
    "notes": {
     "format": "markdown",
     "content": "check the expected values"
    }
    }
   # Note optional comments omitted
)
suite.add_expectation(expectation_configuration=expectation_configuration)

# Expectation 2

expectation_configuration = ExpectationConfiguration(
   # Name of expectation type being added
   expectation_type="expect_table_columns_to_match_ordered_list",
   # These are the arguments of the expectation
   # The keys allowed in the dictionary are Parameters and
   # Keyword Arguments of this Expectation Type
   kwargs={
      "column_list": [
         "vendor_id", "pickup_datetime", "dropoff_datetime","passenger_count", "trip_distance", "rate_code_id", "store_and_fwd_flag", "pickup_location_id","dropoff_location_id", "payment_type", "fare_amount", "extra","mta_tax", "tip_amount","tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge"
      ]
   },
   # This is how you can optionally add a comment about this expectation.
   # It will be rendered in Data Docs.
   # See this guide for details:
   # `How to add comments to Expectations and display them in Data Docs`.
   meta={
      "notes": {
         "format": "markdown",
         "content": "col orders"
      }
   }
)

suite.add_expectation(expectation_configuration=expectation_configuration)

# Expectation 3

expectation_configuration = ExpectationConfiguration(
   expectation_type="expect_column_values_to_not_be_null",
   kwargs={
      "column": "vendor_id",
      "mostly": 1.0,
   },
   meta={
      "notes": {
         "format": "markdown",
         "content": "validate column not null"
      }
   }
)

suite.add_expectation(expectation_configuration=expectation_configuration)


# Add the Expectation to the suite
suite.add_expectation(expectation_configuration=expectation_configuration)

# validate the expecation 

print(context.get_expectation_suite(expectation_suite_name=expectation_suite_name))
context.save_expectation_suite(expectation_suite=suite, expectation_suite_name=expectation_suite_name)

suite_identifier = ExpectationSuiteIdentifier(expectation_suite_name=expectation_suite_name)
# context.build_data_docs(resource_identifiers=[suite_identifier])
# context.open_data_docs(resource_identifier=suite_identifier)


# run checkpoint

# print(validator.get_expectation_suite(discard_failed_expectations=False))
# validator.save_expectation_suite(discard_failed_expectations=False)

from great_expectations.checkpoint import SimpleCheckpoint

expectation_suite_name = "test_try"


batch_request = RuntimeBatchRequest(
    datasource_name="my_bigquery_datasource",
    data_connector_name="default_runtime_data_connector_name",
    data_asset_name="json_data",  # this can be anything that identifies this data
    runtime_parameters={"query": "SELECT * from GCPQuickStart.taxi limit 1000"},
    batch_identifiers={"default_identifier_name": "default_identifier"},
    # batch_spec_passthrough={
        # "bigquery_temp_table": "ge_temp"
    # },  # this is the name of the table you would like to use a 'temp_table'
)

# batch_request = {'datasource_name': 'getting_started_datasource', 'data_connector_name': 'default_inferred_data_connector_name', 'data_asset_name': 'yellow_tripdata_sample_2019-01.csv', 'limit': 1000}


# batch_request={
# 'datasource_name': 'my_bigquery_datasource', 
# 'data_connector_name': 'default_runtime_data_connector_name', 
# 'data_asset_name': 'json_data', 
# 'runtime_parameters': {"query": "SELECT * from GCPQuickStart.top_rated_inexpensive limit 1000"},
# 'batch_identifiers': {"default_identifier_name": "default_identifier"},
# 'batch_spec_passthrough': {"bigquery_temp_table": "ge_temp"},
# }


checkpoint_config = {
    "class_name": "SimpleCheckpoint",
    "validations": [
        {
            "batch_request": batch_request,
            "expectation_suite_name": expectation_suite_name
        }
    ]
}


checkpoint = SimpleCheckpoint(
    f"_tmp_checkpoint_{expectation_suite_name}",
    context,
    **checkpoint_config
)
checkpoint_result = checkpoint.run()

context.build_data_docs()

validation_result_identifier = checkpoint_result.list_validation_result_identifiers()[0]
print(validation_result_identifier)

context.open_data_docs(resource_identifier=validation_result_identifier)