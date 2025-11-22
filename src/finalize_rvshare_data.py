import pandas as pd
import os

def finalize_rv_data():
    input_file = '../Data/processed/rvshare_api_data.csv'
    output_file = '../Data/processed/rvshare_classb_amenities.csv'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file)

    # clean price
    # it seems price nightly is already float but lets ensure
    df['price_nightly'] = pd.to_numeric(df['price_nightly'], errors='coerce')
    
    # remove price outliers
    Q1 = df['price_nightly'].quantile(0.25)
    Q3 = df['price_nightly'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    original_len = len(df)
    df = df[(df['price_nightly'] >= lower) & (df['price_nightly'] <= upper)]
    print(f"Removed {original_len - len(df)} price outliers.")

    # create amenities count
    # specific columns we have has bathroom has generator is instant book
    # we can also use sleeps greater than 2 as an amenity proxy
    df['amenity_count'] = (
        df['has_bathroom'] + 
        df['has_generator'] + 
        df['is_instant_book'].astype(int)
    )
    
    # categorize year
    df['Vehicle_Age'] = 2025 - df['year']
    
    # rename for power bi clarity
    df.rename(columns={
        'price_nightly': 'Nightly Price',
        'year': 'Year',
        'make_model': 'Model',
        'city': 'City',
        'state': 'State',
        'amenity_count': 'Amenity Count',
        'has_bathroom': 'Has Bathroom',
        'has_generator': 'Has Generator',
        'is_instant_book': 'Instant Book'
    }, inplace=True)

    # select final columns
    final_cols = [
        'id', 'Model', 'Year', 'Vehicle_Age', 'Nightly Price', 
        'Amenity Count', 'Has Bathroom', 'Has Generator', 'Instant Book',
        'sleeps', 'length', 'review_score', 'City', 'State', 'lat', 'lng'
    ]
    
    df_final = df[final_cols].copy()
    
    df_final.to_csv(output_file, index=False)
    print(f"Saved finalized dataset to {output_file}")
    print(df_final.head())

if __name__ == "__main__":
    finalize_rv_data()

