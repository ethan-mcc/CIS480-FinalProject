import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def analyze_nature_impact():
    
    # load data
    # Don't change where anything is in the file path, it's already correct
    if os.path.exists('Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('Data/processed/master_dataset_powerbi.csv')
    else:
        df = pd.read_csv('../Data/processed/master_dataset_powerbi.csv')
    output_dir = 'visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    # filter valid data
    df_clean = df.dropna(subset=['Distance_to_Park_Miles', 'Alt_Housing_Growth_Pct_Capped'])
    
    # 1. scatter plot distance to park vs growth
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_clean, x='Distance_to_Park_Miles', y='Alt_Housing_Growth_Pct_Capped',
                scatter_kws={'alpha':0.3, 'color':'purple'}, line_kws={'color':'black'})
    plt.title('Does Proximity to National Parks Drive Growth?')
    plt.xlabel('Distance to Nearest National Park (Miles)')
    plt.ylabel('Alt Housing Growth (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/H4_Park_Distance_Scatter.png')
    plt.close()
    
    # 2. infrastructure campground density vs growth
    if 'Campgrounds_Within_30mi' in df_clean.columns:
        # bin the campground counts
        df_clean['Campground_Bins'] = pd.cut(df_clean['Campgrounds_Within_30mi'], 
                                             bins=[-1, 0, 5, 10, 20, 1000],
                                             labels=['0', '1-5', '6-10', '11-20', '20+'])
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_clean, x='Campground_Bins', y='Alt_Housing_Growth_Pct_Capped', palette='viridis')
        plt.title('Alt Housing Growth by Campground Density')
        plt.xlabel('Number of Campgrounds within 30 miles')
        plt.ylabel('Avg Alt Housing Growth (%)')
        plt.savefig(f'{output_dir}/H4_Campground_Density_Bar.png')
        plt.close()


if __name__ == "__main__":
    analyze_nature_impact()

