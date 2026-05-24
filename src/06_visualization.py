import os
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd
import osmnx as ox
import numpy as np
import matplotlib.patheffects as pe
import config

def run_visualization():
    print("Starting Module 6: Premium Static Visualizations")
    
    out_dir = os.path.join("outputs", "figures")
    os.makedirs(out_dir, exist_ok=True)
    
    # Set premium publication style
    plt.style.use('dark_background')
    sns.set_theme(style="darkgrid", rc={
        "axes.facecolor": "#161823",
        "figure.facecolor": "#0f1117",
        "grid.color": "#2c2e3b",
        "text.color": "#e4e4e7",
        "axes.labelcolor": "#9ca3af",
        "xtick.color": "#9ca3af",
        "ytick.color": "#9ca3af"
    })
    
    # Load summary data
    print("Loading summary data...")
    summary_path = os.path.join(config.DATA_PROCESSED, "summary_kelurahan.geojson")
    gdf = gpd.read_file(summary_path)
    
    if gdf.crs is None or gdf.crs.to_string() != config.CRS_PROJECTED:
        gdf = gdf.to_crs(config.CRS_PROJECTED)
        
    # =========================================================================
    # VIZ-01: Choropleth Map (Quantile-based)
    # =========================================================================
    print("Generating VIZ-01: Choropleth Map...")
    fig, ax = plt.subplots(1, 1, figsize=(14, 14), facecolor='#0f1117')
    
    # Plot Kelurahan with Quantiles to expose fine variations
    gdf.plot(column='eta_mean', scheme='Quantiles', k=6, cmap='YlOrRd', 
             linewidth=0.8, edgecolor='#0f1117', legend=True, 
             legend_kwds={'loc': 'lower left', 'title': "Mean Circuity (η)\nQuantile Bins", 
                          'frameon': True, 'facecolor': '#161823', 'edgecolor': 'none'}, 
             ax=ax)
             
    # Plot Network
    print("Loading drive network graph for overlay...")
    graph_path = os.path.join(config.DATA_PROCESSED, "jambi_drive.graphml")
    G = ox.load_graphml(graph_path)
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    edges.plot(ax=ax, color='#ffffff', linewidth=0.2, alpha=0.15)
    
    # Labels for all kelurahan
    for idx, row in gdf.iterrows():
        pt = row['geometry'].centroid
        # Differentiate worst 5 from the rest for readability
        is_worst = row.get('is_top_5_worst', False)
        color = '#fca5a5' if is_worst else '#ffffff'
        fontsize = 10 if is_worst else 6
        weight = 'bold' if is_worst else 'normal'
        alpha = 1.0 if is_worst else 0.85
        
        ax.annotate(row[config.FIELD_KELURAHAN], xy=(pt.x, pt.y), xytext=(0, 0), 
                    textcoords="offset points", color=color, weight=weight, 
                    fontsize=fontsize, ha='center', va='center', alpha=alpha,
                    path_effects=[pe.withStroke(linewidth=2.5, foreground="#000000")])
                    
    # Scale Bar (5 km)
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    x_start = x_min + (x_max - x_min)*0.05
    y_pos = y_min + (y_max - y_min)*0.95
    ax.plot([x_start, x_start + 5000], [y_pos, y_pos], color='#e4e4e7', lw=3)
    ax.text(x_start + 2500, y_pos + (y_max - y_min)*0.015, '5 km', color='#e4e4e7', ha='center', va='bottom', fontsize=12, weight='bold')
    
    ax.set_axis_off()
    ax.set_title("Network Circuity (η) Distribution in Jambi", fontsize=20, weight='bold', pad=20, color='#ffffff')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "map_circuity_choropleth.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # =========================================================================
    # VIZ-02: Category Heatmap (Top 20 Worst)
    # =========================================================================
    print("Generating VIZ-02: Category Heatmap...")
    cat_cols = [c for c in gdf.columns if c.startswith('eta_') and c != 'eta_mean'] + ['eta_mean']
    
    # Filter to top 20 worst to make the heatmap readable and impactful
    gdf_sorted = gdf.sort_values('eta_mean', ascending=False).head(20)
    
    df_heatmap = gdf_sorted.set_index(config.FIELD_KELURAHAN)[cat_cols]
    df_heatmap.columns = [c.replace('eta_', '').title() for c in df_heatmap.columns]
    
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#0f1117')
    sns.heatmap(df_heatmap, cmap='YlOrRd', annot=True, fmt=".2f", ax=ax, 
                cbar_kws={'label': 'Circuity Ratio (η)'}, linewidths=0.5, linecolor='#161823')
    
    ax.set_ylabel("Kelurahan (Top 20 Worst)", fontsize=12, weight='bold', color='#e4e4e7')
    ax.set_xlabel("Destination Category", fontsize=12, weight='bold', color='#e4e4e7')
    ax.set_title("Categorical Disconnection across Worst Neighborhoods", fontsize=16, weight='bold', pad=20, color='#ffffff')
    ax.tick_params(axis='y', colors='#e4e4e7')
    ax.tick_params(axis='x', colors='#e4e4e7')
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "heatmap_category_eta.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # =========================================================================
    # VIZ-03: Time-cost Bar Chart
    # =========================================================================
    print("Generating VIZ-03: Time-cost Bar Chart...")
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#0f1117')
    
    # Get top 10 worst and top 5 best
    gdf_worst = gdf.sort_values('daily_time_lost_min', ascending=False).head(15)
    gdf_best = gdf.sort_values('daily_time_lost_min', ascending=True).head(5)
    
    # Combine and sort for display
    gdf_bars = pd.concat([gdf_best, gdf_worst]).sort_values('daily_time_lost_min', ascending=True)
    
    colors = ['#4ade80' if rank > 60 else '#ef4444' if rank <= 15 else '#9ca3af' for rank in gdf_bars['rank_eta']]
    
    bars = ax.barh(gdf_bars[config.FIELD_KELURAHAN], gdf_bars['daily_time_lost_min'], color=colors, height=0.6)
    
    # Add values to bars
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.1f}m',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha='left', va='center', color='#e4e4e7', fontsize=10)
    
    # Mean line
    city_mean = gdf['daily_time_lost_min'].mean()
    ax.axvline(city_mean, color='#facc15', linestyle='--', linewidth=2, zorder=0)
    ax.text(city_mean + 2, 1, f'City Avg: {city_mean:.1f} min', color='#facc15', rotation=90, va='bottom', weight='bold')
    
    ax.set_xlabel("Estimated Daily Time Lost (minutes) assuming 3 trips/day", fontsize=12, weight='bold', color='#9ca3af')
    ax.set_ylabel("Kelurahan", fontsize=12, weight='bold', color='#9ca3af')
    ax.set_title("The Daily Circuity Ratio Penalty (Top 15 Worst vs Top 5 Best)", fontsize=16, weight='bold', pad=20, color='#ffffff')
    ax.grid(axis='x', color='#2c2e3b', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Clean spines
    for spine in ['top', 'right', 'bottom', 'left']:
        ax.spines[spine].set_visible(False)
        
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "barchart_time_loss.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # =========================================================================
    # VIZ-04: Scatter — η vs Euclidean Distance (Short-trip caveat)
    # =========================================================================
    print("Generating VIZ-04: eta vs Euclidean Distance Scatter...")
    od_path = os.path.join(config.DATA_PROCESSED, "od_results.csv")
    df_od = pd.read_csv(od_path)
    
    # Filter valid pairs
    df_scatter = df_od[(df_od['eta'].notna()) & (df_od['eta'] <= 10) & (df_od['d_euclidean_m'] >= 200)].copy()
    df_scatter['d_euclidean_km'] = df_scatter['d_euclidean_m'] / 1000
    
    # Set up 1x3 small multiples
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True, facecolor='#0f1117')
    
    cat_colors = {
        'health': 'Reds',
        'education': 'Blues',
        'economic': 'Greens'
    }
    
    titles = {
        'health': 'Health Facilities',
        'education': 'Educational Institutions',
        'economic': 'Economic & Retail'
    }

    ref_color = '#4ade80'
    trend_color = '#facc15'

    for ax, (cat, cmap) in zip(axes, cat_colors.items()):
        mask = df_scatter['category'] == cat
        subset = df_scatter[mask]
        
        if len(subset) > 0:
            # Hexbin for density, particularly to handle overplotting in 0-4km zone
            hb = ax.hexbin(subset['d_euclidean_km'], subset['eta'], 
                           gridsize=30, cmap=cmap, mincnt=1, alpha=0.8,
                           extent=[0, df_scatter['d_euclidean_km'].max(), 0.9, df_scatter['eta'].max()])
            
            # Add LOESS-style trend line using rolling median
            df_sorted = subset.sort_values('d_euclidean_km')
            window = max(len(df_sorted) // 20, 10)
            rolling_median = df_sorted.set_index('d_euclidean_km')['eta'].rolling(window=window, center=True, min_periods=5).median()
            ax.plot(rolling_median.index, rolling_median.values, color=trend_color, linewidth=2.5, zorder=5)
            
        # Reference line at η = 1.0
        ax.axhline(y=1.0, color=ref_color, linestyle='--', linewidth=1.5, alpha=0.7)
        
        ax.set_title(titles[cat], fontsize=14, weight='bold', color='#ffffff')
        ax.set_xlabel("Euclidean Distance (km)", fontsize=12, weight='bold', color='#9ca3af')
        ax.grid(color='#2c2e3b', linestyle='--', alpha=0.5)
        ax.set_axisbelow(True)
        ax.set_facecolor('#0f1117')
        
        for spine in ['top', 'right', 'bottom', 'left']:
            ax.spines[spine].set_visible(False)
            
    # Set explicit Y-axis label on the first plot
    axes[0].set_ylabel("Circuity Ratio (η)", fontsize=13, weight='bold', color='#e4e4e7')
    
    # Annotate caveat on the first plot only, removing academic citation
    axes[0].annotate('Short trips naturally\nhave higher circuity', 
                xy=(0.5, 8.0), fontsize=11, color='#fca5a5', weight='bold',
                ha='left', va='top',
                path_effects=[pe.withStroke(linewidth=2, foreground="#000000")])
                
    fig.suptitle("Circuity Ratio vs. Euclidean Distance by Category", fontsize=18, weight='bold', color='#ffffff', y=1.05)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "scatter_eta_vs_distance.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualization complete! All files saved in outputs/figures/")

if __name__ == "__main__":
    run_visualization()
