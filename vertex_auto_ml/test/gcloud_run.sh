echo "All args: $0"
echo "First arg: $1"
# gsutil cp gs://vertex-dse-cicd-test-lab-4c0841/pipelines/autoML_tabular.py pipeline_ref.py
gsutil cp $1 pipeline_ref.py