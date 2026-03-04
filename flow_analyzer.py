"""
Flow Analysis Script - Categorize destinations of large USDC transfers
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from config import *
import json

class FlowAnalyzer:
    def __init__(self, transfers_df):
        self.df = transfers_df
        self.address_stats = self._calculate_address_stats()
        self.categories = {
            'morpho': set(),
            'aave_horizon': set(),
            'bridges': set(),
            'exchanges': set(),
            'p2p': set()
        }
        
    def _calculate_address_stats(self):
        """Calculate statistics for each address to help identify exchanges"""
        stats = defaultdict(lambda: {
            'total_received': 0,
            'transfer_count': 0,
            'unique_senders': set(),
            'avg_amount': 0
        })
        
        for _, row in self.df.iterrows():
            to_addr = row['to']
            stats[to_addr]['total_received'] += row['amount_usd']
            stats[to_addr]['transfer_count'] += 1
            stats[to_addr]['unique_senders'].add(row['from'])
        
        # Calculate averages
        for addr in stats:
            stats[addr]['unique_senders_count'] = len(stats[addr]['unique_senders'])
            stats[addr]['avg_amount'] = stats[addr]['total_received'] / stats[addr]['transfer_count']
            stats[addr]['unique_senders'] = list(stats[addr]['unique_senders'])  # Convert set to list for JSON
        
        return dict(stats)
    
    def categorize_addresses(self):
        """Categorize all destination addresses"""
        
        # Step 1: Identify known protocols
        for protocol, addresses in KNOWN_PROTOCOLS.items():
            self.categories[protocol] = set([addr.lower() for addr in addresses])
        
        # Step 2: Identify likely exchanges by pattern
        for addr, stats in self.address_stats.items():
            if (stats['unique_senders_count'] >= EXCHANGE_INDICATORS['min_unique_senders'] and
                stats['transfer_count'] >= EXCHANGE_INDICATORS['min_daily_transfers']):
                self.categories['exchanges'].add(addr)
        
        # Step 3: Everything else is P2P
        all_categorized = set()
        for category in ['morpho', 'aave_horizon', 'bridges', 'exchanges']:
            all_categorized.update(self.categories[category])
        
        all_destinations = set(self.df['to'].unique())
        self.categories['p2p'] = all_destinations - all_categorized
        
        print("\n=== Address Categorization ===")
        for category, addresses in self.categories.items():
            print(f"{category}: {len(addresses)} addresses")
        
        return self.categories
    
    def calculate_flow_distribution(self):
        """Calculate volume and count distribution across categories"""
        
        self.df['category'] = self.df['to'].apply(self._get_category)
        
        # Volume distribution
        volume_by_category = self.df.groupby('category')['amount_usd'].sum()
        count_by_category = self.df.groupby('category').size()
        
        total_volume = volume_by_category.sum()
        total_count = count_by_category.sum()
        
        distribution = pd.DataFrame({
            'volume_usd': volume_by_category,
            'volume_pct': (volume_by_category / total_volume * 100).round(2),
            'transfer_count': count_by_category,
            'count_pct': (count_by_category / total_count * 100).round(2),
            'avg_transfer_size': (volume_by_category / count_by_category).round(2)
        })
        
        distribution = distribution.sort_values('volume_usd', ascending=False)
        
        print("\n=== Flow Distribution ===")
        print(distribution)
        print(f"\nTotal Volume: ${total_volume:,.2f}")
        print(f"Total Transfers: {total_count:,}")
        
        # Save results
        distribution.to_csv('analysis/flow_distribution.csv')
        
        # Save detailed categorized data
        self.df.to_csv('analysis/categorized_transfers.csv', index=False)
        
        return distribution
    
    def _get_category(self, address):
        """Get category for a single address"""
        for category, addresses in self.categories.items():
            if address in addresses:
                return category
        return 'p2p'
    
    def identify_institutional_wallets(self, top_n=50):
        """
        Identify top institutional wallets (excluding protocols and exchanges)
        for sybil analysis
        """
        
        # Filter to P2P addresses only
        p2p_addresses = self.categories['p2p']
        
        # Calculate metrics for each P2P address
        institutional_candidates = []
        
        for addr in p2p_addresses:
            stats = self.address_stats[addr]
            institutional_candidates.append({
                'address': addr,
                'total_volume': stats['total_received'],
                'transfer_count': stats['transfer_count'],
                'unique_senders': stats['unique_senders_count'],
                'avg_amount': stats['avg_amount']
            })
        
        # Sort by total volume
        institutional_candidates = sorted(
            institutional_candidates,
            key=lambda x: x['total_volume'],
            reverse=True
        )[:top_n]
        
        df_institutional = pd.DataFrame(institutional_candidates)
        df_institutional.to_csv('analysis/institutional_wallets.csv', index=False)
        
        print(f"\n=== Top {top_n} Institutional Wallets Identified ===")
        print(df_institutional.head(10))
        
        return df_institutional
    
    def export_for_visualization(self):
        """Export data in format suitable for Sankey diagram"""
        
        # Aggregate flows
        flows = self.df.groupby('category')['amount_usd'].sum()
        
        sankey_data = {
            'nodes': ['Source (USDC)'] + list(flows.index),
            'links': []
        }
        
        for i, (category, volume) in enumerate(flows.items()):
            sankey_data['links'].append({
                'source': 0,  # Source
                'target': i + 1,  # Category
                'value': float(volume),
                'label': f"${volume:,.0f}"
            })
        
        with open('analysis/sankey_data.json', 'w') as f:
            json.dump(sankey_data, f, indent=2)
        
        print("\nExported Sankey diagram data to analysis/sankey_data.json")
        
        return sankey_data

if __name__ == "__main__":
    # Load data
    df = pd.read_csv('data/large_usdc_transfers.csv')
    
    # Analyze
    analyzer = FlowAnalyzer(df)
    analyzer.categorize_addresses()
    distribution = analyzer.calculate_flow_distribution()
    institutional_wallets = analyzer.identify_institutional_wallets(top_n=50)
    analyzer.export_for_visualization()
