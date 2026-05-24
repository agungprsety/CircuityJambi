# Circuity Ratio Analysis — Kota Jambi
**Mini-Project & Article Plan**

> **What is this?**
> A weekend spatial analysis project measuring road network circuity (η = network distance ÷ Euclidean distance) across all kelurahan in Kota Jambi. The goal is to identify which neighborhoods bear the highest "detour cost" to reach essential services — and write a data-driven article about it.

---

## Project Metadata

| Field | Detail |
|---|---|
| **City** | Kota Jambi, Jambi Province, Indonesia |
| **Analyst** | Agung — Highway Engineer, Dinas PUPR Kota Jambi |
| **Duration** | 2 days (weekend sprint) |
| **Data** | Open data only (OSM, BPS, BNPB) |
| **Tools** | Python · OSMnx · NetworkX · GeoPandas · Matplotlib · Folium |
| **Output** | Choropleth map + heatmap + bar chart + 1,500–2,000 word article |
| **Target publication** | Medium / LinkedIn (bilingual ID/EN optional) |

---

## The Core Concept

**Circuity** (also called **detour index** or **route factor**) measures how much longer your actual road-based journey is compared to the straight-line distance.

```
η = d_network / d_euclidean
```

| η Score | Interpretation |
|---|---|
| 1.0 | Perfect grid — physically impossible in practice |
| 1.1–1.3 | Excellent connectivity (e.g. Manhattan ≈ 1.1) |
| 1.4–1.6 | Typical urban network |
| 1.7–2.0 | Poor connectivity — notable detour burden |
| > 2.0 | Severely disconnected — structural barriers present |

> **Literature note:** Several studies found average circuity of 1.2–1.3 in urban road networks (Ballou et al., 2002). Southeast Asian cities show some of the highest and most rapidly growing network sprawl globally (PNAS, 2020). No published circuity benchmark exists for Indonesian secondary cities — **your analysis creates the benchmark**.

> **Terminology:** Circuity = Detour Index = Route Factor. All three terms describe the same ratio and are used interchangeably across transport geography, logistics, and urban morphology literature.

---

## Benchmarking Strategy

There is no existing published η benchmark for Kota Jambi or comparable Indonesian cities. Use three approaches:

1. **Self-benchmarking across kelurahan** — internal variation is your primary story. If the worst kelurahan scores 80% higher than the best, that finding stands alone without external comparison.
2. **Compute peer city benchmarks yourself** — run the same OSMnx script on Palembang, Pekanbaru, Bengkulu, and Banjarmasin (2 extra hours). This creates a local comparison table that does not exist anywhere in the literature.
3. **Boeing's global dataset as ceiling** — Boeing (2021) modeled 8,914 urban areas worldwide. Use this as your reference frame for where Indonesian cities fall globally. Dataset is publicly available at [geoffboeing.com](https://geoffboeing.com/2021/03/worldwide-street-network-models-indicators/).

> **Key methodological caution:** Short trips are always more circuitous than long ones — the detour index decreases as OD distance increases (Levinson & El-Geneidy, 2009). Ensure OD pairs are comparable in distance across kelurahan. Jambi's Batang Hari river creates geography-driven circuity (hard to fix cheaply) vs planning-driven circuity (missing links, dead ends — fixable). Distinguish these in your article.

---

## Data Sources

| Dataset | Source | Format | Notes |
|---|---|---|---|
| Road network | OpenStreetMap via OSMnx | Graph (Python) | `network_type='drive'` |
| Kelurahan boundaries | BPS / BIG Indonesia (`big.go.id`) | Shapefile | ~62 kelurahan in Kota Jambi |
| Hospitals & clinics | OSM `amenity=hospital/clinic` | GeoDataFrame | Cross-check with Kemkes faskes data |
| Schools | OSM `amenity=school/university` | GeoDataFrame | |
| Markets | OSM `amenity=marketplace` | GeoDataFrame | Include Pasar Angso Duo, Simpang Kawat |
| Government offices | OSM `office=government` | GeoDataFrame | |
| Poverty indicators (optional) | BPS PODES 2021 | Table (CSV/XLS) | For equity correlation layer |

