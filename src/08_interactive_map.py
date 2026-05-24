"""
Module 8 — Interactive Map: Premium WebGIS Dashboard
Generates a self-contained HTML file with Leaflet.js, custom dark UI,
glassmorphism sidebar, and embedded GeoJSON data.
"""
import os
import json
import geopandas as gpd
import config

def run_interactive_map():
    print("Starting Module 8: Premium WebGIS Dashboard")

    # Load data
    summary_path = os.path.join(config.DATA_PROCESSED, "summary_kelurahan.geojson")
    dest_path = os.path.join(config.DATA_PROCESSED, "destinations.geojson")

    gdf_kel = gpd.read_file(summary_path)
    gdf_dest = gpd.read_file(dest_path)

    # Ensure WGS84
    if gdf_kel.crs and gdf_kel.crs.to_string() != "EPSG:4326":
        gdf_kel = gdf_kel.to_crs("EPSG:4326")
    if gdf_dest.crs and gdf_dest.crs.to_string() != "EPSG:4326":
        gdf_dest = gdf_dest.to_crs("EPSG:4326")

    # Slim down kelurahan properties to reduce file size
    keep_cols = [
        "NAMOBJ", "WADMKC", "eta_mean", "eta_economic", "eta_education",
        "eta_health", "daily_time_lost_min", "rank_eta",
        "is_top_5_worst", "is_top_5_best", "total_pairs", "disconnected_pairs",
        "geometry"
    ]
    gdf_kel_slim = gdf_kel[keep_cols].copy()

    # Round floats for cleaner display
    for col in ["eta_mean", "eta_economic", "eta_education", "eta_health",
                "daily_time_lost_min"]:
        if col in gdf_kel_slim.columns:
            gdf_kel_slim[col] = gdf_kel_slim[col].round(3)
    gdf_kel_slim["rank_eta"] = gdf_kel_slim["rank_eta"].astype(int)

    # Convert to GeoJSON strings
    kelurahan_geojson = gdf_kel_slim.to_json()
    dest_geojson = gdf_dest[["dest_name", "category", "geometry"]].to_json()

    # Compute stats for the dashboard header
    city_eta = round(gdf_kel["eta_mean"].mean(), 2)
    worst_name = gdf_kel.loc[gdf_kel["rank_eta"] == 1, "NAMOBJ"].values[0]
    best_name = gdf_kel.loc[gdf_kel["rank_eta"] == gdf_kel["rank_eta"].max(), "NAMOBJ"].values[0]
    avg_time = round(gdf_kel["daily_time_lost_min"].mean(), 1)
    
    # Calculate quantiles for a data-driven color scale
    eta_min = round(gdf_kel["eta_mean"].min(), 3)
    q20 = round(gdf_kel["eta_mean"].quantile(0.20), 3)
    q40 = round(gdf_kel["eta_mean"].quantile(0.40), 3)
    q60 = round(gdf_kel["eta_mean"].quantile(0.60), 3)
    q80 = round(gdf_kel["eta_mean"].quantile(0.80), 3)
    q95 = round(gdf_kel["eta_mean"].quantile(0.95), 3)
    eta_max = round(gdf_kel["eta_mean"].max(), 3)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jambi Circuity Ratio — Interactive WebGIS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg-dark: #0f1117;
    --bg-card: rgba(22, 24, 35, 0.85);
    --bg-card-solid: #161823;
    --border: rgba(255,255,255,0.08);
    --text: #e4e4e7;
    --text-muted: #9ca3af;
    --accent: #f4511e;
    --accent-glow: rgba(244,81,30,0.25);
    --green: #4ade80;
    --yellow: #facc15;
    --red: #ef4444;
    --sidebar-w: 380px;
    --header-h: 56px;
  }}

  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--bg-dark);
    color: var(--text);
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }}

  /* ── HEADER ── */
  .header {{
    position: fixed; top: 0; left: 0; right: 0;
    height: var(--header-h);
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px;
    z-index: 1000;
  }}
  .header-title {{
    font-weight: 600; font-size: 15px; letter-spacing: -0.3px;
    display: flex; align-items: center; gap: 10px;
  }}
  .header-title span.dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent-glow);
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.4; }}
  }}
  .header-stats {{
    display: flex; gap: 28px; font-size: 13px;
  }}
  .header-stats .stat {{ display: flex; align-items: center; gap: 6px; }}
  .header-stats .stat-value {{ font-weight: 600; color: var(--accent); }}
  .header-stats .stat-label {{ color: var(--text-muted); }}

  /* ── SIDEBAR ── */
  .sidebar {{
    position: fixed; top: var(--header-h); left: 0; bottom: 0;
    width: var(--sidebar-w);
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--border);
    z-index: 900;
    transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
    overflow-y: auto;
    padding: 20px;
  }}
  .sidebar.collapsed {{ transform: translateX(calc(-1 * var(--sidebar-w))); }}

  .sidebar-toggle {{
    position: fixed;
    top: calc(var(--header-h) + 16px);
    left: var(--sidebar-w);
    width: 32px; height: 32px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: none;
    border-radius: 0 8px 8px 0;
    color: var(--text);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    z-index: 901;
    transition: left 0.35s cubic-bezier(0.4,0,0.2,1);
    font-size: 14px;
  }}
  .sidebar.collapsed + .sidebar-toggle {{ left: 0; }}

  .section-title {{
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1.2px; color: var(--text-muted);
    margin: 20px 0 12px;
  }}
  .section-title:first-child {{ margin-top: 0; }}

  /* Toggle switches */
  .toggle-row {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
  }}
  .toggle-row:last-child {{ border-bottom: none; }}
  .toggle-label {{
    font-size: 13px; font-weight: 400;
    display: flex; align-items: center; gap: 8px;
  }}
  .toggle-label .cat-dot {{
    width: 10px; height: 10px; border-radius: 50%;
    display: inline-block; flex-shrink: 0;
  }}

  .switch {{
    position: relative; width: 40px; height: 22px;
    background: #333; border-radius: 12px; cursor: pointer;
    transition: background 0.25s;
  }}
  .switch.on {{ background: var(--accent); }}
  .switch .knob {{
    position: absolute; top: 2px; left: 2px;
    width: 18px; height: 18px; border-radius: 50%;
    background: white; transition: left 0.25s;
  }}
  .switch.on .knob {{ left: 20px; }}

  /* Info card */
  .info-card {{
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    margin-top: 16px;
  }}
  .info-card h4 {{
    font-size: 13px; font-weight: 600; margin-bottom: 8px;
    color: var(--accent);
  }}
  .info-card p {{
    font-size: 12px; line-height: 1.6; color: var(--text-muted);
  }}

  /* Kelurahan detail panel (shown on click) */
  .detail-panel {{
    background: rgba(244,81,30,0.06);
    border: 1px solid rgba(244,81,30,0.2);
    border-radius: 10px;
    padding: 14px;
    margin-top: 16px;
    display: none;
  }}
  .detail-panel.visible {{ display: block; }}
  .detail-panel h3 {{
    font-size: 15px; font-weight: 600; margin-bottom: 4px;
  }}
  .detail-panel .sub {{ font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }}
  .detail-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
  }}
  .detail-item {{
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 10px;
  }}
  .detail-item .di-label {{ font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .detail-item .di-value {{ font-size: 18px; font-weight: 700; margin-top: 2px; }}
  .detail-item .di-value.bad {{ color: var(--red); }}
  .detail-item .di-value.ok {{ color: var(--yellow); }}
  .detail-item .di-value.good {{ color: var(--green); }}

  /* Legend */
  .legend-bar {{
    margin-top: 16px;
    height: 10px;
    border-radius: 5px;
    background: linear-gradient(to right, #4ade80, #86efac, #fde68a, #fb923c, #ef4444, #b91c1c);
  }}
  .legend-labels {{
    display: flex; justify-content: space-between;
    font-size: 11px; color: var(--text-muted); margin-top: 4px;
  }}

  /* ── MAP ── */
  #map {{
    position: fixed;
    top: var(--header-h); bottom: 0;
    left: var(--sidebar-w); right: 0;
    transition: left 0.35s cubic-bezier(0.4,0,0.2,1);
  }}
  .sidebar.collapsed ~ #map {{ left: 0; }}

  /* Leaflet overrides for dark mode */
  .leaflet-control-zoom a {{
    background: var(--bg-card-solid) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
  }}
  .leaflet-control-zoom a:hover {{ background: #222 !important; }}
  .leaflet-control-attribution {{
    background: rgba(15,17,23,0.7) !important;
    color: var(--text-muted) !important;
    font-size: 10px !important;
  }}
  .leaflet-control-attribution a {{ color: var(--text-muted) !important; }}

  /* Custom popup */
  .leaflet-popup-content-wrapper {{
    background: var(--bg-card-solid) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
  }}
  .leaflet-popup-tip {{ background: var(--bg-card-solid) !important; }}
  .leaflet-popup-content {{ font-family: 'Inter', sans-serif !important; font-size: 13px !important; }}

  /* Scrollbar */
  .sidebar::-webkit-scrollbar {{ width: 4px; }}
  .sidebar::-webkit-scrollbar-track {{ background: transparent; }}
  .sidebar::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 4px; }}

  /* Responsive */
  @media (max-width: 768px) {{
    :root {{ --sidebar-w: 100vw; }}
    .header-stats {{ display: none; }}
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-title">
    <span class="dot"></span>
    Jambi Circuity Ratio — Interactive WebGIS
  </div>
  <div class="header-stats">
    <div class="stat">
      <span class="stat-label">City Mean η</span>
      <span class="stat-value">{city_eta}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Worst</span>
      <span class="stat-value" style="color:#ef4444">{worst_name}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Best</span>
      <span class="stat-value" style="color:#4ade80">{best_name}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Avg Daily Loss</span>
      <span class="stat-value">{avg_time} min</span>
    </div>
  </div>
</div>

<!-- SIDEBAR -->
<div class="sidebar" id="sidebar">
  <div class="section-title">Layers</div>

  <div class="toggle-row">
    <span class="toggle-label">Kelurahan Choropleth</span>
    <div class="switch on" data-layer="choropleth" onclick="toggleLayer(this)"><div class="knob"></div></div>
  </div>
  <div class="toggle-row">
    <span class="toggle-label">Worst 5 Highlight</span>
    <div class="switch on" data-layer="worst5" onclick="toggleLayer(this)"><div class="knob"></div></div>
  </div>

  <div class="section-title">Destinations</div>

  <div class="toggle-row">
    <span class="toggle-label"><span class="cat-dot" style="background:#ef5350"></span> Health (65)</span>
    <div class="switch on" data-layer="health" onclick="toggleLayer(this)"><div class="knob"></div></div>
  </div>
  <div class="toggle-row">
    <span class="toggle-label"><span class="cat-dot" style="background:#42a5f5"></span> Education (366)</span>
    <div class="switch on" data-layer="education" onclick="toggleLayer(this)"><div class="knob"></div></div>
  </div>
  <div class="toggle-row">
    <span class="toggle-label"><span class="cat-dot" style="background:#66bb6a"></span> Economic & Retail (12)</span>
    <div class="switch on" data-layer="economic" onclick="toggleLayer(this)"><div class="knob"></div></div>
  </div>
  <div class="toggle-row" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #333;">
    <span class="toggle-label"><span class="cat-dot" style="background:transparent;border:1px solid #999;"></span> Kelurahan Labels</span>
    <div class="switch on" data-layer="labels" onclick="toggleLayer(this)"><div class="knob"></div></div>
  </div>

  <div class="section-title">Legend — Circuity Ratio (η)</div>
  <div class="legend-bar"></div>
  <div class="legend-labels">
    <span>{eta_min} (best)</span>
    <span>{eta_max} (worst)</span>
  </div>

  <!-- Detail Panel (dynamic) -->
  <div class="detail-panel" id="detailPanel">
    <h3 id="dp-name">—</h3>
    <div class="sub" id="dp-kec">—</div>
    <div class="detail-grid">
      <div class="detail-item">
        <div class="di-label">Overall η</div>
        <div class="di-value" id="dp-eta">—</div>
      </div>
      <div class="detail-item">
        <div class="di-label">Rank</div>
        <div class="di-value" id="dp-rank">—</div>
      </div>
      <div class="detail-item">
        <div class="di-label">Daily Loss</div>
        <div class="di-value" id="dp-time">—</div>
      </div>
      <div class="detail-item">
        <div class="di-label">Health η</div>
        <div class="di-value" id="dp-health">—</div>
      </div>
      <div class="detail-item">
        <div class="di-label">Education η</div>
        <div class="di-value" id="dp-edu">—</div>
      </div>
      <div class="detail-item">
        <div class="di-label">Economic η</div>
        <div class="di-value" id="dp-econ">—</div>
      </div>
    </div>
  </div>

  <div class="info-card">
    <h4>What is η?</h4>
    <p>The circuity ratio (η) measures how much farther you must travel on the actual road network compared to a straight line. An η of 1.5 means you travel 50% farther than necessary. Higher values indicate worse road connectivity.</p>
  </div>
</div>

<!-- SIDEBAR TOGGLE -->
<button class="sidebar-toggle" id="sidebarToggle" onclick="toggleSidebar()">◀</button>

<!-- MAP -->
<div id="map"></div>

<script>
// ── DATA ──
const kelurahanData = {kelurahan_geojson};
const destData = {dest_geojson};

// ── MAP INIT ──
const map = L.map('map', {{ zoomControl: true }}).setView([-1.62, 103.60], 12);

// Dark tiles
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap &copy; CARTO',
  subdomains: 'abcd',
  maxZoom: 19
}}).addTo(map);

