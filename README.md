# **Zoomcamp Capstone Project** - SG Gym Analysis

## 1. **Problem Statement:**

Gym-goers often struggle with overcrowding, leading to a suboptimal workout experience, while gym operators face challenges in managing capacity efficiently to ensure an even distribution of members throughout the day. However, there is often a lack of data-driven insights into when and why gyms experience peak or low occupancy.

ActiveSG gyms, located across various sports centers in Singapore, aim to provide affordable and accessible workout facilities. This project seeks to analyze occupancy trends in these gyms based on location, time of day, day of the week, and external factors such as weather (e.g., rainfall). By leveraging real-time capacity data collected every 30 minutes, we can identify patterns that impact gym utilization. These insights will help gym-goers plan their visits more effectively while enabling gym operators to optimize staffing, equipment availability, and membership management.


## 2. **Overview:**

![image](https://github.com/user-attachments/assets/02585cc6-1afa-4f0e-91ad-5781eeaf167f)

<ins>Pipeline Design Architecture:</ins>
1. Data Source: Sourced from 2 areas -- (1) [ActiveSG gym capacity](https://activesg.gov.sg/gym-capacity), (2) [Rainfall across Singapore](https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view)
2. Data Lake: Extracted data is pushed into Google Cloud Storage Buckets as parquet files partitioned by date
3. Data Warehouse: Parquet files are ingested to BigQuery
4. BI Platform: Dashboard is developed using Tableau Desktop and published to Tableau server. (Tableau server acts as the BI gateway or query proxy between BigQuery and the published dashboards)
