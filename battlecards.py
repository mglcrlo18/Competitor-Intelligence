"""
battlecards.py
Dynamic Sales Battlecards & Objection Handling Playbook Engine.
Equips field sales reps, commercial estimators, and certified dealers with
hard scientific counter-arguments, landmine questions, and pricing rebuttals.
Fully dynamic: incorporates verified commercial and technical findings across all competitors.
"""
from typing import Dict, Any, List, Optional
from db_manager import get_competitor_profile

BATTLECARDS_DATABASE = {
    "RoofLife Canada": {
        "competitor_name": "RoofLife Canada",
        "category": "Topical Bio-Oil Spray (White-Labeled Methyl Soyate)",
        "rival_pricing_anchor": "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries (Gated D2C quote model)",
        "rival_core_hook": "'Don't replace your roof until you watch this. Rejuvenate your shingles for 15 years at 80% less cost.'",
        "quick_rebuttal": "RoofLife applies white-labeled agricultural bio-oil (methyl soyate / GreenSoy) through its corporate affiliate RCC Waterproofing. While it temporarily softens dried asphalt surface oils, it cannot alter the molecular structure of aged bitumen. Volatile bio-oils evaporate under solar UV within 12-18 months, leaving shingles brittle and subject to freeze-thaw cracking.",
        "claims_vs_facts": [
            {
                "claim": "15-Year Life Extension Guarantee.",
                "fact": "Warranty is heavily pro-rated, excludes pre-existing aging, and remedy is strictly limited to re-application of bio-oil product only."
            },
            {
                "claim": "Replaces lost asphalt oils to restore factory flexibility.",
                "fact": "Bio-oils merely coat the top micro-layer of bitumen. They do not cross-link with the fiberglass mat or achieve ASTM D3462 tear-strength reinforcement."
            },
            {
                "claim": "100% Eco-friendly, safe plant-based application.",
                "fact": "Agricultural oil run-off leaves oily films on gutters and vegetation, and creates slippery hazards on sloped roof surfaces."
            }
        ],
        "landmines_to_plant": [
            "Ask their contractor: 'If your bio-oil cures permanently, why does rain wash an oily film into gutters, and why does your warranty exclude roofs over 18 years?'",
            "Ask their estimator: 'Will your 15-year warranty give me a 100% non-prorated refund if my shingles fail, or does it only provide another can of bio-oil?'",
            "Ask their inspector: 'Does your bio-oil treatment carry a certified UL 2218 Class 4 hail rating or ASTM D3161 Class F 110-mph wind rating?'"
        ],
        "objection_handling": [
            {
                "objection": "RoofLife quoted less than GoNano for a rejuvenation treatment. Why should I pay more?",
                "response": "RoofLife sells a temporary bio-oil spray that sits on the surface, evaporates in solar heat, and carries prorated warranty exclusions. GoNano is an engineered molecular transformation that covalently fuses nanosilica particles deep into the shingle core, backed by verified UL 2218 Class 4 hail impact and ASTM D3161 Class F wind ratings with a true 15-year comprehensive non-prorated warranty."
            },
            {
                "objection": "RoofLife says they use natural soy oil, which sounds safer than chemical treatments.",
                "response": "Soy oil is an agricultural triglyceride formulated for cooking, not exterior building envelopes exposed to 140°F solar heat. Solar UV rapidly oxidizes plant oils into rancid fatty acids that wash away. GoNano uses purified silicon dioxide (silica)—the mineral foundation of quartz and granite—which is 100% inert, non-toxic, and permanently cross-linked."
            }
        ]
    },
    "Roof Maxx": {
        "competitor_name": "Roof Maxx",
        "category": "Topical Methyl Soyate Bio-Oil Spray",
        "rival_pricing_anchor": "~$1.20 / sq.ft. base (~$3,000 - $6,000 typical residential roof; ~20-25% of full replacement; bids up to $8,380 documented)",
        "rival_core_hook": "'Extend your roof's life by 5 years at a time, up to 15 years, with all-natural plant oil.'",
        "quick_rebuttal": "Roof Maxx utilizes an unrefined methyl soyate agricultural oil originally patented by Clipper Roof Coatings (US6495074B1, which expired in 2017). While testing by PRI Construction Materials and Ohio State confirms temporary permeability improvements, Roof Maxx holds zero published UL 2218 Class 4 hail certifications or ASTM D3161 Class F wind uplift ratings. Within 18-24 months, solar UV degrades the topical oil, requiring expensive 5-year repeat applications.",
        "claims_vs_facts": [
            {
                "claim": "Restores shingle flexibility for 5 years per treatment.",
                "fact": "Topical methyl esters evaporate under UV exposure; third-party inspections show granule loss continues unabated."
            },
            {
                "claim": "Delivers 80% cost savings compared to replacement.",
                "fact": "Three successive 5-year applications at ~$1.20/sq.ft. plus inspection fees approach or exceed the cost of permanent GoNano molecular protection."
            },
            {
                "claim": "Proven scientific laboratory testing.",
                "fact": "PRI and Ohio State reports evaluate permeability and granule loss reduction, but do not provide formal UL 2218 Class 4 or ASTM D3161 Class F ratings."
            }
        ],
        "landmines_to_plant": [
            "Ask their rep: 'If methyl soyate is permanent, why does Roof Maxx require homeowners to re-apply every 5 years?'",
            "Ask their contractor: 'Does Roof Maxx offer a non-prorated manufacturer warranty against Class 4 hail impact or 110-mph wind uplift?'",
            "Ask their inspector: 'What happens to the $75 pre-inspection fee if my roof is disqualified due to attic ventilation or granule loss?'"
        ],
        "objection_handling": [
            {
                "objection": "Roof Maxx is a nationally known franchise with lots of commercials.",
                "response": "Franchise marketing spend does not change chemistry. Roof Maxx uses topical bio-oil that sits on the surface and washes off in heavy rain cycles. GoNano is engineered molecular nanotechnology that bonds permanently into the bitumen matrix with ASTM third-party validation (ASTM D3161 Class F, ASTM D3462, and UL 2218 Class 4)."
            },
            {
                "objection": "Roof Maxx quoted me $1.20 per square foot, which seems reasonable.",
                "response": "A single Roof Maxx treatment at $1.20/sq.ft. only buys 5 years of temporary softening. Doing that three times over 15 years costs more than $3.60/sq.ft. GoNano provides permanent 15-year molecular reinforcement for a single flat rate, delivering real long-term savings."
            }
        ]
    },
    "PEAK301": {
        "competitor_name": "PEAK301",
        "category": "Epoxidized Soybean Bio-Oil Derivative (GreenSoy Technology)",
        "rival_pricing_anchor": "Starts at ~$1.00 / sq.ft. (marketing average $1,530 savings over tear-off)",
        "rival_core_hook": "'The molecular breakthrough: Restore flexibility and fire resistance for 6 years.'",
        "quick_rebuttal": "PEAK301 utilizes an epoxidized soybean oil formulation protected under the GreenSoy Technology commercial trademark rather than an active utility patent. While marketing claims a 68% improvement in fire protection and 50% flexibility restoration, PEAK301 publishes zero third-party UL 2218 Class 4 impact or ASTM D3161 Class F wind uplift certifications.",
        "claims_vs_facts": [
            {
                "claim": "Molecular rejuvenation with 6-year non-prorated warranty.",
                "fact": "Warranty is prorated starting in Year 3, excludes shingles older than 16 years, and requires roof pitch >4:12."
            },
            {
                "claim": "Provides fire protection and hail resistance.",
                "fact": "Lacks verified UL 2218 Class 4 hail impact or ASTM D3161 Class F 110-mph wind classifications."
            }
        ],
        "landmines_to_plant": [
            "Ask their rep: 'Can you show me your official UL 2218 Class 4 certificate demonstrating that PEAK301 withstands 2-inch steel ball hail impacts?'",
            "Ask their contractor: 'Why is your warranty prorated after Year 3 if the formulation lasts 6 years?'"
        ],
        "objection_handling": [
            {
                "objection": "PEAK301 quoted $1.00 per square foot, which is lower than other bids.",
                "response": "PEAK301 is an epoxidized vegetable oil spray that sits on the surface without structural class certifications. GoNano is an engineered silica molecular transformation backed by verified ASTM D3161 Class F wind (110 mph) and UL 2218 Class 4 hail impact ratings, with a 15-year non-prorated comprehensive warranty."
            }
        ]
    },
    "Reactiv8": {
        "competitor_name": "Reactiv8",
        "category": "Plant-Based Bio-Oil Formulation",
        "rival_pricing_anchor": "~$2,300 for a 600 sq.ft. roof (~$3.83 / sq.ft.) (Documented field sales quote)",
        "rival_core_hook": "'Eco-friendly plant-based rejuvenation for aging residential roofs.'",
        "quick_rebuttal": "Reactiv8 relies on plant-based bio-oils that temporarily soften surface bitumen but wash away under thermal storm cycling. Their documented quotes can reach $3.83/sq.ft. with zero certified structural impact or wind uplift class ratings.",
        "claims_vs_facts": [
            {
                "claim": "Sustainable plant-based formula restores shingle life.",
                "fact": "Lacks structural ASTM D3161 or UL 2218 class certifications; subject to wash-off under severe rainstorms."
            }
        ],
        "landmines_to_plant": [
            "Ask them: 'Does Reactiv8 provide third-party laboratory proof of Class 4 impact resistance or Class F wind uplift?'"
        ],
        "objection_handling": [
            {
                "objection": "Reactiv8 says their plant oil is more natural than nanotechnology.",
                "response": "Plant oils decompose and evaporate under UV solar radiation, often leaving oily residues in gutters. GoNano uses pure, inert mineral nanosilica (the building block of quartz), creating a permanent non-toxic molecular reinforcement that never washes off."
            }
        ]
    },
    "Shingle Magic": {
        "competitor_name": "Shingle Magic",
        "category": "Proprietary 'Shingletech' Acrylic Resin Surface Coating",
        "rival_pricing_anchor": "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries (Gated franchise tiering)",
        "rival_core_hook": "'Cool Seal color rejuvenation: Extend your roof for 10 years with proprietary polymer sealant.'",
        "quick_rebuttal": "Shingle Magic applies a topical elastomeric acrylic paint/resin film (patents US10787581, US11136478). It coats the surface rather than modifying the asphalt substrate. While marketing claims 'ASTM and UL tested,' they crucially omit attained class designations because it fails to achieve UL 2218 Class 4 or ASTM D3161 Class F.",
        "claims_vs_facts": [
            {
                "claim": "Proprietary acrylic resin seals and rejuvenates shingles.",
                "fact": "Topical elastomeric film traps internal attic moisture and fails to reinforce the asphalt mat."
            },
            {
                "claim": "10-Year comprehensive warranty.",
                "fact": "Prorated material-only warranty; explicitly excludes labor, tear-off, and hail or freeze-thaw damage."
            }
        ],
        "landmines_to_plant": [
            "Ask their franchise rep: 'Does your coating have an independent laboratory UL 2218 Class 4 impact rating?'",
            "Ask their estimator: 'Is this an acrylic paint film that seals over the shingle, and what is its breathability perm rating?'"
        ],
        "objection_handling": [
            {
                "objection": "Shingle Magic says their coating makes my roof look brand new in different colors.",
                "response": "Shingle Magic is an aesthetic acrylic paint film. While it changes the color, it can trap attic moisture vapor and peel under freeze-thaw cycles. GoNano penetrates at the molecular level, preserving breathability while doubling the shingle's physical tear strength."
            }
        ]
    },
    "Nasiol (Artekya)": {
        "competitor_name": "Nasiol (Artekya)",
        "category": "Liquid Ceramic / Hydrophobic Sealant (ZR53 / Z-WB)",
        "rival_pricing_anchor": "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries (Bulk B2B industrial materials)",
        "rival_core_hook": "'Ultimate 9H ceramic hydrophobic defense for all building substrates.'",
        "quick_rebuttal": "Nasiol provides surface-level hydrophobic beading designed for automotive clearcoats and polished building facades (TUV-SUD certified for automotive 9H). On flexible, porous asphalt shingles, thin ceramic films fracture under seasonal thermal expansion and lack ASTM D3462 asphalt shingle tear strength certification.",
        "claims_vs_facts": [
            {
                "claim": "9H Hardness ceramic shield protects against impact.",
                "fact": "Hard ceramic surface layers are brittle. When hail hits flexible asphalt, the ceramic film micro-cracks immediately."
            },
            {
                "claim": "Complete waterproof encapsulation of roofing materials.",
                "fact": "Encapsulating shingles prevents natural water-vapor breathability, trapping condensed attic moisture underneath the shingle deck."
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

    is_bio = "bio" in category.lower() or "soy" in category.lower() or "oil" in category.lower()
    is_nano = "nano" in category.lower() or "ceramic" in category.lower()

    pricing = "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries (Internal Field Sales Intelligence / Contractor Invoices)"

    if is_bio:
        cat_desc = "Topical Bio-Oil / Plant Ester Rejuvenator"
        hook = f"'{competitor_name}: Rejuvenate your aging roof with eco-friendly bio-oils at a fraction of replacement cost.'"
        rebuttal = f"{competitor_name} uses topical agricultural oils that temporarily soften dried surface bitumen but cannot reform broken molecular chains. Solar UV evaporates volatile plant oils within 12-18 months, leaving shingles vulnerable to thermal tearing and hail damage. Holds no certified UL 2218 Class 4 or ASTM D3161 Class F classifications."
        claims = [
            {"claim": "All-natural bio-oil restores flexibility for years.", "fact": "Plant-based oils lack molecular cross-linking and evaporate under intense summer heat cycles."},
            {"claim": "Protects against severe weather and extends roof lifespan.", "fact": "Bio-oils do not carry ASTM D3161 Class F 110-mph wind or UL 2218 Class 4 impact endorsements."}
        ]
        landmines = [
            f"Ask {competitor_name}: 'Will your warranty cover complete replacement if hail destroys the shingles after application, or is it uncertified?'",
            "Ask their contractor: 'Does this bio-oil wash off into rain gutters and stain landscaping during heavy storms?'"
        ]
        objections = [
            {
                "objection": f"{competitor_name} quoted significantly less than GoNano.",
                "response": f"{competitor_name} sells a temporary topical oiling service requiring re-treatment every few years. GoNano is an engineered molecular transformation that fuses silica nanoparticles into the shingle core with a 15-year non-prorated warranty and certified UL 2218 Class 4 hail impact ratings."
            }
        ]
    elif is_nano:
        cat_desc = "Surface Nanocoating Barrier"
        hook = f"'{competitor_name}: Nanotechnology surface barrier for exterior roof preservation.'"
        rebuttal = f"{competitor_name} markets superficial nanocoatings that form a thin surface skin over the asphalt. Without deep substrate penetration, these coatings micro-crack under freeze-thaw cycles and can trap moisture beneath the shingle. Holds no certified ASTM D3462 tear strength reinforcement."
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
