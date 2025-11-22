import pandas as pd
import requests
import time
import random
import os
import json
from datetime import datetime

def fetch_rvshare_data():
    # 1. load county coordinates
    land_area_file = '../Data/raw/gazetteer/county_land_area.csv'
    if not os.path.exists(land_area_file):
        print(f"Error: {land_area_file} not found. Run download_land_area.py first.")
        return

    print("Loading county coordinates...")
    # read file handling potential tab delimiters if the original download was tab separated
    # but my previous script saved it as csv lets try csv first
    try:
        df_counties = pd.read_csv(land_area_file)
    except:
        df_counties = pd.read_csv(land_area_file, delimiter='\t')

    # ensure we have coordinates
    # the gazetteer file usually has intptlat and intptlong
    # my download land area py script outputted columns geoid name land area sq miles
    # wait my previous script download land area py only saved those 3 columns
    # i need to re download or re parse the raw gazetteer file to get the lat long
    # the raw file is in data raw gazetteer but extracted
    # lets check if we can find the raw txt file in that directory to get lat long
    
    gazetteer_dir = '../Data/raw/gazetteer'
    raw_files = [f for f in os.listdir(gazetteer_dir) if f.endswith('.txt') and 'counties' in f]
    
    if not raw_files:
        print("Error: Raw gazetteer text file not found to extract Lat/Long.")
        # fallback try to use a library or just fail
        # ill try to re read the zip or just finding the txt file is best
        return

    raw_file_path = os.path.join(gazetteer_dir, raw_files[0])
    print(f"Reading raw gazetteer file for coordinates: {raw_files[0]}")
    
    # gazetteer format is fixed width or tab separated usually tab or multiple spaces
    # its usually iso 8859 1 encoded
    df_geo = pd.read_csv(raw_file_path, sep='\t', encoding='ISO-8859-1', dtype={'GEOID': str})
    # clean column names remove whitespace
    df_geo.columns = [c.strip() for c in df_geo.columns]
    
    if 'INTPTLAT' not in df_geo.columns or 'INTPTLONG' not in df_geo.columns:
        print(f"Error: Lat/Long columns not found. Columns: {df_geo.columns}")
        return

    print(f"Found {len(df_geo)} counties with coordinates.")

    # 2. setup output
    output_file = '../Data/pre_processed_data/rvshare_api_data.csv'
    processed_ids = set()
    
    # ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # if file exists load it to resume deduplicate
    if os.path.exists(output_file):
        try:
            existing_df = pd.read_csv(output_file)
            processed_ids = set(existing_df['id'].astype(str))
            print(f"Resuming... {len(processed_ids)} unique RVs already collected.")
        except:
            print("Could not read existing file, starting fresh.")

    # 3. iterate and fetch
    results_list = []
    
    # create a requests session for better performance
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    })

    total_counties = len(df_geo)
    
    print("Starting API collection...")
    print("NOTE: This will filter for CLASS B vehicles as requested.")
    
    # shuffle to get a random sample of us if we stop early
    # df geo df geo sample frac 1 reset index drop true

    for i, row in df_geo.iterrows():
        lat = row['INTPTLAT']
        lng = row['INTPTLONG']
        county_name = row['NAME']
        
        # simple progress
        if i % 50 == 0:
            print(f"Processing {i}/{total_counties}: {county_name}...")
            # save progress periodically
            if results_list:
                new_df = pd.DataFrame(results_list)
                # append to file
                new_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
                results_list = [] # clear buffer
                print(f"  Saved batch. Total unique RVs: {len(processed_ids)}")

        try:
            # fetch up to 3 pages per county to get deep coverage
            for page in range(1, 4):
                url = f"https://rvshare.com/rv-rental.json?location={county_name}&lat={lat}&lng={lng}&rvshare_mode=false&rv_class=Class%20B%20Camping%20Van&distance=50&limit=50&page={page}"
                
                resp = session.get(url, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('data', {}).get('results', [])
                    pagination = data.get('pagination', {})
                    
                    if not items:
                        break # no more items stop paging for this county

                    for item in items:
                        rv_id = str(item.get('id'))
                        
                        # deduplicate
                        if rv_id in processed_ids:
                            continue
                        
                        attrs = item.get('attributes', {})
                        rv_type = attrs.get('type', '')
                        
                        # extract fields
                        rv_data = {
                            'id': rv_id,
                            'headline': attrs.get('headline'),
                            'make_model': attrs.get('rv_make_model'),
                            'year': attrs.get('rv_year'),
                            'type': rv_type,
                            'price_nightly': attrs.get('rate'),
                            'sleeps': attrs.get('how_many_it_sleeps'),
                            'length': attrs.get('length'),
                            'fresh_water_tank': attrs.get('fresh_water_tank'),
                            'electric_service': attrs.get('electric_service'),
                            'generator_included': attrs.get('generator_usage_included'),
                            'lat': attrs.get('location', {}).get('lat'),
                            'lng': attrs.get('location', {}).get('lng'),
                            'state': attrs.get('location', {}).get('state'),
                            'city': attrs.get('location', {}).get('name'),
                            'review_score': attrs.get('reviews', {}).get('score'),
                            'review_count': attrs.get('reviews', {}).get('count'),
                            'is_instant_book': attrs.get('is_instant_book'),
                            'search_county': county_name
                        }
                        
                        # simple amenity inference
                        rv_data['has_bathroom'] = 1 if (rv_data['fresh_water_tank'] or 0) > 10 else 0
                        rv_data['has_generator'] = 1 if (rv_data['generator_included'] or 0) > 0 else 0
                        
                        results_list.append(rv_data)
                        processed_ids.add(rv_id)
                    
                    # stop if weve reached the last page
                    if page >= pagination.get('totalPages', 1):
                        break
                
                else:
                    break # stop paging on error

        except Exception as e:
            print(f"  Error fetching {county_name}: {e}")
            time.sleep(2) # longer pause on error

        # faster rate limiting we need to move fast to cover 3000 counties
        time.sleep(0.05) 
    
    # final save
    if results_list:
        new_df = pd.DataFrame(results_list)
        new_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
        print(f"Saved final batch.")
        
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    fetch_rvshare_data()

