#!/usr/bin/env python3
"""
Master Data Pipeline Runner
Runs all data collection and processing scripts in the correct order
"""

import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"error here : {e}")
        return False
    except FileNotFoundError:
        print(f"broken script: {script_name}")
        return False

def main():
    """Run the complete data pipeline"""
    
    # change to src directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    steps = [
        ("download_census_api.py", "Download Census Data"),
        ("download_land_area.py", "Download Land Area Data"),
        ("clean_data.py", "Clean and Merge County Data"),
        ("process_rvshare_clean.py", "Process RVshare Amenity Data"),
    ]
    
    results = []
    for script, description in steps:
        success = run_script(script, description)
        results.append((description, success))
        
        if not success:
            print(f"broken at {description}")
            sys.exit(1)
    
    # completed
    print("done")

if __name__ == "__main__":
    main()

