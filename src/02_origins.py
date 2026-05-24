import os
import json
import geopandas as gpd
import osmnx as ox
import networkx as nx
import config

def generate_origins():
    print(f"Starting Module 2: Origin Generation")
    
    # FR-02-1 Load shapefile
    print(f"Loading kelurahan boundaries from {config.KELURAHAN_GEOJSON}...")
    gdf = gpd.read_file(config.KELURAHAN_GEOJSON)
    
    # FR-02-1 Reproject to EPSG:32748
    print(f"Reprojecting to {config.CRS_PROJECTED}...")
    if gdf.crs is None or gdf.crs.to_string() != config.CRS_PROJECTED:
        gdf = gdf.to_crs(config.CRS_PROJECTED)
        
    # FR-02-2 Compute polygon centroid for each kelurahan
    print("Computing centroids...")
    centroids = gdf.geometry.centroid
    
    # FR-02-3 Snap each centroid to nearest OSM drive network node
    print("Loading drive network graph...")
    graph_path = os.path.join(config.DATA_PROCESSED, "jambi_drive.graphml")
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Graph not found at {graph_path}. Please run Module 1 first.")
    
    G_proj = ox.load_graphml(graph_path)
    
    print("Snapping centroids to nearest network nodes...")
    X = centroids.x.values
    Y = centroids.y.values
    
    nearest_nodes = ox.distance.nearest_nodes(G_proj, X, Y)
    
    # FR-02-4 Store result as {kelurahan_id: node_id} mapping
    kelurahan_names = gdf[config.FIELD_KELURAHAN].values
    
    origin_mapping = {}
    for name, node in zip(kelurahan_names, nearest_nodes):
        origin_mapping[str(name)] = int(node)
        
    mapping_path = os.path.join(config.DATA_PROCESSED, "origin_mapping.json")
    with open(mapping_path, "w") as f:
        json.dump(origin_mapping, f, indent=4)
        
    print(f"Saved origin mapping to {mapping_path}")
    
    # FR-02-5 Log count of origins successfully snapped
    print(f"\nCount of origins successfully snapped: {len(origin_mapping)}")
    print("--- Origin Generation Complete ---")

if __name__ == "__main__":
    generate_origins()
