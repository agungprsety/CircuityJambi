import os
import geopandas as gpd
import pandas as pd
import osmnx as ox
import config

def acquire_destinations():
    print("Starting Module 3: Destination Acquisition")
    
    # Load boundary polygon
    print(f"Loading boundary from {config.KELURAHAN_GEOJSON}...")
    gdf_bounds = gpd.read_file(config.KELURAHAN_GEOJSON)
    if gdf_bounds.crs is None or gdf_bounds.crs.to_string() != 'EPSG:4326':
        gdf_bounds = gdf_bounds.to_crs(epsg=4326)
    boundary_polygon = gdf_bounds.unary_union
    
    all_features = []
    
    for category, tags in config.DEST_TAGS.items():
        print(f"Querying features for category: {category} with tags {tags}...")
        try:
            # FR-03-1 & FR-03-2 Query features
            features = ox.features_from_polygon(boundary_polygon, tags=tags)
            
            if features.empty:
                print(f"WARNING: Zero results returned for category '{category}'")
                continue
                
            # Keep name if it exists
            if 'name' in features.columns:
                features['dest_name'] = features['name'].fillna('Unnamed')
            else:
                features['dest_name'] = 'Unnamed'
                
            features = features[['geometry', 'dest_name']].copy()
            features['category'] = category
            
            all_features.append(features)
        except Exception as e:
            # FR-03-5 Log warning and continue
            print(f"WARNING: Failed to query category '{category}'. Exception: {e}")
            continue

    if not all_features:
        raise ValueError("No destinations found for any category.")
        
    dest_gdf = pd.concat(all_features, ignore_index=True)
    
    # FR-03-3 Compute centroid for polygon destinations
    print("Computing centroids for all destinations...")
    # Reproject to projected CRS to get accurate metric centroids
    dest_gdf = dest_gdf.to_crs(config.CRS_PROJECTED)
    dest_gdf['geometry'] = dest_gdf.geometry.centroid
    
    # FR-03-4 Snap all destination centroids to nearest graph nodes
    print("Loading drive network graph...")
    graph_path = os.path.join(config.DATA_PROCESSED, "jambi_drive.graphml")
    G_proj = ox.load_graphml(graph_path)
    
    print("Snapping destinations to nearest network nodes...")
    X = dest_gdf.geometry.x.values
    Y = dest_gdf.geometry.y.values
    nearest_nodes = ox.distance.nearest_nodes(G_proj, X, Y)
    
    dest_gdf['node_id'] = nearest_nodes
    dest_gdf['dest_id'] = dest_gdf.index
    
    # FR-03-6 Save raw destination GeoDataFrame to data/destinations.geojson
    out_path = os.path.join(config.DATA_PROCESSED, "destinations.geojson")
    print(f"Saving destinations to {out_path}...")
    
    # GeoJSON expects WGS84 (EPSG:4326), but we can save projected if we want.
    # It's safer to reproject to WGS84 for GeoJSON standard, though we need projected coords later.
    # We will save it in WGS84 and the next module will project it.
    dest_gdf.to_crs(epsg=4326).to_file(out_path, driver="GeoJSON")
    
    print(f"Count of destinations successfully acquired: {len(dest_gdf)}")
    print("--- Destination Acquisition Complete ---")

if __name__ == "__main__":
    acquire_destinations()
