import analyze_h1_income
import analyze_h2_density
import analyze_h3_housing
import analyze_h4_nature
import analyze_h5_climate
import analyze_h6_remote
import analyze_pricing
import os

# Make it easy to run, did use batch but I'm on macos / windows / manjaro sometimes so wanted to not have to deal with the ENDL in windows.
def run_all_analysis():    
    # ensure visuals directory exists
    os.makedirs('visuals', exist_ok=True)
    
    analyze_h1_income.analyze_income_impact()
    analyze_h2_density.analyze_density_impact()
    analyze_h3_housing.analyze_housing_cost()
    analyze_h4_nature.analyze_nature_impact()
    analyze_h5_climate.analyze_climate_impact()
    analyze_h6_remote.analyze_remote_work()
    analyze_pricing.analyze_pricing()
    
    print("All visualizations are done in this dir 'Analysis/visuals/'")

if __name__ == "__main__":
    run_all_analysis()

