import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def analyze_pricing():
    
    # load data
    # Don't change where anything is in the file path, it's already correct
    if os.path.exists('Data/processed/rvshare_classb_amenities.csv'):
        input_file = 'Data/processed/rvshare_classb_amenities.csv'
    else:
        input_file = '../Data/processed/rvshare_classb_amenities.csv'
    if not os.path.exists(input_file):
        print("Run finalize_rvshare_data.py first")
        return

    df = pd.read_csv(input_file)
    output_dir = 'visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. price vs amenity count
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='Amenity Count', y='Nightly Price', 
                scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.title('Impact of Amenity Count on Nightly Rental Price')
    plt.xlabel('Total Amenities')
    plt.ylabel('Nightly Price ($)')
    plt.savefig(f'{output_dir}/RV_Price_vs_Amenities.png')
    plt.close()
    
    # 2. bathroom premium
    plt.figure(figsize=(8, 6))
    sns.barplot(data=df, x='Has Bathroom', y='Nightly Price', palette='Blues')
    plt.title('Price Premium for Having a Bathroom')
    plt.xticks([0, 1], ['No Bathroom', 'Has Bathroom'])
    plt.ylabel('Avg Nightly Price ($)')
    plt.savefig(f'{output_dir}/RV_Bathroom_Premium.png')
    plt.close()

if __name__ == "__main__":
    analyze_pricing()

