# Economic Penalty Calculation for Circuity (VOT + VOC)

This document breaks down the methodology used to calculate the economic penalty—comprising the **Value of Time (VOT)** and **Vehicle Operating Cost (VOC)**—resulting from poor street network connectivity (circuity). 

---

## 1. Underlying Parameters

These parameters are defined in `src/config.py` (assuming a Jambi 2024 context):

| Parameter | Value | Derivation |
|---|---|---|
| Value of Time (VOT) | `155 IDR / minute` | World Bank 30%-of-GRDP/capita approach |
| Vehicle Operating Cost (VOC) | `350 IDR / km` | Motorcycle running cost (fuel + maintenance) |
| Speed Assumption | `25 km/h` | Urban congested speed for motorcycle |
| Frequency | `3 trips / day` | Routine daily trips (work, school, market) |
| Working Days | `250 days / year` | Estimated annual commuting days |

---

## 2. Detailed Derivation of Value of Time (VOT)

### 2.1 Methodology

The Value of Time represents the economic cost of time spent traveling instead of engaging in productive or leisure activities. We follow the **World Bank's standard approach for non-work travel time in developing countries**, which estimates VOT as a fraction of the traveler's income per unit time.

The World Bank recommends:
- **Work trips:** VOT ≈ 100% of the wage rate per hour
- **Non-work trips:** VOT ≈ **30% of household income per hour** (a conservative lower bound)

Since circuity affects *all* trips — not only commuting but also trips to markets, health facilities, and schools — we use the **non-work (30%) convention** as a conservative baseline. This avoids overstating the penalty.

### 2.2 Step-by-Step Derivation

**Step 1 — Obtain GRDP per Capita:**

According to BPS (Badan Pusat Statistik), Kota Jambi's GRDP per capita (PDRB per kapita ADHB) for 2023 is approximately:

> **Rp 64.64 million / capita / year**

This is the most recent published figure. No 2024 figure was available at the time of analysis.

**Step 2 — Convert to Hourly Rate:**

Assuming 250 working days × 8 hours/day = 2,000 working hours/year:

```
Hourly income = Rp 64,640,000 / 2,000 hours = Rp 32,320 / hour
```

**Step 3 — Apply the 30% Non-Work Factor:**

```
VOT (hourly) = 30% × Rp 32,320 = Rp 9,696 / hour
```

**Step 4 — Convert to Per-Minute:**

```
VOT (per minute) = Rp 9,696 / 60 = Rp 161.6 / minute
```

**Step 5 — Rounding:**

We round down to **Rp 155 / minute** to maintain a conservative estimate and account for the fact that GRDP per capita overstates the income of lower-income commuters who are disproportionately affected by circuity.

### 2.3 Is Rp 155/min Reasonable?

| Check | Value |
|---|---|
| Raw derivation | Rp 161.6/min |
| Value used | Rp 155/min (≈ 4% below raw) |
| Implied daily VOT (for 28 min lost) | Rp 4,340 |
| Implied annual VOT (250 days) | Rp 1,085,000 |

The value is deliberately conservative. For context, Indonesia's national minimum wage (UMK) for Kota Jambi in 2024 is approximately Rp 3.2 million/month, which translates to ~Rp 266/min at 200 working hours/month. Our VOT of Rp 155/min is well below this, confirming the conservative posture.

### 2.4 Limitations of the VOT Approach

1. **GRDP ≠ Actual Household Income.** GRDP per capita includes corporate profits and government spending, so it overstates individual income. However, the 30% factor and the downward rounding partially compensate.
2. **No income stratification.** We apply a uniform VOT across all kelurahan. In reality, south-bank residents (who suffer the worst circuity) likely have *lower* incomes, meaning our VOT may overstate their actual willingness-to-pay for time savings. Conversely, it may understate the impact for higher-income north-bank commuters.
3. **No trip-purpose weighting.** A trip to a hospital during an emergency has a far higher implicit VOT than a trip to the market. Our uniform rate treats all trips equally.

---

## 3. Detailed Derivation of Vehicle Operating Cost (VOC)

### 3.1 Methodology

VOC represents the direct out-of-pocket cost of operating a vehicle per kilometer, encompassing fuel, maintenance, tire wear, and depreciation. We follow the general framework used by the **Kementerian Pekerjaan Umum (PU)** for BOK (Biaya Operasional Kendaraan) analysis, simplified for motorcycles.

### 3.2 Component Breakdown

For a typical Indonesian motorcycle (110–125cc automatic/matic):