// ── COLOR SCALE ──
function getColor(eta) {{
  if (eta == null) return 'transparent';
  
  // Data-driven stops based on quantiles to expose slight variations
  const stops = [
    [{eta_min}, [74, 222, 128]],    // green (best)
    [{q20}, [134, 239, 172]],       // light green
    [{q40}, [253, 230, 138]],       // yellow
    [{q60}, [251, 146, 60]],        // orange
    [{q80}, [239, 68, 68]],         // red
    [{q95}, [153, 27, 27]],         // dark red
    [{eta_max}, [69, 10, 10]]       // deep crimson (worst outliers)
  ];
  
  if (eta <= stops[0][0]) return `rgb(${{stops[0][1].join(',')}})`;
  if (eta >= stops[stops.length-1][0]) return `rgb(${{stops[stops.length-1][1].join(',')}})`;

  for (let i = 1; i < stops.length; i++) {{
    if (eta <= stops[i][0]) {{
      const v0 = stops[i-1][0], v1 = stops[i][0];
      // Prevent division by zero if quantiles are identical
      if (v1 === v0) return `rgb(${{stops[i][1].join(',')}})`;
      const f = (eta - v0) / (v1 - v0);
      const c0 = stops[i-1][1], c1 = stops[i][1];
      const r = Math.round(c0[0] + f * (c1[0] - c0[0]));
      const g = Math.round(c0[1] + f * (c1[1] - c0[1]));
      const b = Math.round(c0[2] + f * (c1[2] - c0[2]));
      return `rgb(${{r}},${{g}},${{b}})`;
    }}
  }}
  return 'transparent';
}}

