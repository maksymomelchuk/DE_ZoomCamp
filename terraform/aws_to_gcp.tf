resource "google_project_service" "my_aws_to_gcp_storagetransfer" {
  project = var.project
  service = "my_aws_to_gcp_storagetransfer.googleapis.com"
}


data "google_storage_transfer_project_service_account" "default" {
  project = var.project
}

resource "google_storage_bucket" "my_aws_to_gcp_storage_transfer" {
  name          = "my_aws_to_gcp_storage_transfer"
  storage_class = "STANDARD"
  project       = var.project
  location      = "EU"
}

resource "google_storage_bucket_iam_member" "my_aws_to_gcp_storage_transfer-iam" {
  bucket     = google_storage_bucket.my_aws_to_gcp_storage_transfer.name
  role       = "roles/storage.admin"
  member     = "serviceAccount:${data.google_storage_transfer_project_service_account.default.email}"
  depends_on = [google_storage_bucket.my_aws_to_gcp_storage_transfer]
}

resource "google_storage_transfer_job" "s3-bucket-nightly-backup" {
  description = "Execute a cloud transfer job via terraform"
  project     = var.project

  transfer_spec {

    transfer_options {
      delete_objects_unique_in_sink = false
    }
    aws_s3_data_source {
      bucket_name = "nyc-tlc"
      aws_access_key {
        access_key_id     = "AKIA5JWRRN6CGCIK754C"
        secret_access_key = "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"
      }
    }
    gcs_data_sink {
      bucket_name = google_storage_bucket.my_aws_to_gcp_storage_transfer.name
      path        = ""
    }
  }

  schedule {
    schedule_start_date {
      year  = 2022
      month = 05
      day   = 28
    }
    schedule_end_date {
      year  = 2022
      month = 05
      day   = 28
    }

  }

  depends_on = [google_storage_bucket_iam_member.my_aws_to_gcp_storage_transfer-iam]
}