> **Priority action before Saturday:** Download BPS kelurahan boundary shapefile. Everything else pulls automatically through OSMnx.

---

## Origin-Destination Pair Design

### Origins
- Centroid of each kelurahan polygon (~62 origins)
- Snap each centroid to nearest OSM road node using `ox.distance.nearest_nodes()`

### Destinations (by trip category)

| Category | Key destinations in Kota Jambi | OSM tag |
|---|---|---|
| **Health** | RSUD Raden Mattaher, RS Bratanata, Puskesmas Kotabaru, Puskesmas Talang Banjar | `amenity=hospital`, `amenity=clinic` |
| **Education** | SMAN 1, SMAN 3, SMAN 5, SMK cluster Jambi Selatan | `amenity=school`, `amenity=university` |
| **Economic** | Pasar Angso Duo, Pasar Simpang Kawat, Pasar Talang Banjar, WTC Batanghari | `amenity=marketplace`, `shop=mall` |
| **Civic** | Balai Kota Jambi, Kantor Gubernur, Kantor BPJS | `office=government` |

> Total OD pairs: ~62 kelurahan × ~30 destinations = ~1,860 routing calculations.

---

## Methodology

### Phase 1 — Data Collection (~2 hours)

1. Download Jambi drive network via OSMnx. Project to UTM Zone 48S (EPSG:32748) for metric accuracy.
2. Load kelurahan boundaries. Compute centroids. Project to same CRS.
3. Query all destination categories using `ox.features_from_place()`.
4. Snap all origins and destinations to nearest graph nodes.
5. Save graph locally as `.graphml` to avoid re-downloading.

### Phase 2 — Routing & Distance Calculation (~3 hours)

1. For each OD pair compute:
   - **Network distance** → `nx.shortest_path_length(G, orig, dest, weight='length')`
   - **Euclidean distance** → direct coordinate geometry (shapely `.distance()`)
2. Calculate η = d_network / d_euclidean. Store all results in a flat dataframe.
3. Flag unreachable pairs (`nx.NetworkXNoPath`) as `NaN` — do **not** drop them. A disconnected node is a finding.
4. Aggregate by kelurahan: mean η overall, mean η by trip category.
5. Rank kelurahan from highest to lowest mean η. Flag worst 10 and best 10.

### Phase 3 — Analysis (~2 hours)

1. **Spatial pattern check** — are high-η kelurahan spatially clustered? Near the river? Peripheral?
2. **Trip type comparison** — is health access η worse than market access η? Build a kelurahan × category heatmap.
3. **Convert to time cost** — excess travel time per trip:
   ```
   time_lost_min = (η - 1) × avg_euclidean_dist_km / 25 km/h × 60
   ```
   Assume 3 trips/day. Compute annual hours lost per kelurahan.
4. **Identify structural causes** — for worst-η kelurahan, inspect OSM visually. River crossing issue? Dead-end street? Missing bridge? This grounds your policy recommendation.

---

## Starter Code

### Setup & Network Download

```python
import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

# Download Jambi City road network
G = ox.graph_from_place(
    "Kota Jambi, Jambi, Indonesia",
    network_type='drive',
    simplify=True
)

# Project to UTM 48S for metric accuracy
G_proj = ox.project_graph(G, to_crs="EPSG:32748")

# Save locally — run this once
ox.save_graphml(G_proj, "jambi_drive.graphml")
```

### Query Destinations

```python
dest_queries = {
    'health':    {'amenity': ['hospital', 'clinic']},
    'education': {'amenity': ['school', 'university']},
    'economic':  {'amenity': 'marketplace'},
    'civic':     {'office': 'government'},
}

dests = {}
for cat, tags in dest_queries.items():
    gdf = ox.features_from_place("Kota Jambi, Jambi, Indonesia", tags=tags)
    gdf['category'] = cat
    gdf['centroid'] = gdf.geometry.centroid
    dests[cat] = gdf

all_dests = pd.concat(dests.values(), ignore_index=True)
```

### Compute Circuity Ratio (η)

