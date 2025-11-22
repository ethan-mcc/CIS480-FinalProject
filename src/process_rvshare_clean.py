"""
Clean RVshare Class B Data Processor
Processes RVshare data (from scraping or existing CSV) focusing on Class B RVs
Creates analysis-ready dataset for amenity pricing analysis
"""

import pandas as pd
import numpy as np
import re
import os
import glob

def clean_price(price_str):
    """Convert price string like '$95' or '$1,990' to numeric"""
    if pd.isna(price_str) or price_str == '':
        return np.nan
    cleaned = str(price_str).replace('$', '').replace(',', '')
    try:
        return float(cleaned)
    except:
        return None

def extract_amenities_list(amenity_str):
    """Convert comma-separated amenity string to list"""
    if pd.isna(amenity_str) or amenity_str == '':
        return []
    return [a.strip() for a in str(amenity_str).split(',')]

def create_amenity_features(df):
    """
    Create binary amenity features from amenity columns
    
    Args:
        df: DataFrame with bathroom, kitchen, entertainment, temperature_control columns
    
    Returns:
        DataFrame with added binary amenity columns
    """
    
    # define amenity mappings
    amenity_map = {
        # bathroom
        'has_shower': ['shower'],
        'has_toilet': ['toilet'],
        'has_bathroom_sink': ['bathroom sink'],
        
        # kitchen
        'has_refrigerator': ['refrigerator', 'fridge'],
        'has_microwave': ['microwave'],
        'has_kitchen_sink': ['kitchen sink'],
        'has_stove': ['range', 'stove', 'range (stove)'],
        'has_oven': ['oven'],
        
        # entertainment
        'has_tv': ['tv', 'television'],
        'has_dvd_player': ['dvd player', 'dvd'],
        'has_radio': ['am/fm radio', 'radio', 'am/fm'],
        'has_cd_player': ['cd player'],
        'has_bluetooth': ['bluetooth', 'ipod docking station'],
        
        # climate
        'has_ac': ['air conditioning', 'roof air conditioning', 'in dash air conditioning', 'a/c', 'ac'],
        'has_heating': ['heating', 'furnace', 'hot & cold water supply'],
        
        # other
        'has_slide_out': ['slide out', 'slideout'],
        'has_generator': ['generator'],
        'has_awning': ['awning'],
    }
    
    # combine all amenity columns into one text field per row
    amenity_cols = ['bathroom', 'kitchen', 'entertainment', 'temperature_control']
    existing_cols = [col for col in amenity_cols if col in df.columns]
    
    if not existing_cols:
        print("  WARNING: No amenity columns found")
        return df
    
    df['all_amenities_text'] = df[existing_cols].fillna('').agg(' '.join, axis=1).str.lower()
    
    # create binary features
    for feature_name, keywords in amenity_map.items():
        df[feature_name] = df['all_amenities_text'].apply(
            lambda x: 1 if any(keyword in x for keyword in keywords) else 0
        )
    
    # count total amenities
    amenity_feature_cols = list(amenity_map.keys())
    df['total_amenities'] = df[amenity_feature_cols].sum(axis=1)
    
    return df

