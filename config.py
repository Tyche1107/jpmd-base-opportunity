"""
Configuration file for JPMD Base Analysis
"""

# API Keys
BASESCAN_API_KEY = "413E91H5PDDZYTVRY8AMK4D7FVTE65Z989"
DUNE_API_KEY = "tTVICcVIhr9yZjdfg2IXxkB5b65T6tks"

# Base Chain Configuration
BASE_CHAIN_ID = 8453
BASESCAN_API_URL = "https://api.basescan.org/v2/api"

# USDC Contract on Base
USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Analysis Parameters
DAYS_TO_ANALYZE = 90
MIN_TRANSFER_AMOUNT = 100000  # $100k minimum

# Known Protocol Addresses (Base)
KNOWN_PROTOCOLS = {
    # Morpho
    "morpho": [
        "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb",  # Morpho Blue
        "0x23055618898e202386e6c13955a58D3C68200BFB",  # Morpho Vault 1
    ],
    
    # Aave Horizon (permissioned)
    "aave_horizon": [
        "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5",  # Aave Pool
    ],
    
    # Bridge Contracts
    "bridges": [
        "0x49048044D57e1C92A77f79988d21Fa8fAF74E97e",  # Base Bridge
        "0x4200000000000000000000000000000000000010",  # Standard Bridge
        "0x3154Cf16ccdb4C6d922629664174b904d80F2C35",  # LayerZero Endpoint
        "0x1a44076050125825900e736c501f859c50fE728c",  # Stargate Router
    ],
    
    # Major Exchanges (deposit addresses - will be identified by pattern)
    "exchanges": [
        "0x40ec5B33f54e0E8A33A975908C5BA1c14e5BbbDf",  # Polygon: ERC20 Bridge
        "0x3c3a81e81dc49A522A592e7622A7E711c06bf354",  # Coinbase 1
        "0xA090e606E30bD747d4E6245a1517EbE430F0057e",  # Coinbase 2
    ],
}

# Flatten all known protocol addresses
ALL_KNOWN_ADDRESSES = set()
for protocol_type, addresses in KNOWN_PROTOCOLS.items():
    ALL_KNOWN_ADDRESSES.update([addr.lower() for addr in addresses])

# Exchange patterns (will be identified by high frequency incoming transfers)
EXCHANGE_INDICATORS = {
    "min_unique_senders": 100,  # Exchanges receive from many unique addresses
    "min_daily_transfers": 50,  # High frequency
}
