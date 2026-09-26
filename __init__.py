"""
M&A VDR Diligence OS Package.
Derived from project-atlas-due-diligence and Herjavec Group Risk OS.
"""

from .vdr_parser import VDRParser
from .diligence_evaluator import DiligenceEvaluator
from .investor_os_client import InvestorOSClient

__all__ = ["VDRParser", "DiligenceEvaluator", "InvestorOSClient"]
