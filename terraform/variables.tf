variable "credentials" {
  description = "My Credentials"
  default     = "C:/Users/Me/Desktop/Zoomcamp/my-creds.json"
}

variable "project" {
  description = "Project"
  default     = "your-project"
}

variable "region" {
  description = "Region"
  default     = "asia-southeast1"
}

variable "location" {
  description = "Project Location"
  default     = "asia-southeast1"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "bq_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "your-bucket-name"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}