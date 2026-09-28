"""
battlecards.py
Dynamic Sales Battlecards & Objection Handling Playbook Engine.
Equips field sales reps, commercial estimators, and certified dealers with
hard scientific counter-arguments, landmine questions, and pricing rebuttals.
Fully dynamic: supports all competitors from the Google Sheet & database.
"""
from typing import Dict, Any, List
from db_manager import get_competitor_profile

BATTLECARDS_DATABASE = {
    "RoofLife Canada": {
        "competitor_name": "RoofLife Canada",
        "category": "Topical Bio-Oil Spray",
        "rival_pricing_anchor": "$1,800 - $2,800 per typical home (approx. $0.65 - $0.85/sq.ft.)",
        "rival_core_hook": "'Don't replace your roof until you watch this. Rejuvenate your shingles for 15 years at 80% less cost.'",
        "quick_rebuttal": "RoofLife applies an agricultural bio-oil (soybean/vegetable ester) that temporarily softens dried asphalt surface oils, but cannot alter the chemical structure of aged asphalt. Within 12-18 months, volatile bio-oils evaporate under intense solar UV, leaving shingles brittle and washed out.",
        "claims_vs_facts": [
            {
                "claim": "15-Year Life Extension Guarantee.",
                "fact": "Warranty is heavily pro-rated and contains pre-existing roof age exclusions. Laboratory testing shows topical bio-oils lose flexibility benefits after seasonal UV degradation."
            },
            {
                "claim": "Replaces lost asphalt oils to restore factory flexibility.",
                "fact": "Bio-oils merely coat and swell the top micro-layer of bitumen. They do not cross-link with the underlying fiberglass mat or prevent granule delamination."
            },
            {
                "claim": "100% Eco-friendly, safe plant-based application.",
                "fact": "Agricultural oil run-off leaves greasy stains on gutters, driveways, and vegetation, and creates slippery hazards on sloped surfaces during heavy rain."
            }
        ],
        "landmines_to_plant": [
            "Ask their contractor: 'If your bio-oil cures into the shingle, why does rain wash an oily film into our gutters and downspouts?'",
            "Ask their estimator: 'Will your 15-year warranty give me a 100% non-prorated refund if my shingles lose granules next spring, or is it pro-rated?'",
            "Ask their inspector: 'Does your bio-oil treatment increase the shingle tear-strength and wind-uplift rating to Class 3 or Class 4, or is it uncertified?'"
        ],
        "objection_handling": [
            {
                "objection": "RoofLife quoted me $1,800, while GoNano is $3,200. Why should I pay more?",
                "response": "RoofLife is selling a temporary oiling service that needs re-treatment every few years and washes off. GoNano is an engineered molecular transformation that fuses silica nanoparticles into the bitumen at the molecular level, backed by a true 15-year warranty. Paying $1,800 twice for temporary oiling costs more than permanent GoNano protection."
            },
            {
                "objection": "RoofLife says they use natural soy oil, which sounds safer than chemicals.",
                "response": "Soy oil is formulated for cooking, not exterior building envelopes exposed to 140°F solar heat. Solar UV rapidly oxidizes plant oils into rancid fatty acids. GoNano uses purified silicon dioxide (silica)—the same mineral element found in quartz and granite—which is 100% inert, non-toxic, non-volatile, and cannot wash away."
            }
        ]
    },
    "Nasiol (Artekya)": {
        "competitor_name": "Nasiol (Artekya)",
        "category": "Liquid Ceramic / Hydrophobic Sealant",
        "rival_pricing_anchor": "$1.40 - $1.90 / sq.ft. (plus extensive surface prep labor)",
        "rival_core_hook": "'Ultimate 9H ceramic hydrophobic defense for all building substrates.'",
        "quick_rebuttal": "Nasiol provides surface-level hydrophobic beading designed for automotive clearcoats and polished building facades. On flexible, porous asphalt shingles, thin ceramic films fracture under seasonal thermal expansion and seal interior moisture in, accelerating blister rot.",
        "claims_vs_facts": [
            {
                "claim": "9H Hardness ceramic shield protects against impact.",
                "fact": "Hard ceramic surface layers are brittle. When hail hits flexible asphalt, the ceramic film micro-cracks immediately."
            },
            {
                "claim": "Complete waterproof encapsulation of roofing materials.",
                "fact": "Encapsulating shingles prevents natural water-vapor breathability, trapping condensed attic moisture underneath the shingle deck and rotting plywood sheathing."
            }
        ],
        "landmines_to_plant": [
            "Ask them: 'Is your ceramic coating certified as breathable (perm rating > 5) so my roof deck doesn't rot from attic moisture condensation?'",
            "Ask them: 'Can you show me ASTM D3462 nail tear-strength data demonstrating that your ceramic liquid reinforces the asphalt mat?'"
        ],
        "objection_handling": [
            {
                "objection": "Nasiol showed me water beading off a shingle like a freshly waxed car.",
                "response": "Water beading is cosmetic surface tension. When water beads on a shingle, it does not stop internal asphalt embrittlement or hail impacts. GoNano penetrates deep into the shingle core, permanently cross-linking the bitumen so the shingle stays structurally pliable and hurricane-resistant."
            }
        ]
    },
    "RevivaRoof": {
        "competitor_name": "RevivaRoof",
        "category": "Restorative Bio-Spray",
        "rival_pricing_anchor": "$1,900 - $2,900 per home",
        "rival_core_hook": "'The Science of Compliance: Guaranteed insurance alignment and roof life extension.'",
        "quick_rebuttal": "RevivaRoof heavily markets to insurance brokers under their 'Science of Compliance' campaign. However, forensic adjusters evaluate shingle granular adhesion and physical wind resistance, not surface oiling. When insurance claims are filed after major storms, uncertified bio-oil coatings are rejected as cosmetic maintenance.",
        "claims_vs_facts": [
            {
                "claim": "Guarantees insurance policy renewal by restoring shingle compliance.",
                "fact": "Insurance carriers require certified ASTM impact and wind ratings. Most adjusters classify bio-oils as temporary cosmetic coatings."
            }
        ],
        "landmines_to_plant": [
            "Ask them: 'Can you provide a letter from my insurance company stating that your bio-oil spray qualifies for an insurance premium discount or halts policy cancellation?'",
            "Ask them: 'Does this treatment carry an ASTM D3161 Class F 110-mph wind rating endorsement?'"
        ],
        "objection_handling": [
            {
                "objection": "My insurance company told me I need a new roof, and RevivaRoof said their spray will fix it.",
                "response": "Insurance adjusters use drone thermal imaging and physical tear tests. When an adjuster finds a roof that was merely sprayed with agricultural oil, they will still flag it as high-risk. GoNano provides certified engineering reports demonstrating measurable substrate reinforcement."
            }
        ]
    },
    "Roof Maxx": {
        "competitor_name": "Roof Maxx",
        "category": "Methyl Soyate Bio-Oil Spray",
        "rival_pricing_anchor": "$0.75 - $1.00 / sq.ft. ($1,800 - $2,600 per residential roof)",
        "rival_core_hook": "'Extend your roof's life by 5 years at a time, up to 15 years, with all-natural plant oil.'",
        "quick_rebuttal": "Roof Maxx's methyl soyate formula is a light bio-solvent that acts like lotion on dry skin. While shingles feel temporarily pliable for a few months, the bio-oil does not repair cracked bitumen chains or re-anchor loose ceramic granules. Within 18-24 months, UV solar radiation burns away the surface oil, requiring expensive repeated applications.",
        "claims_vs_facts": [
            {
                "claim": "Restores shingle flexibility for 5 years per treatment.",
                "fact": "Topical methyl esters evaporate under UV exposure; third-party inspections show granule loss continues unabated."
            },
            {
                "claim": "Meets 80% cost savings compared to replacement.",
                "fact": "Three 5-year applications plus pre-inspection fees equal or exceed the cost of permanent GoNano molecular protection."
            }
        ],
        "landmines_to_plant": [
            "Ask their rep: 'If methyl soyate is permanent, why do you require re-application every 5 years?'",
            "Ask their contractor: 'Does Roof Maxx offer a non-prorated manufacturer warranty against Class 3 or 4 hail impact?'"
        ],
        "objection_handling": [
            {
                "objection": "Roof Maxx is a nationally known franchise with lots of commercials.",
                "response": "Franchise marketing spend does not change chemistry. Roof Maxx uses topical bio-oil that sits on the surface and washes off in heavy rain. GoNano is engineered molecular nanotechnology that bonds permanently into the bitumen matrix with ASTM third-party validation."
            }
        ]
    }
}

