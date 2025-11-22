# Alternative Housing Market Analysis

## Overview
This project analyzes the rise of alternative housing (RVs, vans, boats) across the United States. It combines Census data, geographic information, and RV rental listings to identify key drivers of this market shift.

**High-Level Workflow:**
1.  **Data Collection:** Python scripts fetch demographic data (Census), geographic data (National Parks, Campgrounds), and rental pricing (RVshare).
2.  **Processing:** Data is cleaned, merged into a master dataset, and enriched with calculated metrics like "Distance to National Park."
3.  **Analysis:** The system tests specific hypotheses (Income, Climate, Remote Work) and generates visual insights.

## Usage

### Prerequisites
*   Python 3.x

**1. Activate Virtual Environment**
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**2. Install Dependencies**
```bash
pip install pandas numpy requests matplotlib seaborn statsmodels
```

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


