import pandas as pd
import numpy as np
import glob
import os
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    # calculate great circle distance between two points on the earth specified in decimal degrees
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    # i know random trig from developing so many games without an engine 
    # I know this is probably overkill 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # radius of earth in miles
    return c * r

def calculate_park_distance():

    # load master dataset
    master_file = '../Data/processed/master_dataset_powerbi.csv'
    if not os.path.exists(master_file):
        print("Error: Master dataset not found. Run clean_data.py first.")
        return
    
    df_master = pd.read_csv(master_file)
    df_master['GeoID'] = df_master['GeoID'].astype(str).str.zfill(5)
    print(f"Loaded {len(df_master)} counties from master dataset.")

    # load county coordinates gazetteer (a word a learned for just geo dictionary)
    gazetteer_files = glob.glob('../Data/raw/gazetteer/*.txt')
    if not gazetteer_files:
        print("Error: Gazetteer text file not found.")
        return
    
    print(f"Loading coordinates from {gazetteer_files[0]}...")
    # gazetteer is usually tab separated iso-8859-1 (sorry i am always on random platforms)
    df_geo = pd.read_csv(gazetteer_files[0], sep='\t', encoding='ISO-8859-1', dtype={'GEOID': str})
    df_geo.columns = [c.strip() for c in df_geo.columns] # clean whitespace from headers
    
    if 'INTPTLAT' not in df_geo.columns or 'INTPTLONG' not in df_geo.columns:
        print("Error: Lat/Long columns not found in Gazetteer.")
        return

    df_geo = df_geo[['GEOID', 'INTPTLAT', 'INTPTLONG']].copy()
    df_geo.rename(columns={'GEOID': 'GeoID', 'INTPTLAT': 'County_Lat', 'INTPTLONG': 'County_Lon'}, inplace=True)
    
    # merge coordinates into master
    df_master = df_master.merge(df_geo, on='GeoID', how='left')
    print(f"Merged coordinates. Missing coords: {df_master['County_Lat'].isna().sum()}")

    # load national parks
    parks_file = '../Data/raw/national_parks_coords.csv'
    if not os.path.exists(parks_file):
        print("Error: National Parks file not found.")
        return
        
    df_parks = pd.read_csv(parks_file)
    print(f"Loaded {len(df_parks)} National Parks.")

    # calculate distances
    print("Calculating distances (this might take a moment)...")
    
    # prepare arrays for vectorization or efficient looping
    # since we have 3000 counties and 60 parks a nested loop is fine 180000 ops is instant
    
    min_distances = []
    nearest_parks = []

    park_lats = df_parks['Lat'].values
    park_lons = df_parks['Lon'].values
    park_names = df_parks['Name'].values
    
    for idx, row in df_master.iterrows():
        c_lat = row['County_Lat']
        c_lon = row['County_Lon']
        
        if pd.isna(c_lat) or pd.isna(c_lon):
            min_distances.append(np.nan)
            nearest_parks.append(None)
            continue
            
        # vectorized haversine for one county vs all parks
        # its cleaner to just loop or use a ckdtree but lets stick to simple loop for clarity if needed
        # but actually numpy vectorization is better (this is way to complicated )
        
        # convert single point to radians
        lat1, lon1 = map(radians, [c_lat, c_lon])
        
        # convert all parks to radians
        lat2 = np.radians(park_lats)
        lon2 = np.radians(park_lons)
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 3956
        dist_miles = c * r
        
        # find min
        min_idx = np.argmin(dist_miles)
        min_distances.append(dist_miles[min_idx])
        nearest_parks.append(park_names[min_idx])
        
        if idx % 500 == 0:
            print(f"  Processed {idx} counties...")

    df_master['Distance_to_Park_Miles'] = min_distances
    df_master['Nearest_Park'] = nearest_parks

    # 5. save
    df_master.to_csv(master_file, index=False)
    print(f"Saved updated dataset with Park Distances to {master_file}")
    print(df_master[['GeoID_Name', 'Distance_to_Park_Miles', 'Nearest_Park']].head())

if __name__ == "__main__":
    calculate_park_distance()

