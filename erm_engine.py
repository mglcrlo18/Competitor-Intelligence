"""
erm_engine.py
Enterprise Risk Management (ERM) & Chief Risk Officer (CRO) Assessment Framework
Compliant with ISO 31000 and COSO ERM standards adapted for Competitive Market Intelligence.
Fully dynamic: scales across all monitored entities in the Google Sheets & SQLite database.
"""
from typing import Dict, Any, List
import pandas as pd
from db_manager import get_competitor_profile, get_all_competitor_profiles

PROFILES_CACHE = {
    "RoofLife Canada": {
        "inherent_threat_score": 8.8,
        "inherent_threat_level": "CRITICAL",
        "control_efficacy_score": 6.2,
        "control_efficacy_level": "MODERATE",
        "residual_threat_score": 5.5,
        "residual_threat_level": "HIGH",
        "polarity_var_90d": 24.5,
        "primary_exposure": "D2C Market Share Cannibalization & Aggressive Ad Funnel",
        "kcis": [
            {"indicator": "PPC Ad Spend Spike", "threshold": "> $20,000/mo", "status": "TRIGGERED", "severity": "HIGH"},
            {"indicator": "Rival Dealer Recruitment in Ontario", "threshold": "> 5 new contractors/quarter", "status": "ACTIVE", "severity": "HIGH"},
            {"indicator": "Customer Price Undercutting", "threshold": "< 20% of full replacement", "status": "TRIGGERED", "severity": "CRITICAL"}
        ],
        "reverse_stress_scenario": "RoofLife secures an exclusive commercial partnership with a top-tier retail home improvement chain (e.g. Home Depot or Lowe's), locking out competing local contractor channels.",
        "contingency_mitigation": "Accelerate GoNano 15-Year Molecular Warranty campaigns targeting commercial insurance adjusters and property managers."
    },
    "Nasiol (Artekya)": {
        "inherent_threat_score": 7.5,
        "inherent_threat_level": "HIGH",
        "control_efficacy_score": 7.0,
        "control_efficacy_level": "STRONG",
        "residual_threat_score": 3.8,
        "residual_threat_level": "MODERATE",
        "polarity_var_90d": 16.0,
        "primary_exposure": "Technical Brand Confusion & DIY Ceramic Surface Dilution",
        "kcis": [
            {"indicator": "Launch of Exterior Architecture Line", "threshold": "New architectural SKU debut", "status": "WATCHLIST", "severity": "MEDIUM"},
            {"indicator": "International Distributor Expansion", "threshold": "> 3 overseas hubs", "status": "ACTIVE", "severity": "MEDIUM"}
        ],
        "reverse_stress_scenario": "Nasiol successfully re-educates the market to equate cheap topical ceramic sprays with true deep-penetration molecular nanotech.",
        "contingency_mitigation": "Publish independent laboratory ASTM D3462 tensile strength and wind/hail tear testing proving GoNano structural superiority."
    },
    "RevivaRoof": {
        "inherent_threat_score": 6.8,
        "inherent_threat_level": "HIGH",
        "control_efficacy_score": 6.5,
        "control_efficacy_level": "MODERATE",
        "residual_threat_score": 4.2,
        "residual_threat_level": "MODERATE",
        "polarity_var_90d": 18.5,
        "primary_exposure": "Insurance Preemption through 'Science of Compliance' Campaign",
        "kcis": [
            {"indicator": "Underwriting Endorsements", "threshold": "Direct mention in insurance renewal letters", "status": "ACTIVE", "severity": "HIGH"},
            {"indicator": "Local Roofing Association Sponsorships", "threshold": "> 3 state conventions", "status": "TRIGGERED", "severity": "MEDIUM"}
        ],
        "reverse_stress_scenario": "State insurance boards approve bio-oil restorative sprays as certified mitigations against policy cancellation for aging shingle roofs.",
        "contingency_mitigation": "Partner with forensic roofing engineering firms to show bio-oil asphalt degradation and granule washout under thermal cycling."
    },
    "Spray-Net": {
        "inherent_threat_score": 6.0,
        "inherent_threat_level": "MODERATE",
        "control_efficacy_score": 7.5,
        "control_efficacy_level": "STRONG",
        "residual_threat_score": 2.9,
        "residual_threat_level": "LOW",
        "polarity_var_90d": 11.0,
        "primary_exposure": "Aesthetic Curb-Appeal Dominance in Franchise Markets",
        "kcis": [
            {"indicator": "Franchise Territory Growth", "threshold": "> 10 new territories/year", "status": "ACTIVE", "severity": "MEDIUM"}
        ],
        "reverse_stress_scenario": "Spray-Net expands its custom spray rigs to bundle nanocoating solutions directly into exterior remodeling contracts.",
        "contingency_mitigation": "Position GoNano as the performance substrate protection layer that contractors apply before or in synergy with aesthetic treatments."
    }
}

