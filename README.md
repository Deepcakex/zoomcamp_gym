# **Zoomcamp Capstone Project** - SG Gym Analysis

## 1. **Problem Statement:**

Gym-goers often struggle with overcrowding, leading to a suboptimal workout experience, while gym operators face challenges in managing capacity efficiently to ensure an even distribution of members throughout the day. However, there is often a lack of data-driven insights into when and why gyms experience peak or low occupancy.

ActiveSG gyms, located across various sports centers in Singapore, aim to provide affordable and accessible workout facilities. This project seeks to analyze occupancy trends in these gyms based on location, time of day, day of the week, and external factors such as weather (e.g., rainfall). By leveraging real-time capacity data collected every 30 minutes, we can identify patterns that impact gym utilization. These insights will help gym-goers plan their visits more effectively while enabling gym operators to optimize staffing, equipment availability, and membership management.


## 2. **Overview:**

![image](https://github.com/user-attachments/assets/3d4e60b5-0364-4ac8-afa6-205e3bbd2a94)

<ins>Pipeline Design Architecture:</ins>
1. **Data Source**: Sourced from 2 areas -- (1) [ActiveSG gym capacity](https://activesg.gov.sg/gym-capacity), (2) [Rainfall across Singapore](https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view)
2. **Data Lake**: Extracted data is pushed into _Google Cloud Storage Buckets_ as parquet files partitioned by date
3. **Data Warehouse**: Parquet files are ingested to _BigQuery_
4. **BI Platform**: Dashboard is developed using _Tableau Desktop_ and published to _Tableau Server_. (Tableau Server acts as the BI gateway or query proxy between BigQuery and the published dashboards)
