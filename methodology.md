# Methodology

## Study Area

The study area is **Kota Jambi**, the capital of Jambi Province, Sumatra, Indonesia. Kota Jambi is a medium-sized Indonesian city bisected by the **Batang Hari river**, which creates a significant natural barrier between the north and south banks. The city is subdivided into **68 kelurahan** (neighborhoods) across 11 kecamatan (districts).

Administrative boundaries are sourced from the **BPS PODES 2021** kelurahan boundary shapefile, stored in GeoJSON format (`EPSG:4326`). All spatial computations are performed in the **UTM Zone 48S** projected coordinate system (`EPSG:32748`) to ensure metric accuracy.

---

## Road Network Acquisition

The drive network for Kota Jambi is downloaded from **OpenStreetMap (OSM)** using the `osmnx` Python library (Boeing, 2017). The network is extracted as a directed graph of type `drive`, representing all road segments available for motor vehicle travel within the city boundary.

**Network statistics:**

| Parameter | Value |
|---|---|
| Nodes (intersections) | 19,840 |
| Edges (road segments) | 48,191 |
| Network type | Directed, drive |
| Source | OpenStreetMap |
| Extraction library | `osmnx` |

The graph is saved locally as a `GraphML` file for reproducible offline reuse, avoiding repeated API calls to the Overpass server.

---

## Origin Definition

Each of the 68 kelurahan serves as a single **origin**. The origin point for each kelurahan is defined as the **geometric centroid** of its administrative polygon, computed in the projected CRS (`EPSG:32748`).

Each centroid is then **snapped to the nearest network node** using `osmnx.distance.nearest_nodes()`. This ensures that all routing calculations begin from a valid position on the road graph, rather than an arbitrary off-network point. The mapping from kelurahan name to network node ID is saved as a JSON lookup table (`origin_mapping.json`).

---

## Destination Acquisition

Public service destinations are queried from OpenStreetMap using `osmnx.features_from_polygon()` with the following category tags:

| Category | OSM Tags | Count |
|---|---|---|
| **Health** | `amenity: [hospital, clinic]` | 65 |
| **Education** | `amenity: [school, university]` | 366 |
| **Economic** | `amenity: marketplace`, `shop: *` | 12 |
| **Total** | | **443** |

For destinations with polygon geometries (e.g., hospital buildings, school campuses), the **centroid** of the polygon is used as the destination point. All destination points are snapped to the nearest network node, consistent with the origin snapping methodology.

---

## Routing and Circuity Computation

### Origin–Destination Matrix

Every origin (68 kelurahan) is paired with every destination (443 facilities), producing a full **origin–destination (OD) matrix** of **30,124 pairs**.

### Shortest-Path Routing

For each OD pair, the **shortest weighted path** is computed on the road network graph using Dijkstra's algorithm (`networkx.shortest_path_length()` with `weight='length'`). The weight attribute is the physical road segment length in meters, as provided by OSM.

### Euclidean Distance

The **straight-line (Euclidean) distance** between the origin centroid and the destination point is computed in the projected CRS using Shapely's `distance()` method, yielding a result in meters.

### Circuity Ratio (η)

The circuity ratio for each OD pair is defined as:

> **η = d_network / d_Euclidean**

Where:
- `d_network` = shortest road network path length (m)
- `d_Euclidean` = straight-line distance (m)

A value of η = 1.0 indicates a perfectly direct route. Higher values indicate increasing detour inefficiency.

### Disconnected Pairs

If no valid path exists between an origin and destination node on the network graph, the pair is flagged as **disconnected** (`NetworkXNoPath` exception). Out of 30,124 total pairs, **68 pairs (0.23%)** were disconnected.

---

## Filtering and Quality Control

Two filters are applied before aggregation to remove statistical outliers:

| Filter | Threshold | Rationale |
|---|---|---|
| **Maximum η** | η ≤ 10 | Values above 10 are almost always artifacts of edge-snapping errors |
| **Minimum Euclidean distance** | d_Euclidean ≥ 200 m | Very short trips produce artificially inflated η values (Levinson & El-Geneidy, 2009) |

After filtering, **29,941 valid OD pairs** remain for aggregation analysis.

---

## Aggregation

