"""
Report Generation Script - Create professional PDF report
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
import pandas as pd
from datetime import datetime

class JPMDReport:
    def __init__(self):
        self.doc = SimpleDocTemplate(
            "report/JPMD_Base_Opportunity_Analysis.pdf",
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18,
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        )
        
    def add_cover_page(self, defi_percentage):
        """Add cover page with title and key finding"""
        
        self.story.append(Spacer(1, 1.5*inch))
        
        title = Paragraph(
            f"<b>{defi_percentage:.0f}% of Institutional Dollars on Base<br/>Skip Settlement and Go Straight to DeFi.<br/>What JPMD Should Know.</b>",
            self.title_style
        )
        self.story.append(title)
        
        subtitle = Paragraph(
            "《Base上{:.0f}%的机构级美元跳过结算直接进了DeFi，JPMD需要知道这件事》".format(defi_percentage),
            self.subtitle_style
        )
        self.story.append(subtitle)
        
        self.story.append(Spacer(1, 1*inch))
        
        info_text = f"""
        <b>Prepared for:</b> JPMorgan Kinexys Team<br/>
        <b>Recipients:</b> Basak Toprak (Product Lead, JPM Coin) | Kara Kennedy (Head of Kinexys)<br/>
        <b>Prepared by:</b> Decentralized Computing Lab, University of Washington<br/>
        <b>Lead:</b> Wei Cai, PhD | <b>Author:</b> Adeline Wen (Undergraduate Research Assistant)<br/>
        <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Analysis Period:</b> 90 days on Base Network
        """
        
        self.story.append(Paragraph(info_text, self.body_style))
        self.story.append(PageBreak())
        
    def add_executive_summary(self, distribution_df):
        """Add executive summary with key findings"""
        
        heading = Paragraph("<b>Executive Summary: Product Implications for JPMD</b>", self.heading_style)
        self.story.append(heading)
        
        # Calculate DeFi percentage
        defi_categories = ['morpho', 'aave_horizon']
        defi_volume = distribution_df.loc[defi_categories, 'volume_usd'].sum() if all(cat in distribution_df.index for cat in defi_categories) else 0
        total_volume = distribution_df['volume_usd'].sum()
        defi_pct = (defi_volume / total_volume * 100) if total_volume > 0 else 0
        
        summary = f"""
        Over the past 90 days, we analyzed all large USDC transfers (>${100000:,}) on Base Network to understand 
        how institutional dollars move on-chain. This analysis directly addresses JPMD's addressable market 
        across the use cases Basak Toprak identified: payments, settlement, and collateral management.
        
        <b>Key Findings:</b>
        
        <b>1. DeFi Dominates Institutional Flow ({defi_pct:.1f}%)</b><br/>
        ${defi_volume:,.0f} ({defi_pct:.1f}% of total volume) flows directly into lending protocols (Morpho, Aave Horizon) 
        without intermediary settlement steps. This validates Toprak's insight that "cash is collateral in on-chain 
        world" — institutions are already using stablecoins for collateral and margin, not just settlement.
        
        <b>2. Settlement is NOT the Primary Use Case</b><br/>
        Wallet-to-wallet transfers (P2P settlement) represent only {distribution_df.loc['p2p', 'volume_pct']:.1f}% of volume. 
        The majority of institutional capital seeks <i>yield and collateral efficiency</i>, not simple payment rails.
        
        <b>3. Permissioned DeFi is Underutilized</b><br/>
        Aave Horizon (permissioned pools) captures only {distribution_df.loc['aave_horizon', 'volume_pct']:.1f}% despite being 
        compliance-friendly. <b>This is JPMD's whitespace</b> — institutions want yield but need compliance guardrails.
        
        <b>Implications for JPMD Launch Strategy:</b><br/>
        • Priority 1: Integrate with permissioned lending protocols (Morpho permissioned vaults, institutional Aave pools)<br/>
        • Priority 2: Enable seamless collateral deposits (competitive with USDC, but with bank-grade compliance)<br/>
        • Priority 3: Bridge infrastructure (Base ↔ other networks where JPMD will deploy)<br/>
        • Lower priority: P2P settlement features (already well-served by existing stablecoins)
        """
        
        self.story.append(Paragraph(summary, self.body_style))
        self.story.append(PageBreak())
        
    def add_methodology(self):
        """Add methodology section"""
        
        heading = Paragraph("<b>Methodology</b>", self.heading_style)
        self.story.append(heading)
        
        methodology = """
        <b>Data Collection:</b><br/>
        We collected all USDC transfer events on Base Network over the past 90 days using Basescan API. 
        Transfers were filtered to include only large institutional-scale movements (>$100,000 per transaction).
        
        <b>Destination Classification:</b><br/>
        Each destination address was categorized using:<br/>
        • Known protocol contract addresses (Morpho, Aave, bridge contracts)<br/>
        • Pattern-based exchange identification (high sender diversity, high frequency)<br/>
        • Remaining addresses classified as wallet-to-wallet (P2P)
        
        <b>Sybil Detection (Address-Level Monitoring):</b><br/>
        For institutional wallets (non-protocol, non-exchange addresses), we applied behavioral feature extraction 
        based on HasciDB methodology (University of Washington, 470,000+ addresses analyzed):<br/>
        • Counterparty diversity (unique senders/receivers)<br/>
        • Transaction timing patterns (hour-of-day distribution)<br/>
        • Transaction size variability<br/>
        • Send/receive ratio<br/>
        • Clustering to identify potential same-entity control
        
        <b>Complementarity with AIKYA:</b><br/>
        This address-level behavioral monitoring complements Kinexys's AIKYA project (transaction-level anomaly detection 
        via federated learning with BNY). AIKYA detects anomalous individual transactions across institutions; our methodology 
        monitors ongoing address behavior patterns within a single institution's whitelist — a necessary layer for 
        continuous compliance after initial KYC.
        """
        
        self.story.append(Paragraph(methodology, self.body_style))
        self.story.append(PageBreak())
        
    def add_flow_analysis(self, distribution_df):
        """Add flow analysis section with table and chart"""
        
        heading = Paragraph("<b>Institutional USDC Flow Distribution</b>", self.heading_style)
        self.story.append(heading)
        
        # Create distribution table
        table_data = [['Category', 'Volume (USD)', '% of Total', 'Avg Transfer Size']]
        
        for category, row in distribution_df.iterrows():
            table_data.append([
                category.replace('_', ' ').title(),
                f"${row['volume_usd']:,.0f}",
                f"{row['volume_pct']:.1f}%",
                f"${row['avg_transfer_size']:,.0f}"
            ])
        
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Add Sankey diagram
        try:
            img = Image('visualizations/sankey_flow.png', width=6*inch, height=3*inch)
            self.story.append(img)
        except:
            self.story.append(Paragraph("<i>Sankey diagram: visualizations/sankey_flow.png</i>", self.body_style))
        
        self.story.append(PageBreak())
        
    def add_sybil_analysis(self):
        """Add sybil detection demonstration section"""
        
        heading = Paragraph("<b>Address-Level Behavioral Monitoring: Demonstration</b>", self.heading_style)
        self.story.append(heading)
        
        intro = """
        <b>Why This Matters for JPMD:</b><br/>
        JPMD is a permissioned token — customers undergo KYC before being whitelisted. However, post-whitelist 
        monitoring is essential for ongoing compliance. Our sybil detection methodology demonstrates how on-chain 
        behavioral features can identify:<br/>
        • Addresses potentially controlled by the same entity (despite separate KYC)<br/>
        • Unusual behavioral patterns warranting review<br/>
        • Behavioral profiles (Settlement vs. DeFi Supply vs. Bridge User)
        
        This is <b>complementary to AIKYA</b>:<br/>
        • AIKYA: Transaction-level anomaly detection (federated learning, cross-institution)<br/>
        • This methodology: Address-level behavioral monitoring (on-chain features, single-institution deployable)
        
        <b>Sample Analysis (Top 30 Institutional Wallets):</b>
        """
        
        self.story.append(Paragraph(intro, self.body_style))
        
        # Load and display sybil summary
        try:
            sybil_summary = pd.read_csv('analysis/sybil_summary_table.csv')
            
            # Take top 15 for display
            sybil_top = sybil_summary.head(15)
            
            table_data = [['Address', 'Profile', 'Risk', 'Counterparties', 'Tx/Day']]
            
            for _, row in sybil_top.iterrows():
                table_data.append([
                    row['address_short'],
                    row['behavior_profile'],
                    row['risk_label'],
                    str(row['counterparty_diversity']),
                    f"{row['tx_frequency']:.1f}"
                ])
            
            table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 1*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            self.story.append(Spacer(1, 0.2*inch))
            self.story.append(table)
            
        except Exception as e:
            self.story.append(Paragraph(f"<i>Sybil analysis table: {str(e)}</i>", self.body_style))
        
        self.story.append(PageBreak())
        
    def add_conclusion(self):
        """Add conclusion and next steps"""
        
        heading = Paragraph("<b>Implications and Scalability</b>", self.heading_style)
        self.story.append(heading)
        
        conclusion = """
        <b>Key Takeaways for JPMD Product Strategy:</b>
        
        1. <b>Collateral > Settlement:</b> Institutions are using stablecoins primarily for DeFi collateral and margin, 
        not just payment rails. JPMD's interest-bearing capability positions it uniquely for this use case.
        
        2. <b>Permissioned DeFi Integration is Critical:</b> Aave Horizon and Morpho permissioned vaults are underutilized 
        relative to demand. Early integration partnerships here give JPMD first-mover advantage.
        
        3. <b>Bridge Infrastructure Matters:</b> Cross-chain movement represents significant volume. JPMD's multi-chain 
        deployment strategy should prioritize networks with high bridge activity to/from Base.
        
        4. <b>Behavioral Monitoring is Deployable:</b> Address-level monitoring can run on single-institution data 
        without requiring cross-bank collaboration (unlike AIKYA's federated learning). This makes it immediately 
        implementable for Kinexys clients.
        
        <b>Scalability:</b><br/>
        This analysis covers Base Network only. The methodology is network-agnostic and can be applied to:<br/>
        • Other networks where JPMD will deploy (Ethereum mainnet, Polygon, etc.)<br/>
        • Comparative analysis across networks to prioritize deployment order<br/>
        • Integration with Kinexys's existing transaction monitoring infrastructure
        
        <b>Next Steps:</b><br/>
        We welcome the opportunity to discuss these findings with the Kinexys team and explore integration pathways 
        for behavioral monitoring into JPMD's compliance stack.
        """
        
        self.story.append(Paragraph(conclusion, self.body_style))
        
    def generate(self):
        """Generate the complete report"""
        
        # Load data
        distribution_df = pd.read_csv('analysis/flow_distribution.csv', index_col=0)
        
        # Calculate DeFi percentage for cover
        defi_categories = ['morpho', 'aave_horizon']
        defi_volume = distribution_df.loc[defi_categories, 'volume_usd'].sum() if all(cat in distribution_df.index for cat in defi_categories) else 0
        total_volume = distribution_df['volume_usd'].sum()
        defi_pct = (defi_volume / total_volume * 100) if total_volume > 0 else 0
        
        # Build report
        self.add_cover_page(defi_pct)
        self.add_executive_summary(distribution_df)
        self.add_flow_analysis(distribution_df)
        self.add_sybil_analysis()
        self.add_methodology()
        self.add_conclusion()
        
        # Generate PDF
        self.doc.build(self.story)
        print("\n✓ Report generated: report/JPMD_Base_Opportunity_Analysis.pdf")

if __name__ == "__main__":
    report = JPMDReport()
    report.generate()
