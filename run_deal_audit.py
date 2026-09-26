"""
M&A Virtual Data Room (VDR) Due Diligence Runner.
Executive terminal interface for Private Equity deal teams and M&A operating partners.
Generates Investment Committee (IC) Risk Scorecards with defensible EBITDA valuation haircuts.
"""

import sys
import json
import argparse
from .vdr_parser import VDRParser
from .diligence_evaluator import DiligenceEvaluator
from .investor_os_client import InvestorOSClient

def main():
    parser = argparse.ArgumentParser(description="Herjavec Portfolio Risk OS: M&A Due Diligence Evaluator")
    parser.add_argument("--company", type=str, default="Apex Financial Technologies Inc.", help="Target Acquisition Company Name")
    parser.add_argument("--ebitda", type=float, default=6_500_000.0, help="Target Reported EBITDA in USD")
    parser.add_argument("--multiple", type=float, default=14.0, help="Baseline Target Enterprise Multiple (e.g. 14x)")
    parser.add_argument("--concentration", type=float, default=0.38, help="Top-3 Customer Revenue Concentration (0.0 - 1.0)")
    parser.add_argument("--critical-cves", type=int, default=3, help="Unpatched Critical CVEs found in Pen-Test")
    parser.add_argument("--high-cves", type=int, default=7, help="Unpatched High CVEs found in Pen-Test")
    parser.add_argument("--soc2", action="store_true", default=False, help="Target possesses active SOC 2 Type II report")
    parser.add_argument("--s3-leaks", type=int, default=1, help="Public S3 buckets detected in external scan")

    args = parser.parse_args()

    evaluator = DiligenceEvaluator()
    client = InvestorOSClient()

    financials = {
        "ebitda": args.ebitda,
        "arr": args.ebitda * 3.8,
        "top_3_customer_concentration": args.concentration
    }

    security = {
        "critical_cves": args.critical_cves,
        "high_cves": args.high_cves,
        "medium_cves": 12,
        "has_soc2_type2": args.soc2,
        "soc2_unqualified_opinion": args.soc2,
        "public_s3_buckets_detected": args.s3_leaks,
        "mfa_enforcement_ratio": 0.88
    }

    evaluation = evaluator.evaluate_deal(
        company_name=args.company,
        financial_metrics=financials,
        security_metrics=security,
        baseline_ebitda_multiple=args.multiple
    )

    payload = client.format_ic_diligence_payload(evaluation)
    receipt = client.dispatch_scorecard(payload)

    print("=" * 80)
    print("💼 HERJAVEC GROUP - PORTFOLIO RISK OS | M&A DUE DILIGENCE SCORECARD")
    print("=" * 80)
    print(f"Target Company:            {evaluation['company_name']}")
    print(f"Reported LTM EBITDA:       ${financials['ebitda']:,.2f}")
    print(f"Baseline Multiple:         {evaluation['financial_summary']['baseline_multiple']}x")
    print(f"Baseline Enterprise Value: ${evaluation['financial_summary']['baseline_valuation']:,.2f}")
    print("-" * 80)
    print("🔍 QUANTITATIVE RISK ADJUSTMENTS & DILIGENCE FINDINGS:")
    for idx, flag in enumerate(evaluation['diligence_evaluation']['red_flags'], 1):
        print(f"  [{idx}] {flag}")
    print(f"  • Direct Cyber Debt Liability:      -${evaluation['diligence_evaluation']['cve_debt_liability_usd']:,.2f}")
    print(f"  • Adjusted Enterprise Multiple:      {evaluation['diligence_evaluation']['adjusted_multiple']}x")
    print(f"  • Adjusted Enterprise Value:        ${evaluation['diligence_evaluation']['adjusted_valuation']:,.2f}")
    print("=" * 80)
    print(f"🎯 RECOMMENDED VALUATION HAIRCUT:      -${evaluation['diligence_evaluation']['recommended_valuation_haircut_usd']:,.2f} ({evaluation['diligence_evaluation']['haircut_percentage']}%)")
    print(f"📌 INVESTMENT COMMITTEE DECISION:      {evaluation['diligence_evaluation']['decision']}")
    print(f"🌐 Ingested into Herjavec Risk OS:     {receipt['dashboard_preview_url']}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
