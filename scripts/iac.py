import yaml
import re
import pulumi
import sys
import os
import base64

from google.oauth2 import service_account as osa
from collections import defaultdict, namedtuple
from pulumi import resource, Output
from pulumi.automation import errors
from pulumi_gcp import storage, bigquery, serviceaccount, projects
from pulumi import automation as auto
from cerberus import Validator


results = namedtuple('results', ['sorted', 'cyclic'])
def graph_sort(l: str):
    n_heads = defaultdict(int)
    tails = defaultdict(list)
    heads = []
    for h, t in l:
        n_heads[t]+=1
        if h in tails:
            tails[h].append(t)
        else:
            tails[h] = [t]
            heads.append(h)
    ordered = [h for h in heads if h not in n_heads]
    for h in ordered:
        for t in tails[h]:
            n_heads[t]-=1
            if not n_heads[t]:
                ordered.append(t)
    cyclic = [n for n, heads in n_heads.items() if heads]
    return results(ordered, cyclic)


def validate_dataset_manifest(manifest: str):
    schema = eval(open('./schemas/dataset.py', 'r').read())
    validator = Validator(schema)
    try:
        if validator.validate(manifest, schema):
            return
    except:
        print("##### Dataset Exception - " + manifest['dataset_id'])
        raise auto.InlineSourceRuntimeError(validator.errors)


def dataset(manifest: str):
    validate_dataset_manifest(manifest)

    dts = bigquery.Dataset(
        resource_name=manifest['resource_name'] + '_dataset',
        dataset_id=manifest['dataset_id'],
        description=manifest['description'],
        labels={
            'cost_center': manifest['metadata']['cost_center'],
            'dep': manifest['metadata']['dep'],
            'bds': manifest['metadata']['bds'],
        },
        default_table_expiration_ms=manifest['table_expiration_ms'],
        location='northamerica-northeast1'
    )
    readers = [
        reader.replace('user:', '').replace('serviceAccount:', '') 
        for reader in manifest['users']['readers']
    ]
    writers = [
        writer.replace('user:', '').replace('serviceAccount:', '') 
        for writer in manifest['users']['writers']
    ]
    for reader in readers:
        bigquery.DatasetAccess(
            resource_name=manifest['resource_name'] + '_reader_iam',
            dataset_id=dts.dataset_id,
            user_by_email=reader,
            role='roles/bigquery.dataViewer'
        )
    for writer in writers:
        bigquery.DatasetAccess(
            resource_name=manifest['resource_name'] + '_writer_iam',
            dataset_id=dts.dataset_id,
            user_by_email=writer,
            role='roles/bigquery.dataEditor'
        )


def validate_table_manifest(manifest: str):
    schema = eval(open('./schemas/table.py', 'r').read())
    validator = Validator(schema)
    try:
        if validator.validate(manifest, schema):
            return
    except:
        print("##### Table Exception - " + manifest['table_id'])
        raise auto.InlineSourceRuntimeError(validator.errors)


def table(manifest: str):
    validate_table_manifest(manifest)

    readers = [reader for reader in manifest['users']['readers']]
    writers = [writer for writer in manifest['users']['writers']]

    tbl = bigquery.Table(
        resource_name=manifest['resource_name'] + '_table',
        dataset_id=manifest['dataset_id'],
        table_id=manifest['table_id'],
        deletion_protection=False,
        expiration_time=manifest['expiration_ms'],
        friendly_name=manifest['friendly_name'],
        labels={
            'cost_center': manifest['metadata']['cost_center'],
            'dep': manifest['metadata']['dep'],
            'bds': manifest['metadata']['bds'],
        },
        schema=manifest['schema']
    )
    readers = bigquery.IamBinding(
        resource_name=manifest['resource_name'] + '_read_iam',
        dataset_id=tbl.dataset_id,
        table_id=tbl.table_id,
        role='roles/bigquery.dataViewer',
        members=readers
    )
    writers = bigquery.IamBinding(
        resource_name=manifest['resource_name'] + '_write_iam',
        dataset_id=tbl.dataset_id,
        table_id=tbl.table_id,
        role='roles/bigquery.dataEditor',
        members=writers
    )


def validate_materialized_manifest(manifest: str):
    schema = eval(open('./schemas/materialized.py', 'r').read())
    validator = Validator(schema)
    try:
        if validator.validate(manifest, schema):
            return
    except:
        print("##### Materialized Exception - " + manifest['table_id'])
        raise auto.InlineSourceRuntimeError(validator.errors)


