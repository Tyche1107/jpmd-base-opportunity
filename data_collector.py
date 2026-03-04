"""
Data Collection Script for Base USDC Transfers
Fetches large USDC transfers (>$100k) from the past 90 days on Base
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import json
from config import *
from tqdm import tqdm

class BaseDataCollector:
    def __init__(self):
        self.api_key = BASESCAN_API_KEY
        self.api_url = BASESCAN_API_URL
        self.usdc_contract = USDC_CONTRACT
        self.session = requests.Session()
        
    def get_current_block(self):
        """Get the current block number on Base"""
        params = {
            'chainid': BASE_CHAIN_ID,
            'module': 'proxy',
            'action': 'eth_blockNumber',
            'apikey': self.api_key
        }
        response = self.session.get(self.api_url, params=params)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        data = response.json()
        return int(data['result'], 16)
    
    def get_block_by_timestamp(self, timestamp):
        """Get block number by timestamp"""
        params = {
            'chainid': BASE_CHAIN_ID,
            'module': 'block',
            'action': 'getblocknobytime',
            'timestamp': int(timestamp),
            'closest': 'before',
            'apikey': self.api_key
        }
        response = self.session.get(self.api_url, params=params)
        data = response.json()
        if data['status'] == '1':
            return int(data['result'])
        return None
    
    def get_usdc_transfers(self, start_block, end_block, batch_size=10000):
        """
        Fetch USDC transfer events
        Transfer event signature: 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
        """
        all_transfers = []
        current_start = start_block
        
        print(f"Fetching USDC transfers from block {start_block} to {end_block}...")
        
        with tqdm(total=end_block-start_block) as pbar:
            while current_start < end_block:
                current_end = min(current_start + batch_size, end_block)
                
                params = {
                    'chainid': BASE_CHAIN_ID,
                    'module': 'logs',
                    'action': 'getLogs',
                    'address': self.usdc_contract,
                    'fromBlock': current_start,
                    'toBlock': current_end,
                    'topic0': '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
                    'apikey': self.api_key
                }
                
                try:
                    response = self.session.get(self.api_url, params=params)
                    data = response.json()
                    
                    if data['status'] == '1' and data['result']:
                        all_transfers.extend(data['result'])
                    
                    pbar.update(batch_size)
                    current_start = current_end + 1
                    time.sleep(0.2)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error fetching blocks {current_start}-{current_end}: {e}")
                    time.sleep(1)
        
        return all_transfers
    
    def parse_transfer(self, log):
        """Parse transfer log to extract from, to, and amount"""
        # Topics: [event_sig, from_address, to_address]
        # Data: amount
        
        from_addr = '0x' + log['topics'][1][-40:]
        to_addr = '0x' + log['topics'][2][-40:]
        amount_hex = log['data']
        amount = int(amount_hex, 16) / 1e6  # USDC has 6 decimals
        
        return {
            'hash': log['transactionHash'],
            'block': int(log['blockNumber'], 16),
            'timestamp': int(log['timeStamp'], 16),
            'from': from_addr.lower(),
            'to': to_addr.lower(),
            'amount_usd': amount
        }
    
    def collect_large_transfers(self):
        """Main collection function"""
        # Calculate block range for past 90 days
        end_timestamp = int(datetime.now().timestamp())
        start_timestamp = int((datetime.now() - timedelta(days=DAYS_TO_ANALYZE)).timestamp())
        
        print("Getting block numbers...")
        end_block = self.get_current_block()
        start_block = self.get_block_by_timestamp(start_timestamp)
        
        if not start_block:
            # Fallback: approximate (Base ~2 second blocks)
            blocks_in_90_days = DAYS_TO_ANALYZE * 24 * 60 * 60 // 2
            start_block = end_block - blocks_in_90_days
        
        print(f"Analyzing blocks {start_block} to {end_block}")
        print(f"Date range: {datetime.fromtimestamp(start_timestamp)} to {datetime.fromtimestamp(end_timestamp)}")
        
        # Fetch transfers
        raw_transfers = self.get_usdc_transfers(start_block, end_block)
        
        print(f"Processing {len(raw_transfers)} transfer events...")
        
        # Parse transfers
        transfers = []
        for log in tqdm(raw_transfers):
            try:
                transfer = self.parse_transfer(log)
                if transfer['amount_usd'] >= MIN_TRANSFER_AMOUNT:
                    transfers.append(transfer)
            except Exception as e:
                print(f"Error parsing log: {e}")
                continue
        
        df = pd.DataFrame(transfers)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Save raw data
        output_file = 'data/large_usdc_transfers.csv'
        df.to_csv(output_file, index=False)
        print(f"\nSaved {len(df)} large transfers (>$100k) to {output_file}")
        print(f"Total volume: ${df['amount_usd'].sum():,.2f}")
        print(f"Average transfer: ${df['amount_usd'].mean():,.2f}")
        
        return df

if __name__ == "__main__":
    collector = BaseDataCollector()
    df = collector.collect_large_transfers()
