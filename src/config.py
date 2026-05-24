# src/config.py — edit before running

CITY_NAME     = "Kota Jambi, Jambi, Indonesia"
CRS_PROJECTED = "EPSG:32748"   # UTM Zone 48S
AVG_SPEED_KMH = 25             # Urban congested speed assumption
TRIPS_PER_DAY = 3              # For daily time-cost calculation

# Shapefile field names — dynamically verified from data
FIELD_KELURAHAN  = "NAMOBJ"
FIELD_KECAMATAN  = "WADMKC"

# Destination categories
DEST_TAGS = {
    "health":    {"amenity": ["hospital", "clinic"]},
    "education": {"amenity": ["school", "university"]},
    "economic":  {"amenity": "marketplace", "shop": True},
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
KELURAHAN_GEOJSON = DATA_RAW + "kelurahan_boundaries.geojson"
