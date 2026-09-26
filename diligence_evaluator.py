"""
M&A Due Diligence Evaluator Engine.
Derived from project-atlas-due-diligence mathematical models.
Quantifies technical debt, CVE liabilities, compliance posture, and calculates
defensible valuation haircuts for private equity buyout funds.
"""

from typing import Dict, Any, List

class DiligenceEvaluator:
    """
    Evaluates target company M&A risk and computes enterprise valuation haircut.
    """

    CRITICAL_CVE_LIABILITY_USD = 25_000.0
    HIGH_CVE_LIABILITY_USD = 8_000.0
    MEDIUM_CVE_LIABILITY_USD = 2_000.0
    PUBLIC_BUCKET_PENALTY_USD = 50_000.0

    def calculate_cve_liability(self, security_metrics: Dict[str, Any]) -> float:
        critical_cost = security_metrics.get("critical_cves", 0) * self.CRITICAL_CVE_LIABILITY_USD
        high_cost = security_metrics.get("high_cves", 0) * self.HIGH_CVE_LIABILITY_USD
        medium_cost = security_metrics.get("medium_cves", 0) * self.MEDIUM_CVE_LIABILITY_USD
        bucket_penalty = security_metrics.get("public_s3_buckets_detected", 0) * self.PUBLIC_BUCKET_PENALTY_USD

        return float(critical_cost + high_cost + medium_cost + bucket_penalty)

    def evaluate_deal(
        self,
        company_name: str,
        financial_metrics: Dict[str, float],
        security_metrics: Dict[str, Any],
        baseline_ebitda_multiple: float = 12.0
    ) -> Dict[str, Any]:
        ebitda = financial_metrics.get("ebitda", 0.0)
        baseline_valuation = ebitda * baseline_ebitda_multiple
        red_flags: List[str] = []

        # 1. CVE Technical Debt
        cve_liability = self.calculate_cve_liability(security_metrics)
        if cve_liability > 100_000:
            red_flags.append(f"Elevated cyber technical debt: ${cve_liability:,.2f} in remediation liabilities")

        # 2. SOC 2 / Compliance Haircut
        compliance_discount_factor = 1.0
        if not security_metrics.get("has_soc2_type2", False):
            compliance_discount_factor -= 0.10  # 10% valuation haircut
            red_flags.append("Missing SOC 2 Type II certification; enterprise sales friction risk")
        elif not security_metrics.get("soc2_unqualified_opinion", False):
            compliance_discount_factor -= 0.05  # 5% haircut for qualified opinion
            red_flags.append("Qualified auditor opinion in SOC 2 Type II report")

        # 3. Customer Concentration Penalty
        concentration = financial_metrics.get("top_3_customer_concentration", 0.0)
        concentration_discount_factor = 1.0
        if concentration > 0.35:
            concentration_discount_factor -= 0.08  # 8% haircut for extreme customer concentration
            red_flags.append(f"High customer concentration: Top 3 clients represent {concentration*100:.1f}% of ARR")

        # 4. MFA & Identity Drift Penalty
        mfa_ratio = security_metrics.get("mfa_enforcement_ratio", 1.0)
        if mfa_ratio < 0.95:
            red_flags.append(f"MFA enforcement below enterprise threshold: {mfa_ratio*100:.1f}%")

        # Combine discounts
        total_discount_factor = compliance_discount_factor * concentration_discount_factor
        adjusted_multiple = round(baseline_ebitda_multiple * total_discount_factor, 2)
        
        # Valuation after multiple adjustment minus direct dollar liabilities
        adjusted_valuation = (ebitda * adjusted_multiple) - cve_liability
        total_haircut_usd = baseline_valuation - adjusted_valuation

        # Recommendation logic
        if total_haircut_usd > (0.25 * baseline_valuation):
            decision = "RENEGOTIATE_MAJOR_HAIRCUT"
        elif total_haircut_usd > (0.10 * baseline_valuation):
            decision = "PROCEED_WITH_VALUATION_ADJUSTMENT"
        else:
            decision = "PROCEED_CLEAN"

        return {
            "company_name": company_name,
            "financial_summary": {
                "ebitda": ebitda,
                "baseline_multiple": baseline_ebitda_multiple,
                "baseline_valuation": round(baseline_valuation, 2)
            },
            "diligence_evaluation": {
                "cve_debt_liability_usd": round(cve_liability, 2),
                "adjusted_multiple": adjusted_multiple,
                "adjusted_valuation": round(adjusted_valuation, 2),
                "recommended_valuation_haircut_usd": round(total_haircut_usd, 2),
                "haircut_percentage": round((total_haircut_usd / baseline_valuation) * 100, 2) if baseline_valuation > 0 else 0.0,
                "decision": decision,
                "red_flags": red_flags
            }
        }
