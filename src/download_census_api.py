import requests
import pandas as pd
import os

def download_census_data():
    """Download county-level Census data for all US counties"""
    
    print("Downloading county-level Census data...")
    
    # download detailed tables b series
    print("Fetching detailed tables...")
    params_detailed = {
        'get': 'NAME,B25077_001E,B01003_001E,B08006_001E,B08006_017E',
        'for': 'county:*',
        'in': 'state:*'
    }
    
    try:
        response = requests.get("https://api.census.gov/data/2023/acs/acs5", params=params_detailed)
        response.raise_for_status()
        data = response.json()
        df_detailed = pd.DataFrame(data[1:], columns=data[0])
        print(f"Downloaded {len(df_detailed)} counties (detailed tables)")
    except Exception as e:
        print(f"Error downloading detailed tables: {e}")
        return None
    
    # download subject tables s series income
    print("Fetching subject tables (income)...")
    params_subject = {
        'get': 'NAME,S1901_C01_012E',
        'for': 'county:*',
        'in': 'state:*'
    }
    
    try:
        response = requests.get("https://api.census.gov/data/2023/acs/acs5/subject", params=params_subject)
        response.raise_for_status()
        data = response.json()
        df_subject = pd.DataFrame(data[1:], columns=data[0])
        print(f"Downloaded {len(df_subject)} counties (subject tables)")
    except Exception as e:
        print(f"Error downloading subject tables: {e}")
        return None
    
    # merge the two datasets
    df_detailed['GeoID'] = df_detailed['state'] + df_detailed['county']
    df_subject['GeoID'] = df_subject['state'] + df_subject['county']
    
    df = df_detailed.merge(df_subject[['GeoID', 'S1901_C01_012E']], on='GeoID', how='left')
    
    # rename columns
    df.rename(columns={
        'S1901_C01_012E': 'Median_Household_Income',
        'B25077_001E': 'Median_Home_Value',
        'B01003_001E': 'Population',
        'B08006_001E': 'Total_Workers',
        'B08006_017E': 'Worked_From_Home'
    }, inplace=True)
    
    # convert to numeric
    for col in ['Median_Household_Income', 'Median_Home_Value', 'Population', 'Total_Workers', 'Worked_From_Home']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # calculate remote work percentage
    df['Remote_Work_Pct'] = (df['Worked_From_Home'] / df['Total_Workers']) * 100
    
    # save
    output_dir = '../Data/raw/census_api'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'county_data_2023.csv')
    df.to_csv(output_file, index=False)
    
    print(f"Merged and saved {len(df)} counties")
    print(f"Saved to {output_file}")
    print(f"\nSample data:")
    print(df[['GeoID', 'NAME', 'Median_Household_Income', 'Median_Home_Value', 'Population', 'Remote_Work_Pct']].head())
    return df

if __name__ == "__main__":
    download_census_data()
