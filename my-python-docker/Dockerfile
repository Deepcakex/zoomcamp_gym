# Step 1: Use an official Python base image (Python 3.9 slim version)
FROM python:3.9-slim
USER root
# Step 2: Update apt and install necessary dependencies
RUN apt-get update -y && \
    apt-get install -y wget curl ca-certificates && \
    apt-get install -y chromium chromium-driver && \
    apt-get install -y openjdk-8-jdk

# Step 3: Install Python dependencies
RUN pip install --no-cache-dir pandas selenium webdriver-manager beautifulsoup4 pytz pyspark requests lxml fastparquet pyarrow google-cloud-storage google-cloud-bigquery pandas-gbq 

# Step 4: Set environment variables for Chrome and Chromedriver path
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/lib/chromium/chromedriver

# Step 5: Set working directory (if needed)
WORKDIR /app

# Step 6: Command to run the app or container (if you have a script)
# CMD ["python", "your_script.py"]
