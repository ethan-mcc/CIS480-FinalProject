"""
Process RVshare Class B Data
Converts scraped JSON data into clean CSV for analysis
"""

import pandas as pd
import json
import os

def process_scraped_data(input_file, output_file):
    """
    Process scraped RVshare JSON data into clean CSV
    
    Args:
        input_file: Path to scraped JSON file
        output_file: Path to save cleaned CSV
    """
    print("="*60)
    print("Processing RVshare Class B Data")
    print("="*60)
    
    # load json data
    print(f"\nLoading data from: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"ERROR: File not found: {input_file}")
        print("Please run scrape_rvshare_classb.py first to collect data.")
        return None
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} listings")
    
    # convert to dataframe
    df = pd.DataFrame(data)
    
    if len(df) == 0:
        print("WARNING: No data found in file")
        return None
    
    print("\nData Summary:")
    print(f"  - Total listings: {len(df)}")
    print(f"  - Columns: {len(df.columns)}")
    
    # clean and validate data
    print("\nCleaning data...")
    
    # remove duplicates based on listing id
    df = df.drop_duplicates(subset=['listing_id'], keep='first')
    print(f"  - After removing duplicates: {len(df)} listings")
    
    # remove listings without price
    df = df.dropna(subset=['price_nightly'])
    print(f"  - After removing missing prices: {len(df)} listings")
    
    # remove extreme outliers likely data errors
    # keep prices between 50 and 1000 night
    df = df[(df['price_nightly'] >= 50) & (df['price_nightly'] <= 1000)]
    print(f"  - After removing price outliers: {len(df)} listings")
    
    # calculate total amenities
    amenity_cols = [col for col in df.columns if col.startswith('has_')]
    if amenity_cols:
        df['total_amenities'] = df[amenity_cols].sum(axis=1)
        print(f"  - Calculated total amenities across {len(amenity_cols)} features")
    
    # sort by state and price
    df = df.sort_values(['state', 'price_nightly'])
    
    # save to csv
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"SUCCESS! Saved to: {output_file}")
    print(f"{'='*60}")
    
    # Print statistics
    print("\nFinal Dataset Statistics:")
    print(f"  - Total Records: {len(df)}")
    print(f"  - States Covered: {df['state'].nunique()}")
    print(f"  - Year Range: {df['year'].min():.0f} - {df['year'].max():.0f}")
    
    print("\nPrice Statistics:")
    print(df['price_nightly'].describe())
    
    if 'total_amenities' in df.columns:
        print("\nAmenity Statistics:")
        print(df['total_amenities'].describe())
    
    print("\nTop 5 States by Listing Count:")
    print(df['state'].value_counts().head())
    
    print("\nSample Data:")
    print(df[['name', 'year', 'price_nightly', 'state', 'total_amenities']].head(10))
    
    return df

if __name__ == "__main__":
    input_file = '../Data/raw/rvshare_classb_scraped.json'
    output_file = '../Data/processed/rvshare_classb_amenities.csv'
    
    df = process_scraped_data(input_file, output_file)
    
    if df is not None:
        print("\n" + "="*60)
        print("READY FOR POWER BI!")
        print("="*60)
        print(f"\nImport this file into Power BI:")
        print(f"  {output_file}")