```python
# Load kelurahan (replace with your actual shapefile path)
kel = gpd.read_file("kelurahan_jambi.shp").to_crs("EPSG:32748")
kel['centroid'] = kel.geometry.centroid

# Reload graph if needed
# G_proj = ox.load_graphml("jambi_drive.graphml")

# Snap origins to nearest node
orig_nodes = ox.distance.nearest_nodes(
    G_proj,
    X=kel.centroid.x.values,
    Y=kel.centroid.y.values
)

results = []

for i, (kel_row, orig) in enumerate(zip(kel.itertuples(), orig_nodes)):
    for _, dest_row in all_dests.iterrows():
        dest_pt = dest_row['centroid']
        dest_node = ox.distance.nearest_nodes(G_proj, dest_pt.x, dest_pt.y)

        d_euc = kel_row.centroid.distance(dest_pt)  # metres (projected CRS)

        try:
            d_net = nx.shortest_path_length(G_proj, orig, dest_node, weight='length')
            eta = d_net / d_euc if d_euc > 0 else np.nan
        except nx.NetworkXNoPath:
            d_net, eta = np.nan, np.nan  # disconnected — note, don't drop

        results.append({
            'kelurahan':     kel_row.NAMOBJ,
            'kecamatan':     kel_row.KECAMATAN,
            'dest_name':     dest_row.get('name', 'unnamed'),
            'category':      dest_row['category'],
            'd_euclidean_m': d_euc,
            'd_network_m':   d_net,
            'eta':           eta
        })

df = pd.DataFrame(results)
df.to_csv("od_results_jambi.csv", index=False)  # save immediately

# Aggregate
summary = df.groupby(['kelurahan', 'kecamatan']).agg(
    eta_mean=('eta', 'mean'),
    disconnected=('eta', lambda x: x.isna().sum())
).reset_index()

kel_result = kel.merge(summary, left_on='NAMOBJ', right_on='kelurahan')
```

---

## Visualizations

### Viz 1 — Choropleth Map (Main Output)
- Each kelurahan polygon filled by mean η score
- Colormap: `RdYlGn_r` (red = high tax, green = low tax)
- Overlay road network as thin grey lines
- Label top 5 worst and best kelurahan
- Add Batang Hari river polygon to explain geographic barriers
- Export: 300dpi PNG

### Viz 2 — Heatmap (η by Kelurahan × Trip Type)
- Rows = kelurahan sorted by mean η
- Columns = health / education / economic / civic
- Cell color = η value (`YlOrRd`)
- Annotate each cell with η value
- Reveals whether the burden is uniform or category-specific

### Viz 3 — Bar Chart (Minutes Wasted Per Day)
- Convert η to time: `time_lost = (η - 1) × avg_dist_km / 25 × 60`
- Assume 3 trips/day
- Horizontal bar chart, sorted descending
- Highlight top 5 in red
- Add city average as vertical reference line
- **This is the article's most shareable visual — it translates ratio to felt experience**

---

## Article Structure

**Target length:** 1,500–2,000 words
**Tone:** Data-driven but readable. Every technical term explained in one sentence.
**Suggested title:** *"The Circuity Ratio: A Spatial Analysis of Road Network Inefficiency in Kota Jambi"*
**Popular alternative:** *"Jambi's Hidden Road Problem: You're Traveling 60% Farther Than You Should Be"*

### Section 1 — Lede (~200 words)
Open with a specific commuter story from the worst-η kelurahan. Describe a daily trip to the nearest hospital by road. Then reveal: in a straight line, it is only X km. They travel 80% farther than necessary, every day. This is the circuity ratio.

### Section 2 — Background (~300 words)
Explain η simply. Show the formula. Cite global benchmarks: Manhattan ≈ 1.1, typical Southeast Asian city 1.4–1.6, poorly planned cities > 2.0. Introduce Jambi's geography — river, bridges, urban expansion — as structural context.

### Section 3 — Key Findings (~600 words)
- **Finding 1:** Jambi's mean circuity ratio (headline number)
- **Finding 2:** Worst 3–5 kelurahan and what they share geographically
- **Finding 3:** Health access η is systematically worse than market access η in peripheral kelurahan — the most vulnerable residents pay the highest detour cost to reach a hospital
- Embed all three visualizations here