Results are aggregated at the **kelurahan level**:

- **Mean η (overall):** Arithmetic mean of all valid η values for each kelurahan
- **Mean η (per category):** Separate mean for Health, Education, and Economic destinations
- **Daily time lost:** Estimated as:

  > `time_lost_per_trip = (η - 1) × avg_d_Euclidean_km / avg_speed_kmh × 60`
  >
  > `daily_time_lost = time_lost_per_trip × trips_per_day`

  Using an assumed average urban congested speed of **25 km/h** and **3 trips per day** (reflecting typical urban trip-chaining behavior: home → work, work → errand, errand → home).

- **Ranking:** Kelurahan are ranked 1 (worst, highest η) to 68 (best, lowest η)
- **Flags:** Top 5 worst and Top 5 best kelurahan are flagged for visualization emphasis

The aggregated summary is spatially joined back to the kelurahan polygon GeoDataFrame and exported as `summary_kelurahan.geojson`.

---

## Visualization

Four static publication-quality visualizations are generated:

| Figure | Type | Content |
|---|---|---|
| VIZ-01 | Choropleth map | Spatial distribution of mean η across all 68 kelurahan, with network overlay and kelurahan labels |
| VIZ-02 | Category heatmap | η breakdown by destination category for the Top 20 worst kelurahan, with overall mean column |
| VIZ-03 | Horizontal bar chart | Daily time loss penalty, comparing Top 15 worst vs Top 5 best kelurahan, with city average reference line |
| VIZ-04 | Hexbin scatter (small multiples) | η vs Euclidean distance, one panel per facility category, demonstrating the short-trip circuity decay pattern |

All figures use a dark theme (`#0f1117` background), are exported at 300 DPI, and are rendered using `matplotlib` and `seaborn`.

An interactive **WebGIS dashboard** is also generated as a standalone HTML file using **Leaflet.js**, containing the full choropleth, destination markers, and a detail panel with kelurahan-level statistics.

---

## Software Environment

| Library | Purpose |
|---|---|
| `osmnx` | Road network download and graph operations |
| `networkx` | Shortest-path routing (Dijkstra) |
| `geopandas` | Spatial data handling and CRS transformations |
| `pandas` | Tabular data manipulation |
| `numpy` | Numerical operations |
| `matplotlib` | Static visualization rendering |
| `seaborn` | Heatmap visualization |
| `shapely` | Geometric computations (centroids, distances) |

Python version: 3.11+

---

## Limitations

1. **Single origin per kelurahan:** Using the administrative centroid as the sole origin point does not capture intra-kelurahan variation. Residents on the periphery of large kelurahan may experience significantly different circuity from those near the centroid.

2. **OSM data completeness:** OpenStreetMap coverage in secondary Indonesian cities may be incomplete. Informal roads, private access roads, and recently constructed links may be missing from the network graph, potentially inflating circuity values.

3. **Static routing:** The analysis uses static shortest-path routing without traffic congestion modeling. Real-world travel times vary by time of day and traffic conditions.

4. **Speed assumption:** A uniform average speed of 25 km/h is applied across all road types. In practice, arterial roads support faster speeds than residential lanes.

5. **Destination completeness:** OSM may not contain all health clinics, schools, or markets in Kota Jambi. The economic category (12 destinations) is particularly sparse and may underrepresent the true availability of markets and shops.

6. **Short-trip bias:** Despite the 200-meter minimum filter, residual short-trip inflation may persist in some kelurahan where destinations are clustered very close to the centroid.

---

## References

- Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems*, 65, 126–139.
- Boeing, G. (2021). Street network models and indicators for every urban area in the world. *Geographical Analysis*, 54(3), 519–535.
- Levinson, D. & El-Geneidy, A. (2009). The minimum circuity frontier and the journey to work. *Regional Science and Urban Economics*, 39(6), 732–738.
- Ballou, R.H., Rahardja, H. & Sakai, N. (2002). Selected country circuity factors for road travel distance estimation. *Transportation Research Part A*, 36(9), 843–848.
- Barrington-Leigh, C. & Millard-Ball, A. (2020). Global trends in urban road network sprawl. *Proceedings of the National Academy of Sciences*, 117(4), 1941–1950.
