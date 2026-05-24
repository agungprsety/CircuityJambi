# The Circuity Ratio: A Spatial Analysis of Road Network Inefficiency in Kota Jambi

*By Agung — Highway Engineer, Dinas PUPR Kota Jambi*

---

## 1. The Extra Minutes Nobody Accounts For

Imagine you live in Arab Melayu, a riverside kelurahan in Kecamatan Pelayangan, Kota Jambi. The nearest health clinic is less than a kilometer away as the crow flies. But you are not a crow. You are a resident on the south bank of the Batang Hari river, and the road network between you and that clinic twists through unpaved lanes, doubles back along the riverbank, and forces you out onto a major arterial road before cutting back in. By the time you arrive, you have traveled 3.4 times the straight-line distance.

This is not a traffic problem. The road is not congested. There is simply no direct path.

We call this the **circuity ratio** — the invisible penalty paid not in tolls or fuel, but in time and distance, every single day, by residents of neighborhoods where the road network simply does not connect destinations efficiently. In Arab Melayu, this tax amounts to nearly **100 minutes of extra travel per day** — more than 416 hours per year — for a resident making three routine trips.

This article presents the first systematic measurement of road network circuity across all 68 kelurahan in Kota Jambi, using open-source data and reproducible Python methods. The findings are striking — and they have direct implications for how PUPR Kota Jambi should prioritize road investment.

---

## 2. What Is Circuity, and Why Does It Matter?

**Network circuity** (η, *eta*) is a dimensionless ratio that compares the actual road network distance to the straight-line (Euclidean) distance between two points:

> **η = d_network / d_Euclidean**

A value of **η = 1.0** is a perfect straight-line road. A value of **η = 1.5** means you travel 50% farther on the road network than the direct route. Anything above **η = 2.0** indicates severe network inefficiency — the topology of the road network is fundamentally broken in that area.

Global benchmarks from Boeing (2021), who computed street-network indicators for 100 countries, put the typical urban circuity for Southeast Asian cities in the **1.15–1.35** range. This aligns with foundational research by Ballou et al. (2002) which established a **1.20–1.30** baseline for typical road networks globally. Compact, grid-planned cities like Singapore average around 1.1. Organically grown secondary cities — common across Sumatra and Borneo — tend toward the higher end of that range, around 1.25–1.30.

One important caveat: as Levinson & El-Geneidy (2009) demonstrated, short trips naturally produce higher circuity ratios. A 300-meter journey through a local residential block will almost always look more inefficient than a 5-kilometer arterial commute, simply because the local detour constitutes a larger fraction of the total journey. Our analysis filters trips shorter than 200 meters to minimize this distortion.

Jambi's geography makes it a particularly interesting case. The Batang Hari river bisects the urban area, creating a natural barrier. Kecamatan Pelayangan and Danau Teluk on the south bank are connected to the city center only through a limited number of crossing points. Informal urban growth along the riverbank has outpaced formal road planning, leaving many neighborhoods accessible only through winding, poorly connected lanes.

---

## 3. Key Findings

### Finding 1: Jambi's Mean Circuity Is Well Above the Regional Baseline

Across 30,124 origin-destination pairs — every residential kelurahan centroid to every health, education, and economic destination in the city — Kota Jambi records a **mean circuity ratio of η = 1.70**.

This is significantly above the 1.25–1.30 baseline expected for a secondary Indonesian city. Residents across the city, on average, travel **70% farther** than the straight-line distance to reach everyday services. The mean daily time penalty, assuming three routine trips per day at an average urban speed of 25 km/h, is **28.2 minutes per day**.

*(See Figure 1: Choropleth Map — spatial distribution of η across all kelurahan)*

### Finding 2: The South Bank Carries a Disproportionate Burden

The five worst-performing kelurahan are not distributed randomly. They are geographically concentrated in **Kecamatan Pelayangan and Danau Teluk**, almost entirely on the south bank of the Batang Hari:

| Rank | Kelurahan | Kecamatan | Mean η | Daily Time Lost |
|---|---|---|---|---|
| 1 | Arab Melayu | Pelayangan | **3.45** | 95 min |
| 2 | Mudung Laut | Pelayangan | **3.13** | 95 min |
| 3 | Tengah | Pelayangan | **3.00** | 85 min |
| 4 | Jelmu | Pelayangan | **3.00** | 91 min |
| 5 | Ulu Gedong | Danau Teluk | **2.99** | 95 min |

By contrast, the best-performing kelurahan — Mayang Mangurai (η = 1.30), Kenali Asam Atas (η = 1.33), and Beliung (η = 1.35) — are all in **Kecamatan Alam Barajo and Kota Baru**, on the north bank, where the road grid is more regular and destinations are directly accessible.

This is a textbook example of **geography-driven circuity**: the Batang Hari river is not going anywhere. However, geography explains the *location* of the inefficiency, not its *magnitude*. Arab Melayu's η = 3.45 is not merely "slightly disconnected" — it is categorically dysfunctional. An η of 1.5–1.7 would be expected for a riverbank neighborhood. A value of 3.4 suggests that road planning in this area has simply not kept pace with settlement growth.

### Finding 3: The Hidden Economic Tax

When we translate these time and distance penalties into a financial metric using standard transport economics (Value of Time + Vehicle Operating Cost), the abstract concept of "inefficiency" becomes a very real economic tax.

