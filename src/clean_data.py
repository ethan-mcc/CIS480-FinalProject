import os
import pandas as pd
import glob
import numpy as np

def clean_data():
    
    # 1. load policymap data dependent variable
    print("\n[1/6] Loading PolicyMap data (Dependent Variable)...")
    policymap_files = glob.glob('../Data/raw/PolicyMap Data (County) (Percent change 5 years).csv')
    if not policymap_files:
        print("ERROR: PolicyMap data not found.")
        return
    
    df_target = pd.read_csv(policymap_files[0])
    df_target = df_target.dropna(subset=['GeoID'])
    
    value_col = [c for c in df_target.columns if c not in ['GeoID', 'GeoID_Name', 'GeoID_Description', 'SitsinState', 'GeoID_Formatted', 'TimeFrame', 'GeoVintage', 'Source', 'Location']]
    if value_col:
        df_target = df_target[['GeoID', 'GeoID_Name', value_col[0]]].copy()
        df_target.rename(columns={value_col[0]: 'Alt_Housing_Growth_Pct'}, inplace=True)
        df_target['GeoID'] = df_target['GeoID'].astype(str).str.replace('"', '').str.zfill(5)
    else:
        print("ERROR: Could not identify value column in PolicyMap data.")
        return

    # load census api data income housing population remote work

    census_files = glob.glob('../Data/raw/census_api/county_data_2023.csv')
    if census_files:
        df_census = pd.read_csv(census_files[0])
        df_census['GeoID'] = df_census['GeoID'].astype(str).str.zfill(5)
        
        # select relevant columns
        df_census = df_census[['GeoID', 'Median_Household_Income', 'Median_Home_Value', 
                               'Population', 'Remote_Work_Pct']].copy()
        
    else:
        print("Run download_census_api.py first?")
        df_census = pd.DataFrame(columns=['GeoID', 'Median_Household_Income', 'Median_Home_Value', 'Population', 'Remote_Work_Pct'])

    # load land area data
    land_files = glob.glob('../Data/raw/gazetteer/county_land_area.csv')
    if land_files:
        df_land = pd.read_csv(land_files[0])
        df_land['GeoID'] = df_land['GeoID'].astype(str).str.zfill(5)
        df_land = df_land[['GeoID', 'Land_Area_Sq_Miles']].copy()
    else:
        print("  WARNING: Land area data not found. Run download_land_area.py first.")
        df_land = pd.DataFrame(columns=['GeoID', 'Land_Area_Sq_Miles'])

    # load climate data noaa
    print("\n[4/6] Loading climate data...")
    climate_files = glob.glob('../Data/raw/Noaa-countyaveragetemperature*.csv')
    if climate_files:
        df_climate = pd.read_csv(climate_files[0], header=3)
        
        if 'Value' in df_climate.columns and 'ID' in df_climate.columns:
            df_climate.rename(columns={'Value': 'Avg_Temp_F'}, inplace=True)
            
            # map state abbreviations to fips codes
            state_map = {
                'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09', 'DE': '10',
                'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
                'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27',
                'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34', 'NM': '35',
                'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44',
                'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53',
                'WV': '54', 'WI': '55', 'WY': '56'
            }
            
            def convert_noaa_id(noaa_id):
                parts = str(noaa_id).split('-')
                if len(parts) == 2:
                    state_abbr, county_code = parts
                    state_fips = state_map.get(state_abbr)
                    if state_fips:
                        return f"{state_fips}{county_code}"
                return None

            df_climate['GeoID'] = df_climate['ID'].apply(convert_noaa_id)
            df_climate = df_climate.dropna(subset=['GeoID'])
            df_climate = df_climate[['GeoID', 'Avg_Temp_F']]
            df_climate['Avg_Temp_F'] = pd.to_numeric(df_climate['Avg_Temp_F'], errors='coerce')
    else:
        print("  WARNING: Climate data not found.")
        df_climate = pd.DataFrame(columns=['GeoID', 'Avg_Temp_F'])

    # --- merge all data ---
    df_final = df_target.copy()
    
    # merge census data
    if not df_census.empty:
        before = len(df_final)
        df_final = df_final.merge(df_census, on='GeoID', how='left')
    
    # merge land area
    if not df_land.empty:
        df_final = df_final.merge(df_land, on='GeoID', how='left')
    
    # calculate population density
    if 'Population' in df_final.columns and 'Land_Area_Sq_Miles' in df_final.columns:
        df_final['Population_Density'] = df_final['Population'] / df_final['Land_Area_Sq_Miles']
    
    # merge climate
    if not df_climate.empty:
        df_final = df_final.merge(df_climate, on='GeoID', how='left')
    
    # outlier detection for growth
    Q1 = df_final['Alt_Housing_Growth_Pct'].quantile(0.25)
    Q3 = df_final['Alt_Housing_Growth_Pct'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_final['Is_Outlier_Growth'] = ((df_final['Alt_Housing_Growth_Pct'] < lower_bound) | 
                                     (df_final['Alt_Housing_Growth_Pct'] > upper_bound))
    
    # winsorizing capping extreme values
    p05 = df_final['Alt_Housing_Growth_Pct'].quantile(0.05)
    p95 = df_final['Alt_Housing_Growth_Pct'].quantile(0.95)
    df_final['Alt_Housing_Growth_Pct_Capped'] = df_final['Alt_Housing_Growth_Pct'].clip(lower=p05, upper=p95)

    # state column
    df_final['State_FIPS'] = df_final['GeoID'].str[:2]
    
    # income bands for power bi slicers
    if 'Median_Household_Income' in df_final.columns:
        df_final['Income_Band'] = pd.qcut(df_final['Median_Household_Income'], 
                                           q=4, 
                                           labels=['Low', 'Medium-Low', 'Medium-High', 'High'],
                                           duplicates='drop')
    
    # climate zones for power bi slicers
    if 'Avg_Temp_F' in df_final.columns:
        bins = [0, 40, 55, 70, 100]
        labels = ['Cold (<40)', 'Cool (40-55)', 'Moderate (55-70)', 'Hot (>70)']
        df_final['Climate_Zone'] = pd.cut(df_final['Avg_Temp_F'], bins=bins, labels=labels)
    
    # density categories
    if 'Population_Density' in df_final.columns:
        df_final['Density_Category'] = pd.qcut(df_final['Population_Density'], 
                                                q=4, 
                                                labels=['Rural', 'Low-Density', 'Medium-Density', 'Urban'],
                                                duplicates='drop')

    # save result
    output_dir = '../Data/processed'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'master_dataset_powerbi.csv')
    df_final.to_csv(output_file, index=False)
    
    print(f"DOne: {output_file}")
    
    for col in ['Alt_Housing_Growth_Pct', 'Median_Household_Income', 'Median_Home_Value', 
                'Population_Density', 'Avg_Temp_F', 'Remote_Work_Pct']:
        if col in df_final.columns:
            pct = (df_final[col].notna().sum() / len(df_final)) * 100
            print(f"  - {col}: {pct:.1f}% complete")

if __name__ == "__main__":
    clean_data()
