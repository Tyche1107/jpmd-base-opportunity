#!/usr/bin/env python3
"""
Create shocking visualizations for JPMorgan JPMD opportunity cost analysis
"""

import json
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'

# Load data
with open('data/opportunity_cost_analysis.json') as f:
    data = json.load(f)

# 1. JPMD vs USDC Market Share - Shocking Pie Chart
fig, ax = plt.subplots(figsize=(10, 8))

market_data = [data['usdc_supply'], 0.001]  # JPMD ~$0
labels = ['Base USDC\n$2.5B', 'JPMD\n~$0']
colors = ['#2ecc71', '#e74c3c']
explode = (0.05, 0.2)

wedges, texts, autotexts = ax.pie(market_data, labels=labels, autopct='%1.2f%%',
                                    colors=colors, startangle=90, explode=explode,
                                    textprops={'fontsize': 13, 'fontweight': 'bold'})

# Highlight JPMD's 0%
autotexts[1].set_color('white')
autotexts[1].set_fontsize(16)

ax.set_title('JPMorgan JPMD Market Share on Base Network\nPermissioned Token = 0.00% of $2.5B Market',
             fontsize=14, fontweight='bold', pad=20)

# Add annotation
ax.annotate('100% market\nlocked out', 
            xy=(0.3, 0.5), xytext=(-0.8, 0.3),
            arrowprops=dict(arrowstyle='->', color='red', lw=3),
            fontsize=14, color='red', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='yellow', alpha=0.8))

plt.tight_layout()
plt.savefig('charts/jpmd_market_share.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/jpmd_market_share.png")

# 2. Base USDC Ecosystem Breakdown - Where the Money Flows
fig, ax = plt.subplots(figsize=(10, 7))

categories = ['Aave V3', 'Aerodrome\nDEX', 'Uniswap\nV3', 'Compound', 'Other\nDeFi', 'Wallets/\nCEX']
values = [450, 280, 180, 120, 270, 1200]  # Millions
colors = ['#3498db', '#9b59b6', '#e67e22', '#1abc9c', '#34495e', '#95a5a6']

bars = ax.barh(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, values)):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2,
            f' ${val}M',
            ha='left', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Total Value Locked ($ Millions)', fontsize=13, fontweight='bold')
ax.set_title('Base Network USDC Ecosystem ($2.5B Total)\n52% in DeFi Protocols - JPMD Has 0% Access',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add JPMD annotation
ax.text(1400, 5.5, 'JPMD\n(Permissioned):\n$0 in ALL\ncategories',
        fontsize=12, color='red', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='yellow', alpha=0.8),
        ha='center')

plt.tight_layout()
plt.savefig('charts/base_usdc_breakdown.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/base_usdc_breakdown.png")

# 3. Opportunity Cost Scenarios - What JPMD Could Have Been
fig, ax = plt.subplots(figsize=(12, 7))

scenarios = ['Current\nReality', 'Conservative\n(1%)', 'Moderate\n(5%)', 'Aggressive\n(15%)']
tvls = [0, 25, 125, 375]  # Millions
colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']

bars = ax.bar(scenarios, tvls, color=colors, alpha=0.8, edgecolor='black', linewidth=2)

# Add value labels
for bar, val in zip(bars, tvls):
    height = bar.get_height()
    if val > 0:
        label = f'${val}M\n({val/10:.0f}x\ndeployment)'
    else:
        label = '$0\n(FAILURE)'
    ax.text(bar.get_x() + bar.get_width()/2., height,
            label,
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Potential TVL ($ Millions)', fontsize=13, fontweight='bold')
ax.set_title('JPMD Opportunity Cost: What Could Have Been\nIf JPMD Were Permissionless on Base',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add $10M deployment cost line
ax.axhline(y=10, color='red', linestyle='--', linewidth=2, label='$10M Deployment Cost')
ax.legend(fontsize=11, loc='upper left')

# Add annotation
ax.annotate('Even 1% would have\njustified the cost', 
            xy=(1, 25), xytext=(1.5, 100),
            arrowprops=dict(arrowstyle='->', color='green', lw=2),
            fontsize=12, color='green', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))

plt.tight_layout()
plt.savefig('charts/opportunity_scenarios.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/opportunity_scenarios.png")

# 4. ROI Comparison - JPMD vs Competitors
fig, ax = plt.subplots(figsize=(10, 7))

products = ['Circle USDC\n(Base)', 'Ondo USDY\n(Public)', 'BlackRock BUIDL\n(Permissioned)', 'JPMD\n(Permissioned)']
market_share = [100, 0.007, 0.007, 0.0]  # Approximate % of Base market
adoption = [2500000, 643, 57, 0]  # Users/holders

x = np.arange(len(products))
width = 0.35

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Market share bars
bars1 = ax1.bar(products, market_share, color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'],
                alpha=0.8, edgecolor='black', linewidth=2)

ax1.set_ylabel('Market Share on Base (%)', fontsize=13, fontweight='bold')
ax1.set_title('Base Network Market Dominance\nJPMD: 0.00% (Complete Failure)',
              fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)
ax1.set_yscale('log')

# Add value labels
for bar, val in zip(bars1, market_share):
    height = bar.get_height()
    if val > 0:
        label = f'{val:.3f}%' if val < 1 else f'{val:.0f}%'
    else:
        label = '0.00%'
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             label, ha='center', va='bottom', fontsize=10, fontweight='bold')

# User count comparison
bars2 = ax2.bar(products, adoption, color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'],
                alpha=0.8, edgecolor='black', linewidth=2)

ax2.set_ylabel('Number of Users/Holders', fontsize=13, fontweight='bold')
ax2.set_title('User Adoption Comparison\nPermissioned Tokens Struggle on Public Chains',
              fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)
ax2.set_yscale('log')

# Add value labels
for bar, val in zip(bars2, adoption):
    height = bar.get_height()
    if val > 0:
        label = f'{val:,}'
    else:
        label = '0'
    ax2.text(bar.get_x() + bar.get_width()/2., height if height > 0 else 0.1,
             label, ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/roi_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/roi_comparison.png")

print("\n✅ All JPMD visualizations created successfully!")
print("📁 Saved to: charts/")
