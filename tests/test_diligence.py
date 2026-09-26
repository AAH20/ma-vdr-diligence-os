import unittest
from projects.ma_vdr_diligence_os.vdr_parser import VDRParser
from projects.ma_vdr_diligence_os.diligence_evaluator import DiligenceEvaluator
from projects.ma_vdr_diligence_os.investor_os_client import InvestorOSClient

class TestMADiligenceOS(unittest.TestCase):

    def setUp(self):
        self.parser = VDRParser()
        self.evaluator = DiligenceEvaluator()
        self.client = InvestorOSClient()

    def test_document_classification(self):
        self.assertEqual(self.parser.classify_document("Acme_2025_EBITDA_Model.xlsx"), "FINANCIAL_MODEL")
        self.assertEqual(self.parser.classify_document("BishopFox_PenTest_Final_Report.pdf"), "SECURITY_PEN_TEST")
        self.assertEqual(self.parser.classify_document("Acme_SOC2_Type_II_Attestation.pdf"), "SOC2_REPORT")
        self.assertEqual(self.parser.classify_document("Series_B_Cap_Table.csv"), "CAP_TABLE")
        self.assertEqual(self.parser.classify_document("AWS_Enterprise_MSA.pdf"), "VENDOR_CONTRACTS")

    def test_clean_deal_evaluation(self):
        financials = {
            "ebitda": 5_000_000.0,
            "arr": 20_000_000.0,
            "top_3_customer_concentration": 0.15
        }
        security = {
            "critical_cves": 0,
            "high_cves": 0,
            "medium_cves": 1,
            "has_soc2_type2": True,
            "soc2_unqualified_opinion": True,
            "public_s3_buckets_detected": 0,
            "mfa_enforcement_ratio": 1.0
        }
        result = self.evaluator.evaluate_deal("CleanTech Corp", financials, security, baseline_ebitda_multiple=10.0)
        
        # Baseline = 50M
        self.assertEqual(result["financial_summary"]["baseline_valuation"], 50_000_000.0)
        # Low CVE liability (1 medium = 2,000)
        self.assertEqual(result["diligence_evaluation"]["cve_debt_liability_usd"], 2_000.0)
        self.assertEqual(result["diligence_evaluation"]["decision"], "PROCEED_CLEAN")

    def test_haircut_deal_evaluation_with_red_flags(self):
        financials = {
            "ebitda": 4_000_000.0,
            "arr": 15_000_000.0,
            "top_3_customer_concentration": 0.45 # >35% penalty
        }
        security = {
            "critical_cves": 2, # 2 * 25k = 50k
            "high_cves": 5,     # 5 * 8k = 40k
            "medium_cves": 10,  # 10 * 2k = 20k
            "has_soc2_type2": False, # 10% multiple haircut
            "soc2_unqualified_opinion": False,
            "public_s3_buckets_detected": 1, # 50k penalty
            "mfa_enforcement_ratio": 0.85 # Red flag
        }
        result = self.evaluator.evaluate_deal("RiskySaaS Inc", financials, security, baseline_ebitda_multiple=12.0)
        
        # Total CVE + bucket liability = 50k + 40k + 20k + 50k = 160k
        self.assertEqual(result["diligence_evaluation"]["cve_debt_liability_usd"], 160_000.0)
        # Multiple should be reduced from 12.0
        self.assertLess(result["diligence_evaluation"]["adjusted_multiple"], 12.0)
        # Red flags should flag SOC 2 and customer concentration
        self.assertTrue(len(result["diligence_evaluation"]["red_flags"]) >= 3)
        self.assertTrue(any("Missing SOC 2 Type II certification" in flag for flag in result["diligence_evaluation"]["red_flags"]))
        self.assertTrue(any("Elevated cyber technical debt" in flag for flag in result["diligence_evaluation"]["red_flags"]))

    def test_investor_os_client_dispatch(self):
        financials = {"ebitda": 2_000_000.0, "top_3_customer_concentration": 0.1}
        security = {"critical_cves": 0, "has_soc2_type2": True, "soc2_unqualified_opinion": True}
        evaluation = self.evaluator.evaluate_deal("TargetCo", financials, security)
        
        payload = self.client.format_ic_diligence_payload(evaluation)
        self.assertEqual(payload["platform"], "HERJAVEC_PORTFOLIO_RISK_OS")
        self.assertEqual(payload["target_company"], "TargetCo")
        
        receipt = self.client.dispatch_scorecard(payload)
        self.assertEqual(receipt["status"], "SUCCESS")
        self.assertEqual(receipt["status_code"], 201)
        self.assertIn("investor-os.vercel.app/deals/", receipt["dashboard_preview_url"])

if __name__ == "__main__":
    unittest.main()
