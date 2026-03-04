"""
Generate realistic synthetic data for analysis demonstration
Based on actual Base USDC flow patterns from public reports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from config import *

# Real protocol addresses on Base
REAL_ADDRESSES = {
    'morpho': [
        '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'.lower(),  # Morpho Blue
        '0x23055618898e202386e6c13955a58D3C68200BFB'.lower(),  # Morpho Vault
    ],
    'aave_horizon': [
        '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5'.lower(),  # Aave Pool
    ],
    'bridges': [
        '0x49048044D57e1C92A77f79988d21Fa8fAF74E97e'.lower(),  # Base Bridge
        '0x4200000000000000000000000000000000000010'.lower(),  # Standard Bridge
        '0x3154Cf16ccdb4C6d922629664174b904d80F2C35'.lower(),  # LayerZero
        '0x1a44076050125825900e736c501f859c50fE728c'.lower(),  # Stargate
    ],
    'exchanges': [
        '0x3c3a81e81dc49A522A592e7622A7E711c06bf354'.lower(),  # Coinbase
        '0xA090e606E30bD747d4E6245a1517EbE430F0057e'.lower(),  # Coinbase 2
    ],
}

def generate_institutional_wallets(n=100):
    """Generate realistic institutional wallet addresses"""
    wallets = []
    for i in range(n):
        # Generate random Ethereum address
        addr = '0x' + ''.join(random.choices('0123456789abcdef', k=40))
        wallets.append(addr.lower())
    return wallets

def generate_transfers(n_transfers=5000):
    """
    Generate realistic transfer data based on known Base USDC patterns:
    - DeFi (Morpho + Aave): ~60% of volume
    - Bridges: ~20% of volume
    - Exchanges: ~10% of volume
    - P2P: ~10% of volume
    """
    
    institutional_wallets = generate_institutional_wallets(100)
    
    # Distribution targets (volume-weighted)
    volume_distribution = {
        'morpho': 0.45,  # 45% to Morpho (higher lending yield)
        'aave_horizon': 0.12,  # 12% to Aave Horizon (permissioned, newer)
        'bridges': 0.22,  # 22% to bridges (cross-chain arbitrage)
        'exchanges': 0.11,  # 11% to exchanges (CEX deposits)
        'p2p': 0.10,  # 10% to P2P (direct transfers)
    }
    
    transfers = []
    
    start_timestamp = int((datetime.now() - timedelta(days=DAYS_TO_ANALYZE)).timestamp())
    end_timestamp = int(datetime.now().timestamp())
    
    base_block = 10000000
    
    for i in range(n_transfers):
        # Random category (volume-weighted)
        category = np.random.choice(
            list(volume_distribution.keys()),
            p=list(volume_distribution.values())
        )
        
        # Select destination based on category
        if category in REAL_ADDRESSES:
            to_addr = random.choice(REAL_ADDRESSES[category])
        else:  # p2p
            to_addr = random.choice(institutional_wallets)
        
        # From address (institutional wallet)
        from_addr = random.choice(institutional_wallets)
        
        # Amount (log-normal distribution, realistic for institutional transfers)
        # Mean ~500k, with tail up to 10M+
        if category == 'morpho':
            # Larger deposits to Morpho (seeking yield)
            amount_mean = 800000
            amount_std = 1000000
        elif category == 'aave_horizon':
            amount_mean = 600000
            amount_std = 800000
        elif category == 'bridges':
            # Very large bridge transfers (cross-chain moves)
            amount_mean = 1200000
            amount_std = 1500000
        elif category == 'exchanges':
            amount_mean = 500000
            amount_std = 600000
        else:  # p2p
            # Smaller P2P transfers
            amount_mean = 300000
            amount_std = 400000
        
        amount = max(MIN_TRANSFER_AMOUNT, np.random.lognormal(
            mean=np.log(amount_mean),
            sigma=0.8
        ))
        
        # Random timestamp within range
        timestamp = random.randint(start_timestamp, end_timestamp)
        block = base_block + (timestamp - start_timestamp) // 2  # ~2 second blocks
        
        # Random hash
        tx_hash = '0x' + ''.join(random.choices('0123456789abcdef', k=64))
        
        transfers.append({
            'hash': tx_hash,
            'block': block,
            'timestamp': timestamp,
            'from': from_addr,
            'to': to_addr,
            'amount_usd': amount,
            'datetime': datetime.fromtimestamp(timestamp)
        })
    
    df = pd.DataFrame(transfers)
    
    print(f"Generated {len(df)} synthetic transfers")
    print(f"Total volume: ${df['amount_usd'].sum():,.2f}")
    print(f"Average transfer: ${df['amount_usd'].mean():,.2f}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    
    # Distribution breakdown
    print("\nExpected distribution:")
    for category, pct in volume_distribution.items():
        print(f"  {category}: {pct*100:.1f}%")
    
    df.to_csv('data/large_usdc_transfers.csv', index=False)
    print("\n✓ Saved to data/large_usdc_transfers.csv")
    
    return df

if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING SYNTHETIC DATA FOR DEMONSTRATION")
    print("=" * 80)
    print("\nNote: This uses realistic patterns based on public Base Network reports.")
    print("For production: replace with actual Basescan/Dune API data.\n")
    
    df = generate_transfers(n_transfers=8000)  # Realistic 90-day institutional volume
