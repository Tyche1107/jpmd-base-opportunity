"""
Visualization Script - Generate charts and diagrams
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import json

def create_sankey_diagram():
    """Create Sankey diagram showing USDC flow"""
    
    # Load flow distribution
    distribution = pd.read_csv('analysis/flow_distribution.csv', index_col=0)
    
    # Create Sankey
    labels = ['Institutional USDC\n(>$100k transfers)']
    
    # Add category nodes
    category_labels = {
        'morpho': 'Morpho\n(Lending)',
        'aave_horizon': 'Aave Horizon\n(Permissioned)',
        'bridges': 'Cross-chain\nBridges',
        'exchanges': 'Centralized\nExchanges',
        'p2p': 'Wallet-to-Wallet\n(P2P)'
    }
    
    sources = []
    targets = []
    values = []
    colors = []
    
    color_map = {
        'morpho': 'rgba(99, 102, 241, 0.6)',       # Indigo - DeFi
        'aave_horizon': 'rgba(139, 92, 246, 0.6)', # Purple - Permissioned DeFi
        'bridges': 'rgba(59, 130, 246, 0.6)',      # Blue - Infrastructure
        'exchanges': 'rgba(16, 185, 129, 0.6)',    # Green - CeFi
        'p2p': 'rgba(251, 191, 36, 0.6)'           # Amber - Direct
    }
    
    for category, row in distribution.iterrows():
        labels.append(category_labels.get(category, category))
        sources.append(0)
        targets.append(len(labels) - 1)
        values.append(row['volume_usd'])
        colors.append(color_map.get(category, 'rgba(156, 163, 175, 0.6)'))
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color='white', width=2),
            label=labels,
            color=['rgba(71, 85, 105, 0.8)'] + [color_map.get(cat, 'gray') for cat in distribution.index]
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            label=[f"${v/1e6:.1f}M ({distribution.loc[distribution.index[i], 'volume_pct']:.1f}%)" 
                   for i, v in enumerate(values)]
        )
    )])
    
    fig.update_layout(
        title={
            'text': "Base Network: Institutional USDC Flow Distribution (90 Days)",
            'font': {'size': 20, 'family': 'Arial, sans-serif'}
        },
        font=dict(size=12, family='Arial, sans-serif'),
        height=600,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    fig.write_html('visualizations/sankey_flow.html')
    fig.write_image('visualizations/sankey_flow.png', width=1200, height=600)
    
    print("✓ Sankey diagram created: visualizations/sankey_flow.html")
    
    return fig

def create_distribution_chart():
    """Create bar chart showing volume distribution"""
    
    distribution = pd.read_csv('analysis/flow_distribution.csv', index_col=0)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Volume chart
    colors = ['#6366F1', '#8B5CF6', '#3B82F6', '#10B981', '#FBBF24']
    distribution['volume_usd'].plot(kind='barh', ax=ax1, color=colors)
    ax1.set_xlabel('Volume (USD)', fontsize=12)
    ax1.set_title('Volume Distribution by Category', fontsize=14, fontweight='bold')
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M'))
    
    # Percentage chart
    distribution['volume_pct'].plot(kind='barh', ax=ax2, color=colors)
    ax2.set_xlabel('Percentage (%)', fontsize=12)
    ax2.set_title('Percentage Distribution by Category', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('visualizations/distribution_chart.png', dpi=300, bbox_inches='tight')
    
    print("✓ Distribution chart created: visualizations/distribution_chart.png")
    
    return fig

def create_risk_distribution():
    """Create visualization of sybil risk distribution"""
    
    sybil_results = pd.read_csv('analysis/sybil_analysis_results.csv')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Risk label distribution
    risk_counts = sybil_results['risk_label'].value_counts()
    colors_risk = {'Clean': '#10B981', 'Medium': '#FBBF24', 'Higher': '#EF4444'}
    risk_counts.plot(kind='bar', ax=ax1, color=[colors_risk[x] for x in risk_counts.index])
    ax1.set_title('Risk Distribution Across Institutional Wallets', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Wallets', fontsize=12)
    ax1.set_xlabel('Risk Category', fontsize=12)
    ax1.tick_params(axis='x', rotation=0)
    
    # Behavior profile distribution
    behavior_counts = sybil_results['behavior_profile'].value_counts()
    behavior_counts.plot(kind='bar', ax=ax2, color='#6366F1')
    ax2.set_title('Behavioral Profile Distribution', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of Wallets', fontsize=12)
    ax2.set_xlabel('Profile Type', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('visualizations/sybil_analysis.png', dpi=300, bbox_inches='tight')
    
    print("✓ Sybil analysis chart created: visualizations/sybil_analysis.png")
    
    return fig

def create_summary_statistics():
    """Generate summary statistics image"""
    
    distribution = pd.read_csv('analysis/flow_distribution.csv', index_col=0)
    transfers = pd.read_csv('analysis/categorized_transfers.csv')
    
    total_volume = distribution['volume_usd'].sum()
    total_transfers = distribution['transfer_count'].sum()
    avg_transfer = total_volume / total_transfers
    
    # Top category
    top_category = distribution.iloc[0]
    
    # Create summary figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    summary_text = f"""
    BASE NETWORK - INSTITUTIONAL USDC FLOW ANALYSIS
    90-Day Period Summary
    
    Total Volume:              ${total_volume:,.0f}
    Total Large Transfers:     {total_transfers:,}
    Average Transfer Size:     ${avg_transfer:,.0f}
    
    TOP DESTINATION CATEGORY
    {top_category.name.upper()}: {top_category['volume_pct']:.1f}% (${top_category['volume_usd']:,.0f})
    
    BREAKDOWN BY CATEGORY:
    """
    
    for category, row in distribution.iterrows():
        summary_text += f"    {category.upper():<20} {row['volume_pct']:>6.1f}%    ${row['volume_usd']:>15,.0f}\n"
    
    ax.text(0.1, 0.5, summary_text, fontsize=11, family='monospace', 
            verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.savefig('visualizations/summary_stats.png', dpi=300, bbox_inches='tight')
    
    print("✓ Summary statistics created: visualizations/summary_stats.png")
    
    return fig

if __name__ == "__main__":
    print("Generating visualizations...")
    
    create_sankey_diagram()
    create_distribution_chart()
    create_risk_distribution()
    create_summary_statistics()
    
    print("\n✓ All visualizations generated successfully!")
