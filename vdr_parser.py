"""
Virtual Data Room (VDR) Document Parser.
Classifies and extracts structured quantitative metrics from M&A diligence documents
(financials, cap tables, pen-test reports, SOC 2 reports, vendor agreements).
"""

from typing import Dict, List, Any

class VDRParser:
    """
    Parses and categorizes Virtual Data Room documents into standardized telemetry.
    """

    SUPPORTED_DOC_TYPES = [
        "FINANCIAL_MODEL",
        "SECURITY_PEN_TEST",
        "SOC2_REPORT",
        "CAP_TABLE",
        "VENDOR_CONTRACTS"
    ]

    def classify_document(self, filename: str, content_snippet: str = "") -> str:
        name_lower = filename.lower()
        content_lower = content_snippet.lower()

        if any(k in name_lower or k in content_lower for k in ["p&l", "ebitda", "financial", "income_statement", "balance_sheet"]):
            return "FINANCIAL_MODEL"
        elif any(k in name_lower or k in content_lower for k in ["penetration", "pentest", "pen_test", "vulnerability", "burp", "cve"]):
            return "SECURITY_PEN_TEST"
        elif any(k in name_lower or k in content_lower for k in ["soc2", "soc 2", "type ii", "type i", "attestation", "iso27001"]):
            return "SOC2_REPORT"
        elif any(k in name_lower or k in content_lower for k in ["cap_table", "equity", "shareholder", "ownership"]):
            return "CAP_TABLE"
        elif any(k in name_lower or k in content_lower for k in ["msa", "vendor", "sla", "procurement"]):
            return "VENDOR_CONTRACTS"
        return "GENERAL_DILIGENCE"

    def extract_financial_metrics(self, payload: Dict[str, Any]) -> Dict[str, float]:
        return {
            "arr": float(payload.get("arr", 10_000_000.0)),
            "ebitda": float(payload.get("ebitda", 2_500_000.0)),
            "gross_margin": float(payload.get("gross_margin", 0.78)),
            "annual_churn_rate": float(payload.get("annual_churn_rate", 0.08)),
            "top_3_customer_concentration": float(payload.get("top_3_customer_concentration", 0.22))
        }

    def extract_security_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "critical_cves": int(payload.get("critical_cves", 0)),
            "high_cves": int(payload.get("high_cves", 0)),
            "medium_cves": int(payload.get("medium_cves", 0)),
            "has_soc2_type2": bool(payload.get("has_soc2_type2", False)),
            "soc2_unqualified_opinion": bool(payload.get("soc2_unqualified_opinion", False)),
            "public_s3_buckets_detected": int(payload.get("public_s3_buckets_detected", 0)),
            "mfa_enforcement_ratio": float(payload.get("mfa_enforcement_ratio", 1.0))
        }
