# Findings - Circuity Project

## Project Overview
- **Name**: Circuity Ratio Analyzer — Kota Jambi
- **Purpose**: Computes road network circuity ratio (η) for Kota Jambi.
- **Metric**: η = (Actual Road Distance) / (Euclidean Distance).
- **Target POIs**: Health clinics, schools, and markets.
- **Outcome**: Identifying disconnected grids where travel is inefficient.

## Technical Details
- **Language**: Python 3.9+
- **Key Libraries**: `osmnx`, `geopandas`, `folium` (assumed for WebGIS), `streamlit`.
- **Pipeline**:
  1. `01_network`: OSM drive network.
  2. `02_origins`: Kelurahan centroids.
  3. `03_destinations`: POI extraction.
  4. `04_routing`: Shortest-path computation (heavy).
  5. `05_aggregation`: Neighborhood-level metrics.
  6. `06_visualization`: Static figures.
  7. `08_interactive_map`: WebGIS dashboard.

## Deployment
- **Dashboard URL**: http://circuity-jambi.netlify.app/
- **License**: MIT
