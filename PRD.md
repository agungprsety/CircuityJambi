# Product Requirements Document
## Circuity Ratio Analyzer — Kota Jambi
**Version:** 1.0
**Date:** May 2026
**Author:** Agung — Highway Engineer, Dinas PUPR Kota Jambi
**Status:** Draft — Ready for Agentic Execution

---

## 1. Overview

### 1.1 Problem Statement

Road network inefficiency in Indonesian secondary cities is poorly documented. Planners in Kota Jambi currently prioritize road maintenance using IRI (roughness index) and traffic volume — neither of which captures whether the network *topology* forces residents into unnecessarily long detours to reach essential services.

There is no published circuity benchmark for Kota Jambi or any comparable Sumatran city. Decision-makers have no spatial evidence to prioritize connectivity improvements over surface rehabilitation.

### 1.2 Proposed Solution

Build a reproducible, open-data Python analysis pipeline that computes the **circuity ratio** (road network circuity ratio η) for every kelurahan in Kota Jambi, then publish findings as a data-driven article targeting planners, policymakers, and urban researchers.

### 1.3 Definition

```
η = d_network / d_euclidean
```

Where η is the ratio of actual network travel distance to straight-line distance between an origin and destination. η = 1.0 is a perfect grid; η > 1.5 indicates meaningful detour burden.

### 1.4 Success Criteria

| Criterion | Target |
|---|---|
| Pipeline runs end-to-end without manual intervention | Yes |
| All 62 kelurahan in Kota Jambi have a computed η score | ≥ 90% coverage (allowing for disconnected nodes) |
| Three publication-quality visualizations exported | Yes |
| Article draft complete | 1,500–2,000 words |
| Code published to GitHub | Yes, with README |
| Time to complete full pipeline + article | ≤ 2 days |

---

## 2. Stakeholders

| Role | Name / Entity | Interest |
|---|---|---|
| **Owner / Analyst** | Agung, Dinas PUPR Kota Jambi | Conducts analysis, writes article |
| **Primary reader** | Dinas PUPR & Bappeda Kota Jambi | Policy recommendations for road investment |
| **Secondary reader** | Urban planners, transport researchers (Indonesia) | Methodological replication in other cities |
| **Agentic executor** | AI coding assistant (Claude Code or similar) | Executes pipeline from this PRD |

---

## 3. Scope

### 3.1 In Scope

- Road network download and preprocessing for Kota Jambi
- Origin-destination pair generation (kelurahan centroids × service destinations)
- Network routing and circuity ratio computation
- Aggregation and ranking by kelurahan
- Three visualizations: choropleth map, heatmap, bar chart
- Interactive web map (Folium) with layer controls, popups, and embeddable HTML export
- Optional deployment via GitHub Pages, Netlify, or lightweight local server
- Optional peer city comparison (Palembang, Pekanbaru, Bengkulu, Banjarmasin)
- Article draft following the defined five-section structure
- GitHub repository with documented code

### 3.2 Out of Scope

- Real-time traffic data integration (Waze, Google Maps API)
- Full-stack web application (backend API, database, user auth) — the interactive map is a static HTML artifact, not a web app
- Pedestrian or transit network analysis
- Survey or primary data collection
- Formal peer-reviewed journal submission (post-weekend extension only)

---

## 4. Data Requirements

### 4.1 Input Datasets

| Dataset | Source | Format | Required | Notes |
|---|---|---|---|---|
| Road network (drive) | OpenStreetMap via OSMnx | Graph object | **Yes** | `network_type='drive'`, `simplify=True` |
| Kelurahan boundaries | BPS / BIG Indonesia (`big.go.id`) | Shapefile (.shp) | **Yes** | ~62 kelurahan, Kota Jambi |
| Hospital / clinic locations | OSM `amenity=hospital/clinic` | GeoDataFrame | **Yes** | Cross-check vs Kemkes faskes if available |
| School locations | OSM `amenity=school/university` | GeoDataFrame | **Yes** | |
| Market locations | OSM `amenity=marketplace` | GeoDataFrame | **Yes** | |
| Government offices | OSM `office=government` | GeoDataFrame | **Yes** | |
| Poverty indicators | BPS PODES 2021 | CSV / XLS | Optional | For equity correlation extension |
| Peer city networks | OSM via OSMnx | Graph objects | Optional | Palembang, Pekanbaru, Bengkulu, Banjarmasin |

### 4.2 Data Assumptions