def materialized(manifest: str):
    validate_materialized_manifest(manifest)

    readers = [reader for reader in manifest['users']['readers']]
    writers = [writer for writer in manifest['users']['writers']]

    mat = bigquery.TableMaterializedViewArgs(
        query=manifest['params']['query'],
        enable_refresh=manifest['params']['refresh'],
        refresh_interval_ms=manifest['params']['refresh_ms']
    )
    tbl = bigquery.Table(
        resource_name=manifest['resource_name'],
        dataset_id=manifest['dataset_id'],
        table_id=manifest['table_id'],
        deletion_protection=False,
        expiration_time=manifest['expiration_ms'],
        friendly_name=manifest['friendly_name'],
        labels={
            'cost_center': manifest['metadata']['cost_center'],
            'dep': manifest['metadata']['dep'],
            'bds': manifest['metadata']['bds'],
        },
        materialized_view=mat
    )
    readers = bigquery.IamBinding(
        resource_name=manifest['resource_name'] + '_read_iam',
        dataset_id=tbl.dataset_id,
        table_id=tbl.table_id,
        role='roles/bigquery.dataViewer',
        members=readers
    )
    writers = bigquery.IamBinding(
        resource_name=manifest['resource_name'] + '_write_iam',
        dataset_id=tbl.dataset_id,
        table_id=tbl.table_id,
        role='roles/bigquery.dataEditor',
        members=writers
    )


def scheduled(manifest: str, sa=None):
    validate_scheduled_manifest(manifest)

    scheduled = bigquery.DataTransferConfig(
        resource_name=manifest['resource_name'],
        display_name=manifest['display_name'],
        data_source_id='scheduled_query',
        schedule=manifest['schedule'],
        destination_dataset_id=manifest['destination_dataset_id'],
        location='northamerica-northeast1',
        params={
            'destination_table_name_template': manifest['params']['destination_table_name'],
            'write_disposition': manifest['params']['write_disposition'],
            'query': manifest['params']['query']
        })
        # service_account_name=sa.email)


def validate_scheduled_manifest(manifest: str):
    schema = eval(open('./schemas/scheduled.py').read())
    validator = Validator(schema)
    try:
        if validator.validate(manifest, schema):
            return
    except:
        print("##### Scheduled Exception - " + manifest['display_name'])
        raise auto.InlineSourceRuntimeError(validator.errors)


def bucket(manifest: str):
    validate_bucket_manifest(manifest)

    readers = [reader for reader in manifest['users']['readers'] or []]
    writers = [writer for writer in manifest['users']['writers'] or []]

    bucket = storage.Bucket(
        manifest['resource_name'],
        name=manifest['resource_name'],
        force_destroy=True,
        lifecycle_rules=[storage.BucketLifecycleRuleArgs(
            action=storage.BucketLifecycleRuleActionArgs(
                type=manifest['lifecycle_type']
            ),
            condition=storage.BucketLifecycleRuleConditionArgs(
                age=manifest['lifecycle_age_days']
            ),
        )],
        location="northamerica-northeast1",
        labels={
            'cost_center': manifest['metadata']['cost_center'],
            'dep': manifest['metadata']['dep'],
            'bds': manifest['metadata']['bds'],
        }
    )
    if readers:
        storage.BucketIAMBinding(
            resource_name=manifest['resource_name'] + '_read_iam',
            bucket=bucket.id,
            role="roles/storage.objectViewer",
            members=readers)
    if writers:
        storage.BucketIAMBinding(
            resource_name=manifest['resource_name'] + '_write_iam',
            bucket=bucket.id,
            role="roles/storage.objectAdmin",
            members=writers)


def validate_bucket_manifest(manifest: str):
    schema = eval(open('./schemas/bucket.py').read())
    validator = Validator(schema)
    try:
        if validator.validate(manifest, schema):
            return
    except:
        print("##### Bucket Exception - " + manifest['bucket_name'])
        raise auto.InlineSourceRuntimeError(validator.errors)