### Section 4 — Policy Implication (~400 words)
Connectivity tax is a diagnostic tool. Highest-η kelurahan = priority investment zones — not because roads are bad, but because network topology is broken. One missing link (a bridge, a cut-through) can reduce η for an entire neighborhood. Suggest: incorporate circuity metric into Jambi's road maintenance prioritization alongside IRI and traffic volume.

> Distinguish **geography-driven circuity** (river/topography — costly to fix) from **planning-driven circuity** (missing links, dead ends — fixable with targeted investment).

### Section 5 — Closing (~200 words)
Publish Python code on GitHub. Invite peer cities in Sumatra to replicate. Frame as a replicable open-data methodology — expands readership beyond Jambi and positions you as a methodologist.

---

## Key References

| Reference | Why it matters |
|---|---|
| Boeing, G. (2017). OSMnx. *Computers, Environment and Urban Systems*, 65, 126–139. | Methodological backbone — cite for all OSMnx-based analysis |
| Boeing, G. (2021). Street Network Models and Indicators for Every Urban Area in the World. *Geographical Analysis*. | Global benchmark dataset — use to position Jambi internationally |
| Levinson, D. & El-Geneidy, A. (2009). The minimum circuity frontier and the journey to work. *Regional Science and Urban Economics*, 39(6). | Establishes that short trips are more circuitous — important caveat |
| Ballou et al. (2002). Selected country circuity factors. *Transportation Research Part A*, 36, 843–848. | Establishes 1.2–1.3 as the urban baseline range |
| Cubukcu, K.M. (2020). Using circuity as a network efficiency measure. *Spatial Information Research*. | Confirms circuity = detour index = route factor |
| Barrington-Leigh & Millard-Ball (2020). Global trends toward urban street-network sprawl. *PNAS*. | Southeast Asia framing + context for high circuity values |

---

## Weekend Schedule

### Saturday

| Time | Task |
|---|---|
| 08:00–09:00 | Environment setup. Install osmnx, networkx, geopandas. Download Jambi graph. Get BPS kelurahan shapefile. |
| 09:00–12:00 | Run routing loop. **This is the slow step (30–60 min compute).** While it runs, draft article outline. |
| 13:00–15:00 | Aggregation and exploratory analysis. Find headline η. Identify best/worst kelurahan. Note disconnected nodes. |
| 15:00–18:00 | Build Viz 1 (choropleth) and Viz 2 (heatmap). Export 300dpi. |

### Sunday

| Time | Task |
|---|---|
| 08:00–09:30 | Build Viz 3 (time-cost bar chart). Compute minutes/day lost per kelurahan. |
| 09:30–13:00 | Write the article. Follow five-section plan. Aim for complete, not perfect. |
| 14:00–16:00 | Edit, embed visuals, publish. Post on Medium or LinkedIn. Share GitHub repo link. |

---

## Pre-Weekend Checklist

- [ ] Python environment ready: `osmnx`, `networkx`, `geopandas`, `matplotlib`, `seaborn`, `folium`
- [ ] BPS batas kelurahan Kota Jambi shapefile downloaded from `big.go.id`
- [ ] GitHub repo created (even empty) for code sharing
- [ ] Medium or LinkedIn account ready to publish
- [ ] Boeing (2017) paper read — 20 minutes, establishes your methodological grounding
- [ ] (Optional) Decide on 2–3 peer cities to benchmark against (Palembang, Pekanbaru, Bengkulu)

---

## Optional Extensions (Post-Weekend)

- **Equity layer** — correlate mean η by kelurahan with BPS PODES poverty rate. Do poorer neighborhoods have higher circuity ratio? Likely yes.
- **Peer city comparison** — run same script on Palembang, Pekanbaru, Bengkulu, Banjarmasin. Creates a Sumatran comparison table that doesn't exist anywhere in the literature.
- **Temporal analysis** — compare OSM network from 2018 vs 2024 using Overpass historical API. Has circuity improved or worsened as Jambi expanded?
- **Journal submission** — after article is published and cited by practitioners, submit extended version to *Jurnal Perencanaan Wilayah dan Kota*, *Applied Geography*, or *Environment and Planning B*.

---
