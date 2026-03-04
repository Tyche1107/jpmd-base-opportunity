# Executive Summary: JPMD Base Opportunity Analysis

**For:** JPMorgan Kinexys Team (Basak Toprak, Kara Kennedy)  
**From:** University of Washington Decentralized Computing Lab  
**Date:** March 3, 2026

---

## Key Finding

**57% of institutional USDC on Base flows directly into DeFi protocols** (Morpho + Aave + Bridges), not settlement.

## Why This Matters for JPMD

Basak Toprak stated: "Cash is collateral in the on-chain world." Our analysis quantifies exactly where that collateral goes on Base Network — JPMD's addressable markets, ranked by current volume:

### 1. **DeFi Collateral** (57% of volume)
- **Morpho**: 44% ($3.78B over 90 days)
- **Aave Horizon**: 10% ($821M)
- **Bridges**: 36% ($3.06B) — cross-chain arbitrage/collateral

**Opportunity:** Permissioned lending integration is JPMD's whitespace. Aave Horizon (permissioned) is underutilized despite compliance advantages.

### 2. **Settlement** (Only 4% of volume)
- **P2P wallet transfers**: $356M
- Smallest category by far

**Implication:** Settlement is NOT the primary use case. Institutions want yield + compliance, not just payment rails.

### 3. **Exchange Deposits** (6% of volume)
- $555M to CEX wallets
- Lower priority (well-served by existing stablecoins)

---

## Strategic Implications

### Priority 1: Permissioned DeFi Integration
- Partner with Morpho for permissioned vaults
- Integrate with Aave Horizon institutional pools
- **Competitive edge:** Interest-bearing + compliance (vs non-interest-bearing stablecoins)

### Priority 2: Bridge Infrastructure
- High cross-chain volume indicates multi-network demand
- JPMD's multi-chain strategy should prioritize high-bridge-volume networks

### Priority 3: Behavioral Monitoring
- Demonstrated sybil detection methodology (50 institutional wallets analyzed)
- **Complements AIKYA:** Address-level monitoring + transaction-level anomaly detection
- Single-institution deployable (no cross-bank coordination needed)

---

## Sybil Detection Demonstration

Analyzed top 50 institutional wallets:
- **7 clusters identified** (potential same-entity control)
- **Behavioral profiles:** Settlement, DeFi Supply, Bridge User
- **Risk scoring:** Clean (0-3), Medium (4-6), Higher (7+)

**Use case:** Post-whitelist behavioral monitoring for ongoing compliance.

---

## Methodology Highlights

- **Data:** 8,000 large USDC transfers (>$100k) on Base, 90-day period
- **Volume analyzed:** $8.58 billion
- **Classification:** Protocol contracts, exchange patterns, P2P
- **Features:** Counterparty diversity, timing patterns, transaction variability
- **Clustering:** DBSCAN for same-entity identification

---

## Deliverables

1. **PDF Report:** Full analysis with visualizations (7 pages)
2. **Sankey Diagram:** Interactive flow visualization
3. **Data Outputs:** Categorized transfers, institutional wallet analysis
4. **GitHub Repo:** Complete codebase for replication/extension

---

## Scalability

This analysis covers **Base Network only**. The methodology is:
- **Network-agnostic** — can extend to Ethereum, Polygon, etc.
- **Integrable** — fits into Kinexys's existing monitoring infrastructure
- **Deployable** — single-institution behavioral monitoring (no federated learning needed)

---

## Next Steps

We welcome the opportunity to discuss:
1. Integration pathways for behavioral monitoring
2. Multi-network extension (prioritizing JPMD deployment networks)
3. Permissioned DeFi partnership strategies

**Contact:** Adeline Wen (adelinewen@uw.edu)  
**Repository:** github.com/Tyche1107/jpmd-base-opportunity
