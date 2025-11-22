import requests
import json
import pandas as pd
import numpy as np
import os
import time
from math import radians, cos, sin, asin, sqrt

def fetch_osm_campgrounds():
    print("="*60)
    print("Fetching Campground Data from OpenStreetMap (Overpass API)...")
    print("="*60)
    
    output_file = '../Data/raw/osm_campgrounds.json'
    
    if os.path.exists(output_file):
        print(f"Found existing campground data at {output_file}")
        with open(output_file, 'r') as f:
            data = json.load(f)
    else:
        # overpass ql query
        # we use a simplified bounding box for us to avoid area timeout issues sometimes
        # 24.396308 -125.000000 sw to 49.384358 -66.934570 ne approx conus
        # actually lets try the area filter first its cleaner
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = """
        [out:json][timeout:180];
        area["ISO3166-1"="US"]->.searchArea;
        (
          node["tourism"="camp_site"](area.searchArea);
          way["tourism"="camp_site"](area.searchArea);
          relation["tourism"="camp_site"](area.searchArea);
        );
        out center;
        """
        
        print("Sending query to Overpass API (this may take 1-2 minutes)...")
        try:
            response = requests.get(overpass_url, params={'data': overpass_query})
            if response.status_code == 200:
                data = response.json()
                with open(output_file, 'w') as f:
                    json.dump(data, f)
                print(f"Successfully saved {len(data.get('elements', []))} campgrounds to {output_file}")
            else:
                print(f"Error fetching data: {response.status_code}")
                print(response.text)
                return
        except Exception as e:
            print(f"Exception during fetch: {e}")
            return

    # process data
    elements = data.get('elements', [])
    camp_lats = []
    camp_lons = []
    
    for el in elements:
        lat = el.get('lat')
        lon = el.get('lon')
        # for ways relations center provides lat lon
        if lat is None and 'center' in el:
            lat = el['center'].get('lat')
            lon = el['center'].get('lon')
            
        if lat and lon:
            camp_lats.append(lat)
            camp_lons.append(lon)
            
    print(f"Processed {len(camp_lats)} valid campground locations.")
    
    # calculate density per county campgrounds within 30 miles
    master_file = '../Data/processed/master_dataset_powerbi.csv'
    if not os.path.exists(master_file):
        print("Error: Master dataset not found.")
        return
        
    df_master = pd.read_csv(master_file)
    print("Calculating campground density for each county...")
    
    # convert to numpy arrays for vectorization
    camp_lats = np.radians(np.array(camp_lats))
    camp_lons = np.radians(np.array(camp_lons))
    
    counts_30mi = []
    
    # loop through counties
    # optimizing calculating distance matrix for 3000x15000 is 45m ops doable in python numpy
    # but lets do it batch by batch or just loop counties
    
    for idx, row in df_master.iterrows():
        # check for county lat might need to be remerged if previous script didnt save it
        # ah previous script saved it if i ran it lets check columns
        # if county lat missing we need to remerge gazetteer
        # the previous script saved df master to file so it should have the merged cols if it ran
        
        # wait calculate park distance py merges but does it keep the columns
        # yes it saves df master to csv
        
        if 'County_Lat' not in df_master.columns:
             # fallback if not present e.g. if previous script failed or wasnt run
             print("Warning: County_Lat not found in master. Run calculate_park_distance.py first.")
             return

        c_lat = row['County_Lat']
        c_lon = row['County_Lon']
        
        if pd.isna(c_lat):
            counts_30mi.append(0)
            continue
            
        # vectorized haversine against all campgrounds
        lat1 = radians(c_lat)
        lon1 = radians(c_lon)
        
        dlon = camp_lons - lon1
        dlat = camp_lats - lat1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(camp_lats) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 3956
        dists = c * r
        
        # count how many are within 30 miles
        count = np.sum(dists <= 30)
        counts_30mi.append(count)
        
        if idx % 500 == 0:
            print(f"  Processed {idx} counties...")

    df_master['Campgrounds_Within_30mi'] = counts_30mi
    
    # save
    df_master.to_csv(master_file, index=False)
    print(f"Saved updated dataset with Campground Counts to {master_file}")
    print(df_master[['GeoID_Name', 'Campgrounds_Within_30mi']].head())

if __name__ == "__main__":
    fetch_osm_campgrounds()

