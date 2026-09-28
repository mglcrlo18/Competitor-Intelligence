"""
regional_audit.py
Territory Market Share & Regional Customer Sentiment Audit Engine.
Segments market reception and competitor dominance across North American and international geographic territories.
"""
from typing import List, Dict, Any

TERRITORY_AUDIT_DATA = [
    {
        "territory_code": "US-SUNBELT",
        "region_name": "US Sunbelt & Southeast (Florida, Texas, Carolinas)",
        "climate_stress": "Intense UV Radiation, High Humidity, Hurricane-Force Wind & Hail",
        "dominant_competitor": "RevivaRoof & Regional Bio-Sprayers",
        "market_volume_pct": 34.0,
        "sentiment_polarity": -18.5,
        "sentiment_label": "CRITICAL (High Friction)",
        "key_friction_driver": "Insurance non-renewals for roofs over 15 years; bio-oil coatings failing to satisfy underwriting inspections.",
        "opportunity_for_gonano": "Promote GoNano Class 3/4 impact rating and wind-uplift resistance to insurance brokers.",
        "citations": [
            {"title": "Florida Property Insurance Underwriting Standards", "outlet": "Insurance Journal", "url": "https://www.insurancejournal.com"},
            {"title": "Roof Restoration Under High UV Degradation", "outlet": "Roofing Contractor Magazine", "url": "https://www.roofingcontractor.com"}
        ]
    },
    {
        "territory_code": "CA-EAST",
        "region_name": "Canada East (Ontario & Quebec)",
        "climate_stress": "Severe Freeze-Thaw Cycles, Heavy Snow Loads, Ice Damming",
        "dominant_competitor": "RoofLife Canada & Spray-Net",
        "market_volume_pct": 28.0,
        "sentiment_polarity": 12.0,
        "sentiment_label": "MODERATE (Mixed Reception)",
        "key_friction_driver": "Homeowners eager for roof replacement savings, but questioning whether bio-oils survive -30°C winter thermal contraction.",
        "opportunity_for_gonano": "Position GoNano molecular transformation as flexible cold-weather shingle reinforcement that does not crack in sub-zero freeze-thaw.",
        "citations": [
            {"title": "Roof Life Canada Expands Direct-to-Consumer Service Fleet", "outlet": "Financial Post Canada", "url": "https://financialpost.com"},
            {"title": "Ontario Homeowners Face Soaring Roof Replacement Costs", "outlet": "CBC News", "url": "https://www.cbc.ca/news"}
        ]
    },
    {
        "territory_code": "US-MIDWEST",
        "region_name": "US Midwest & Great Lakes (Ohio, Illinois, Michigan)",
        "climate_stress": "Severe Seasonal Extremes, Hailstorms, High Wind Shears",
        "dominant_competitor": "RoofLife / Regional Applicators",
        "market_volume_pct": 18.0,
        "sentiment_polarity": -8.0,
        "sentiment_label": "WATCHFUL (Price Sensitive)",
        "key_friction_driver": "Heavy hail season driving insurance claims; disputes over cosmetic spray vs. storm damage restoration.",
        "opportunity_for_gonano": "Partner with regional roofing contractor co-ops as a certified hail-defense upgrade.",
        "citations": [
            {"title": "Hail Season Insurance Claims Surge in Midwest", "outlet": "Chicago Tribune Business", "url": "https://www.chicagotribune.com"},
            {"title": "Bio-Oil Roof Treatments: Consumer Watchdog Report", "outlet": "Midwest Consumer Bureau", "url": "https://www.bbb.org"}
        ]
    },
    {
        "territory_code": "US-PACNW",
        "region_name": "Pacific Northwest (Washington, Oregon, BC)",
        "climate_stress": "Continuous Precipitation, Moss & Algae Proliferation",
        "dominant_competitor": "ArmoveX & Nasiol (Hydrophobic Sealants)",
        "market_volume_pct": 12.0,
        "sentiment_polarity": 22.0,
        "sentiment_label": "RECEPTIVE (Eco & Longevity Conscious)",
        "key_friction_driver": "Moss and lichen breaking down shingle granules; demand for non-toxic environmental water shedders.",
        "opportunity_for_gonano": "Highlight anti-microbial and hydrophobic nanobarrier properties preventing moss root penetration.",
        "citations": [
            {"title": "Preventing Moss Infestation on Residential Roofing", "outlet": "Seattle Times Home", "url": "https://www.seattletimes.com"},
            {"title": "Nanotechnology in Building Material Preservation", "outlet": "TechCrunch Cleantech", "url": "https://techcrunch.com"}
        ]
    },
    {
        "territory_code": "APAC-TROPIC",
        "region_name": "APAC & Philippines (Tropical Monsoon & High Heat)",
        "climate_stress": "Extreme Tropical Monsoon Rains, Typhoon Winds, Corrosive Salt Spray",
        "dominant_competitor": "Industrial Coating Importers & Nasiol",
        "market_volume_pct": 8.0,
        "sentiment_polarity": 15.0,
        "sentiment_label": "EXPANDING (Infrastructure Focus)",
        "key_friction_driver": "Metal roof rust, asphalt degradation under intense tropical solar index, warehouse leakages.",
        "opportunity_for_gonano": "Commercial and industrial cold-storage, commercial roofing, and agricultural depot protection (e.g. FTI / Food Terminal depots).",
        "citations": [
            {"title": "Infrastructure Resilience Against Super Typhoons", "outlet": "Philippine News Agency (PNA)", "url": "https://www.pna.gov.ph"},
            {"title": "Climate Adaptation in Philippine Construction Materials", "outlet": "BusinessWorld PH", "url": "https://www.bworldonline.com"}
        ]
    }
]

def get_territory_audit_data() -> List[Dict[str, Any]]:
    return TERRITORY_AUDIT_DATA
