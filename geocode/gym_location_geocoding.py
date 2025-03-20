from geopy.geocoders import GoogleV3
import pandas as pd
import time

df = pd.read_csv('gymlist.csv')

API_KEY = "BVzaSyAeSEhk3sG1yZtVe52fbdek1ysplDDE3C" #Fake key
geolocator = GoogleV3(api_key=API_KEY)

def get_coordinates(location):
    try:
        geocode_result = geolocator.geocode(location, timeout=10)
        time.sleep(0.5)  # Add a delay to avoid rate limits
        if geocode_result:
            return pd.Series([geocode_result.latitude, geocode_result.longitude])
        else:
            return pd.Series([None, None])  # No results found
    except Exception as e:
        print(f"Error geocoding {location}: {e}")
        return pd.Series([None, None])

df[['Latitude', 'Longitude']] = df['Gym Name'].apply(get_coordinates)

df.to_csv('gymlist_geocode.csv', index=False)
# Note: The 2 'Toa Payoh' locations have exact same coordinates which is incorrect. This is manually edited in the output file.