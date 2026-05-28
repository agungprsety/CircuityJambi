import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import os
import config

st.set_page_config(page_title="Jambi Circuity Ratio", layout="wide", initial_sidebar_state="expanded")

# Inject custom CSS to make it look even less "HTML-y" and more WebGIS
st.markdown("""
<style>
    .css-18e3th9 { padding-top: 1rem; }
    .css-1d391kg { padding-top: 1rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    summary_path = os.path.join(config.DATA_PROCESSED, "summary_kelurahan.geojson")
    dest_path = os.path.join(config.DATA_PROCESSED, "destinations.geojson")
    road_path = os.path.join(config.DATA_PROCESSED, "road_network.geojson")
    
    gdf_kel = gpd.read_file(summary_path)
    gdf_dest = gpd.read_file(dest_path)
    gdf_road = gpd.read_file(road_path) if os.path.exists(road_path) else None
    
    if gdf_kel.crs is None or gdf_kel.crs.to_string() != "EPSG:4326":
        gdf_kel = gdf_kel.to_crs("EPSG:4326")
    if gdf_dest.crs is None or gdf_dest.crs.to_string() != "EPSG:4326":
        gdf_dest = gdf_dest.to_crs("EPSG:4326")
    if gdf_road is not None and (gdf_road.crs is None or gdf_road.crs.to_string() != "EPSG:4326"):
        gdf_road = gdf_road.to_crs("EPSG:4326")
        
    return gdf_kel, gdf_dest, gdf_road

gdf_kelurahan, gdf_dests, gdf_roads = load_data()

# --- SIDEBAR ---
st.sidebar.title("🗺️ Circuity Ratio Explorer")
st.sidebar.markdown("Analyze the road network circuity ratio (η) across Jambi.")

st.sidebar.header("Map Controls")
show_destinations = st.sidebar.checkbox("Show Destinations", value=True)

selected_categories = []
if show_destinations:
    categories = gdf_dests['category'].unique().tolist()
    selected_categories = st.sidebar.multiselect("Filter Destinations", categories, default=categories)

show_roads = st.sidebar.checkbox("Show Road Network", value=True)
highlight_worst = st.sidebar.checkbox("Highlight Top 5 Worst Kelurahan", value=True)

st.sidebar.markdown("---")
st.sidebar.info("**What is η?**\n\nThe Circuity Ratio (η) measures how much farther you must travel on the road network compared to a straight line. High η = severe spatial disconnection.")

# --- MAIN APP ---
st.title("Jambi: Urban Circuity & Accessibility")

# Calculate Center
bounds = gdf_kelurahan.total_bounds
center_lon = (bounds[0] + bounds[2]) / 2
center_lat = (bounds[1] + bounds[3]) / 2

# Create Folium Map with Dark Mode Tiles
m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB dark_matter")

# Colormap
min_eta = gdf_kelurahan['eta_mean'].min()
max_eta = gdf_kelurahan['eta_mean'].max()
colormap = cm.LinearColormap(colors=['#FFECA1', '#FFB74D', '#F4511E', '#B71C1C'], 
                             vmin=min_eta, vmax=max_eta)
colormap.caption = "Mean Circuity Ratio (η)"

def style_function(feature):
    eta = feature['properties'].get('eta_mean')
    return {
        'fillColor': colormap(eta) if pd.notna(eta) else 'transparent',
        'color': '#444444',
        'weight': 1,
        'fillOpacity': 0.75
    }

def highlight_function(feature):
    eta = feature['properties'].get('eta_mean')
    return {
        'fillColor': colormap(eta) if pd.notna(eta) else 'transparent',
        'color': 'white',
        'weight': 2,
        'fillOpacity': 0.95
    }

tooltip = folium.features.GeoJsonTooltip(
    fields=[config.FIELD_KELURAHAN, config.FIELD_KECAMATAN, 'eta_mean', 'rank_eta', 'daily_time_lost_min'],
    aliases=['Kelurahan:', 'Kecamatan:', 'Mean Circuity (η):', 'Rank (1=Worst):', 'Daily Time Lost (min):'],
    localize=True,
    style="background-color: #2b2b2b; color: white; border: 1px solid #555; border-radius: 5px; box-shadow: 0px 4px 6px rgba(0,0,0,0.3); font-family: sans-serif; font-size: 13px; padding: 10px;"
)

folium.GeoJson(
    gdf_kelurahan,
    name="Circuity (η) by Kelurahan",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=tooltip
).add_to(m)

# Road Network layer (above Kelurahan layer, below Destinations/worst outline)
if gdf_roads is not None and show_roads:
    folium.GeoJson(
        gdf_roads,
        name="Road Network",
        style_function=lambda x: {
            'color': '#26c6da',  # light blue
            'weight': 1.2,
            'opacity': 0.75
        }
    ).add_to(m)

m.add_child(colormap)

# Top 5 Worst Highlight
if highlight_worst:
    worst_5 = gdf_kelurahan[gdf_kelurahan['is_top_5_worst'] == True]
    if not worst_5.empty:
        folium.GeoJson(
            worst_5,
            name="Top 5 Worst",
            style_function=lambda x: {'fillColor': 'transparent', 'color': '#FF1744', 'weight': 3, 'dashArray': '5, 5'},
            tooltip=folium.features.GeoJsonTooltip(
                fields=[config.FIELD_KELURAHAN],
                aliases=['Worst Connectivity:'],
                style="background-color: #4a0000; color: #ff8a80; font-weight: bold; border: 1px solid red;"
            )
        ).add_to(m)

# Destinations
if show_destinations and selected_categories:
    color_map = {
        'health': '#ef5350',
        'education': '#42a5f5',
        'economic': '#66bb6a',
        'civic': '#ffa726'
    }
    
    filtered_dests = gdf_dests[gdf_dests['category'].isin(selected_categories)]
    
    for idx, row in filtered_dests.iterrows():
        cat = row['category']
        color = color_map.get(cat, 'gray')
        
        # Use simple HTML for popup to keep it fast
        popup_html = f"<div style='color:black; font-family:sans-serif;'><b>{row['dest_name']}</b><br/>{cat.title()}</div>"
        
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            popup=folium.Popup(popup_html, max_width=250),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            weight=1
        ).add_to(m)

# Render map in Streamlit
st_data = st_folium(m, use_container_width=True, height=700)
