terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.19.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project = var.project
  region  = var.region
}

#Type this for credentials in terminal (WINDOWS):
# $env:GOOGLE_CREDENTIALS="C:/Users/Me/Desktop/Zoomcamp/my-creds.json"
# echo $env:GOOGLE_CREDENTIALS

resource "google_storage_bucket" "capstone_bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "capstone_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}