- OSM road network for Kota Jambi is sufficiently complete for drive routing (validated by prior OSM quality audits)
- BPS kelurahan shapefile uses field `NAMOBJ` for kelurahan name and `KECAMATAN` for kecamatan name — **confirm column names before running**
- All coordinates projected to EPSG:32748 (UTM Zone 48S) for metric distance accuracy
- Missing destinations (e.g. no marketplace tagged in OSM for a given area) are handled gracefully — log warning, do not halt pipeline

---

## 5. Functional Requirements

### 5.1 Pipeline Modules

#### Module 1 — Network Acquisition
**ID:** MOD-01
**Input:** City name string
**Output:** Projected NetworkX graph saved as `.graphml`

| Requirement | Detail |
|---|---|
| FR-01-1 | Download drive network for "Kota Jambi, Jambi, Indonesia" using `ox.graph_from_place()` |
| FR-01-2 | Project to EPSG:32748 using `ox.project_graph()` |
| FR-01-3 | Save graph to `data/jambi_drive.graphml` to prevent re-download on subsequent runs |
| FR-01-4 | Log node count, edge count, and CRS to console on completion |

#### Module 2 — Origin Generation
**ID:** MOD-02
**Input:** Kelurahan shapefile
**Output:** GeoDataFrame with kelurahan centroids snapped to nearest graph node

| Requirement | Detail |
|---|---|
| FR-02-1 | Load shapefile, reproject to EPSG:32748 |
| FR-02-2 | Compute polygon centroid for each kelurahan |
| FR-02-3 | Snap each centroid to nearest OSM drive network node using `ox.distance.nearest_nodes()` |
| FR-02-4 | Store result as `{kelurahan_id: node_id}` mapping |
| FR-02-5 | Log count of origins successfully snapped |

#### Module 3 — Destination Acquisition
**ID:** MOD-03
**Input:** City name string, destination tag dictionary
**Output:** GeoDataFrame of all destinations with category labels and centroids

| Requirement | Detail |
|---|---|
| FR-03-1 | Query each destination category using `ox.features_from_place()` |
| FR-03-2 | Accept categories: `health`, `education`, `economic`, `civic`, `retail` |
| FR-03-3 | Compute centroid for polygon destinations (hospitals, schools with area geometry) |
| FR-03-4 | Snap all destination centroids to nearest graph nodes |
| FR-03-5 | If a category returns zero results, log warning and continue — do not raise exception |
| FR-03-6 | Save raw destination GeoDataFrame to `data/destinations.geojson` |

#### Module 4 — Routing Engine
**ID:** MOD-04
**Input:** Origin node mapping, destination node mapping, projected graph
**Output:** Flat results dataframe saved to `data/od_results.csv`

| Requirement | Detail |
|---|---|
| FR-04-1 | Iterate all origin × destination combinations |
| FR-04-2 | Compute network distance using `nx.shortest_path_length(G, orig, dest, weight='length')` |
| FR-04-3 | Compute Euclidean distance using projected geometry `.distance()` |
| FR-04-4 | Compute η = d_network / d_euclidean; assign `NaN` if d_euclidean == 0 |
| FR-04-5 | Catch `nx.NetworkXNoPath` — assign `NaN` for both distances, set `disconnected=True` flag |
| FR-04-6 | Save results to CSV immediately after completion (do not hold in memory only) |
| FR-04-7 | Log progress every 100 OD pairs |
| FR-04-8 | Output columns: `kelurahan`, `kecamatan`, `dest_id`, `dest_name`, `category`, `d_euclidean_m`, `d_network_m`, `eta`, `disconnected` |

#### Module 5 — Aggregation
**ID:** MOD-05
**Input:** `data/od_results.csv`, kelurahan GeoDataFrame
**Output:** Kelurahan-level summary GeoDataFrame saved to `data/summary_kelurahan.geojson`

| Requirement | Detail |
|---|---|
| FR-05-1 | Compute per kelurahan: mean η (all categories), mean η per category, count of disconnected pairs, count of total pairs |
| FR-05-2 | Compute time cost: `time_lost_min = (eta_mean - 1) × avg_d_euclidean_km / 25 × 60` |
| FR-05-3 | Compute daily time lost assuming 3 trips/day |
| FR-05-4 | Rank kelurahan 1–N by mean η (1 = worst connectivity) |
| FR-05-5 | Flag top 5 worst and top 5 best kelurahan as boolean columns |
| FR-05-6 | Merge summary back to kelurahan polygon GeoDataFrame |
| FR-05-7 | Save to `data/summary_kelurahan.geojson` |

