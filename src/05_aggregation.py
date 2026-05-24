import os
import pandas as pd
import geopandas as gpd
import config

def run_aggregation():
    print("Starting Module 5: Aggregation")
    
    input_csv = os.path.join(config.DATA_PROCESSED, "od_results.csv")
    df = pd.read_csv(input_csv)
    
    # Pre-filter counts (Total pairs and Disconnected)
    total_pairs = df.groupby('kelurahan').size().rename('total_pairs')
    disconnected_pairs = df.groupby('kelurahan')['disconnected'].sum().astype(int).rename('disconnected_pairs')
    
    # Apply user-requested filters while preserving disconnected logic
    print("Applying filters (eta <= 10, d_euclidean_m >= 200)...")
    valid_mask = ((df['eta'] <= 10) | df['eta'].isna()) & ((df['d_euclidean_m'] >= 200) | df['d_euclidean_m'].isna())
    df = df[valid_mask].copy()
    
    # Mean eta overall
    mean_eta = df.groupby('kelurahan')['eta'].mean().rename('eta_mean')
    
    # Mean eta per category
    cat_eta = df.pivot_table(index='kelurahan', columns='category', values='eta', aggfunc='mean')
    cat_eta.columns = [f'eta_{col}' for col in cat_eta.columns]
    
    # Avg euclidean distance (in km) for time loss calculation
    df['d_euclidean_km'] = df['d_euclidean_m'] / 1000
    avg_euclidean = df.groupby('kelurahan')['d_euclidean_km'].mean().rename('avg_d_euclidean_km')
    
    # Combine summaries
    summary = pd.concat([total_pairs, disconnected_pairs, mean_eta, avg_euclidean, cat_eta], axis=1)
    
    # FR-05-2 Compute time cost
    # time_lost_min = (eta_mean - 1) × avg_d_euclidean_km / 25 × 60
    summary['time_lost_min'] = (summary['eta_mean'] - 1) * summary['avg_d_euclidean_km'] / 25 * 60
    
    # FR-05-3 Compute daily time lost assuming 3 trips/day
    summary['daily_time_lost_min'] = summary['time_lost_min'] * 3
    
    # FR-05-4 Rank kelurahan 1-N by mean eta (1 = worst connectivity = highest eta)
    summary['rank_eta'] = summary['eta_mean'].rank(ascending=False, method='min')
    
    # FR-05-5 Flag top 5 worst and top 5 best
    summary['is_top_5_worst'] = summary['rank_eta'] <= 5
    summary['is_top_5_best'] = summary['eta_mean'].rank(ascending=True, method='min') <= 5
    
    # Ensure index is accessible for merging
    summary = summary.reset_index()
    
    # FR-05-6 Merge summary back to kelurahan polygon GeoDataFrame
    print(f"Loading kelurahan boundaries from {config.KELURAHAN_GEOJSON}...")
    gdf = gpd.read_file(config.KELURAHAN_GEOJSON)
    
    gdf_summary = gdf.merge(summary, left_on=config.FIELD_KELURAHAN, right_on='kelurahan', how='left')
    
    # Drop redundant column if it exists and clean up NaN values in boolean columns
    if 'kelurahan' in gdf_summary.columns and 'kelurahan' != config.FIELD_KELURAHAN:
        gdf_summary = gdf_summary.drop(columns=['kelurahan'])
        
    gdf_summary['is_top_5_worst'] = gdf_summary['is_top_5_worst'].fillna(False).astype(bool)
    gdf_summary['is_top_5_best'] = gdf_summary['is_top_5_best'].fillna(False).astype(bool)
    
    # FR-05-7 Save to data/summary_kelurahan.geojson
    output_path = os.path.join(config.DATA_PROCESSED, "summary_kelurahan.geojson")
    
    # Need to save with WGS84 for GeoJSON mapping typically, assuming it's WGS84 originally
    if gdf_summary.crs is None or gdf_summary.crs.to_string() != "EPSG:4326":
        gdf_summary = gdf_summary.to_crs("EPSG:4326")
        
    gdf_summary.to_file(output_path, driver='GeoJSON')
    print(f"Aggregation complete! Summary saved to {output_path}")

if __name__ == "__main__":
    run_aggregation()