| Component | Assumption | Cost per km |
|---|---|---|
| **Fuel (BBM)** | Pertalite @ Rp 10,000/L, consumption ~45 km/L | **Rp 222/km** |
| **Engine Oil** | Rp 45,000 per 2,000 km | **Rp 22/km** |
| **Tire Replacement** | Rp 300,000/pair per 15,000 km | **Rp 20/km** |
| **Routine Service** | Rp 100,000 per 3,000 km | **Rp 33/km** |
| **Depreciation** | Rp 15M purchase, 10-year life, 10,000 km/year | **Rp 150/km** |
| **Other (brake pads, chain, etc.)** | Miscellaneous | **~Rp 30/km** |
| **Total (full BOK)** | | **≈ Rp 477/km** |

### 3.3 Why We Use Rp 350/km (Not the Full Rp 477)

The full BOK includes **fixed costs** (depreciation, insurance) that are incurred regardless of how far you ride. For a *marginal cost analysis* — asking "how much does each extra kilometer of circuity cost?" — only the **variable (running) costs** are relevant:

```
Variable costs only: Rp 222 (fuel) + Rp 22 (oil) + Rp 20 (tires) + Rp 33 (service) + Rp 30 (misc)
                   = Rp 327/km
```

We round to **Rp 350/km** to include a modest allowance for accelerated depreciation from additional wear on lower-quality roads (common in high-circuity areas). This aligns with the commonly cited range for motorcycle BOK in Indonesian transport studies (Rp 300–500/km depending on road conditions).

### 3.4 Limitations of the VOC Approach

1. **Price sensitivity.** Fuel prices change (Pertalite has fluctuated). A Rp 2,000/L increase in fuel price would raise VOC by ~Rp 44/km.
2. **Road quality interaction.** Motorcycles on poor-quality roads (common in high-circuity kelurahan) consume more fuel and wear components faster. Our Rp 350/km may actually *understate* the cost in the worst-affected areas.
3. **No externalities.** We do not account for emissions, accident risk, or health costs from longer rides — all of which increase with circuity.

---

## 4. Speed Assumption: 25 km/h

### 4.1 Justification

The assumed average travel speed of **25 km/h** represents the effective door-to-door speed for a motorcycle in urban Kota Jambi, accounting for:

- **Intersections and stops:** Traffic signals, unsignalized junctions, pedestrian crossings
- **Road surface quality:** Unpaved or deteriorated surfaces in peripheral kelurahan
- **Mixed traffic:** Motorcycles, angkot, becak, and pedestrians sharing the road
- **Acceleration/deceleration cycles:** Typical for short urban trips

### 4.2 How Does This Compare to Research?

Studies on urban motorcycle speeds across Indonesian secondary cities report:

| City | Context | Avg Speed |
|---|---|---|
| Banda Aceh | Arterial roads, peak hours | 25–30 km/h |
| Makassar | Urban roads, peak hours | 25–41 km/h |
| Greater Jakarta | Dense commuting corridors | ~26 km/h |
| Samarinda | High-volume periods | 12–13 km/h |

Our **25 km/h** sits at the **lower end of peak-hour arterial speeds**, which is appropriate because:
1. Circuity-affected trips often traverse **collector and local roads**, not arterials — these roads are slower.
2. Many high-circuity kelurahan (e.g., Arab Melayu, Mudung Laut) have **narrow, unpaved, or poorly maintained roads** where 25 km/h may even be generous.
3. We are modeling **effective trip speed** (including stops), not free-flow speed.

### 4.3 Sensitivity

The speed assumption linearly affects the VOT penalty (slower speed = more time = higher cost). A sensitivity check:

| Speed | Daily Time Lost (η=1.70, 5km Eucl.) | Daily VOT |
|---|---|---|
| 20 km/h | 35.3 min | Rp 5,472 |
| **25 km/h** | **28.2 min** | **Rp 4,371** |
| 30 km/h | 23.5 min | Rp 3,643 |
| 35 km/h | 20.2 min | Rp 3,131 |

The ±5 km/h range produces a ~25% swing in VOT penalty, making this a moderately sensitive parameter.

---

## 5. The Core Metric: η (Eta)

The entire calculation is driven by the **Circuity Factor (η)**, which is the ratio of the actual network distance to the straight-line Euclidean distance:

```
η = Network Distance / Euclidean Distance
```

Therefore, **(η - 1)** represents the *excess* proportion of travel caused by the road network deviating from a straight line.

---

## 6. Calculating Value of Time (VOT) Penalty

This calculates the economic cost of the extra *time* spent traveling due to circuity:

