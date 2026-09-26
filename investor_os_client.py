"""
Investor OS API Client.
Formats and dispatches the Investment Committee (IC) Due Diligence Report
into the Herjavec Group Portfolio Risk OS (investor-os.vercel.app).
"""

import time
import hashlib
from typing import Dict, Any

class InvestorOSClient:
    """
    Client for dispatching quantitative risk & haircut scorecards to investor-os.vercel.app.
    """

    def __init__(self, api_base_url: str = "https://investor-os.vercel.app/api", auth_token: str = "mock_herjavec_token"):
        self.api_base_url = api_base_url
        self.auth_token = auth_token

    def format_ic_diligence_payload(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats evaluation dictionary to the exact schema accepted by Investor OS.
        """
        company = evaluation["company_name"]
        dil = evaluation["diligence_evaluation"]
        fin = evaluation["financial_summary"]

        record_id = f"deal_{hashlib.md5(company.encode()).hexdigest()[:10]}"
        return {
            "record_id": record_id,
            "platform": "HERJAVEC_PORTFOLIO_RISK_OS",
            "target_company": company,
            "timestamp": int(time.time()),
            "metrics": {
                "ebitda": fin["ebitda"],
                "baseline_multiple": fin["baseline_multiple"],
                "baseline_valuation": fin["baseline_valuation"],
                "adjusted_multiple": dil["adjusted_multiple"],
                "adjusted_valuation": dil["adjusted_valuation"],
                "valuation_haircut_usd": dil["recommended_valuation_haircut_usd"],
                "haircut_pct": dil["haircut_percentage"]
            },
            "cve_debt_usd": dil["cve_debt_liability_usd"],
            "recommendation": dil["decision"],
            "red_flags": dil["red_flags"],
            "audit_trail_signature": hashlib.sha256(f"{company}:{dil['adjusted_valuation']}".encode()).hexdigest()
        }

    def dispatch_scorecard(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates dispatching the deal scorecard to investor-os.vercel.app/api/diligence-scorecard.
        """
        if not payload.get("target_company") or "metrics" not in payload:
            raise ValueError("Malformed Investor OS payload: missing required metadata")

        return {
            "status": "SUCCESS",
            "portfolio_record_id": payload["record_id"],
            "ingested_to": f"{self.api_base_url}/diligence-scorecard",
            "status_code": 201,
            "dashboard_preview_url": f"https://investor-os.vercel.app/deals/{payload['record_id']}"
        }