Using the World Bank's conservative approach for non-work Value of Time (30% of Jambi's GRDP per capita) and standard Indonesian motorcycle operating costs (Rp 350/km, fuel + maintenance), the residents of the most circuitous kelurahans are paying millions of Rupiah per year simply because the roads don't connect. 

In Arab Melayu, the average resident loses approximately **95 minutes** and travels **extra kilometers** every single day. Economically, this translates to an invisible "connectivity tax" of roughly **Rp 3.6 Million per person, per year** (Rp ~14,000/day). For a family of three, that is over Rp 10 Million entirely wasted on bad road topology—almost a third of the annual minimum wage (UMK) simply burned in transit.

*(See Figure 5: Bar Chart — All 62 Kelurahan ranked by their annual connectivity tax)*

*(See Figure 6: Scatter Plot — Exponential relationship between Circuity Ratio and Annual Economic Cost)*

*(See Figure 2: Category Heatmap — circuity breakdown by destination type, Top 20 worst kelurahan)*

### Finding 4: Economic Access Is the Hardest to Reach

Across all destination categories, **economic access (markets, shops) shows the highest city-wide mean circuity** at η = 1.83, followed by education (η = 1.70) and health (η = 1.67).

For the worst-performing kelurahan, the pattern is even more pronounced. In Mudung Laut, the circuity to economic destinations reaches **η = 4.99** — meaning residents travel *five times the straight-line distance* to reach the nearest market. In Arab Melayu, even health facilities — the highest-urgency category — have an average circuity of **η = 3.63**.

*(See Figure 3: Bar Chart — daily time penalty ranking, comparing Top 15 Worst vs Top 5 Best)*

*(See Figure 4: Scatter Hexbin — circuity vs. Euclidean distance, by facility category)*

---

## 4. What Should PUPR Do with This?

### Circuity as a Diagnostic Tool

The conventional inputs to road prioritization in Indonesia are the **Road Condition Index (IRI)** and traffic volume. Both measure the quality and use of existing roads. Neither tells you whether the road network, in aggregate, is *topologically fit for purpose* — whether its geometry efficiently connects people to services.

Circuity η fills this gap. It is a **network-level diagnostic**, not a road-level one. A perfect road with IRI = 0 and zero potholes still produces η = 3.4 if the road forces residents to make a 3-kilometer loop to cross a 300-meter gap.

### Two Types of Circuity, Two Types of Intervention

It is essential to distinguish:

1. **Geography-driven circuity**: Where rivers, topography, or rail corridors force detours. The south bank kelurahan will never achieve η = 1.3 without new river crossings. The policy question here is infrastructure investment — bridges, ferries, elevated connectors.

2. **Planning-driven circuity**: Where road networks simply weren't designed with connectivity in mind. Many informal settlement areas on the north bank show η values of 1.6–1.8 — above geographic necessity. Here, the intervention is simpler: identify the "missing links" — short connector roads of 200–500 meters that would dramatically reduce detour ratios for entire neighborhoods.

### A Concrete Recommendation

We recommend that **PUPR Kota Jambi incorporate η into its annual road investment scoring framework**, alongside IRI and traffic volume. Specifically:

- Flag any kelurahan with **η > 2.0** for immediate network topology review
- Mandate a "missing link analysis" for all kelurahan in Kecamatan Pelayangan and Danau Teluk
- Prioritize any infrastructure investment that increases river crossing points to the south bank
- In RPJMD spatial planning documents, establish **η ≤ 1.5** as a target for all urban kelurahan by 2030

A neighborhood doesn't need a new expressway. It often just needs one 400-meter connecting road that unlocks direct access to an entire quadrant of the city.

---

## 5. Open Method, Replicable Everywhere

Every dataset and script used in this analysis is publicly available. The road network was downloaded from **OpenStreetMap** using the `osmnx` library (Boeing, 2017). Administrative boundaries are kelurahan shapefile. All routing was computed in Python using `NetworkX`, with routing done at average urban congested speed (25 km/h).

The full pipeline — from raw data download to final visualizations — is available on GitHub at **[github.com/agung/circuity-jambi]** *(link forthcoming)*. It can be adapted for any Indonesian city with an OSM road network within approximately 2 hours of compute time.

We invite researchers and engineers in Palembang, Pekanbaru, Bengkulu, and Banjarmasin to replicate this analysis. The methodology is identical across cities; only the boundary files and place names change.

---

## Data Sources

| Source | Use |
|---|---|
| OpenStreetMap contributors | Road network, destination POIs |
| BPS PODES 2021 | Kelurahan administrative boundaries |
| Boeing, G. (2017). OSMnx. *Computers, Environment and Urban Systems*, 65. | Network download and graph analysis |
| Boeing, G. (2021). Street Network Models. *Geographical Analysis*. | Global circuity benchmarks |
| Levinson & El-Geneidy (2009). *Regional Science and Urban Economics*, 39(6). | Short-trip circuity theory |
| Ballou et al. (2002). *Transportation Research Part A*, 36. | Country-level baseline circuity factors |

---

*The author is a highway engineer at Dinas PUPR Kota Jambi. This analysis was conducted independently using open-source tools and public data. All code and data are reproducible.*