**A. Extra Time per Trip (minutes):** 
The extra distance traveled is calculated as `(η - 1) * Euclidean Distance`. To find the time spent covering this extra distance, we divide by the assumed speed (25 km/h) and multiply by 60 to convert to minutes.

```
Time Lost = [ (η - 1) × Euclidean Distance (km) / 25 km/h ] × 60
```

**B. Daily Time Lost:** 

```
Daily Time Lost = Time Lost per Trip × 3 trips/day
```

**C. Daily VOT Cost:** 

```
Daily VOT (IDR) = Daily Time Lost × 155 IDR/min
```

## 7. Calculating Vehicle Operating Cost (VOC) Penalty

This calculates the physical cost of traveling the extra *distance* (e.g., fuel consumption, vehicle wear and tear):

**A. Extra Distance per Trip (km):**

```
Extra Distance = (η - 1) × Euclidean Distance (km)
```

**B. Daily Extra Distance (km):**

```
Daily Extra Distance = Extra Distance per Trip × 3 trips/day
```

**C. Daily VOC Cost:**

```
Daily VOC (IDR) = Daily Extra Distance × 350 IDR/km
```

## 8. Combining the Costs (Total Economic Penalty)

Finally, the VOT and VOC are combined to estimate the total economic burden imposed by the street network's circuity.

**A. Daily Total Penalty:** 

```
Daily Total Cost (IDR) = Daily VOT + Daily VOC
```

**B. Annual Total Penalty:** 

```
Annual Total Cost (IDR) = Daily Total Cost × 250 days/year
```

---

## 9. On Using Motorcycle Only — Is It Appropriate?

### 9.1 The Case FOR a Motorcycle-Only Model

The decision to model only motorcycles is **defensible for Kota Jambi** based on the following evidence:

1. **Overwhelming modal dominance.** Motorcycles are the primary mode of transport in Kota Jambi. BPS and UNJA research consistently show that private motorcycles hold the largest modal share, with the city having over 750,000 registered motorcycles — exceeding its human population (~630,000). The motorcycle is not merely "common"; it is the default mode of transport for virtually all trip purposes.

2. **Target population alignment.** The residents most affected by circuity — those in peripheral, poorly-connected kelurahan like Arab Melayu, Mudung Laut, and Ulu Gedong — are almost exclusively motorcycle-dependent. These communities have minimal car ownership and negligible public transit access.

3. **Methodological simplicity.** A single-mode model avoids the need for trip-mode-split assumptions, which would introduce additional uncertainty without substantially changing the conclusions.

4. **Conservative estimate.** Motorcycles have the *lowest* VOC of any motorized mode. If we included cars (VOC ≈ Rp 1,500–2,500/km) or angkot fares, the total economic penalty would be significantly higher. The motorcycle-only model thus understates the aggregate cost.

### 9.2 The Case AGAINST (Limitations)

Despite the above, a motorcycle-only model has meaningful blind spots:

1. **It excludes non-motorized trips.** Residents too poor to own a motorcycle — or children walking to school — experience circuity penalties in *time only* (no VOC), but their VOT may differ substantially. Walking speed (~4 km/h) would produce time penalties 6× larger than motorcycle, making circuity even more devastating for pedestrians.

2. **It ignores multi-modal chains.** Some trips involve motorcycle → angkot → walking. The circuity penalty for these compound trips is harder to quantify but potentially larger.

3. **Car users exist.** While a minority, car users exist and face higher VOC penalties per km. Excluding them understates the *aggregate* economic cost across the city.

4. **Emergency and freight trips.** Ambulances and goods delivery vehicles face circuity penalties with far higher implicit VOT (a medical emergency) or VOC (a loaded truck). These are excluded entirely.

5. **Future modal shift.** As Jambi grows and incomes rise, car ownership will increase. A motorcycle-only model may become less representative over time.

### 9.3 Recommendation

**For this study, the motorcycle-only approach is appropriate and sufficient.** It correctly captures the dominant travel behavior in Kota Jambi and produces a conservative lower-bound estimate of the true economic penalty.

However, for a more complete picture, future work should consider:

| Enhancement | What It Would Add |
|---|---|
| **Pedestrian layer** | Time-only penalty at 4 km/h for walking trips (especially school access) |
| **Car layer** | Higher VOC (Rp 1,500–2,500/km) for the car-owning minority |
| **Multi-modal sensitivity** | Weighted average across modes using survey-based modal split |
| **Income stratification** | Different VOT by kelurahan income level (BPS Susenas data) |

These extensions would strengthen the analysis for policy documents (e.g., RPJMD submissions) but are not required for the core finding: **the road network topology in south-bank Kota Jambi imposes a severe and measurable economic penalty on its residents.**
