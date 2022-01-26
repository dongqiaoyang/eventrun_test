import os
from google.cloud import pubsub_v1
import yaml

publisher = pubsub_v1.PublisherClient()
topic_name = 'projects/cio-exegol-lab-3dabae/topics/cloud-run-topic'
# publisher.create_topic(name=topic_name)
project_id='cio-exegol-lab-3dabae'

def list_manifests(root: str):
    yml_list = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith('.yaml') or name.endswith('.yml'):
                yml_list.append(path + '/' + name)
    return yml_list

list_views=list_manifests(root="/workspace/resources/views")

print('ge started')

for i in range(len(list_views)):
    
    with open(str(list_views[i])) as a_yaml_file:
        parameter = yaml.load(a_yaml_file,Loader=yaml.FullLoader)
        
    # future = publisher.publish(topic_name, b'My first message!', spam='eggs')
    
    dict_send={}
    dict_send['project_id']=project_id
    dict_send['dataset_id']=parameter['expectation_suite']['dataset_id']
    dict_send['bucket_id']=parameter['expectation_suite']['bucket_id']
    dict_send['bigquery_dataset']=parameter['expectation_suite']['dataset_id']
    dict_send['query']=parameter['expectation_suite']['query']
    dict_send['properties']=parameter['expectation_suite']['checks']
    # dict_send['dataset_id']='ge_test'
    # dict_send['bucket_id']='cio-exegol-lab-3dabae-ge-test'
    # dict_send['bigquery_dataset']='ge_test'
    # dict_send['query']='SELECT * FROM ge_test.test_table1'
    # dict_send['properties']=parameter['expectation_suite']
    
    print(dict_send)
    
    future = publisher.publish(topic_name, str.encode(str(dict_send)), spam='eggs')
    future.result()
    
    
