
provider "google" {
  project = "acn-montreal-ai-hackathon"
  region  = "northamerica-northeast1"
  zone    = "northamerica-northeast1-c"
}


variable "project_id" {
  type    = string
  default = "staging"
}

### Set-Location "C:\Users\dong.qiao.yang\OneDrive - Accenture\Documents\GitHub\eventrun_test\serverless_spark\tf"
### terraform apply -var="project_id=acn-montreal-ai-hackathon"


#### create sspark file bucket

resource "google_storage_bucket" "jobs-scripts-bucket" {
  name          = format("%s-jobs-scripts", var.project_id)
  location      = "NORTHAMERICA-NORTHEAST1"
  force_destroy = true
}

#### create sspark pubsub topic

resource "google_pubsub_topic" "sspark-topic" {
  name = "sspark"
}

#### create subnetwork 
resource "google_compute_network" "sspark-network" {
  name = "sspark-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "sspark-private-subnet" {
  name          = "sspark-private-subnet"
  ip_cidr_range = "10.0.0.0/8"
  region        = "northamerica-northeast1"
  network       = google_compute_network.sspark-network.id
  private_ip_google_access = true
}


#### create firewall rule

resource "google_compute_firewall" "sspark-ingress-rule" {
  name    = "sspark-ingress-rule"
  network = google_compute_network.sspark-network.name
  priority  = 1000
  direction = "INGRESS"
  source_ranges = ["10.0.0.0/8"]
  allow {
  protocol = "all"
  }
}

#### create sspark cloud run app (deploy)



#### create sspark pubsub subsription 



#### create sspark service account