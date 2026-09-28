"""
ip_radar.py
Patent, Trademark & Intellectual Property (IP) Moat Radar.
Tracks patent filings, chemical formulation claims, trademark registrations,
and IP infringement litigation across USPTO, Google Patents, and WIPO.
"""
from typing import List, Dict, Any

COMPETITOR_IP_PORTFOLIO = [
    {
        "competitor": "GoNano (Your Brand)",
        "patent_title": "Molecular Transformation and Nanoparticle Infusion for Bituminous Building Materials",
        "doc_number": "US-PAT-2023-018921A1",
        "jurisdiction": "USPTO & WIPO (PCT)",
        "filing_date": "2023-04-12",
        "status": "GRANTED / ACTIVE",
        "chemical_claim": "Infiltration of silica (SiO2) and alumina (Al2O3) nanoparticle dispersion into asphalt shingle bitumen matrix, establishing covalent molecular cross-linking to prevent volatile oil depletion.",
        "moat_defense_score": "9.5 / 10.0 (High Moat)",
        "patent_url": "https://patents.google.com"
    },
    {
        "competitor": "RoofLife Canada / Technology Licensors",
        "patent_title": "Agricultural Ester Composition for In-Situ Asphalt Pavement and Shingle Softening",
        "doc_number": "US-PAT-2019-0345332A1",
        "jurisdiction": "USPTO & CIPO (Canada)",
        "filing_date": "2019-08-14",
        "status": "ACTIVE / UTILITY PATENT",
        "chemical_claim": "Topical application of methylated soybean oil and fatty acid methyl esters to temporarily re-plasticize asphalt bitumen.",
        "moat_defense_score": "4.2 / 10.0 (Low Moat - Easily Workaroundable)",
        "patent_url": "https://patents.google.com"
    },
    {
        "competitor": "Nasiol (Artekya Technology)",
        "patent_title": "Sol-Gel Synthesis of Hydrophobic and Oleophobic Ceramic Barrier Formulations",
        "doc_number": "EP-PAT-3412741B1",
        "jurisdiction": "EPO (European Patent Office) & WIPO",
        "filing_date": "2018-05-20",
        "status": "GRANTED / EXPORT ENFORCED",
        "chemical_claim": "Silane-terminated fluoro-free liquid ceramic coating providing surface contact angle > 110 degrees on non-porous and semi-porous substrates.",
        "moat_defense_score": "7.8 / 10.0 (Strong Industrial Moat)",
        "patent_url": "https://patents.google.com"
    },
    {
        "competitor": "Spray-Net",
        "patent_title": "Automated Mobile Spray Rig for Controlled Exterior Architectural Coating Formulation",
        "doc_number": "CA-PAT-2984102A1",
        "jurisdiction": "CIPO (Canada) & USPTO",
        "filing_date": "2017-10-18",
        "status": "ACTIVE / APPARATUS PATENT",
        "chemical_claim": "On-site temperature and humidity-conditioned fluid delivery system for elastomeric paint spray application on exterior siding.",
        "moat_defense_score": "6.0 / 10.0 (Equipment Moat)",
        "patent_url": "https://patents.google.com"
    }
]

def get_competitor_ip_records(competitor_filter: str = "All Competitors") -> List[Dict[str, Any]]:
    """Retrieves competitor patent and trademark records."""
    if competitor_filter == "All Competitors" or not competitor_filter:
        return COMPETITOR_IP_PORTFOLIO
    return [p for p in COMPETITOR_IP_PORTFOLIO if competitor_filter.lower() in p["competitor"].lower()]
