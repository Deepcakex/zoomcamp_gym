from google.cloud import storage, bigquery
import pandas as pd
import io
import pyarrow.parquet as pq
import os

# Set up your Google Cloud details
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "my-creds.json"
BUCKET_NAME = "your-bucket-name"
GCS_FOLDER = "data/"  # Folder containing the Parquet files
BQ_PROJECT = "your-project"
BQ_DATASET = "bq_dataset"
BQ_TABLE = "gymdata"

# Initialize clients
storage_client = storage.Client()
bigquery_client = bigquery.Client()

# List all Parquet files in the bucket
bucket = storage_client.bucket(BUCKET_NAME)
blobs = bucket.list_blobs(prefix=GCS_FOLDER)

# Read all Parquet files into DataFrames
dfs = []
for blob in blobs:
    if blob.name.endswith(".parquet"):
        print(f"Reading: {blob.name}")
        file_stream = io.BytesIO(blob.download_as_bytes())  # Download the file
        df = pq.read_table(file_stream).to_pandas()  # Read Parquet into DataFrame
        dfs.append(df)

# Combine all DataFrames
if dfs:
    new_data = pd.concat(dfs, ignore_index=True)
    print(f"Total new records: {len(new_data)}")

    # Fetch existing data from BigQuery
    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
    query = f"SELECT DISTINCT * FROM `{table_id}`"
    
    try:
        existing_data = bigquery_client.query(query).to_dataframe()
        print(f"Existing records in BQ: {len(existing_data)}")

        # Merge new data with existing data, keeping only unique rows
        combined_data = pd.concat([existing_data, new_data]).drop_duplicates()
    except Exception as e:
        print(f"Error fetching existing data: {e}")
        combined_data = new_data  # If table does not exist, upload all new data

    # Only upload new unique records
    new_unique_records = combined_data[~combined_data.duplicated()]
    
    if not new_unique_records.empty:
        job = bigquery_client.load_table_from_dataframe(new_unique_records, table_id, job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"  # Change to "WRITE_APPEND" if you want to always append
        ))
        job.result()  # Wait for the job to complete

        print(f"Successfully uploaded {len(new_unique_records)} unique rows to {table_id}")
    else:
        print("No new unique records to upload.")
else:
    print("No Parquet files found in the bucket.")
