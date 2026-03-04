"""
Main Analysis Pipeline
Orchestrates the entire analysis workflow
"""

import sys
import os
from datetime import datetime

def run_pipeline():
    """Run the complete analysis pipeline"""
    
    print("=" * 80)
    print("JPMD BASE OPPORTUNITY ANALYSIS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    steps = [
        ("1. Data Collection", "python data_collector.py"),
        ("2. Flow Analysis", "python flow_analyzer.py"),
        ("3. Sybil Detection", "python sybil_detector.py"),
        ("4. Visualization Generation", "python visualizations.py"),
        ("5. Report Generation", "python generate_report.py"),
    ]
    
    for step_name, command in steps:
        print(f"\n{'='*80}")
        print(f"STEP: {step_name}")
        print(f"{'='*80}\n")
        
        result = os.system(command)
        
        if result != 0:
            print(f"\n❌ ERROR in {step_name}")
            print("Pipeline stopped.")
            sys.exit(1)
        
        print(f"\n✓ {step_name} completed successfully")
    
    print("\n" + "=" * 80)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nOutputs:")
    print("  • Report: report/JPMD_Base_Opportunity_Analysis.pdf")
    print("  • Data: data/large_usdc_transfers.csv")
    print("  • Analysis: analysis/")
    print("  • Visualizations: visualizations/")
    print("\nNext: Review the PDF report and push to GitHub")

if __name__ == "__main__":
    run_pipeline()
