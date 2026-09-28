"""
dealer_intel.py
Contractor, Applicator & Dealer Network Intelligence Engine.
Tracks contractor sentiment, applicator churn, and dealer dissatisfaction
to identify high-probability recruitment targets for GoNano certified networks.
"""
from typing import List, Dict, Any

DEALER_INTEL_RECORDS = [
    {
        "contractor_id": "DEALER-01",
        "region": "Ontario, Canada",
        "current_rival_brand": "RoofLife Canada Applicator",
        "sentiment_status": "HIGH DISSATISFACTION (Poaching Target)",
        "reported_friction": "Contractor hit with 14 customer callbacks after severe winter; shingles treated with bio-oil showed curling. RoofLife corporate refused warranty support, forcing contractor to absorb customer compensation costs.",
        "recruitment_strategy": "Present GoNano ASTM cold-weather freeze-thaw lab certificates and offer GoNano Certified Applicator territory exclusivity.",
        "forum_source": "Canadian Roofing Contractors Discussion Group",
        "source_url": "https://www.google.com/search?q=ontario+roofing+contractor+rejuvenation+reviews"
    },
    {
        "contractor_id": "DEALER-02",
        "region": "Dallas / Fort Worth, Texas",
        "current_rival_brand": "RevivaRoof Network Member",
        "sentiment_status": "MODERATE DISSATISFACTION",
        "reported_friction": "Local insurance adjusters refusing to accept RevivaRoof certificates for hail-damaged roofs; homeowners demanding refunds because insurance cancelled their policies anyway.",
        "recruitment_strategy": "Arm contractor with GoNano Class 3/4 impact test data to win insurance broker recommendations.",
        "forum_source": "Texas Storm Restoration Contractor Forum",
        "source_url": "https://www.google.com/search?q=texas+roofing+contractor+insurance+coating+disputes"
    },
    {
        "contractor_id": "DEALER-03",
        "region": "Florida Sunbelt (Tampa / Orlando)",
        "current_rival_brand": "Independent Bio-Spray Contractor",
        "sentiment_status": "HIGH DISSATISFACTION (Immediate Target)",
        "reported_friction": "Intense summer heat causes agricultural bio-oil to evaporate in 8 months. Homeowners notice roofs returning to dull gray, causing customer trust crisis.",
        "recruitment_strategy": "Demonstrate GoNano silica nanoparticle thermal stability (tested up to 120°C substrate temperature without breakdown).",
        "forum_source": "Reddit r/Roofing Professional Network",
        "source_url": "https://reddit.com/r/Roofing"
    },
    {
        "contractor_id": "DEALER-04",
        "region": "Pacific Northwest (Seattle / Portland)",
        "current_rival_brand": "Regional Sealant Applicator",
        "sentiment_status": "CONTENT / OBSERVING",
        "reported_friction": "Satisfied with basic water shedding, but customer requests for non-toxic, eco-safe permanent nanotechnology are growing.",
        "recruitment_strategy": "Offer co-branded green marketing materials highlighting GoNano zero-VOC profile.",
        "forum_source": "Pacific Northwest Builders Exchange",
        "source_url": "https://www.google.com/search?q=pacific+northwest+roofing+contractors"
    }
]

def get_dealer_intel_records() -> List[Dict[str, Any]]:
    return DEALER_INTEL_RECORDS