function etaClass(v) {{
  if (v == null) return '';
  if (v >= 2.0) return 'bad';
  if (v >= 1.5) return 'ok';
  return 'good';
}}

// ── LAYERS ──
const layers = {{}};

// Choropleth
layers.choropleth = L.geoJSON(kelurahanData, {{
  style: function(f) {{
    return {{
      fillColor: getColor(f.properties.eta_mean),
      color: 'rgba(255,255,255,0.15)',
      weight: 1,
      fillOpacity: 0.4
    }};
  }},
  onEachFeature: function(f, layer) {{
    layer.on({{
      mouseover: function(e) {{
        e.target.setStyle({{ weight: 2, color: 'rgba(255,255,255,0.8)', fillOpacity: 0.6 }});
      }},
      mouseout: function(e) {{
        layers.choropleth.resetStyle(e.target);
      }},
      click: function(e) {{
        showDetail(f.properties);
        map.fitBounds(e.target.getBounds(), {{ padding: [50, 50] }});
      }}
    }});
  }}
}}).addTo(map);

// Worst 5 borders
layers.worst5 = L.geoJSON(kelurahanData, {{
  filter: function(f) {{ return f.properties.is_top_5_worst === true; }},
  style: function() {{
    return {{
      fillColor: 'transparent',
      color: '#FF1744',
      weight: 2,
      dashArray: '4, 4',
      fillOpacity: 0,
      interactive: false
    }};
  }}
}}).addTo(map);