def process_classb_data(input_files=None, output_file='../Data/processed/rvshare_classb_amenities.csv'):
    """
    Process RVshare data and create Class B focused dataset
    
    Args:
        input_files: List of CSV files or glob pattern (default: existing rvshare data)
        output_file: Path to save processed CSV
    """
    
    # default to existing data if no input specified
    if input_files is None:
        # try to find data in scrapingexamplerepo or data raw
        patterns = [
            '../scrapingexamplerepo/rvshare/data/rvshare_*.csv',
            '../Data/raw/rvshare_*.csv',
            '../Data/raw/rvshare_classb_scraped.json',
            '../Data/pre_processed_data/rvshare_api_data.csv',
            '../Data/processed/rvshare_api_data.csv'
        ]
        
        found_files = []
        for pattern in patterns:
            found_files.extend(glob.glob(pattern))
        
        if not found_files:
            print("\nERROR: No RVshare data files found.")
            print("Searched in:")
            for pattern in patterns:
                print(f"  - {pattern}")
            print("\nPlease either:")
            print("  1. Run scrape_rvshare_classb.py to collect new data")
            print("  2. Place existing CSV files in Data/raw/")
            return None
        
        input_files = found_files
        print(f"\nFound {len(input_files)} data file(s)")
    
    # load data
    print("\nLoading data...")
    dfs = []
    
    for file in input_files if isinstance(input_files, list) else [input_files]:
        print(f"  - {os.path.basename(file)}")
        
        if file.endswith('.json'):
            # load json format from scraper
            import json
            with open(file, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            # load csv format
            df = pd.read_csv(file)
        
        dfs.append(df)
    
    # combine all dataframes
    df_all = pd.concat(dfs, ignore_index=True)
    
    # check for required columns
    if 'price_nightly' not in df_all.columns and 'rate' in df_all.columns:
        df_all['price_nightly'] = df_all['rate']
    elif 'price_nightly' not in df_all.columns:
        print("  WARNING: 'price_nightly' column not found. Using available columns.")
        if 'rate' in df_all.columns:
             df_all['price_nightly'] = df_all['rate']
        else:
             # Check if we have 'price_nightly_clean' already
             if 'price_nightly_clean' in df_all.columns:
                 df_all['price_nightly'] = df_all['price_nightly_clean']
             else:
                 print("  ERROR: No price column found (looked for 'price_nightly', 'rate', or 'price_nightly_clean').")
                 return None

    # show vehicle type distribution
    if 'vehicle_type' in df_all.columns:
        print("\nVehicle Type Distribution:")
        for vtype, count in df_all['vehicle_type'].value_counts().head(10).items():
            print(f"  - {vtype}: {count:,}")
    
    if 'vehicle_type' in df_all.columns:
        class_b_mask = df_all['vehicle_type'].str.contains('Class B', case=False, na=False)
    elif 'vehicle_class' in df_all.columns:
        class_b_mask = df_all['vehicle_class'].str.contains('Class B', case=False, na=False)
    else:
        print("  WARNING: No vehicle type column found, using all data")
        class_b_mask = pd.Series([True] * len(df_all))
    
    df = df_all[class_b_mask].copy()
    
    # clean price data
    print("clean the prices")
    # Convert to string first to handle numeric inputs if already clean
    df['price_nightly_clean'] = df['price_nightly'].astype(str).apply(clean_price)
    
    if 'price_weekly' in df.columns:
        df['price_weekly_clean'] = df['price_weekly'].apply(clean_price)
    if 'price_monthly' in df.columns:
        df['price_monthly_clean'] = df['price_monthly'].apply(clean_price)
    
    # remove listings without valid price
    df = df.dropna(subset=['price_nightly_clean'])
    
    # remove extreme outliers likely data errors
    df = df[(df['price_nightly_clean'] >= 45) & (df['price_nightly_clean'] <= 1000)]
    
    # extract state from location if needed
    if 'state' not in df.columns and 'location' in df.columns:
        df['state'] = df['location'].str.extract(r',\s*([A-Z]{2})$')
    
    # create amenity features
    df = create_amenity_features(df)
    
    # select final columns
    base_cols = ['name', 'location', 'state', 'year', 'vehicle_type', 'sleeps', 'length',
                 'price_nightly_clean']
    
    # add optional columns if they exist
    optional_cols = ['price_weekly_clean', 'price_monthly_clean', 'vehicle_class', 'make', 'model']
    for col in optional_cols:
        if col in df.columns:
            base_cols.append(col)
    
    # add amenity columns
    amenity_cols = [col for col in df.columns if col.startswith('has_')]
    amenity_cols.append('total_amenities')
    
    final_cols = [col for col in base_cols + amenity_cols if col in df.columns]
    df_final = df[final_cols].copy()
    
    # remove duplicates
    if 'name' in df_final.columns:
        df_final = df_final.drop_duplicates(subset=['name'], keep='first')
    
    # sort by state and price
    sort_cols = []
    if 'state' in df_final.columns:
        sort_cols.append('state')
    sort_cols.append('price_nightly_clean')
    df_final = df_final.sort_values(sort_cols)
    
    # save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_final.to_csv(output_file, index=False)
    
    display_cols = ['name', 'year', 'price_nightly_clean', 'total_amenities']
    if 'state' in df_final.columns:
        display_cols.append('state')
    display_cols = [c for c in display_cols if c in df_final.columns]
    
    return df_final

if __name__ == "__main__":
    df = process_classb_data()
    
    if df is not None:
        print("done ready!")
