import pytz
from datetime import datetime
timezone = pytz.timezone('Asia/Singapore')
current_time = datetime.now(timezone)
print("Current date and time", current_time.strftime('%Y-%m-%d %H:%M:%S'))


import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import re
from google.cloud import storage

os.environ["PATH"] += ":/usr/bin/chromedriver"

URL = r"https://activesg.gov.sg/gym-capacity"
UA = "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3"

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode (no GUI)
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(f'user-agent={UA}')

webdriver.Chrome(options=chrome_options)

# Initialize the ChromeDriver
driver = webdriver.Chrome(options=chrome_options)

# Open the URL
driver.get(URL)

# Wait until the page is fully loaded by checking for a specific element
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'chakra-badge')))

# Get the page source
page_source = driver.page_source

# Parse the page content using BeautifulSoup
soup = bs(page_source, 'lxml')

# Print the text content of the page (you can also target specific elements here)
print(soup.text)

# Prepare a list of dictionaries to hold the data
gym_data = []

for item in soup.find_all(class_='chakra-card__body'):
    gym_data.append({
        'Gym Name': item.find('p', class_='chakra-text').get_text(),
        'Capacity %': item.find('span', class_='chakra-badge').get_text()
    })

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(gym_data)

try:
  # Clean the 'Capacity' column by removing '%' and 'full'
  df['Capacity %'] = df['Capacity %'].str.replace('%', '').str.replace('full', '').str.strip()
except:
  pass

df['As of datetime'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
print(df)

formatted_time = current_time.strftime('%Y-%m-%d_%H%M')

file_name = f"gym_{formatted_time}.parquet"

df.to_parquet(file_name)

print("Current directory:", os.getcwd())
print(f"DataFrame saved as: {file_name}")

# Define GCS bucket details
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "my-creds.json"
bucket_name = "your-bucket-name"
folder_name = current_time.strftime('%Y-%m-%d')
destination_blob = f"data/{folder_name}/{file_name}"  # Path in GCS

# Initialize GCS client
client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob(destination_blob)

# Upload the file
blob.upload_from_filename(file_name)

print(f" Uploaded {file_name} to gs://{bucket_name}/{destination_blob}")