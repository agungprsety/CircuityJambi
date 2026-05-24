# Circuity Ratio Analyzer — Kota Jambi

An open-source Python analysis pipeline that computes the **road network circuity ratio (η)** for every kelurahan (neighborhood) in Kota Jambi, Indonesia. 

The circuity ratio compares the actual road network distance to the straight-line (Euclidean) distance between a residential neighborhood and key public services (health clinics, schools, and markets). A high η indicates a disconnected street grid where residents must travel much farther than necessary, paying a daily "circuity ratio" in time and distance.

This repository powers the findings in the article: *"The Circuity Ratio: A Spatial Analysis of Road Network Inefficiency in Kota Jambi"*.

## 🗺️ Interactive WebGIS Dashboard

You can explore the final results on the interactive dashboard:
**(Replace with your GitHub Pages URL: https://agung.github.io/circuity-jambi)**

## 🚀 Getting Started

### Prerequisites

You need Python 3.9+ installed on your system.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/agung/circuity-jambi.git
   cd circuity-jambi
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Running the Pipeline

The analysis is broken down into sequential modules. You must run them in order, as each step depends on the output of the previous step.

```bash
# 1. Download and process the OpenStreetMap drive network
python src/01_network.py

# 2. Extract residential origin centroids from kelurahan boundaries
python src/02_origins.py

# 3. Download destination POIs (Health, Education, Economic) from OSM
python src/03_destinations.py

# 4. Compute shortest-path routing (Warning: Takes ~30-60 mins depending on CPU)
python src/04_routing.py

# 5. Aggregate origin-destination pairs into Kelurahan-level metrics
python src/05_aggregation.py

# 6. Generate premium static visualizations (saved to outputs/figures/)
python src/06_visualization.py

# 8. Generate the interactive HTML WebGIS dashboard
python src/08_interactive_map.py
```

*Note: Module 7 (Peer City Comparison) is optional and currently reserved for future expansion.*

## 📂 Repository Structure

```
circuity-jambi/
├── article/                   # Drafts and final article text
├── data/
│   ├── raw/                   # Input boundaries (BPS PODES kelurahan.geojson)
│   └── processed/             # Generated graphs, destinations, and OD matrices
├── docs/                      # GitHub pages deployment (contains index.html)
├── outputs/
│   ├── figures/               # Static visualizations (maps, charts, scatter plots)
│   └── interactive_map.html   # Standalone WebGIS dashboard
├── src/                       # Python pipeline modules
│   ├── config.py              # Central configuration (tags, projections, speeds)
│   ├── 01_network.py          
│   ├── 02_origins.py          
│   ├── 03_destinations.py     
│   ├── 04_routing.py          
│   ├── 05_aggregation.py      
│   ├── 06_visualization.py    
│   ├── 08_interactive_map.py  
│   └── app.py                 # Streamlit dashboard version (optional)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 📊 Data Sources

- **Road Network & POIs:** OpenStreetMap contributors (via `osmnx`)
- **Administrative Boundaries:** BPS PODES 2021 (Kelurahan boundaries)
- **Methodology Reference:** Levinson, D. & El-Geneidy, A. (2009). The minimum circuity frontier. *Regional Science and Urban Economics*, 39(6).

## 📄 License

This project is open-source and available under the MIT License. Feel free to fork and adapt the pipeline for your own city!
