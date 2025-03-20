import requests
import pandas as pd
from datetime import datetime, timedelta
from geopy.distance import geodesic
import pytz
from google.cloud import storage, bigquery
import io
import pyarrow.parquet as pq
import os


# Initialize empty list to store all rainfall records
all_rainfall_records = []

# Define the start and end time
sg_tz = pytz.timezone('Asia/Singapore')
today = datetime.now(sg_tz)
start_time = datetime(today.year, today.month, today.day, 7, 0)  # 7:00 AM
end_time = datetime(today.year, today.month, today.day, 22, 30)  # 10:30 PM

# Initialize the current time to start_time
current_time = start_time
current_date = current_time.strftime("%Y-%m-%d") #to add date suffix to parquet filename

# Loop through the time intervals from 7:00 AM to 10:30 PM with a 30-minute increment
while current_time <= end_time:
    # Format the current time as the URL query parameter
    url = f"https://api-open.data.gov.sg/v2/real-time/api/rainfall?date={current_time.isoformat()}"

    # Make the request
    response = requests.get(url)
    data = response.json()

    # Extract station details and create the station dataframe
    stations = data['data']['stations']
    station_df = pd.DataFrame([{
        'station_id': s['id'],
        'station_name': s['name'],
        'latitude': s['location']['latitude'],
        'longitude': s['location']['longitude']
    } for s in stations])

    # Extract all rainfall readings
    for reading in data['data']['readings']:
        timestamp = reading['timestamp']
        for entry in reading['data']:
            entry['timestamp'] = timestamp  # Add timestamp to each reading
            all_rainfall_records.append(entry)

    # Increment time by 30 minutes
    current_time += timedelta(minutes=30)


# Convert the accumulated rainfall records to a DataFrame
rainfall_df = pd.DataFrame(all_rainfall_records)

# Merge with station data
sg_rainfall_df = station_df.merge(rainfall_df, left_on='station_id', right_on='stationId').drop(columns=['stationId'])

# Function to calculate the distance between two lat-long coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters

#Load the gym location and respective spatial coordinates
gymlist_geocode = pd.read_csv('gymlist_geocode.csv')

# Find the nearest station for each gym
nearest_stations = []

for _, gym in gymlist_geocode.iterrows():
    gym_coords = (gym['Latitude'], gym['Longitude'])
    nearest_station = None
    min_distance = float('inf')  # Set initial distance to a very large value

    for _, station in station_df.iterrows():
        station_coords = (station['latitude'], station['longitude'])
        distance = calculate_distance(gym_coords[0], gym_coords[1], station_coords[0], station_coords[1])

        if distance < min_distance:
            min_distance = distance
            nearest_station = station['station_name']

    nearest_stations.append(nearest_station)

# Add the nearest station to the gym dataframe
gymlist_geocode['nearest_station'] = nearest_stations
combined_df = pd.merge(gymlist_geocode, station_df, left_on='nearest_station', right_on='station_name', how='left')
combined_df.drop(columns=['station_name', 'Latitude', 'Longitude', 'latitude', 'longitude'], inplace=True)

# Final dataset with data recorded every 30 mins
final_df = pd.merge(combined_df, sg_rainfall_df, left_on='station_id', right_on='station_id', how='left')
final_df.drop(columns=['station_id','station_name','latitude','longitude'], inplace=True)
final_df = final_df.rename(columns={'nearest_station': 'Nearest Station'})
final_df["timestamp"] = pd.to_datetime(final_df["timestamp"]).dt.round("30min") #Roundoff to nearest 30 min
final_df = final_df.drop_duplicates()
final_df["timestamp"] = pd.to_datetime(final_df["timestamp"]) + pd.Timedelta(hours=8)
print(final_df.head())

file_name = f"rainfall_{current_date}.parquet"
final_df.to_parquet(file_name, engine='pyarrow', index=False)

############################
#@@ Saving to GCS Bucket @@#
############################
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "my-creds.json"
bucket_name = "your-bucket-name"
destination_blob = f"rainfall/{file_name}"  # Path in GCS

client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob(destination_blob)

blob.upload_from_filename(file_name)
print(f" Uploaded {file_name} to gs://{bucket_name}/{destination_blob}")

###########################
#@@ Storing in Bigquery @@#
###########################
GCS_FOLDER = "rainfall/"  # Folder containing the Parquet files
BQ_PROJECT = "your-project"
BQ_DATASET = "bq_dataset"
BQ_TABLE = "rainfall"

# Initialize clients
storage_client = storage.Client()
bigquery_client = bigquery.Client()

# List all Parquet files in the bucket
bucket = storage_client.bucket(bucket_name)
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

        print(f" Successfully uploaded {len(new_unique_records)} unique rows to {table_id}")
    else:
        print("No new unique records to upload.")
else:
    print("No Parquet files found in the bucket.")
