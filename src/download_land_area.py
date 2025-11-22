import requests
import pandas as pd
import os

def download_land_area():
    """Download 2023 Census Gazetteer file with county land areas"""
    
    print("Downloading county land area data...")
    
    # 2023 gazetteer file url
    url = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_counties_national.zip"
    
    try:
        # download the zip file
        print(f"Fetching from {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        # save temporarily
        temp_zip = '../Data/raw/temp_gazetteer.zip'
        with open(temp_zip, 'wb') as f:
            f.write(response.content)
        
        print("Downloaded zip file, extracting...")
        
        # extract and read
        import zipfile
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall('../Data/raw/gazetteer')
        
        # read the txt file tab delimited
        gaz_file = '../Data/raw/gazetteer/2023_Gaz_counties_national.txt'
        df = pd.read_csv(gaz_file, sep='\t', encoding='latin1')
        
        print(f"Loaded {len(df)} counties")
        print(f"Columns: {df.columns.tolist()}")
        
        # create geoid from geoid column
        df['GeoID'] = df['GEOID'].astype(str).str.zfill(5)
        
        # keep relevant columns
        df_clean = df[['GeoID', 'NAME', 'ALAND_SQMI']].copy()
        df_clean.rename(columns={'ALAND_SQMI': 'Land_Area_Sq_Miles'}, inplace=True)
        
        # save
        output_file = '../Data/raw/gazetteer/county_land_area.csv'
        df_clean.to_csv(output_file, index=False)
        
        print(f"Saved to {output_file}")
        print(df_clean.head())
        
        # clean up temp file
        os.remove(temp_zip)
        
        return df_clean
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    download_land_area()