// All Kelurahan Labels
layers.labels = L.geoJSON(kelurahanData, {{
  style: {{ fillOpacity: 0, weight: 0, opacity: 0 }},
  onEachFeature: function(f, layer) {{
    const center = layer.getBounds().getCenter();
    const isWorst = f.properties.is_top_5_worst;
    
    // Style matches the static visualization
    const color = isWorst ? '#ff8a80' : 'rgba(255,255,255,0.4)';
    const weight = isWorst ? '700' : '500';
    const size = isWorst ? '12px' : '9px';
    const shadow = isWorst ? '0 1px 4px rgba(0,0,0,0.9)' : 'none';
    
    const label = L.divIcon({{
      className: '',
      html: `<div style="color:${{color}};font-family:Inter,sans-serif;font-size:${{size}};font-weight:${{weight}};text-shadow:${{shadow}};white-space:nowrap;text-align:center;transform:translate(-50%,-50%);pointer-events:none;">${{f.properties.NAMOBJ}}</div>`,
      iconSize: [0, 0],
      iconAnchor: [0, 0]
    }});
    L.marker(center, {{ icon: label, interactive: false }}).addTo(map);
  }}
}});
// Add labels to map by default
map.addLayer(layers.labels);

// Destinations by category
const catColors = {{
  health: '#ef5350',
  education: '#42a5f5',
  economic: '#66bb6a'
}};

