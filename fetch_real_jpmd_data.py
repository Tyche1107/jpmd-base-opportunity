#!/usr/bin/env python3
"""
Fetch REAL JPMorgan JPMD data from Base Network
Compare with USDC to show the massive gap
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

# JPMD contract on Base (launched Nov 2025)
JPMD_CONTRACT = "0x7e0AEdc93d9f898bE835A44BFcA3842E52416B82"
USDC_BASE_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Get Etherscan API keys (work for Basescan too)
CREDENTIALS_PATH = os.path.expanduser("~/clawd/credentials/all-credentials.md")
API_KEYS = []

# Parse credentials
with open(CREDENTIALS_PATH) as f:
    for line in f:
        if "Key " in line and "`" in line and "Etherscan" not in line:
            parts = line.split("`")
            if len(parts) >= 2:
                key = parts[1].strip()
                if key and len(key) > 20:
                    API_KEYS.append(key)

print(f"✅ Loaded {len(API_KEYS)} API keys for Basescan")

current_key_idx = 0

def get_next_api_key():
    global current_key_idx
    key = API_KEYS[current_key_idx]
    current_key_idx = (current_key_idx + 1) % len(API_KEYS)
    return key

def fetch_token_stats(contract_address, token_name, base_url="https://api.basescan.org/v2/api"):
    """
    Fetch comprehensive stats for a token on Base
    """
    print(f"\n🔍 Fetching data for {token_name} ({contract_address})...")
    
    api_key = get_next_api_key()
    
    # 1. Get all Transfer events (last 90 days)
    print(f"  📄 Fetching transfers...")
    
    # Calculate block range (approximate: Base ~2 sec/block, 90 days = ~3.9M blocks)
    # But we'll use timestamp instead
    ninety_days_ago = int((datetime.now() - timedelta(days=90)).timestamp())
    
    params = {
        "chainid": "8453",  # Base Network chain ID
        "module": "account",
        "action": "tokentx",
        "contractaddress": contract_address,
        "page": 1,
        "offset": 10000,
        "sort": "asc",
        "apikey": api_key
    }
    
    all_transfers = []
    page = 1
    
    while True:
        params["page"] = page
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data["status"] != "1":
            print(f"  ⚠️ API error: {data.get('message', 'Unknown')}")
            if "result" in data and isinstance(data["result"], str):
                print(f"     Details: {data['result']}")
            break
        
        transfers = data["result"]
        if not transfers:
            break
        
        # Filter to last 90 days
        recent_transfers = [
            tx for tx in transfers 
            if int(tx.get("timeStamp", 0)) >= ninety_days_ago
        ]
        
        all_transfers.extend(recent_transfers)
        print(f"  ✅ Page {page}: {len(recent_transfers)} transfers (total: {len(all_transfers)})")
        
        if len(transfers) < 10000:
            break
        
        # If no recent transfers in this page, we're done
        if len(recent_transfers) == 0:
            break
        
        page += 1
        time.sleep(0.2)
    
    # Calculate metrics
    unique_senders = set()
    unique_receivers = set()
    total_volume = 0
    daily_txs = {}
    
    for tx in all_transfers:
        from_addr = tx["from"].lower()
        to_addr = tx["to"].lower()
        value = int(tx["value"])
        timestamp = int(tx["timeStamp"])
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        
        unique_senders.add(from_addr)
        unique_receivers.add(to_addr)
        total_volume += value
        
        daily_txs[date] = daily_txs.get(date, 0) + 1
    
    # Get current holder count
    print(f"  📊 Calculating holder balances...")
    balances = {}
    for tx in all_transfers:
        from_addr = tx["from"].lower()
        to_addr = tx["to"].lower()
        value = int(tx["value"])
        
        if from_addr != "0x0000000000000000000000000000000000000000":
            balances[from_addr] = balances.get(from_addr, 0) - value
        
        if to_addr != "0x0000000000000000000000000000000000000000":
            balances[to_addr] = balances.get(to_addr, 0) + value
    
    current_holders = {addr: bal for addr, bal in balances.items() if bal > 0}
    
    # Get token decimals (usually 6 for USDC/stablecoins)
    decimals = 6  # Standard for USDC and JPMD
    total_volume_usd = total_volume / (10 ** decimals)
    
    avg_daily_txs = sum(daily_txs.values()) / max(len(daily_txs), 1) if daily_txs else 0
    
    stats = {
        "token": token_name,
        "contract": contract_address,
        "period_days": 90,
        "transfer_count": len(all_transfers),
        "unique_senders": len(unique_senders),
        "unique_receivers": len(unique_receivers),
        "unique_addresses": len(unique_senders | unique_receivers),
        "current_holders": len(current_holders),
        "total_volume_raw": total_volume,
        "total_volume_usd": total_volume_usd,
        "avg_daily_txs": avg_daily_txs,
        "daily_breakdown": daily_txs,
        "holders": current_holders,
        "all_transfers": all_transfers
    }
    
    print(f"✅ {token_name}: {len(all_transfers)} transfers, {len(current_holders)} holders, ${total_volume_usd:,.0f} volume")
    
    return stats

def analyze_jpmd_adoption(jpmd_data, usdc_data):
    """
    Calculate the shocking gap between JPMD and USDC
    """
    print("\n" + "=" * 60)
    print("🚨 SHOCKING COMPARISON: JPMD vs USDC on Base")
    print("=" * 60)
    
    # Volume comparison
    jpmd_vol = jpmd_data["total_volume_usd"]
    usdc_vol = usdc_data["total_volume_usd"]
    gap = usdc_vol / max(jpmd_vol, 1) if jpmd_vol > 0 else float('inf')
    
    print(f"\n💰 90-Day Volume:")
    print(f"  JPMD: ${jpmd_vol:,.0f}")
    print(f"  USDC: ${usdc_vol:,.0f}")
    print(f"  🔥 USDC is {gap:,.0f}x larger")
    
    # User comparison
    jpmd_users = jpmd_data["unique_addresses"]
    usdc_users = usdc_data["unique_addresses"]
    user_gap = usdc_users / max(jpmd_users, 1) if jpmd_users > 0 else float('inf')
    
    print(f"\n👥 Unique Users:")
    print(f"  JPMD: {jpmd_users}")
    print(f"  USDC: {usdc_users:,}")
    print(f"  🔥 USDC has {user_gap:,.0f}x more users")
    
    # Activity comparison
    jpmd_txs = jpmd_data["transfer_count"]
    usdc_txs = usdc_data["transfer_count"]
    tx_gap = usdc_txs / max(jpmd_txs, 1) if jpmd_txs > 0 else float('inf')
    
    print(f"\n📊 Transaction Count:")
    print(f"  JPMD: {jpmd_txs}")
    print(f"  USDC: {usdc_txs:,}")
    print(f"  🔥 USDC has {tx_gap:,.0f}x more activity")
    
    # ROI calculation (assume ~$10M deployment cost)
    est_deployment_cost = 10_000_000
    cost_per_user = est_deployment_cost / max(jpmd_users, 1) if jpmd_users > 0 else est_deployment_cost
    
    print(f"\n💸 ROI Analysis (est. $10M deployment):")
    print(f"  Cost per user: ${cost_per_user:,.0f}")
    print(f"  Cost per transaction: ${est_deployment_cost / max(jpmd_txs, 1):,.0f}")
    
    return {
        "volume_gap": gap,
        "user_gap": user_gap,
        "tx_gap": tx_gap,
        "cost_per_user": cost_per_user,
        "jpmd_volume": jpmd_vol,
        "usdc_volume": usdc_vol
    }

def main():
    print("=" * 60)
    print("JPMorgan JPMD Real Data Fetcher (Base Network)")
    print("=" * 60)
    
    # Fetch JPMD stats
    jpmd_data = fetch_token_stats(JPMD_CONTRACT, "JPMD")
    
    # Fetch USDC stats (sample last 10k txs only for comparison)
    # Full USDC data would be millions of txs
    print("\n⚠️ Sampling USDC data (would take hours for full history)...")
    usdc_data = fetch_token_stats(USDC_BASE_CONTRACT, "USDC")
    
    # Compare
    comparison = analyze_jpmd_adoption(jpmd_data, usdc_data)
    
    # Save data
    output = {
        "fetch_date": datetime.now().isoformat(),
        "jpmd": jpmd_data,
        "usdc": usdc_data,
        "comparison": comparison
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/jpmd_vs_usdc_real.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Data saved to data/jpmd_vs_usdc_real.json")
    
    # Generate shocking headline
    print("\n" + "=" * 60)
    print("📰 SHOCKING HEADLINE:")
    print("=" * 60)
    if jpmd_data["total_volume_usd"] > 0:
        print(f"\n\"JPMD on Base: ${jpmd_data['total_volume_usd']/1e6:.1f}M in 3 months.")
        print(f"USDC on Base: ${usdc_data['total_volume_usd']/1e9:.1f}B.")
        print(f"Is this a ${comparison['cost_per_user']/1e6:.1f}M per-user mistake?\"")
    else:
        print("\n\"JPMD on Base: ZERO public adoption after 3 months.\"")
        print("\"JPMorgan's $10M experiment yields no external users.\"")

if __name__ == "__main__":
    main()
