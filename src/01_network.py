import os
import networkx as nx
import osmnx as ox
import geopandas as gpd
import config

def acquire_network():
    print(f"Starting Module 1: Network Acquisition for {config.CITY_NAME}")
    graph_path = os.path.join(config.DATA_PROCESSED, "jambi_drive.graphml")
    
    if os.path.exists(graph_path):
        print(f"Graph already exists at {graph_path}. Skipping download.")
        return
    
    # Load kelurahan boundaries to get the polygon
    print(f"Loading boundary from {config.KELURAHAN_GEOJSON}...")
    gdf = gpd.read_file(config.KELURAHAN_GEOJSON)
    
    # Reproject to WGS84 just in case it's not (OSMnx expects WGS84 for downloading)
    if gdf.crs and gdf.crs.to_string() != 'EPSG:4326':
        gdf = gdf.to_crs(epsg=4326)
        
    boundary_polygon = gdf.unary_union
    
    print("Downloading drive network using osmnx.graph_from_polygon...")
    # FR-01-1 Download drive network using polygon
    G = ox.graph_from_polygon(boundary_polygon, network_type='drive', simplify=True)
    
    # FR-01-2 Project to EPSG:32748
    print(f"Projecting graph to {config.CRS_PROJECTED}...")
    G_proj = ox.project_graph(G, to_crs=config.CRS_PROJECTED)
    
    # FR-01-3 Save graph
    print(f"Saving graph to {graph_path}...")
    ox.save_graphml(G_proj, filepath=graph_path)
    
    # FR-01-4 Log node count, edge count, and CRS
    num_nodes = len(G_proj.nodes)
    num_edges = len(G_proj.edges)
    crs = G_proj.graph['crs']
    
    print("\n--- Network Acquisition Complete ---")
    print(f"Nodes: {num_nodes}")
    print(f"Edges: {num_edges}")
    print(f"CRS:   {crs}")

if __name__ == "__main__":
    os.makedirs(config.DATA_PROCESSED, exist_ok=True)
    acquire_network()
