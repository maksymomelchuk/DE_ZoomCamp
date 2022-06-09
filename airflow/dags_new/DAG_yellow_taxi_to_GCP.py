

from airflow import DAG
import os

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator

from ingest_to_gcp import upload_to_gcp


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trip_data_all')

# Definition of downloaded files

URL_PREFIX = 'https://nyc-tlc.s3.amazonaws.com/trip+data/'
FILE_NAME = 'yellow_tripdata_'
URL_TEMPLATE = URL_PREFIX + FILE_NAME + \
    '{{ execution_date.strftime("%Y-%m") }}.parquet'
OUTPUT_FILE_TEMPLATE = 'yellow_taxi_{{ execution_date.strftime("%Y-%m") }}'
YEAR = '{{ execution_date.strftime("%Y") }}'


local_workflow = DAG(

    "Yellow_taxi_to_GCP",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2020, 12, 31),
    max_active_runs=3
)


with local_workflow:

    wget_task = BashOperator(
        task_id='wget',
        bash_command=f'curl -sSL {URL_TEMPLATE} > {AIRFLOW_HOME}/{OUTPUT_FILE_TEMPLATE}'
    )

    local_to_gcs_task = PythonOperator(
        task_id="upload_to_cloud",
        python_callable=upload_to_gcp,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"yellow_taxi/{OUTPUT_FILE_TEMPLATE}",
            "local_file": f"{AIRFLOW_HOME}/{OUTPUT_FILE_TEMPLATE}",
        }
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "yellow_taxi",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/yellow_taxi/*"],
            },
        },
    )


wget_task >> local_to_gcs_task >> bigquery_external_table_task
