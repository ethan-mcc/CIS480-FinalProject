# Alternative Housing Market Analysis
# Scroll to the bottom for instructions of how to run everything!


## Visual Analysis Results

### Hypothesis Testing Visualizations

#### H1: Income Analysis
![H1 Income Scatter](Analysis/visuals/H1_Income_Scatter.png)
![H1 Income Boxplot](Analysis/visuals/H1_Income_Boxplot.png)

#### H2: Population Density Analysis
![H2 Density Scatter](Analysis/visuals/H2_Density_Scatter.png)
![H2 Density Bar](Analysis/visuals/H2_Density_Bar.png)

#### H3: Housing Market Analysis
![H3 Housing Scatter](Analysis/visuals/H3_Housing_Scatter.png)

#### H4: Nature Access Analysis
![H4 Park Distance Scatter](Analysis/visuals/H4_Park_Distance_Scatter.png)
![H4 Campground Density Bar](Analysis/visuals/H4_Campground_Density_Bar.png)

#### H5: Climate Analysis
![H5 Climate Scatter](Analysis/visuals/H5_Climate_Scatter.png)
![H5 Climate Bar](Analysis/visuals/H5_Climate_Bar.png)

#### H6: Remote Work Analysis
![H6 Remote Work Scatter](Analysis/visuals/H6_RemoteWork_Scatter.png)

#### RV Pricing Analysis
![RV Price vs Amenities](Analysis/visuals/RV_Price_vs_Amenities.png)
![RV Bathroom Premium](Analysis/visuals/RV_Bathroom_Premium.png)

---

### Regression Analysis Results

#### Individual Hypothesis Regressions
![Regression H1 Income](Analysis/regression/visuals/regression_h1_income.png)
![Regression H2 Density](Analysis/regression/visuals/regression_h2_density.png)
![Regression H3 Housing](Analysis/regression/visuals/regression_h3_housing.png)
![Regression H4a Park Distance](Analysis/regression/visuals/regression_h4a_park_distance.png)
![Regression H4b Campgrounds](Analysis/regression/visuals/regression_h4b_campgrounds.png)
![Regression H5 Climate](Analysis/regression/visuals/regression_h5_climate.png)
![Regression H6 Remote Work](Analysis/regression/visuals/regression_h6_remote.png)

#### Comprehensive Analysis
![Multiple Regression Analysis](Analysis/regression/visuals/regression_multiple.png)
![Regression Summary](Analysis/regression/visuals/regression_summary.png)

---

## Overview
This project analyzes the rise of alternative housing (RVs, vans, boats) across the United States. It combines Census data, geographic information, and RV rental listings to identify key drivers of this market shift.

**High-Level Workflow:**
1.  **Data Collection:** Python scripts fetch demographic data (Census), geographic data (National Parks, Campgrounds), and rental pricing (RVshare).
2.  **Processing:** Data is cleaned, merged into a master dataset, and enriched with calculated metrics like "Distance to National Park."
3.  **Analysis:** The system tests specific hypotheses (Income, Climate, Remote Work) and generates visual insights.

## Usage

### Prerequisites
*   Python 3.9 or higher
*   pip (Python package manager)

### Setup Instructions

**1. Clone the Repository**
```bash
git clone https://github.com/ethan-mcc/CIS480-FinalProject.git
cd CIS480-FinalProject
```

**2. Create Virtual Environment**
```bash
# macOS/Linux
python3 -m venv venv

# Windows
python -m venv venv
```

**3. Activate Virtual Environment**
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

> **Note:** The virtual environment (`venv/`) is not tracked in git. You must create it locally using the steps above.

### 1. Build the Dataset
Run the master pipeline to download and process all raw data.
```bash
python src/run_all.py
```

### Unfinished data processing: python src/scrape_rvshare_classb.py

### 2. Add Geographic Features
Calculate distances to parks and count local campgrounds (required for full analysis).
```bash
python src/calculate_park_distance.py
python src/fetch_campgrounds.py
```

### 3. Generate Analysis & Visuals
Run the visual analysis pipeline to test hypotheses and create charts.
```bash
python Analysis/run_analysis_pipeline.py
```

## Outputs

### Data Files (`Data/processed/`)
*   `master_dataset_powerbi.csv`: The comprehensive county-level dataset used for hypothesis testing. Contains columns for Income, Density, Climate, Remote Work, and Park Distance.
*   `rvshare_classb_amenities.csv`: A detailed list of Class B RV rentals with pricing and amenity features (Bathroom, Generator, etc.).

### Visualizations (`Analysis/visuals/`)
*   **H1_Income_Scatter.png**: Relationship between median income and housing growth.
*   **H4_Park_Distance_Scatter.png**: Impact of proximity to National Parks.
*   **H6_RemoteWork_Scatter.png**: Correlation between remote work and alternative housing.
*   **RV_Price_vs_Amenities.png**: Pricing model showing value of added amenities.