def get_battlecard(competitor_name: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves or dynamically builds a full battlecard for any target competitor."""
    if not competitor_name or not str(competitor_name).strip():
        competitor_name = "RoofLife Canada"
    competitor_name = str(competitor_name).strip()
    for key, card in BATTLECARDS_DATABASE.items():
        if key.lower() in competitor_name.lower() or competitor_name.lower() in key.lower():
            return card

    # Dynamically build based on competitor profile
    prof = get_competitor_profile(competitor_name)
    category = prof.get("category", "Roof Restoration & Preservation") if prof else "Roof Restoration"
    tech = prof.get("core_technology", "Surface restoration formulation") if prof else "Surface coating"
    domain = prof.get("domain", f"{competitor_name.lower().replace(' ', '')}.com") if prof else f"{competitor_name.lower().replace(' ', '')}.com"
    notes = prof.get("notes", "") if prof else ""

    is_bio = "bio" in category.lower() or "soy" in category.lower() or "oil" in category.lower()
    is_nano = "nano" in category.lower() or "ceramic" in category.lower()

    if is_bio:
        cat_desc = "Topical Bio-Oil / Plant Ester Rejuvenator"
        pricing = "$0.65 - $0.90 / sq.ft. (approx. $1,700 - $2,500 per home)"
        hook = f"'{competitor_name}: Rejuvenate your aging roof with eco-friendly bio-oils at a fraction of replacement cost.'"
        rebuttal = f"{competitor_name} uses topical agricultural oils that temporarily soften dried surface bitumen but cannot reform broken molecular chains. Solar UV evaporates volatile plant oils within 12-18 months, leaving shingles vulnerable to thermal tearing and hail damage."
        claims = [
            {"claim": "All-natural bio-oil restores flexibility for years.", "fact": "Plant-based oils lack molecular cross-linking and evaporate under intense summer heat cycles."},
            {"claim": "Protects against severe weather and extends roof lifespan.", "fact": "Bio-oils do not carry ASTM D3462 Class 3/4 impact or wind-uplift endorsements."}
        ]
        landmines = [
            f"Ask {competitor_name}: 'Will your warranty cover complete replacement if hail destroys the shingles after application?'",
            "Ask their contractor: 'Does this bio-oil wash off into rain gutters and stain landscaping during heavy storms?'"
        ]
        objections = [
            {
                "objection": f"{competitor_name} quoted significantly less than GoNano.",
                "response": f"{competitor_name} is selling a temporary oiling service requiring re-treatment every few years. GoNano is an engineered molecular transformation that fuses silica nanoparticles into the shingle core with a 15-year non-prorated warranty."
            }
        ]
    elif is_nano:
        cat_desc = "Surface Nanocoating Barrier"
        pricing = "$1.10 - $1.70 / sq.ft."
        hook = f"'{competitor_name}: Nanotechnology surface barrier for exterior roof preservation.'"
        rebuttal = f"{competitor_name} markets superficial nanocoatings that form a thin surface skin over the asphalt. Without deep substrate penetration, these coatings micro-crack under freeze-thaw cycles and can trap moisture beneath the shingle."
        claims = [
            {"claim": "Nanotechnology barrier seals shingles from weather.", "fact": "Superficial coatings can trap attic moisture vapor and peel under thermal cycling."}
        ]
        landmines = [
            f"Ask {competitor_name}: 'Is your coating breathable (allowing attic vapor to escape) or is it a topical film?'",
            "Ask their rep: 'Can you show me third-party lab proof that your formula penetrates into the bitumen mat?'"
        ]
        objections = [
            {
                "objection": f"Why GoNano over {competitor_name}'s nanocoating?",
                "response": f"{competitor_name} provides a topical barrier. GoNano doesn't just coat the surface—it infuses silica and alumina nanoparticles deep into the asphalt matrix, permanently strengthening the shingle."
            }
        ]
    else:
        cat_desc = f"{category} Provider"
        pricing = "$0.75 - $1.20 / sq.ft."
        hook = f"'{competitor_name}: Professional roof preservation and life extension.'"
        rebuttal = f"Most regional roof restorers apply topical sealants or basic cosmetic washes. While shingles look darker initially, the underlying asphalt remains brittle. GoNano provides certified molecular reinforcement."
        claims = [
            {"claim": "Long-term roof protection guarantee.", "fact": "Guarantees are typically prorated with exclusions for pre-existing aging and hail impact."}
        ]
        landmines = [
            f"Ask {competitor_name}: 'Is your warranty prorated, and does it cover labor and materials?'",
            "Ask them: 'Does this treatment increase physical tear strength according to ASTM D3462?'"
        ]
        objections = [
            {
                "objection": f"Why should I choose GoNano over {competitor_name}?",
                "response": "GoNano is backed by independent ASTM laboratory testing and a true 15-year comprehensive warranty, delivering permanent structural transformation rather than cosmetic maintenance."
            }
        ]

    return {
        "competitor_name": competitor_name,
        "category": cat_desc,
        "rival_pricing_anchor": pricing,
        "rival_core_hook": hook,
        "quick_rebuttal": rebuttal,
        "claims_vs_facts": claims,
        "landmines_to_plant": landmines,
        "objection_handling": objections
    }
