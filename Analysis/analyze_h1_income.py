import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import statsmodels.api as sm

def analyze_income_impact():
    
    # load data
    # Don't change where anything is in the file path, it's already correct
    # Use absolute path or correct relative path depending on execution context
    # Assuming execution from project root
    if os.path.exists('Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('Data/processed/master_dataset_powerbi.csv')
    else:
        # Fallback to relative path if run from inside Analysis/
        df = pd.read_csv('../Data/processed/master_dataset_powerbi.csv')
    output_dir = 'visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    # filter for valid data
    df_clean = df.dropna(subset=['Median_Household_Income', 'Alt_Housing_Growth_Pct_Capped'])
    
    # this scatter plot with trend line
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_clean, x='Median_Household_Income', y='Alt_Housing_Growth_Pct_Capped', 
                scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
    plt.title('Impact of Median Household Income on Alternative Housing Growth')
    plt.xlabel('Median Household Income ($)')
    plt.ylabel('Alt Housing Growth (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/H1_Income_Scatter.png')
    plt.close()
    
    # box plot by income band
    if 'Income_Band' in df_clean.columns:
        plt.figure(figsize=(10, 6))
        order = ['Low', 'Medium-Low', 'Medium-High', 'High']
        sns.boxplot(data=df_clean, x='Income_Band', y='Alt_Housing_Growth_Pct_Capped', order=order)
        plt.title('Alternative Housing Growth Distribution by Income Level')
        plt.savefig(f'{output_dir}/H1_Income_Boxplot.png')
        plt.close()

if __name__ == "__main__":
    analyze_income_impact()

