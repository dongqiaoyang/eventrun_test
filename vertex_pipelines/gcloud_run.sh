#!/bin/bash

echo "All arguments: $0"
echo "Project name: $1"

mkdir -p pipelines

gsutil -m cp -r gs://vertex-$1/pipelines/* ./pipelines/

ls -lR