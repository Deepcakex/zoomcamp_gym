# **ActiveSG Gym Analysis** 

## 1. **Problem Statement:**

Gym-goers often struggle with overcrowding, leading to a suboptimal workout experience, while gym operators face challenges in managing capacity efficiently to ensure an even distribution of members throughout the day. However, there is often a lack of data-driven insights into when and why gyms experience peak or low occupancy.

ActiveSG gyms, located across various sports centers in Singapore, aim to provide affordable and accessible workout facilities. This project seeks to analyze occupancy trends in these gyms based on location, time of day, day of the week, and external factors such as weather (e.g., rainfall). By leveraging real-time capacity data collected every 30 minutes, we can identify patterns that impact gym utilization. These insights will help gym-goers plan their visits more effectively while enabling gym operators to optimize staffing, equipment availability, and membership management.

&nbsp;
## 2. **Overview:**

![image](https://github.com/user-attachments/assets/21409939-30db-49f5-83d1-32317f3197d6)

### <ins>Pipeline Design Architecture:</ins>
1. **Data Source**: Sourced from 2 areas -- (1) [ActiveSG gym capacity](https://activesg.gov.sg/gym-capacity), (2) [Rainfall across Singapore](https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view)
2. **IaC Provisioning:** _Terraform_ is used to provision Google Cloud Infrastructure for data lake and warehouse
3. **Workflow Orchestration:** _Kestra_ installed on Google Cloud Compute Engine within Docker containers
4. **Storage & Ingestion**: Extracted data is pushed to _Google Cloud Storage Buckets_ (Data Lake) as parquet files and ingested to _BigQuery_ (Data Warehouse)
5. **Data Visualization**: Dashboard is developed using _Tableau Desktop_ and published to _Tableau Server_ (Tableau Server acts as the BI gateway or query proxy between BigQuery and the published dashboards)

&nbsp;
## 3. **Resources Setup**
### <ins>3.1 Identify Data Sources</ins>
(1) [ActiveSG gym capacity](https://activesg.gov.sg/gym-capacity), 
- Contains the percentage capacity of various ActiveSG gyms updated at regular intervals (0% means completely empty and 100% implies full).
- The opening hours of the gym varies by location, usually between 7am-9.30pm/10pm.
- To better capture the occupancy rates, data collection will be scheduled at every 30 min interval from 7.30am-9pm.


(2) [Rainfall across Singapore](https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view)
- Contains the rainfall data in various collection stations all over the island.
- This is an additional dataset to better understand the effects of weather on gym utilization
- Complete rain data is scheduled for retrieval at 11pm daily, where data points are taken at every 30 min interval from 7.30am-9pm.



### <ins>3.2 Creating Resources</ins>
This creates resources within Google Cloud Platform (GCP), where the service account is created followed by storage buckets and BigQuery. Ensure that the 3 roles are assigned to this service account, following which we will create a new key which is named **my-creds.json**.

![image](https://github.com/user-attachments/assets/c9ef31c7-ca5b-4898-bf00-ac15c0fc790c)

Both the **main.tf** file and the **variables.tf** should be located in the same directory. The following commands are run on VScode to (1) Initialize terraform, (2) Review changes, (3) Create resources on Google Cloud.

```
terraform init
terraform plan
terraform apply
```

### <ins>3.3 Setting up workflow resources</ins>
For setting up Kestra within Google Cloud, refer to the following [guide](https://www.youtube.com/watch?v=qwA7-hm7d2o) (skipped the cloud postgres SQL section as it wasn't relevant). 

Installation and Docker setup are not covered in the video but the steps may be found below. 
```
> sudo apt update
> sudo apt install -y ca-certificates curl gnupg
> sudo install -m 0755 -d /etc/apt/keyrings
> curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
> sudo chmod a+r /etc/apt/keyrings/docker.asc
> echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
> sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
> sudo docker --version
```

Run the Kestra UI by keying in the following in the compute engine SSH
```
sudo docker compose up
```
Input http://12.345.678.91:8080/ in the url to open Kestra UI. (URL is for illustration purposes)

![image](https://github.com/user-attachments/assets/8e089b93-0440-4c82-b6ba-3c81c5201e0e)

### <ins>3.4 Building an image on Docker Hub with preinstalled python packages & tools</ins>
For installation of relevant python packages & scraper tools to use within Kestra, you may refer to the file **my-python-docker/Dockerfile**. (Note that this is done on local machine)
```
> cd my-python-docker
> docker build -t my-custom-python-image:latest .
> docker login
> docker tag my-custom-python-image:latest xswordcraftx/my-custom-python-image:latest
> docker push xswordcraftx/my-custom-python-image:latest
```
Published image may be found in this [link](https://hub.docker.com/r/xswordcraftx/my-custom-python-image) 

&nbsp;
## 4. **Deployment**
### <ins>4.1 Geocode the location</ins>
For better visualization on maps, the spatial coordinates of each gym location will be generated through Google Map API.

- **Input File:** gymlist.csv
- **Processing Script:** gym_location_geocoding.py
- **Output File:** gymlist_geocode.csv


### <ins>4.2 Kestra Workflow 1</ins>:
`kestra_gym_scraper.yml` 
- **gym_scraper.py** - To store the gym capacity records of each location within Google Cloud Buckets 
- **bucket_to_bq.py** - Ingest the data from bucket to BigQuery

![image](https://github.com/user-attachments/assets/d3811e75-36ed-46b1-b5cc-000231fc4092)

![image](https://github.com/user-attachments/assets/cd630eb0-4a6d-4cd8-a263-d32e6dc7f510)

### <ins>4.3 Kestra Workflow 2</ins>:
`kestra_sg_rainfall.yml`
- **sg_rainfall.py** - To store the rainfall records of each location within Google Cloud Buckets and ingestion to BigQuery
    - To determine if there is rain around the gym location, each gym will have the nearest rain collection station mapped to it.

![image](https://github.com/user-attachments/assets/945dd5d3-384d-4fe2-892e-a080e3813393)


&nbsp;
## 5. **Dashboard Access:**
### <ins>5.1 Preview</ins>
![ActiveSG Gym Occupancy Dashboard](https://github.com/user-attachments/assets/7551dc1f-2f47-4212-b2f2-f3f0a3656359)

### <ins>5.2 How to access</ins>
Link to dashboard: [ActiveSG Gym Occupancy Dashboard](https://prod-apsoutheast-b.online.tableau.com/#/site/laridef880-186fc6395f/views/sg_gym_capacity/ActiveSGGymOccupancyDashboard?:iid=1)
- **Username1:** `molaxol425@cybtric.com`
- **Password1:** `ABCDe!@#$5`

### <ins>5.3 How to use</ins>
**(IMPT)** Refresh dashboard to latest available data

![image](https://github.com/user-attachments/assets/7d7bde30-e1f8-4211-9deb-22d81d426138)

To reset filters and actions to default

![image](https://github.com/user-attachments/assets/53a8a631-c11d-4982-a777-2ccf7714ae8f)

### <ins>5.4 For your awareness</ins>
- 19/03/2025 - Missing data points in the morning due to compute engine issues on Google Cloud. Restored Kestra at noon but unable to backfill data as it is live.
- This project will stop running on the 8nd May 2025 as GCP credits are set to expire.
- As Tableau Server is on a 14 day free trial account, the URL will be changed every 2 weeks until the grading is complete.

&nbsp;
## 6. **Contributors**

**Author:** Deepcakex
