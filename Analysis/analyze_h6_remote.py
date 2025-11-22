import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def analyze_remote_work():
    
    # load data
    # Don't change where anything is in the file path, it's already correct
    if os.path.exists('Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('Data/processed/master_dataset_powerbi.csv')
    else:
        df = pd.read_csv('../Data/processed/master_dataset_powerbi.csv')
    output_dir = 'visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    # filter for valid data
    df_clean = df.dropna(subset=['Remote_Work_Pct', 'Alt_Housing_Growth_Pct_Capped'])
    
    # 1. scatter plot with trend
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_clean, x='Remote_Work_Pct', y='Alt_Housing_Growth_Pct_Capped',
                scatter_kws={'alpha':0.3, 'color':'teal'}, line_kws={'color':'black'})
    plt.title('Remote Work Prevalence vs. Alternative Housing Growth')
    plt.xlabel('Percentage of Remote Workers (%)')
    plt.ylabel('Alt Housing Growth (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/H6_RemoteWork_Scatter.png')
    plt.close()

if __name__ == "__main__":
    analyze_remote_work()