#### Module 6 — Visualization
**ID:** MOD-06
**Input:** `data/summary_kelurahan.geojson`, `data/od_results.csv`
**Output:** Three PNG files in `outputs/figures/`

| Viz | ID | Spec |
|---|---|---|
| Choropleth map | VIZ-01 | Kelurahan polygons colored by `eta_mean`. Colormap: `RdYlGn_r`. Overlay drive network (grey, linewidth 0.3). Label top 5 worst and best kelurahan. Add north arrow and scale bar. Export: `outputs/figures/map_circuity_choropleth.png` at 300dpi. |
| Category heatmap | VIZ-02 | Rows = kelurahan sorted by `eta_mean`, columns = trip categories. Cell values = category-specific η. Colormap: `YlOrRd`. Annotate each cell. Export: `outputs/figures/heatmap_category_eta.png` at 300dpi. |
| Time-cost bar chart | VIZ-03 | Horizontal bar chart of daily minutes lost per kelurahan, sorted descending. Top 5 bars in red, remainder in grey. Vertical line at city mean. Export: `outputs/figures/barchart_time_loss.png` at 300dpi. |

#### Module 7 — Peer City Comparison (Optional)
**ID:** MOD-07
**Input:** List of peer city name strings
**Output:** Comparison table CSV and summary bar chart

| Requirement | Detail |
|---|---|
| FR-07-1 | Run Modules 1–5 for each peer city: Palembang, Pekanbaru, Bengkulu, Banjarmasin |
| FR-07-2 | Use consistent destination categories across all cities |
| FR-07-3 | Output comparison table: city, mean η, η health, η education, η economic, η civic |
| FR-07-4 | Save to `outputs/peer_city_comparison.csv` |
| FR-07-5 | This module is optional — skip if time-constrained |

#### Module 8 — Interactive Map Deployment
**ID:** MOD-08
**Input:** `outputs/summary_kelurahan.geojson`, `data/destinations.geojson`, `data/od_results.csv`
**Output:** Self-contained interactive HTML map at `outputs/interactive_map.html`

| Requirement | Detail |
|---|---|
| FR-08-1 | Generate a Folium `Map` centred on Kota Jambi with appropriate zoom level |
| FR-08-2 | Add a **choropleth layer** coloring kelurahan polygons by `eta_mean` using `RdYlGn_r` colormap with `GeoJsonTooltip` showing kelurahan name, kecamatan, η mean, rank, and daily time lost |
| FR-08-3 | Add a **destinations layer group** with circle markers for each destination category (health=red, education=blue, economic=green, civic=orange), each with a popup showing destination name and category |
| FR-08-4 | Add a **worst-5 highlight layer** with bold red outlines and labels for the 5 worst-connectivity kelurahan |
| FR-08-5 | Add `folium.LayerControl()` so users can toggle layers on/off |
| FR-08-6 | Add a color legend (HTML overlay) explaining the η color scale |
| FR-08-7 | Add a title banner overlay with project name and brief description |
| FR-08-8 | Save the map as a single self-contained HTML file at `outputs/interactive_map.html` (no external dependencies — all CSS/JS inlined by Folium) |
| FR-08-9 | File size must be under 15 MB to allow GitHub Pages / Netlify hosting |
| FR-08-10 | Optionally copy `interactive_map.html` to `docs/index.html` for GitHub Pages deployment |

---

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-01 | **Reproducibility** | Pipeline must run identically from a clean environment given the same input files |
| NFR-02 | **Runtime** | Full pipeline (Modules 1–6) completes in under 90 minutes on a standard laptop (8GB RAM) |
| NFR-03 | **Error handling** | No silent failures — all exceptions logged with context; pipeline continues where possible |
| NFR-04 | **Open data only** | No proprietary APIs, no paid data sources |
| NFR-05 | **Dependencies** | All packages installable via `pip install -r requirements.txt` |
| NFR-06 | **Output quality** | All figures exported at 300dpi minimum, suitable for article publication |
| NFR-07 | **Code documentation** | Every function has a docstring. Inline comments on non-obvious logic. |
| NFR-08 | **CRS consistency** | All spatial operations performed in EPSG:32748; only reproject for final visualization if needed |

---

## 7. File Structure