['health', 'education', 'economic'].forEach(function(cat) {{
  layers[cat] = L.geoJSON(destData, {{
    filter: function(f) {{ return f.properties.category === cat; }},
    pointToLayer: function(f, latlng) {{
      return L.circleMarker(latlng, {{
        radius: 4,
        fillColor: catColors[cat],
        color: 'rgba(0,0,0,0.3)',
        weight: 1,
        fillOpacity: 0.85
      }});
    }},
    onEachFeature: function(f, layer) {{
      layer.bindPopup(`<b>${{f.properties.dest_name}}</b><br/><span style="color:${{catColors[cat]}}">${{f.properties.category}}</span>`);
    }}
  }}).addTo(map);
}});

// ── TOGGLE LOGIC ──
function toggleLayer(el) {{
  const isOn = el.classList.toggle('on');
  const layerName = el.dataset.layer;
  if (isOn) {{
    map.addLayer(layers[layerName]);
  }} else {{
    map.removeLayer(layers[layerName]);
  }}
}}

function toggleSidebar() {{
  const sb = document.getElementById('sidebar');
  const btn = document.getElementById('sidebarToggle');
  sb.classList.toggle('collapsed');
  btn.textContent = sb.classList.contains('collapsed') ? '▶' : '◀';
  setTimeout(function() {{ map.invalidateSize(); }}, 400);
}}

// ── DETAIL PANEL ──
function showDetail(p) {{
  document.getElementById('detailPanel').classList.add('visible');
  document.getElementById('dp-name').textContent = p.NAMOBJ || '—';
  document.getElementById('dp-kec').textContent = 'Kecamatan ' + (p.WADMKC || '—');

  const eta = p.eta_mean;
  const etaEl = document.getElementById('dp-eta');
  etaEl.textContent = eta != null ? eta.toFixed(3) : '—';
  etaEl.className = 'di-value ' + etaClass(eta);

  document.getElementById('dp-rank').textContent = p.rank_eta || '—';
  document.getElementById('dp-rank').className = 'di-value ' + (p.rank_eta <= 5 ? 'bad' : (p.rank_eta >= 60 ? 'good' : ''));

  const timeEl = document.getElementById('dp-time');
  timeEl.textContent = p.daily_time_lost_min != null ? p.daily_time_lost_min.toFixed(1) + ' min' : '—';
  timeEl.className = 'di-value ' + (p.daily_time_lost_min > 40 ? 'bad' : (p.daily_time_lost_min < 20 ? 'good' : 'ok'));

  const hEl = document.getElementById('dp-health');
  hEl.textContent = p.eta_health != null ? p.eta_health.toFixed(3) : '—';
  hEl.className = 'di-value ' + etaClass(p.eta_health);

  const eEl = document.getElementById('dp-edu');
  eEl.textContent = p.eta_education != null ? p.eta_education.toFixed(3) : '—';
  eEl.className = 'di-value ' + etaClass(p.eta_education);

  const ecEl = document.getElementById('dp-econ');
  ecEl.textContent = p.eta_economic != null ? p.eta_economic.toFixed(3) : '—';
  ecEl.className = 'di-value ' + etaClass(p.eta_economic);
}}
</script>
</body>
</html>"""

    # Write outputs
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    out_path = os.path.join("outputs", "interactive_map.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard saved to {out_path}")

    docs_path = os.path.join("docs", "index.html")
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard copied to {docs_path}")

    fsize = os.path.getsize(out_path) / (1024 * 1024)
    print(f"File size: {fsize:.2f} MB (limit: 15 MB)")

if __name__ == "__main__":
    run_interactive_map()
