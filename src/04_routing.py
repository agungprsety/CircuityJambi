import os
import json
import csv
import numpy as np
import networkx as nx
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import config

def run_routing():
    print("Starting Module 4: Routing Engine")
    
    # Load Origin Mapping
    mapping_path = os.path.join(config.DATA_PROCESSED, "origin_mapping.json")
    with open(mapping_path, "r") as f:
        origin_mapping = json.load(f)
        
    # Load Kelurahan Boundaries to get centroids and Kecamatan
    gdf_bounds = gpd.read_file(config.KELURAHAN_GEOJSON)
    if gdf_bounds.crs is None or gdf_bounds.crs.to_string() != config.CRS_PROJECTED:
        gdf_bounds = gdf_bounds.to_crs(config.CRS_PROJECTED)
        
    centroids = gdf_bounds.geometry.centroid
    
    kelurahan_info = {}
    for idx, row in gdf_bounds.iterrows():
        kel_name = row[config.FIELD_KELURAHAN]
        kec_name = row[config.FIELD_KECAMATAN]
        pt = centroids.iloc[idx]
        kelurahan_info[str(kel_name)] = {
            "kecamatan": kec_name,
            "geom": pt
        }
        
    # Load Destinations
    dest_path = os.path.join(config.DATA_PROCESSED, "destinations.geojson")
    gdf_dests = gpd.read_file(dest_path)
    if gdf_dests.crs is None or gdf_dests.crs.to_string() != config.CRS_PROJECTED:
        gdf_dests = gdf_dests.to_crs(config.CRS_PROJECTED)
        
    # Load Graph
    print("Loading drive network graph...")
    graph_path = os.path.join(config.DATA_PROCESSED, "jambi_drive.graphml")
    G = ox.load_graphml(graph_path)
    
    output_path = os.path.join(config.DATA_PROCESSED, "od_results.csv")
    
    total_pairs = len(origin_mapping) * len(gdf_dests)
    print(f"Total OD pairs to compute: {total_pairs}")
    
    count = 0
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # FR-04-8 Output columns
        writer.writerow(['kelurahan', 'kecamatan', 'dest_id', 'dest_name', 'category', 'd_euclidean_m', 'd_network_m', 'eta', 'disconnected'])
        
        # FR-04-1 Iterate all origin x destination combinations
        for kel_name, orig_node in origin_mapping.items():
            kec_name = kelurahan_info[kel_name]["kecamatan"]
            orig_geom = kelurahan_info[kel_name]["geom"]
            
            for idx, dest_row in gdf_dests.iterrows():
                dest_id = dest_row['dest_id']
                dest_name = dest_row['dest_name']
                category = dest_row['category']
                dest_node = dest_row['node_id']
                dest_geom = dest_row['geometry']
                
                # FR-04-3 Euclidean distance
                d_euclidean = orig_geom.distance(dest_geom)
                
                # FR-04-2 Network distance
                disconnected = False
                try:
                    d_network = nx.shortest_path_length(G, orig_node, dest_node, weight='length')
                except nx.NetworkXNoPath:
                    # FR-04-5 Catch NoPath
                    d_network = np.nan
                    d_euclidean = np.nan
                    disconnected = True
                
                # FR-04-4 Compute eta
                eta = np.nan
                if not disconnected and d_euclidean > 0:
                    eta = d_network / d_euclidean
                
                # FR-04-6 Save results immediately
                writer.writerow([kel_name, kec_name, dest_id, dest_name, category, d_euclidean, d_network, eta, disconnected])
                
                count += 1
                # FR-04-7 Log progress
                if count % 100 == 0:
                    print(f"Processed {count}/{total_pairs} pairs...")
                    
    print(f"Routing computation complete! Results saved to {output_path}")

if __name__ == "__main__":
    run_routing()