```
connectivity-tax-jambi/
│
├── README.md                        # Project overview, setup, usage
├── requirements.txt                 # Python dependencies
│
├── data/
│   ├── raw/
│   │   ├── kelurahan_jambi.shp      # BPS kelurahan boundaries (+ sidecar files)
│   │   └── jambi_drive.graphml      # Downloaded OSM network (auto-generated)
│   ├── destinations.geojson         # Queried service locations (auto-generated)
│   └── od_results.csv               # Raw OD routing results (auto-generated)
│
├── outputs/
│   ├── summary_kelurahan.geojson    # Aggregated results per kelurahan
│   ├── peer_city_comparison.csv     # Optional peer benchmarking
│   ├── interactive_map.html         # Self-contained interactive Folium map
│   └── figures/
│       ├── map_circuity_choropleth.png
│       ├── heatmap_category_eta.png
│       └── barchart_time_loss.png
│
├── src/
│   ├── 01_network.py                # MOD-01: Network acquisition
│   ├── 02_origins.py                # MOD-02: Origin generation
│   ├── 03_destinations.py           # MOD-03: Destination acquisition
│   ├── 04_routing.py                # MOD-04: Routing engine
│   ├── 05_aggregation.py            # MOD-05: Aggregation
│   ├── 06_visualization.py          # MOD-06: Visualizations
│   ├── 07_peer_cities.py            # MOD-07: Peer comparison (optional)
│   ├── 08_interactive_map.py        # MOD-08: Interactive map deployment
│   └── config.py                    # Shared config: city name, CRS, paths, parameters
│
├── docs/
│   └── index.html                   # GitHub Pages deploy (copy of interactive_map.html)
│
└── article/
    └── draft.md                     # Article draft (see Section 8)
```

---

## 8. Article Requirements

### 8.1 Metadata

| Field | Detail |
|---|---|
| **Length** | 1,500–2,000 words |
| **Platform** | Medium and/or LinkedIn |
| **Language** | English (Indonesian translation optional) |
| **Tone** | Data-driven, readable — technical terms always explained inline |
| **Audience** | Urban planners, transport engineers, spatial analysts, policymakers |

### 8.2 Title Options

- *Primary:* "The Circuity Ratio: A Spatial Analysis of Road Network Inefficiency in Kota Jambi"
- *Popular:* "Jambi's Hidden Road Problem: You're Traveling 60% Farther Than You Should Be"

### 8.3 Section Structure

| Section | Title | Length | Key Content |
|---|---|---|---|
| 1 | Lede | ~200 words | Open with a specific commuter story from the worst-η kelurahan. Reveal the straight-line vs network distance gap. Introduce the circuity ratio concept. |
| 2 | Background | ~300 words | Define η. Show the formula. Cite global benchmarks. Introduce Jambi's geography as structural context (Batang Hari river, informal urban growth). |
| 3 | Key Findings | ~600 words | Finding 1: Jambi mean η (headline number). Finding 2: Worst 3–5 kelurahan and geographic explanation. Finding 3: Health access η systematically worse than market access in peripheral kelurahan. Embed all three visualizations. |
| 4 | Policy Implication | ~400 words | Connectivity tax as diagnostic tool. Distinguish geography-driven vs planning-driven circuity. Recommend: incorporate η into PUPR road prioritization alongside IRI and traffic volume. Identify highest-priority missing links. |
| 5 | Closing | ~200 words | Publish code on GitHub. Invite peer city replication. Replicable open-data methodology as the contribution. |

### 8.4 Mandatory Elements

- [ ] η formula displayed visually (not just inline text)
- [ ] At least one direct quote or reference from published circuity literature
- [ ] All three visualizations embedded
- [ ] GitHub repository URL linked
- [ ] Explicit caveat: short trips are more circuitous than long ones (Levinson & El-Geneidy, 2009)
- [ ] Distinction between geography-driven and planning-driven circuity
- [ ] Data sources listed at the end

---

## 9. Key References

| Reference | Use in article |
|---|---|
| Boeing, G. (2017). OSMnx. *Computers, Environment and Urban Systems*, 65, 126–139. | Cite for all OSMnx methodology |
| Boeing, G. (2021). Street Network Models and Indicators for Every Urban Area. *Geographical Analysis*. | Global benchmark framing |
| Levinson, D. & El-Geneidy, A. (2009). The minimum circuity frontier. *Regional Science and Urban Economics*, 39(6). | Short-trip circuity caveat |
| Ballou et al. (2002). Selected country circuity factors. *Transportation Research Part A*, 36, 843–848. | 1.2–1.3 baseline range |
| Barrington-Leigh & Millard-Ball (2020). Global trends in urban street-network sprawl. *PNAS*. | Southeast Asia framing |

