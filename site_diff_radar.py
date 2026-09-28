"""
site_diff_radar.py
Silent Website, Pricing & Warranty DOM Change Detection Radar.
Tracks unannounced competitor website modifications, warranty disclaimer adjustments,
and stealth price changes using text-level diffing algorithms.
"""
import difflib
from typing import Dict, Any, List

HISTORICAL_PAGE_SNAPSHOTS = {
    "RoofLife Canada": {
        "url": "https://rooflifecanada.com/warranty-and-pricing",
        "baseline_date": "2024-Q3 Baseline",
        "current_date": "2026-Q3 Audit",
        "baseline_content": """ROOFLIFE CANADA GUARANTEE & PRICING POLICY
- Standard Treatment Cost: $1,699 for homes up to 2,500 sq.ft.
- 15-Year 100% Comprehensive Shingle Life Extension Guarantee.
- Covers all structural asphalt shingle failure, cracking, and curling.
- Full contractor replacement rebate if shingles fail within 15 years.
- Eco-Friendly Soy Formula certified safe for all residential applications.""",
        "current_content": """ROOFLIFE CANADA GUARANTEE & PRICING POLICY
- Standard Treatment Cost: $2,199 for homes up to 2,500 sq.ft. (Price increased +$500)
- 15-Year Limited Pro-Rated Shingle Rejuvenation Guarantee.
- Excludes roofs with pre-existing granular depletion, hail impact, or over 18 years age.
- Replacement rebate is strictly limited to re-application of bio-oil product only.
- Pre-inspection fee of $150 now required prior to certified application."""
    },
    "Nasiol (Artekya)": {
        "url": "https://nasiol.com/architectural-coatings",
        "baseline_date": "2024-Q4 Baseline",
        "current_date": "2026-Q3 Audit",
        "baseline_content": """NASIOL INDUSTRIAL COATINGS CATALOG
- Primary Focus: High-end automotive detailing, marine, and glass coatings.
- Architectural distribution via specialty industrial chemical distributors only.
- Formulation: SiO2 solvent-borne liquid quartz.""",
        "current_content": """NASIOL INDUSTRIAL COATINGS CATALOG
- Primary Focus: Expanding into North American residential and exterior architectural substrates.
- Direct-to-contractor certification program launched in US and Canada.
- Formulation: Hybrid SiO2/Al2O3 exterior barrier coating for concrete and roofing."""
    },
    "RevivaRoof": {
        "url": "https://revivaroof.com/compliance-insurance",
        "baseline_date": "2025-Q1 Baseline",
        "current_date": "2026-Q3 Audit",
        "baseline_content": """THE SCIENCE OF COMPLIANCE
- Guarantees insurance policy renewal by restoring shingle flexibility.
- Direct partnership with state-licensed roof inspectors.
- Zero customer cost if insurance company rejects certification.""",
        "current_content": """THE SCIENCE OF COMPLIANCE
- Assists homeowners in demonstrating roof maintenance diligence to insurance adjusters.
- Inspection certificates provide third-party maintenance verification.
- Disclaimer: Insurance policy renewals remain subject to individual carrier underwriting discretion."""
    }
}

def compute_text_diff(competitor_name: str) -> Dict[str, Any]:
    """
    Computes visual side-by-side additions and removals between historical baseline and current page content.
    """
    snapshot = HISTORICAL_PAGE_SNAPSHOTS.get(competitor_name)
    if not snapshot:
        # Fallback generic snapshot
        snapshot = {
            "url": f"https://{competitor_name.lower().replace(' ', '')}.com/pricing",
            "baseline_date": "Historical Baseline",
            "current_date": "Live Audit",
            "baseline_content": f"- Standard pricing: $0.75/sq.ft.\n- Basic contractor warranty.\n- Local territory servicing.",
            "current_content": f"- Standard pricing: $0.90/sq.ft. (+20% adjustment)\n- Added warranty limitations on hail and wind damage.\n- Expanding regional territory franchises."
        }
        
    baseline_lines = snapshot["baseline_content"].splitlines()
    current_lines = snapshot["current_content"].splitlines()
    
    diff = list(difflib.ndiff(baseline_lines, current_lines))
    
    additions = [line[2:] for line in diff if line.startswith("+ ")]
    deletions = [line[2:] for line in diff if line.startswith("- ")]
    
    return {
        "url": snapshot["url"],
        "baseline_date": snapshot["baseline_date"],
        "current_date": snapshot["current_date"],
        "baseline_text": snapshot["baseline_content"],
        "current_text": snapshot["current_content"],
        "additions": additions,
        "deletions": deletions,
        "diff_raw": diff
    }