def service_account(team: str):
    sa = serviceaccount.Account(
        team + '-service-account',
        account_id=team + '-service-account',
        display_name=team + ' - service account')
    iam = projects.IAMBinding(
        team + '-bq-admin-iam',
        members=[sa.email.apply(lambda email: f"serviceAccount:{email}")],
        role='roles/bigquery.admin')
    iam = projects.IAMBinding(
        team + '-storage-admin-iam',
        members=[sa.email.apply(lambda email: f"serviceAccount:{email}")],
        role='roles/storage.objectAdmin')
    iam = projects.IAMBinding(
        team + '-cb-build-iam',
        members=[sa.email.apply(lambda email: f"serviceAccount:{email}")],
        role='roles/cloudbuild.builds.editor')
    return sa


def read_yml(path: str):
    file = open(path, 'r')
    try:
        return yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise e


def list_manifest(root: str):
    yml_list = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith('.yaml'):
                yml_list.append(path, '/' + name)
    return yml_list


def read_yml(path: str):
    file = open(path, 'r')
    try:
        return yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise e


def read_diff(path: str = '/workspace/DIFF_TEAM.txt'):
    with open(path, 'r') as file:
        return [item.strip() for item in file.readlines()]


def list_manifests(root: str):
    yml_list = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith('.yaml') or name.endswith('.yml'):
                yml_list.append(path + '/' + name)
    return yml_list


def update(path:str, context=None):
    yml = read_yml(path)

    try:
        if yml and yml['kind'] == 'dataset':
            validate_dataset_manifest(yml)
            dataset(yml)
        if yml and yml['kind'] == 'table':
            validate_table_manifest(yml)
            table(yml)
        if yml and yml['kind'] == 'materialized':
            validate_materialized_manifest(yml)
            materialized(yml)
        # if yml and yml['kind'] == 'scheduled':
        #     validate_scheduled_manifest(yml)
        #     scheduled(yml, sa=context['sa'])
        if yml and yml['kind'] == 'bucket':
            validate_bucket_manifest(yml)
            bucket(yml)
    except auto.errors.CommandError as e:
        raise e


def get_manifast_kind(
    manifest: str,
    kind: str):

    with open(manifest) as file:
        yml = yaml.safe_load(file)
        if yml and yml['kind'] == kind:
            return manifest


def get_value(
    manifest: str,
    key: str):

    with open(manifest) as file:
        yml = yaml.safe_load(file)
        if yml:
            return yml[key]


teams_root = '/workspace/teams/'
manifests_set = list_manifests(teams_root)
dependency_map = list(set([
    (root_manifest, dep_manifest)
    for dep_manifest in manifests_set
    for root_manifest in manifests_set
    if get_value(dep_manifest, 'dependencies')
    and get_value(root_manifest, 'resource_name')
    and get_value(root_manifest, 'resource_name') in get_value(dep_manifest, 'dependencies')
    and root_manifest != dep_manifest
]))


def create_team_key(team: str, path: str = 'team_auth'):
    sa = service_account(team)
    pulumi.export(team + '_sa', sa.name)
    key = serviceaccount.Key(
        team + '_key',
        service_account_id=sa.name,
        public_key_type="TYPE_X509_PEM_FILE")
    storage.BucketObject(
        team + '_key',
        name=team + '/' + team + '.json',
        bucket=path,
        content=key.private_key.apply(lambda x: base64.b64decode(x).decode('utf-8')))
    return key


def render_user_data(key) -> Output:
    temp = base64.b64encode(key.encode("utf-8"))
    temp_str = str(temp, "utf-8")
    return temp_str


def pulumi_program():
    sorted_path = graph_sort(dependency_map).sorted
    sorted_path.extend(list(set(manifests_set) - set(graph_sort(dependency_map).sorted)))
    context = {
        'team_stack': pulumi.get_stack(),
        'project': pulumi.get_project()
    }
    for path in sorted_path:
        if re.search('/workspace/teams/(.+?)/+', path).group(1) == context['team_stack']:
            update(path, context)


if __name__ == "__main__":
    team = sys.argv[1]
    print("TEAM in MAIN: " + team)
    stack = auto.create_or_select_stack(
        stack_name=team,
        project_name='eventrun',
        program=pulumi_program,
        work_dir='/workspace')
    stack.set_config("gpc:region", auto.ConfigValue("northamerica-northeast1"))
    stack.set_config("gcp:project", auto.ConfigValue("eventrun"))
    print('##################### Preview Changes for Team: ' + team + ' #####################')
    stack.refresh()
    preview = stack.preview()
    up = stack.up(on_output=print)
    # print(f"{team} upsert summary: \n{json.dumps(up.summary.resource_changes, indent=4)}")
