"""
Data Collection using Dune Analytics API
More reliable and powerful for institutional-scale analysis
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from config import DUNE_API_KEY, MIN_TRANSFER_AMOUNT, DAYS_TO_ANALYZE, USDC_CONTRACT

class DuneDataCollector:
    def __init__(self):
        self.api_key = DUNE_API_KEY
        self.base_url = "https://api.dune.com/api/v1"
        self.headers = {"X-Dune-API-Key": self.api_key}
        
    def execute_query(self, query_sql):
        """Execute a SQL query on Dune"""
        
        # Create query
        endpoint = f"{self.base_url}/query"
        payload = {
            "query_sql": query_sql,
            "is_private": False
        }
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            query_id = response.json()['query_id']
            print(f"Query created: {query_id}")
            
            # Execute query
            exec_endpoint = f"{self.base_url}/query/{query_id}/execute"
            exec_response = requests.post(exec_endpoint, headers=self.headers)
            
            if exec_response.status_code == 200:
                execution_id = exec_response.json()['execution_id']
                print(f"Execution started: {execution_id}")
                
                # Poll for results
                return self.poll_results(execution_id)
            else:
                print(f"Execution failed: {exec_response.text}")
                return None
        else:
            print(f"Query creation failed: {response.text}")
            return None
    
    def poll_results(self, execution_id, max_wait=300):
        """Poll for query results"""
        
        endpoint = f"{self.base_url}/execution/{execution_id}/results"
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(endpoint, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['state'] == 'QUERY_STATE_COMPLETED':
                    print("Query completed!")
                    return pd.DataFrame(data['result']['rows'])
                elif data['state'] == 'QUERY_STATE_FAILED':
                    print(f"Query failed: {data.get('error', 'Unknown error')}")
                    return None
                else:
                    print(f"Query state: {data['state']} ... waiting")
                    time.sleep(5)
            else:
                print(f"Poll failed: {response.text}")
                time.sleep(5)
        
        print("Query timeout")
        return None
    
    def collect_large_transfers(self):
        """Collect large USDC transfers on Base"""
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=DAYS_TO_ANALYZE)
        
        # Dune SQL query for Base USDC transfers
        query = f"""
        SELECT
            block_time,
            block_number,
            tx_hash,
            "from" as from_address,
            "to" as to_address,
            value / 1e6 as amount_usd,
            tx_index
        FROM base.transactions
        CROSS JOIN UNNEST(traces) AS t(trace)
        WHERE contract_address = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
            AND block_time >= TIMESTAMP '{start_date.strftime('%Y-%m-%d')}'
            AND block_time < TIMESTAMP '{end_date.strftime('%Y-%m-%d')}'
            AND trace.type = 'call'
            AND trace.call_type = 'call'
            AND bytearray_substring(trace.input, 1, 4) = 0xa9059cbb  -- transfer function
            AND value / 1e6 >= {MIN_TRANSFER_AMOUNT}
        ORDER BY block_time DESC
        LIMIT 100000
        """
        
        # Simplified approach: Use direct table query
        # Since Dune free tier has limitations, let's create a more efficient query
        
        simplified_query = f"""
        WITH usdc_transfers AS (
            SELECT
                block_time,
                block_number,
                tx_hash,
                "from",
                "to",
                value / 1e6 AS amount_usd
            FROM erc20_base.evt_Transfer
            WHERE contract_address = LOWER('{USDC_CONTRACT}')
                AND block_time >= CURRENT_DATE - INTERVAL '{DAYS_TO_ANALYZE}' DAY
                AND value / 1e6 >= {MIN_TRANSFER_AMOUNT}
        )
        SELECT *
        FROM usdc_transfers
        ORDER BY block_time DESC
        LIMIT 50000
        """
        
        print(f"Querying Dune for Base USDC transfers...")
        print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Minimum amount: ${MIN_TRANSFER_AMOUNT:,}")
        
        df = self.execute_query(simplified_query)
        
        if df is not None and len(df) > 0:
            # Clean and format data
            df['from'] = df['from'].str.lower()
            df['to'] = df['to'].str.lower()
            df['timestamp'] = pd.to_datetime(df['block_time']).astype(int) // 10**9
            df['datetime'] = pd.to_datetime(df['block_time'])
            df['hash'] = df['tx_hash']
            df['block'] = df['block_number']
            
            # Save
            df.to_csv('data/large_usdc_transfers.csv', index=False)
            
            print(f"\n✓ Collected {len(df)} large transfers")
            print(f"Total volume: ${df['amount_usd'].sum():,.2f}")
            print(f"Average transfer: ${df['amount_usd'].mean():,.2f}")
            print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
            
            return df
        else:
            print("❌ No data retrieved from Dune")
            return None

if __name__ == "__main__":
    collector = DuneDataCollector()
    df = collector.collect_large_transfers()
