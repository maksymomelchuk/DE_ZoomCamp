

from airflow import DAG
import os
import logging

import pandas as pd

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


URL_TEMPLATE = 'https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv'
OUTPUT_FILE_TEMPLATE = 'zones.csv'


local_workflow = DAG(

    "Zones",
    schedule_interval='@once',
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2020, 12, 31),
    max_active_runs=1
)


def format_to_parquet(src_file):
    print("Start checking for CSV file...")
    if not src_file.endswith('.csv'):
        logging.error(
            "Can only accept source files in CSV format, for the moment")
        return
    df = pd.read_csv(f"{AIRFLOW_HOME}/{OUTPUT_FILE_TEMPLATE}")
    df.to_parquet(OUTPUT_FILE_TEMPLATE)

    print("File restructered to parquet")
    print(src_file)
    print(OUTPUT_FILE_TEMPLATE)
    return OUTPUT_FILE_TEMPLATE


with local_workflow:

    wget_task = BashOperator(
        task_id='wget',
        bash_command=f'curl -sSL {URL_TEMPLATE} > {AIRFLOW_HOME}/{OUTPUT_FILE_TEMPLATE}'
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{AIRFLOW_HOME}/{OUTPUT_FILE_TEMPLATE}",
        },
    )

    local_to_gcs_task = PythonOperator(
        task_id="upload_to_cloud",
        python_callable=upload_to_gcp,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"zones/{OUTPUT_FILE_TEMPLATE}",
            "local_file": f"{AIRFLOW_HOME}/{OUTPUT_FILE_TEMPLATE}",
        }
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "zones",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/zones/*"],
            },
        },
    )


wget_task >> format_to_parquet_task >> local_to_gcs_task >> bigquery_external_table_task
