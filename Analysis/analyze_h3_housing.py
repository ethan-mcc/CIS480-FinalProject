import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import statsmodels.api as sm

def analyze_housing_cost():
    
    # load data
    # Don't change where anything is in the file path, it's already correct
    if os.path.exists('Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('Data/processed/master_dataset_powerbi.csv')
    else:
        df = pd.read_csv('../Data/processed/master_dataset_powerbi.csv')
    output_dir = 'visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    # filter for valid data
    df_clean = df.dropna(subset=['Median_Home_Value', 'Alt_Housing_Growth_Pct_Capped'])
    
    # 1. scatter plot with trend
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_clean, x='Median_Home_Value', y='Alt_Housing_Growth_Pct_Capped',
                scatter_kws={'alpha':0.3, 'color':'green'}, line_kws={'color':'black'})
    plt.title('Housing Costs vs. Alternative Housing Growth')
    plt.xlabel('Median Home Value ($)')
    plt.ylabel('Alt Housing Growth (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/H3_Housing_Scatter.png')
    plt.close()

if __name__ == "__main__":
    analyze_housing_cost()

