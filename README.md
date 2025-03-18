# **ActiveSG Gym Analysis** 

## 1. **Problem Statement:**

Gym-goers often struggle with overcrowding, leading to a suboptimal workout experience, while gym operators face challenges in managing capacity efficiently to ensure an even distribution of members throughout the day. However, there is often a lack of data-driven insights into when and why gyms experience peak or low occupancy.

ActiveSG gyms, located across various sports centers in Singapore, aim to provide affordable and accessible workout facilities. This project seeks to analyze occupancy trends in these gyms based on location, time of day, day of the week, and external factors such as weather (e.g., rainfall). By leveraging real-time capacity data collected every 30 minutes, we can identify patterns that impact gym utilization. These insights will help gym-goers plan their visits more effectively while enabling gym operators to optimize staffing, equipment availability, and membership management.


## 2. **Overview:**

![image](https://github.com/user-attachments/assets/8fa0cad8-63ad-408a-b967-47fab62681d6)

### <ins>Pipeline Design Architecture:</ins>
1. **Data Source**: Sourced from 2 areas -- (1) [ActiveSG gym capacity](https://activesg.gov.sg/gym-capacity), (2) [Rainfall across Singapore](https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view)
2. **IaC Provisioning:** _Terraform_ is used to provision Google Cloud Infrastructure for data lake and warehouse
3. **Workflow Orchestration:** _Kestra_ installed on Google Cloud Compute Engine within Docker containers - to schedule data collection and ingestion.
4. **Storage & Ingestion**: Extracted data is pushed to _Google Cloud Storage Buckets_ (Data Lake) as parquet files and ingested to _BigQuery_ (Data Warehouse).
5. **Data Visualization**: Dashboard is developed using _Tableau Desktop_ and published to _Tableau Server_. (Tableau Server acts as the BI gateway or query proxy between BigQuery and the published dashboards)


## 3. **Resources Setup**
### <ins>3.1 Identify Data Sources</ins>
(1) [ActiveSG gym capacity](https://activesg.gov.sg/gym-capacity), 
- Contains the percentage capacity of various ActiveSG gyms updated at regular intervals (0% means completely empty and 100 means full).
- The opening hours of the gym varies by location, usually between 7am-9.30pm/10pm.
- To better capture the occupancy rates, data harvesting will be scheduled at every 30 min interval from 7.30am-9pm.


(2) [Rainfall across Singapore](https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view)
- Contains the rainfall data in various collection stations all over the island.
- This is an additional dataset to better understand the effects of weather on gym utilization
- Complete rain data is scheduled for retrieval at 11pm daily, where data points are taken at every 30 min interval from 7.30am-9pm.



### <ins>3.2 Creating Resources</ins>
This creates resources within Google Cloud Platform (GCP), where the service account is created followed by storage buckets and BigQuery. Ensure that the 3 roles are assigned to this service account, following which we will create a new key which is named **my-creds.json**.

![image](https://github.com/user-attachments/assets/cd46e756-35ba-4ce5-805d-ceb1e5c60a14)

Both the **main.tf** file and the **variables.tf** should be located in the same directory. The following commands are run on VScode to (1) Initialize terraform, (2) Review changes, (3) Create resources on Google Cloud.

```
terraform init
terraform plan
terraform apply
```

### <ins>3.3 Setting up workflow resources</ins>
For setting up Kestra within Google Cloud, refer to the following [guide](https://www.youtube.com/watch?v=qwA7-hm7d2o) (skipped the cloud postgres SQL section as it wasn't relevant).

Run the Kestra UI by keying in the following in the compute engine SSH
```
sudo docker compose up
```
Input http://12.345.678.910:8080/ in the url to open Kestra UI. (URL is fake)

![image](https://github.com/user-attachments/assets/8e089b93-0440-4c82-b6ba-3c81c5201e0e)


## 4. **Deployment Setup**
### Geocode the location
### Python files
### Kestra flow diagram

## 5. **Dashboard Access:**
### Preview
### How to access
### How to use

## 6. **Contributors**
Author:
Email:
Citations:
