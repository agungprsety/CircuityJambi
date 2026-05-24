import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import config

def generate_economic_figures():
    print("Generating Economic Impact Figures...")
    os.makedirs(config.OUTPUT_FIGURES, exist_ok=True)
    
    # Load summary data
    summary_path = os.path.join(config.DATA_PROCESSED, "summary_kelurahan.geojson")
    gdf = gpd.read_file(summary_path)
    
    # Drop rows with missing economic data
    df = gdf.dropna(subset=['annual_cost_total_idr', 'eta_mean']).copy()
    
    # Convert IDR to Millions for readability
    df['annual_cost_juta'] = df['annual_cost_total_idr'] / 1_000_000
    
    # Set seaborn style for premium look
    sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#1e1e24", "figure.facecolor": "#1e1e24", 
                                        "text.color": "white", "axes.labelcolor": "white", 
                                        "xtick.color": "white", "ytick.color": "white",
                                        "grid.color": "#333333", "font.family": "sans-serif"})

    # --- Figure 5: Top 10 Kelurahan by Economic Tax ---
    plt.figure(figsize=(10, 6))
    top10 = df.nlargest(10, 'annual_cost_juta')
    
    ax = sns.barplot(x='annual_cost_juta', y=config.FIELD_KELURAHAN, data=top10, palette="Reds_r")
    
    plt.title("Top 10 Kelurahan: Annual Connectivity Tax per Person", fontsize=14, pad=15, fontweight='bold')
    plt.xlabel("Annual Cost (Millions IDR)", fontsize=11)
    plt.ylabel("")
    
    # Add value labels to the bars
    for i, v in enumerate(top10['annual_cost_juta']):
        ax.text(v + 0.1, i, f" Rp {v:.1f} Jt", color='white', va='center', fontweight='bold', fontsize=10)
        
    # Formatting
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555555')
    ax.spines['left'].set_color('#555555')
    
    plt.tight_layout()
    fig5_path = os.path.join(config.OUTPUT_FIGURES, "fig5_economic_tax_bar.png")
    plt.savefig(fig5_path, dpi=300, bbox_inches='tight', facecolor="#1e1e24")
    print(f"Saved: {fig5_path}")
    plt.close()

    # --- Figure 6: Scatter Plot of Eta vs Economic Cost ---
    plt.figure(figsize=(9, 6))
    
    # Color by rank for visual distinction
    scatter = plt.scatter(df['eta_mean'], df['annual_cost_juta'], 
                          c=df['eta_mean'], cmap='magma', alpha=0.8, edgecolor='white', s=80)
    
    plt.title("Circuity Ratio (η) vs Annual Economic Cost", fontsize=14, pad=15, fontweight='bold')
    plt.xlabel("Mean Circuity Ratio (η)", fontsize=11)
    plt.ylabel("Annual Connectivity Tax (Millions IDR)", fontsize=11)
    
    # Annotate the extreme outliers (Top 3 worst)
    worst3 = df.nlargest(3, 'annual_cost_juta')
    for idx, row in worst3.iterrows():
        plt.annotate(row[config.FIELD_KELURAHAN], 
                     (row['eta_mean'], row['annual_cost_juta']),
                     xytext=(10, -5), textcoords='offset points',
                     fontsize=10, color='white', fontweight='bold')

    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Formatting
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555555')
    ax.spines['left'].set_color('#555555')
    
    plt.tight_layout()
    fig6_path = os.path.join(config.OUTPUT_FIGURES, "fig6_eta_vs_cost_scatter.png")
    plt.savefig(fig6_path, dpi=300, bbox_inches='tight', facecolor="#1e1e24")
    print(f"Saved: {fig6_path}")
    plt.close()

if __name__ == "__main__":
    generate_economic_figures()