---

## 10. Execution Instructions for Agentic Assistant

> **Read this section carefully before executing any code.**

### 10.1 Execution Order

Run modules strictly in order: MOD-01 → MOD-02 → MOD-03 → MOD-04 → MOD-05 → MOD-06 → (MOD-07 optional) → MOD-08

### 10.2 Before Starting

1. Confirm `data/raw/kelurahan_jambi.shp` exists and is readable
2. Confirm kelurahan name field — likely `NAMOBJ` but verify with `gdf.columns` before proceeding
3. Confirm kecamatan field — likely `KECAMATAN`
4. Create all directories in the file structure above if they do not exist
5. Install dependencies: `pip install osmnx networkx geopandas pandas numpy matplotlib seaborn folium shapely`

### 10.3 Critical Constraints

- **Never overwrite `data/jambi_drive.graphml`** if it already exists — load it instead of re-downloading
- **Always save `data/od_results.csv` before aggregation** — the routing loop is the most time-expensive step
- **Do not filter out NaN η values** in aggregation — treat them as disconnected and report the count
- **All distances must be in metres** — verify CRS is EPSG:32748 before any `.distance()` call
- **Figures must be 300dpi** — use `plt.savefig(path, dpi=300, bbox_inches='tight')`

### 10.4 Config File (`src/config.py`)

```python
# src/config.py — edit before running

CITY_NAME     = "Kota Jambi, Jambi, Indonesia"
CRS_PROJECTED = "EPSG:32748"   # UTM Zone 48S
AVG_SPEED_KMH = 25             # Urban congested speed assumption
TRIPS_PER_DAY = 3              # For daily time-cost calculation

# Shapefile field names — confirm before running
FIELD_KELURAHAN  = "NAMOBJ"
FIELD_KECAMATAN  = "KECAMATAN"

# Destination categories
DEST_TAGS = {
    "health":    {"amenity": ["hospital", "clinic"]},
    "education": {"amenity": ["school", "university"]},
    "economic":  {"amenity": "marketplace"},
    "civic":     {"office": "government"},
}

# Peer cities for optional MOD-07
PEER_CITIES = [
    "Kota Palembang, South Sumatra, Indonesia",
    "Kota Pekanbaru, Riau, Indonesia",
    "Kota Bengkulu, Bengkulu, Indonesia",
    "Kota Banjarmasin, South Kalimantan, Indonesia",
]

# Paths
DATA_RAW       = "data/raw/"
DATA_PROCESSED = "data/"
OUTPUT_FIGURES = "outputs/figures/"
OUTPUT_DIR     = "outputs/"
```

### 10.5 Expected Outputs Checklist

After full pipeline execution, verify:

- [ ] `data/jambi_drive.graphml` exists
- [ ] `data/destinations.geojson` exists and has > 0 features
- [ ] `data/od_results.csv` exists and has > 1,000 rows
- [ ] `data/summary_kelurahan.geojson` exists with columns: `kelurahan`, `kecamatan`, `eta_mean`, `eta_health`, `eta_education`, `eta_economic`, `eta_civic`, `time_lost_min`, `rank`, `worst5`, `best5`, `disconnected`
- [ ] `outputs/figures/map_circuity_choropleth.png` at 300dpi
- [ ] `outputs/figures/heatmap_category_eta.png` at 300dpi
- [ ] `outputs/figures/barchart_time_loss.png` at 300dpi
- [ ] `outputs/interactive_map.html` exists, opens in browser, and is under 15 MB
- [ ] `docs/index.html` exists (copy of interactive map for GitHub Pages)
- [ ] `article/draft.md` written following Section 8.3 structure

---

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BPS shapefile field names differ from assumed | Medium | High | Check `gdf.columns` in MOD-02 before proceeding; update `config.py` |
| OSM destination data sparse in Kota Jambi | Medium | Medium | Log missing categories; supplement with manual coordinates if needed |
| Routing loop exceeds 90-minute runtime | Low | Medium | Reduce destination set or parallelize using `multiprocessing` |
| Many disconnected kelurahan-destination pairs | Medium | Medium | Report disconnected count in article as a secondary finding |
| Peer city OSM coverage inconsistent | Medium | Low | MOD-07 is optional — skip if results are unreliable |

---

