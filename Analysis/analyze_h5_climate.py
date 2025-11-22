import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def analyze_climate_impact():
    
    # load data
    # Don't change where anything is in the file path, it's already correct
    if os.path.exists('Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('Data/processed/master_dataset_powerbi.csv')
    else:
        df = pd.read_csv('../Data/processed/master_dataset_powerbi.csv')
    output_dir = 'visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    # filter for valid data
    df_clean = df.dropna(subset=['Avg_Temp_F', 'Alt_Housing_Growth_Pct_Capped'])
    
    # first the scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_clean, x='Avg_Temp_F', y='Alt_Housing_Growth_Pct_Capped', alpha=0.4, color='orange')
    plt.title('Climate vs. Alternative Housing Growth')
    plt.xlabel('Average Annual Temperature (°F)')
    plt.ylabel('Alt Housing Growth (%)')
    
    # highlight moderate zone
    plt.axvspan(55, 70, color='green', alpha=0.1, label='Moderate Zone (55-70°F)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/H5_Climate_Scatter.png')
    plt.close()
    
    # then my bar chart by climate zone
    if 'Climate_Zone' in df_clean.columns:
        plt.figure(figsize=(10, 6))
        # luckily i'm from the midwest so cold is 40f or lower, not arizona where it's 70f lol
        order = ['Cold (<40)', 'Cool (40-55)', 'Moderate (55-70)', 'Hot (>70)']
        sns.barplot(data=df_clean, x='Climate_Zone', y='Alt_Housing_Growth_Pct_Capped', order=order, palette='coolwarm')
        plt.title('Growth by Climate Zone')
        plt.savefig(f'{output_dir}/H5_Climate_Bar.png')
        plt.close()

if __name__ == "__main__":
    analyze_climate_impact()

