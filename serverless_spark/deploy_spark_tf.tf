resource "google_cloudbuild_trigger" "deploy_triggers" {
  provider    = google-beta
  project     = var.project_id
  name        = "cb-deploy-serverless-spark-trigger"
  description = "Cloudbuild Deploy Triggers Creator"
  filename    = "deployment/deploy_serverless_spark.yaml"

  trigger_template {
    branch_name = "main"
    repo_name   = var.repo_name
  }

  substitutions = {
    _DIR                   = var.build_dir
    _GITHUB_KEY_PROJECT_ID = var.secrets_project
    _GITHUB_KEY_VERSION    = "latest"
    _PROJECT_ID            = var.project_id
    _KEY_VERSION           = "latest"
    _TEAM_NAME             = var.project_alias
    _BASE_BRANCH           = var.base_branch
    _REPO_NAME             = var.repo_name
    _BASE_REPO_URI         = format("git@github.com:%s/%s.git", var.repo_owner, var.repo_name)
    _BACKEND_CONFIG_BUCKET = format("gs://pulumi-state-%s", var.project_id)
    _PROJECT_TYPE          = var.project_type
    _GCR_PROJECT           = var.devops_project
  }
}