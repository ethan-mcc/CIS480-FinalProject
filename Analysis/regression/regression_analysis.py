import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import os

def load_data():
    # load the county dataset
    if os.path.exists('Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('Data/processed/master_dataset_powerbi.csv')
    elif os.path.exists('../Data/processed/master_dataset_powerbi.csv'):
        df = pd.read_csv('../Data/processed/master_dataset_powerbi.csv')
    else:
        df = pd.read_csv('../../Data/processed/master_dataset_powerbi.csv')
    return df

def simple_regression(df, x_var, y_var, title, filename, output_dir):
    # clean data
    df_clean = df[[x_var, y_var]].dropna()
    
    # prepare data
    X = df_clean[x_var]
    y = df_clean[y_var]
    X_with_const = sm.add_constant(X)
    
    # fit regression model
    model = sm.OLS(y, X_with_const).fit()
    
    # extract statistics
    slope = model.params[x_var]
    intercept = model.params['const']
    r_squared = model.rsquared
    p_value = model.pvalues[x_var]
    n = len(df_clean)
    
    # create visualization
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # scatter plot
    ax.scatter(X, y, alpha=0.4, s=30, color='steelblue', edgecolors='none')
    
    # regression line
    x_range = np.linspace(X.min(), X.max(), 100)
    y_pred = intercept + slope * x_range
    ax.plot(x_range, y_pred, color='red', linewidth=2, label='Regression Line')
    
    # add statistics text box
    stats_text = f'Equation: y = {slope:.6f}x + {intercept:.2f}\n'
    stats_text += f'R² = {r_squared:.4f}\n'
    stats_text += f'p-value = {p_value:.4e}\n'
    stats_text += f'n = {n:,}'
    
    # position text box based on slope
    if slope > 0:
        text_x = 0.05
    else:
        text_x = 0.95
    
    ax.text(text_x, 0.95, stats_text,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment='top',
            horizontalalignment='left' if slope > 0 else 'right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # labels and title
    ax.set_xlabel(x_var.replace('_', ' '), fontsize=12)
    ax.set_ylabel(y_var.replace('_', ' '), fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}', dpi=300, bbox_inches='tight')
    plt.close()
    
    return {
        'variable': x_var,
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'p_value': p_value,
        'n': n
    }

def multiple_regression(df, x_vars, y_var, output_dir):
    # clean data
    vars_needed = x_vars + [y_var]
    df_clean = df[vars_needed].dropna()
    
    # prepare data
    X = df_clean[x_vars]
    y = df_clean[y_var]
    X_with_const = sm.add_constant(X)
    
    # fit model
    model = sm.OLS(y, X_with_const).fit()
    
    # calculate vif for multicollinearity check
    vif_data = pd.DataFrame()
    vif_data["Variable"] = x_vars
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(len(x_vars))]
    
    # visualize coefficients
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # plot 1 - coefficient values with confidence intervals
    params = model.params[1:]
    conf_int = model.conf_int().iloc[1:]
    errors = np.abs(conf_int.values - params.values.reshape(-1, 1))
    
    y_pos = np.arange(len(params))
    colors = ['green' if p < 0.05 else 'gray' for p in model.pvalues[1:]]
    
    ax1.barh(y_pos, params, xerr=errors[:, 0], color=colors, alpha=0.7, 
             error_kw={'elinewidth': 2, 'capsize': 5})
    ax1.axvline(x=0, color='black', linestyle='--', linewidth=1)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([var.replace('_', ' ') for var in x_vars], fontsize=9)
    ax1.set_xlabel('Coefficient Value', fontsize=11)
    ax1.set_title('Regression Coefficients\n(Green = Significant at p<0.05)', 
                  fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # plot 2 - model statistics
    ax2.axis('off')
    stats_text = "Multiple Regression Statistics\n"
    stats_text += "="*40 + "\n\n"
    stats_text += f"R² = {model.rsquared:.4f}\n"
    stats_text += f"Adjusted R² = {model.rsquared_adj:.4f}\n"
    stats_text += f"F-statistic = {model.fvalue:.2f}\n"
    stats_text += f"Prob (F-statistic) = {model.f_pvalue:.4e}\n"
    stats_text += f"Sample size = {int(model.nobs):,}\n\n"
    stats_text += "Significant Predictors (p < 0.05):\n"
    stats_text += "-"*40 + "\n"
    
    for var in x_vars:
        p_val = model.pvalues[var]
        if p_val < 0.05:
            coef = model.params[var]
            stats_text += f"{var.replace('_', ' ')}: {coef:.6f}\n"
            stats_text += f"  (p = {p_val:.4e})\n"
    
    ax2.text(0.1, 0.9, stats_text, transform=ax2.transAxes,
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/regression_multiple.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return model

def create_summary_table(results, output_dir):
    # create summary table
    summary_df = pd.DataFrame(results)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # format data for display
    display_data = []
    display_data.append(['Hypothesis', 'Variable', 'Slope', 'R²', 'P-Value', 'N'])
    
    hypotheses = ['H1', 'H2', 'H3', 'H4a', 'H4b', 'H5', 'H6']
    
    for i, result in enumerate(results):
        hypothesis = hypotheses[i] if i < len(hypotheses) else f'H{i+1}'
        var_name = result['variable'].replace('_', ' ')
        slope = f"{result['slope']:.6f}"
        r_sq = f"{result['r_squared']:.4f}"
        p_val = f"{result['p_value']:.4e}"
        n = f"{result['n']:,}"
        
        display_data.append([hypothesis, var_name, slope, r_sq, p_val, n])
    
    # create table
    table = ax.table(cellText=display_data, cellLoc='left', loc='center',
                     colWidths=[0.1, 0.3, 0.15, 0.1, 0.15, 0.1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # style header row
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')
    
    # style data rows with alternate colors
    for i in range(1, len(display_data)):
        for j in range(6):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#E7E6E6')
            else:
                cell.set_facecolor('#F2F2F2')
    
    plt.title('Summary of Simple Linear Regressions\nPredicting Alternative Housing Growth', 
              fontsize=14, fontweight='bold', pad=20)
    plt.savefig(f'{output_dir}/regression_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # setup
    output_dir = 'visuals'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # load data
    df = load_data()
    
    # define dependent variable
    y_var = 'Alt_Housing_Growth_Pct_Capped'
    
    # store results
    results = []
    
    # h1 income impact
    result = simple_regression(
        df, 
        'Median_Household_Income', 
        y_var,
        'H1: Impact of Median Household Income on Alternative Housing Growth',
        'regression_h1_income.png',
        output_dir
    )
    results.append(result)
    
    # h2 population density impact
    result = simple_regression(
        df,
        'Population_Density',
        y_var,
        'H2: Impact of Population Density on Alternative Housing Growth',
        'regression_h2_density.png',
        output_dir
    )
    results.append(result)
    
    # h3 housing cost impact
    result = simple_regression(
        df,
        'Median_Home_Value',
        y_var,
        'H3: Impact of Median Home Value on Alternative Housing Growth',
        'regression_h3_housing.png',
        output_dir
    )
    results.append(result)
    
    # h4a distance to parks
    result = simple_regression(
        df,
        'Distance_to_Park_Miles',
        y_var,
        'H4a: Impact of Distance to Nearest National Park',
        'regression_h4a_park_distance.png',
        output_dir
    )
    results.append(result)
    
    # h4b campground density
    result = simple_regression(
        df,
        'Campgrounds_Within_30mi',
        y_var,
        'H4b: Impact of Campground Density (within 30 miles)',
        'regression_h4b_campgrounds.png',
        output_dir
    )
    results.append(result)
    
    # h5 climate impact
    result = simple_regression(
        df,
        'Avg_Temp_F',
        y_var,
        'H5: Impact of Average Temperature on Alternative Housing Growth',
        'regression_h5_climate.png',
        output_dir
    )
    results.append(result)
    
    # h6 remote work impact
    result = simple_regression(
        df,
        'Remote_Work_Pct',
        y_var,
        'H6: Impact of Remote Work Percentage on Alternative Housing Growth',
        'regression_h6_remote.png',
        output_dir
    )
    results.append(result)
    
    # create summary table
    create_summary_table(results, output_dir)
    
    # multiple regression with all predictors
    x_vars = [
        'Median_Household_Income',
        'Population_Density',
        'Median_Home_Value',
        'Distance_to_Park_Miles',
        'Campgrounds_Within_30mi',
        'Avg_Temp_F',
        'Remote_Work_Pct'
    ]
    
    model = multiple_regression(df, x_vars, y_var, output_dir)
    
    print('analysis complete')

if __name__ == "__main__":
    main()