def calculate_erm_threat_matrix(competitor_name: str) -> Dict[str, Any]:
    """
    Computes CRO quantitative risk metrics dynamically for any monitored entity.
    """
    if not competitor_name:
        competitor_name = "RoofLife Canada"

    # Check manual cache first
    for key, p in PROFILES_CACHE.items():
        if key.lower() in competitor_name.lower():
            return p

    # Pull from database
    prof = get_competitor_profile(competitor_name)
    if prof:
        inh = float(prof.get("inherent_threat_score") or 6.0)
        ctrl = float(prof.get("control_efficacy_score") or 6.8)
        res = float(prof.get("residual_threat_score") or (inh * (1.0 - (ctrl / 12.0))))
        category = prof.get("category", "General Competition")
        notes = prof.get("notes", "")

        inh_lvl = "CRITICAL" if inh >= 8.0 else ("HIGH" if inh >= 6.5 else ("MODERATE" if inh >= 5.0 else "LOW"))
        ctrl_lvl = "STRONG" if ctrl >= 7.5 else ("MODERATE" if ctrl >= 6.0 else "WEAK")
        res_lvl = "CRITICAL" if res >= 5.0 else ("HIGH" if res >= 3.8 else ("MODERATE" if res >= 2.5 else "LOW"))
        var_downside = round(inh * 2.8, 1)

        is_bio = "bio" in category.lower() or "soy" in category.lower() or "oil" in category.lower()
        is_nano = "nano" in category.lower()

        if is_bio:
            exposure = "D2C Bio-Oil Marketing & Warranty Claims Price Undercutting"
            kcis = [
                {"indicator": "Contractor Channel Poaching", "threshold": "> 3 applicators switched", "status": "ACTIVE", "severity": "HIGH"},
                {"indicator": "Aggressive Social Ad Penetration", "threshold": "> 10 active Meta ad sets", "status": "TRIGGERED", "severity": "HIGH"},
                {"indicator": "Local Door-to-Door Canvassing", "threshold": "High storm frequency zones", "status": "WATCHLIST", "severity": "MEDIUM"}
            ]
            scenario = f"{competitor_name} expands contractor networks with aggressive 80% cost savings claims, confusing homeowners between topical oils and nanotech."
            mitigation = "Deploy GoNano independent laboratory ASTM D3462 physical tear testing and certified applicator credentials to field reps."
        elif is_nano:
            exposure = "Brand Dilution & Low-Cost Surface Nanocoating Confusion"
            kcis = [
                {"indicator": "Trademark / Brand Encroachment", "threshold": "Patent office filings", "status": "ACTIVE", "severity": "HIGH"},
                {"indicator": "Franchise Expansion in Quebec/Canada", "threshold": "New regional hubs", "status": "TRIGGERED", "severity": "MEDIUM"}
            ]
            scenario = f"{competitor_name} markets superficial nanocoatings that wash off under thermal shock, causing consumer skepticism toward all nanotech."
            mitigation = "Educate commercial adjusters on deep molecular cross-linking versus superficial hydrophobic surface barriers."
        else:
            exposure = "Regional Territory Expansion & Price Competition"
            kcis = [
                {"indicator": "Competitive Quote Inquiries", "threshold": "> 5 homeowner mentions/mo", "status": "ACTIVE", "severity": "MEDIUM"},
                {"indicator": "Digital Ad Visibility", "threshold": "Regional Google search share", "status": "WATCHLIST", "severity": "LOW"}
            ]
            scenario = f"{competitor_name} introduces aggressive regional discounts, increasing competitive sales friction in key target markets."
            mitigation = "Arm local sales partners with GoNano 15-Year Molecular Warranty and non-prorated value proposition."

        return {
            "inherent_threat_score": inh,
            "inherent_threat_level": inh_lvl,
            "control_efficacy_score": ctrl,
            "control_efficacy_level": ctrl_lvl,
            "residual_threat_score": round(res, 1),
            "residual_threat_level": res_lvl,
            "polarity_var_90d": var_downside,
            "primary_exposure": exposure,
            "kcis": kcis,
            "reverse_stress_scenario": scenario,
            "contingency_mitigation": mitigation
        }

    # Default fallback profile
    return {
        "inherent_threat_score": 5.5,
        "inherent_threat_level": "MODERATE",
        "control_efficacy_score": 6.8,
        "control_efficacy_level": "MODERATE",
        "residual_threat_score": 3.1,
        "residual_threat_level": "LOW",
        "polarity_var_90d": 12.5,
        "primary_exposure": "General Regional Competition & Price Friction",
        "kcis": [
            {"indicator": "Digital Ad Frequency Increase", "threshold": "> 15 active ad sets", "status": "WATCHLIST", "severity": "LOW"}
        ],
        "reverse_stress_scenario": "Rival introduces deep discount pricing with aggressive local door-to-door sales crews.",
        "contingency_mitigation": "Strengthen dealer retention rebates and certified installer marketing materials."
    }

def generate_erm_kpi_table() -> pd.DataFrame:
    """Generates structured table comparing ERM ratings across ALL monitored competitors in the database."""
    profiles = get_all_competitor_profiles()
    data = []
    
    for p in profiles:
        name = p["name"]
        if name == "GoNano (Your Brand)":
            continue
        inh = float(p.get("inherent_threat_score") or 5.5)
        ctrl = float(p.get("control_efficacy_score") or 6.8)
        res = float(p.get("residual_threat_score") or 3.0)
        
        if res >= 4.5:
            rating = "HIGH"
        elif res >= 3.0:
            rating = "MODERATE"
        else:
            rating = "LOW"

        var_downside = f"{round(inh * 2.8, 1)}%"
        status = p.get("report_status") or "Monitored"

        data.append({
            "Competitor": name,
            "Category": p.get("category", "Restoration"),
            "Inherent Threat": inh,
            "Control Efficacy": ctrl,
            "Residual Threat": res,
            "Risk Rating": rating,
            "90d VaR Downside": var_downside,
            "Status / Reports": status
        })

    return pd.DataFrame(data)
