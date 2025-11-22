import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import statsmodels.api as sm
import numpy as np

def analyze_density_impact():
    
    # load data
    # Don't change where anything is in the file path, it's already correct
    if os.path.exists('Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('Data/processed/master_dataset_powerbi.csv')
    else:
        df = pd.read_csv('../Data/processed/master_dataset_powerbi.csv')
    output_dir = 'visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    # filter for valid data
    df_clean = df.dropna(subset=['Population_Density', 'Alt_Housing_Growth_Pct_Capped'])
    
    # scatter plot log scale for density due to skew
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_clean, x='Population_Density', y='Alt_Housing_Growth_Pct_Capped', alpha=0.4)
    plt.xscale('log')
    plt.title('Impact of Population Density on Alt Housing Growth (Log Scale)')
    plt.xlabel('Population Density (People/Sq Mile) - Log Scale')
    plt.ylabel('Alt Housing Growth (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/H2_Density_Scatter.png')
    plt.close()
    
    # bar chart by density category
    if 'Density_Category' in df_clean.columns:
        plt.figure(figsize=(10, 6))
        order = ['Rural', 'Low-Density', 'Medium-Density', 'Urban']
        sns.barplot(data=df_clean, x='Density_Category', y='Alt_Housing_Growth_Pct_Capped', order=order, estimator=np.mean)
        plt.title('Average Alternative Housing Growth by Density Category')
        plt.savefig(f'{output_dir}/H2_Density_Bar.png')
        plt.close()

if __name__ == "__main__":
    analyze_density_impact()

