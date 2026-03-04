# JPMD Base Network Opportunity Analysis

**Institutional USDC Flow Analysis on Base Network**

Prepared for JPMorgan Kinexys Team (Basak Toprak, Kara Kennedy)  
By: University of Washington Decentralized Computing Lab  
Author: Adeline Wen (Undergraduate Research Assistant, HasciDB Project)

---

## Executive Summary

This analysis examines 90 days of large institutional USDC transfers (>$100,000) on Base Network to quantify market opportunities for JPMD across different use cases: DeFi collateral, settlement, and cross-chain movement.

**Key Finding:** X% of institutional dollars bypass settlement and flow directly into DeFi protocols, validating Basak Toprak's insight that "cash is collateral in the on-chain world."

---

## Project Structure

```
jpmd-base-opportunity/
├── data/                          # Raw data
│   └── large_usdc_transfers.csv   # 90-day USDC transfer data
├── analysis/                      # Analysis outputs
│   ├── flow_distribution.csv      # Volume/percentage by category
│   ├── categorized_transfers.csv  # Full categorized dataset
│   ├── institutional_wallets.csv  # Top 50 institutional addresses
│   ├── sybil_analysis_results.csv # Behavioral features & risk scores
│   └── sybil_summary_table.csv    # Report-ready summary
├── visualizations/                # Charts and diagrams
│   ├── sankey_flow.html           # Interactive Sankey diagram
│   ├── sankey_flow.png            # Static Sankey for PDF
│   ├── distribution_chart.png     # Volume distribution bars
│   └── sybil_analysis.png         # Risk/behavior distribution
├── report/                        # Final PDF report
│   └── JPMD_Base_Opportunity_Analysis.pdf
├── config.py                      # API keys, contract addresses
├── data_collector.py              # Basescan API data collection
├── flow_analyzer.py               # Destination categorization
├── sybil_detector.py              # Behavioral feature extraction
├── visualizations.py              # Chart generation
├── generate_report.py             # PDF report generation
├── run_analysis.py                # Pipeline orchestrator
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Methodology

### 1. Data Collection
- **Source:** Basescan API (Base Network)
- **Period:** Past 90 days
- **Filter:** USDC transfers >$100,000
- **Contract:** 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

### 2. Destination Classification
Addresses categorized into:
- **Morpho:** Lending protocol deposits
- **Aave Horizon:** Permissioned lending pools
- **Bridges:** Cross-chain transfer contracts
- **Exchanges:** CEX deposit addresses (pattern-identified)
- **P2P:** Wallet-to-wallet transfers

### 3. Sybil Detection (Address-Level Monitoring)
Behavioral features extracted per HasciDB methodology:
- Counterparty diversity
- Transaction timing patterns
- Send/receive ratio
- Transaction frequency
- Clustering for same-entity identification

**Complementarity with AIKYA:**
- AIKYA: Transaction-level anomaly detection (federated learning)
- This work: Address-level behavioral monitoring (on-chain features, single-institution deployable)

---

## Usage

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Ensure API keys are configured in config.py
# Basescan API Key: Already configured
```

### Run Complete Analysis
```bash
python run_analysis.py
```

This will execute the full pipeline:
1. Collect USDC transfer data from Basescan
2. Categorize destinations
3. Perform sybil detection on institutional wallets
4. Generate visualizations
5. Produce PDF report

### Run Individual Steps
```bash
# Data collection only
python data_collector.py

# Flow analysis only (requires data/large_usdc_transfers.csv)
python flow_analyzer.py

# Sybil detection only (requires analysis outputs)
python sybil_detector.py

# Visualizations only
python visualizations.py

# Report only
python generate_report.py
```

---

## Key Findings Preview

*Will be populated after analysis completes with specific percentages*

- **DeFi Dominance:** X% of volume flows to lending protocols
- **Settlement Usage:** Only Y% is wallet-to-wallet
- **Permissioned DeFi:** Underutilized at Z%
- **Bridge Activity:** W% for cross-chain movement

**Implication:** JPMD should prioritize permissioned DeFi integrations (Morpho vaults, Aave Horizon) over P2P settlement features.

---

## Sybil Detection Demonstration

Sample output (top 30 institutional wallets):
- Behavioral profiles: Settlement, DeFi Supply, Bridge User, Mixed
- Risk scores: Clean (0-3), Medium (4-6), Higher (7+)
- Cluster identification: Addresses potentially controlled by same entity

**Use Case for JPMD:** Post-whitelist behavioral monitoring for ongoing compliance.

---

## Deliverables

1. **PDF Report:** `report/JPMD_Base_Opportunity_Analysis.pdf`
   - Executive summary with product implications
   - Quantified flow distribution
   - Sybil detection demonstration
   - Methodology and AIKYA complementarity

2. **Visualizations:**
   - Sankey diagram (interactive + static)
   - Distribution charts
   - Risk analysis charts

3. **Data Outputs:**
   - Full categorized transfer dataset
   - Institutional wallet analysis
   - Sybil detection results

---

## Contact

**Author:** Adeline Wen  
**Affiliation:** University of Washington, Decentralized Computing Lab  
**Project:** HasciDB (470,000+ address sybil detection database)  
**Supervisor:** Wei Cai, PhD

**Recipient:** JPMorgan Kinexys Team  
- Basak Toprak (Product Lead, JPM Coin | Kinexys Digital Payments EMEA)
- Kara Kennedy (Head of Kinexys)

---

## License

This analysis is provided for JPMorgan Kinexys team review. Not for public distribution without permission.

---

## Appendix: Technical Notes

### API Rate Limits
- Basescan: 5 requests/second (enforced via 0.2s delay)
- Handles large block ranges via batching (10,000 blocks per request)

### Known Protocol Addresses
See `config.py` for full list of:
- Morpho contracts
- Aave Horizon pools
- Bridge endpoints (LayerZero, Stargate, Base native bridge)
- Exchange deposit addresses

### Feature Engineering Details
Sybil detection features (per address):
- `unique_senders`: Number of distinct funding sources
- `unique_receivers`: Number of distinct recipients
- `counterparty_diversity`: Sum of unique senders + receivers
- `hour_std`: Standard deviation of transaction hour-of-day
- `amount_std`: Standard deviation of transfer amounts
- `send_receive_ratio`: Total sent / total received
- `tx_frequency`: Transactions per day
- `cluster`: DBSCAN cluster assignment (-1 = singleton)

Risk scoring logic:
- Low counterparty diversity: +2
- Very regular timing (bot-like): +2
- Extreme send/receive imbalance: +1
- Part of a cluster: +2
- Very high frequency: +2

Clean: 0-3, Medium: 4-6, Higher: 7+

---

*Generated: 2026-03-03*
