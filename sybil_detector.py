"""
Sybil Detection Analysis for Institutional Wallets
Based on HasciDB methodology - on-chain behavioral features
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from collections import defaultdict
import requests
import time
from config import *
from tqdm import tqdm

class SybilDetector:
    def __init__(self, institutional_wallets_df, transfers_df):
        self.wallets = institutional_wallets_df
        self.transfers = transfers_df
        self.features = {}
        
    def extract_features(self):
        """
        Extract behavioral features for each institutional wallet:
        1. Funding source diversity (how many unique senders)
        2. Transaction timing patterns (std dev of hour-of-day)
        3. Counterparty diversity (unique addresses interacted with)
        4. Gas price patterns (std dev, mean)
        5. Contract interaction breadth (unique contracts called)
        """
        
        print("Extracting behavioral features for sybil detection...")
        
        features_list = []
        
        for _, wallet in tqdm(self.wallets.iterrows(), total=len(self.wallets)):
            addr = wallet['address']
            
            # Get all transfers involving this address
            sent = self.transfers[self.transfers['from'] == addr]
            received = self.transfers[self.transfers['to'] == addr]
            
            # Feature 1: Funding source diversity
            unique_senders = received['from'].nunique()
            unique_receivers = sent['to'].nunique()
            
            # Feature 2: Transaction timing patterns
            all_txs = pd.concat([sent, received])
            if len(all_txs) > 0:
                all_txs['hour'] = pd.to_datetime(all_txs['timestamp'], unit='s').dt.hour
                hour_std = all_txs['hour'].std() if len(all_txs) > 1 else 0
            else:
                hour_std = 0
            
            # Feature 3: Transaction size patterns
            amount_std = all_txs['amount_usd'].std() if len(all_txs) > 1 else 0
            amount_mean = all_txs['amount_usd'].mean() if len(all_txs) > 0 else 0
            
            # Feature 4: Send/Receive ratio
            total_sent = sent['amount_usd'].sum()
            total_received = received['amount_usd'].sum()
            send_receive_ratio = total_sent / total_received if total_received > 0 else 0
            
            # Feature 5: Transaction frequency
            if len(all_txs) > 0:
                time_range = all_txs['timestamp'].max() - all_txs['timestamp'].min()
                tx_frequency = len(all_txs) / (time_range / 86400) if time_range > 0 else 0  # txs per day
            else:
                tx_frequency = 0
            
            features_list.append({
                'address': addr,
                'unique_senders': unique_senders,
                'unique_receivers': unique_receivers,
                'counterparty_diversity': unique_senders + unique_receivers,
                'hour_std': hour_std,
                'amount_std': amount_std,
                'amount_mean': amount_mean,
                'send_receive_ratio': send_receive_ratio,
                'tx_frequency': tx_frequency,
                'total_txs': len(all_txs)
            })
        
        self.features_df = pd.DataFrame(features_list)
        self.features_df.to_csv('analysis/wallet_features.csv', index=False)
        
        print(f"Extracted features for {len(self.features_df)} wallets")
        return self.features_df
    
    def cluster_wallets(self):
        """
        Use DBSCAN clustering to identify wallets that may belong to same entity
        """
        
        # Prepare feature matrix
        feature_cols = [
            'counterparty_diversity', 'hour_std', 'amount_std',
            'send_receive_ratio', 'tx_frequency'
        ]
        
        X = self.features_df[feature_cols].fillna(0)
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # DBSCAN clustering
        clustering = DBSCAN(eps=0.8, min_samples=2)
        self.features_df['cluster'] = clustering.fit_predict(X_scaled)
        
        # Analyze clusters
        n_clusters = len(set(self.features_df['cluster'])) - (1 if -1 in self.features_df['cluster'] else 0)
        n_noise = list(self.features_df['cluster']).count(-1)
        
        print(f"\n=== Clustering Results ===")
        print(f"Clusters identified: {n_clusters}")
        print(f"Singleton wallets: {n_noise}")
        
        # Show clusters
        for cluster_id in sorted(self.features_df['cluster'].unique()):
            if cluster_id == -1:
                continue
            cluster_wallets = self.features_df[self.features_df['cluster'] == cluster_id]
            print(f"\nCluster {cluster_id}: {len(cluster_wallets)} wallets")
            print(cluster_wallets[['address', 'counterparty_diversity', 'tx_frequency']].head())
        
        return self.features_df
    
    def classify_behavior_profiles(self):
        """
        Classify wallets into behavior profiles:
        - Settlement: high frequency, consistent amounts, many counterparties
        - DeFi Active: moderate frequency, variable amounts, few counterparties
        - Bridge: low frequency, large amounts, specific patterns
        """
        
        def classify(row):
            if row['tx_frequency'] > 5 and row['counterparty_diversity'] > 10:
                return 'Settlement'
            elif row['send_receive_ratio'] < 0.2 and row['amount_mean'] > 500000:
                return 'DeFi Supply'
            elif row['unique_receivers'] < 3 and row['amount_mean'] > 300000:
                return 'Bridge User'
            else:
                return 'Mixed Activity'
        
        self.features_df['behavior_profile'] = self.features_df.apply(classify, axis=1)
        
        print("\n=== Behavior Profiles ===")
        print(self.features_df['behavior_profile'].value_counts())
        
        return self.features_df
    
    def risk_scoring(self):
        """
        Assign risk scores based on behavioral anomalies
        Clean: 0-3, Medium: 4-6, Higher: 7+
        """
        
        def calculate_risk(row):
            risk = 0
            
            # Low counterparty diversity (potential single entity)
            if row['counterparty_diversity'] < 3:
                risk += 2
            
            # Very regular timing (bot-like)
            if row['hour_std'] < 1:
                risk += 2
            
            # Extreme send/receive imbalance
            if row['send_receive_ratio'] < 0.1 or row['send_receive_ratio'] > 10:
                risk += 1
            
            # Part of a cluster
            if row['cluster'] != -1:
                risk += 2
            
            # Very high frequency (potential wash trading)
            if row['tx_frequency'] > 20:
                risk += 2
            
            return risk
        
        self.features_df['risk_score'] = self.features_df.apply(calculate_risk, axis=1)
        
        def risk_label(score):
            if score <= 3:
                return 'Clean'
            elif score <= 6:
                return 'Medium'
            else:
                return 'Higher'
        
        self.features_df['risk_label'] = self.features_df['risk_score'].apply(risk_label)
        
        print("\n=== Risk Distribution ===")
        print(self.features_df['risk_label'].value_counts())
        
        # Save final results
        self.features_df.to_csv('analysis/sybil_analysis_results.csv', index=False)
        
        return self.features_df
    
    def generate_summary_table(self):
        """Generate summary table for report"""
        
        summary = self.features_df[[
            'address', 'behavior_profile', 'risk_label', 'cluster',
            'counterparty_diversity', 'tx_frequency', 'amount_mean'
        ]].copy()
        
        summary = summary.sort_values('amount_mean', ascending=False)
        summary['amount_mean'] = summary['amount_mean'].apply(lambda x: f"${x:,.0f}")
        summary['tx_frequency'] = summary['tx_frequency'].round(2)
        
        # Shorten addresses for display
        summary['address_short'] = summary['address'].apply(lambda x: x[:6] + '...' + x[-4:])
        
        summary_display = summary[[
            'address_short', 'behavior_profile', 'risk_label', 
            'counterparty_diversity', 'tx_frequency', 'amount_mean'
        ]]
        
        summary_display.to_csv('analysis/sybil_summary_table.csv', index=False)
        
        print("\n=== Summary Table (Top 20) ===")
        print(summary_display.head(20).to_string(index=False))
        
        return summary_display

if __name__ == "__main__":
    # Load data
    institutional_wallets = pd.read_csv('analysis/institutional_wallets.csv')
    transfers = pd.read_csv('data/large_usdc_transfers.csv')
    
    # Run sybil detection
    detector = SybilDetector(institutional_wallets, transfers)
    detector.extract_features()
    detector.cluster_wallets()
    detector.classify_behavior_profiles()
    detector.risk_scoring()
    detector.generate_summary_table()
