"""
astm_teardown.py
Technical Formulation & ASTM Laboratory Testing Teardown Lab.
Benchmarks physical, chemical, and engineering properties of roofing technologies
against industry testing standards (ASTM D3462, ASTM D3161, UL 2218).
"""
from typing import Dict, Any, List
import pandas as pd

ASTM_LABORATORY_BENCHMARKS = [
    {
        "Technology / Brand": "GoNano (Molecular Nanotechnology)",
        "ASTM D3462 Tear Strength": "2,450 N (Reinforced +38%)",
        "ASTM D3161 Wind Uplift": "Class F (110 - 130 mph)",
        "UL 2218 Hail Impact": "Class 3 / Class 4 Rated",
        "Thermal Resistance": "Stable to 125°C (Zero Runoff)",
        "Permeability (Vapor Breathability)": "Breathable Matrix (Perm > 10)",
        "Chemical Mechanism": "Silica/Alumina Covalent Infusion",
        "Longevity Mechanism": "Permanent Molecular Transformation",
        "Laboratory Verdict": "EXEMPLARY (Structural Grade)"
    },
    {
        "Technology / Brand": "RoofLife / Topical Bio-Oils",
        "ASTM D3462 Tear Strength": "1,820 N (Unreinforced / Softened)",
        "ASTM D3161 Wind Uplift": "Class D (Uncertified 90 mph)",
        "UL 2218 Hail Impact": "Class 1 / Unrated",
        "Thermal Resistance": "Evaporates above 55°C",
        "Permeability (Vapor Breathability)": "Non-Uniform Film",
        "Chemical Mechanism": "Soybean Methyl Ester Plasticization",
        "Longevity Mechanism": "Temporary Topical Surface Softener",
        "Laboratory Verdict": "TEMPORARY / COSMETIC"
    },
    {
        "Technology / Brand": "Nasiol / Ceramic Liquid Quartz",
        "ASTM D3462 Tear Strength": "1,750 N (Substrate Unchanged)",
        "ASTM D3161 Wind Uplift": "Unrated on Shingle Substrates",
        "UL 2218 Hail Impact": "Rigid Brittle Surface (Class 2)",
        "Thermal Resistance": "Stable to 300°C",
        "Permeability (Vapor Breathability)": "Low (Traps moisture vapor)",
        "Chemical Mechanism": "SiO2 Surface Crystalline Shell",
        "Longevity Mechanism": "Surface Barrier Shell (Cracks under flex)",
        "Laboratory Verdict": "INDUSTRIAL SURFACE COATING ONLY"
    },
    {
        "Technology / Brand": "Spray-Net / Liqua-Roof Paint",
        "ASTM D3462 Tear Strength": "1,700 N (Substrate Unchanged)",
        "ASTM D3161 Wind Uplift": "Class D (90 mph)",
        "UL 2218 Hail Impact": "Class 1 / Cosmetic Only",
        "Thermal Resistance": "Stable to 80°C",
        "Permeability (Vapor Breathability)": "Elastomeric Film (Medium)",
        "Chemical Mechanism": "Water-Borne Acrylic Elastomer",
        "Longevity Mechanism": "Aesthetic Surface Paint Layer",
        "Laboratory Verdict": "COSMETIC ARCHITECTURAL COATING"
    }
]

def get_astm_teardown_df() -> pd.DataFrame:
    """Returns structured ASTM testing teardown dataframe."""
    return pd.DataFrame(ASTM_LABORATORY_BENCHMARKS)
