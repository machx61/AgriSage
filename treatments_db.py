# treatments_db.py
"""
Agrisage Knowledge Base
Regional Context: Himachal Pradesh (Hills Zone)
Focus: Indigenous Knowledge Systems (IKS) & Vrikshayurveda Practices
"""

THEME_COLORS = {
    "mint_green": {"bg": "#E8F8F5", "border": "#2ECC71", "text": "#117A65"},
    "soft_blue": {"bg": "#EBF5FB", "border": "#3498DB", "text": "#1B4F72"},
    "pastel_green": {"bg": "#EAFAF1", "border": "#27AE60", "text": "#196F3D"},
    "soft_yellow": {"bg": "#FEFDE8", "border": "#F1C40F", "text": "#7D6608"},
    "butter_yellow": {"bg": "#FEF9E7", "border": "#F39C12", "text": "#7E5109"},
    "lavender": {"bg": "#F4ECF7", "border": "#8E44AD", "text": "#512E5F"},
    "peach": {"bg": "#FBEEE6", "border": "#E67E22", "text": "#784212"},
    "soft_pink": {"bg": "#FDEDEC", "border": "#E74C3C", "text": "#78281F"},
    "sky_blue": {"bg": "#EAF2F8", "border": "#2980B9", "text": "#1A5276"},
}

TOMATO_DISEASES = {
    "leaf_curl_virus": {
        "name": "Tomato Leaf Curl Virus (Vata Imbalance)",
        "cultural": [
            {
                "action": "Traditional Seed Soak",
                "emoji": "💧",
                "theme": "lavender",
                "summary": "Boost seed immunity right from the start using local Himachal methods!",
                "how": "Soak seeds in cow urine before sowing, especially for kharif-season crops.",
                "frequency": "Once, before sowing"
            },
            {
                "action": "Bright Yellow Fly Traps",
                "emoji": "🟨",
                "theme": "butter_yellow",
                "summary": "Hang yellow sticky cards near the plant canopy to catch sap-sucking whiteflies.",
                "how": "Hang near plant canopy to monitor and trap whitefly vectors.",
                "frequency": "Set once, replace every 2-3 weeks"
            },
            {
                "action": "Quick Removal Action",
                "emoji": "✂️",
                "theme": "soft_pink",
                "summary": "Remove sick plants right away so the Vata imbalance doesn't spread!",
                "how": "Remove and destroy entire plant immediately on symptom appearance.",
                "frequency": "Immediately when identified"
            }
        ],
        "biological": [
            {
                "action": "Panchagavya Root Drench",
                "emoji": "🥛",
                "theme": "soft_blue",
                "summary": "A powerful classical fermented tonic of dairy and cow urine to restore root strength.",
                "how": "Ferment cow milk, curd, ghee, cow urine, and cow dung. Dilute and irrigate the root zone.",
                "frequency": "Every 10-14 days"
            },
            {
                "action": "Neem Leaf Smoke Bath",
                "emoji": "💨",
                "theme": "mint_green",
                "summary": "Purify the air around the leaves using traditional Ayurvedic fumigation.",
                "how": "Burn dried neem leaves near the plant and allow the smoke to pass near the foliage.",
                "frequency": "As needed"
            },
            {
                "action": "Gentle Neem Oil Spa",
                "emoji": "🌿",
                "theme": "pastel_green",
                "summary": "Soapy neem bath prevents whiteflies from spreading the curl virus.",
                "how": "Mix 5 ml neem oil with a couple of drops of liquid soap in 1 litre water. Spray whole plant.",
                "frequency": "Every 7 days"
            }
        ]
    },
    "early_blight": {
        "name": "Early Blight (Pitta Imbalance)",
        "cultural": [
            {
                "action": "Wood Ash Dusting",
                "emoji": "🪵",
                "theme": "soft_yellow",
                "summary": "A simple, local Himachal trick to dry out fungi around the roots!",
                "how": "Dust wood ash directly around the base of the plant.",
                "frequency": "Refresh as needed"
            },
            {
                "action": "Pine Needle Blanket",
                "emoji": "🌲",
                "theme": "peach",
                "summary": "Use fallen pine needles as a protective mulch layer over the soil.",
                "how": "Spread Pinus roxburgii needles around the base of the plant, 5-7cm thick.",
                "frequency": "Refresh every 3-4 weeks"
            }
        ],
        "biological": [
            {
                "action": "Licorice & Honey Root Drink",
                "emoji": "🍯",
                "theme": "butter_yellow",
                "summary": "A soothing classical Pitta-balancing decoction to cool the plant's system.",
                "how": "Prepare a decoction of Yashtimadhu (licorice root) and Madhuca, mix with milk and honey, and irrigate.",
                "frequency": "As needed"
            },
            {
                "action": "Cow Dung Bio-Mix",
                "emoji": "🐄",
                "theme": "mint_green",
                "summary": "A local farm-made pesticide paste applied right to the soil.",
                "how": "Mix cow dung with water and apply to the plant/soil as a natural pesticide.",
                "frequency": "As needed"
            }
        ]
    },
    "powdery_mildew": {
        "name": "Powdery Mildew (Kapha Imbalance)",
        "cultural": [
            {
                "action": "Breezy Plant Spacing",
                "emoji": "🌬️",
                "theme": "sky_blue",
                "summary": "Give plants plenty of personal space to dry out excess Kapha moisture.",
                "how": "Ensure adequate spacing at planting for maximum airflow.",
                "frequency": "At planting time"
            },
            {
                "action": "Buttermilk Pest Traps",
                "emoji": "🥛",
                "theme": "peach",
                "summary": "A clever local trick from Bilaspur to trap pests using fermented dairy!",
                "how": "Set out containers of buttermilk around the crop to act as local pest traps.",
                "frequency": "Refresh weekly"
            }
        ],
        "biological": [
            {
                "action": "Morning Milk Glow Spray",
                "emoji": "☀️",
                "theme": "pastel_green",
                "summary": "Diluted milk under morning sun creates a natural antiseptic action against white mildew.",
                "how": "Mix 1 part milk with 9 parts water. Spray on leaves in morning sunlight.",
                "frequency": "Every 7 days"
            }
        ]
    },
    "root_knot_nematode": {
        "name": "Root-Knot Nematode (Worm Infestation)",
        "cultural": [
            {
                "action": "Neem Cake Soil Mix",
                "emoji": "🪨",
                "theme": "lavender",
                "summary": "Enrich the soil with bitter neem cake to make it hostile for root worms.",
                "how": "Mix neem cake into the soil before planting.",
                "frequency": "Once at planting, refresh every 2-3 months"
            },
            {
                "action": "Marigold Flower Guards",
                "emoji": "🌼",
                "theme": "butter_yellow",
                "summary": "Beautiful marigold roots naturally repel hidden nematodes!",
                "how": "Plant marigolds near or before transplanting tomatoes.",
                "frequency": "At or before planting time"
            }
        ],
        "biological": [
            {
                "action": "7-Day Cold Water & Dung Paste",
                "emoji": "🧊",
                "theme": "sky_blue",
                "summary": "A classical shock-and-heal treatment for infested root zones.",
                "how": "Irrigate with cold water for 7 consecutive days, then apply a cow dung, water, and milk paste to roots.",
                "frequency": "7 consecutive days"
            },
            {
                "action": "Mustard & Vacha Root Paste",
                "emoji": "🌿",
                "theme": "mint_green",
                "summary": "A potent Ayurvedic herbal paste applied directly to affected plant parts.",
                "how": "Combine white mustard, Vacha, and Kushta into a paste. Apply directly to affected root/plant part.",
                "frequency": "As needed"
            }
        ]
    },
    "stem_wound_damage": {
        "name": "Physical Stem Damage & Cracking",
        "cultural": [
            {
                "action": "Preventative Care",
                "emoji": "🌱",
                "theme": "sky_blue",
                "summary": "Protect stems from tools and heavy wind to prevent pathogen entry points.",
                "how": "Handle plants gently during pruning and weeding.",
                "frequency": "Ongoing"
            }
        ],
        "biological": [
            {
                "action": "Banyan & Fig Bark Healing Paste",
                "emoji": "🩹",
                "theme": "soft_yellow",
                "summary": "A classical Ayurvedic band-aid for cracked or wounded stems!",
                "how": "Combine banyan bark, cluster fig bark, cow dung, honey, and ghee into a paste. Apply directly to the wound.",
                "frequency": "Once, or as needed until healed"
            }
        ]
    }
}

POTATO_DISEASES = {
    "late_blight": {
        "name": "Late Blight",
        "cultural": [
            {
                "action": "Ask a Local Elder",
                "emoji": "🗣️",
                "theme": "lavender",
                "summary": "No specific local HP practice is documented yet for late blight.",
                "how": "Consult local elders or use the classical Vrikshayurveda treatments below."
            }
        ],
        "biological": [
            {
                "action": "Sweet Root Licorice Bath",
                "emoji": "🌿",
                "theme": "soft_pink",
                "summary": "Give stressed potato plants a soothing licorice-honey drink to help them fight off cold wet rot!",
                "how": "Prepare a decoction of Yashtimadhu (licorice root) and Madhuca, mixed with milk and honey. Irrigate the affected plant.",
                "frequency": "Test every 10-14 days"
            },
            {
                "action": "Honey-Ghee Smoke Hug",
                "emoji": "🍯",
                "theme": "peach",
                "summary": "Wrap the sick plant in a gentle honey-ghee smoke to calm the stress before it spreads!",
                "how": "Fumigate the affected area with honey and ghee.",
                "frequency": "As needed"
            }
        ]
    },
    "early_blight": {
        "name": "Early Blight",
        "cultural": [
            {
                "action": "Ash Dust Root Cuddle",
                "emoji": "🪵",
                "theme": "soft_yellow",
                "summary": "Himachal farmers have been dusting ash around plants for generations—simple, cheap, and it works!",
                "how": "Dust wood ash around the base of the plant.",
                "frequency": "Refresh as needed"
            }
        ],
        "biological": [
            {
                "action": "Cow Dung Guardian Mix",
                "emoji": "🐄",
                "theme": "mint_green",
                "summary": "A traditional cow-dung mix that local farmers trust as a natural plant protector!",
                "how": "Mix cow dung into a natural pesticide preparation and apply to the plant/soil.",
                "frequency": "As needed"
            },
            {
                "action": "Sweet Root Licorice Bath",
                "emoji": "🌿",
                "theme": "soft_pink",
                "summary": "The same soothing licorice-honey drink also helps calm yellowing, sun-stressed leaves!",
                "how": "Prepare a decoction of Yashtimadhu (licorice root) and Madhuca, mixed with milk and honey. Irrigate.",
                "frequency": "As needed"
            }
        ]
    },
    "black_scurf_common_scab": {
        "name": "Black Scurf & Common Scab",
        "cultural": [
            {
                "action": "IKS Research Gap Identified",
                "emoji": "🕵️",
                "theme": "soft_pink",
                "summary": "Vrikshayurveda centers on trees and leaves; it doesn't have a clear category for tuber-skin conditions.",
                "how": "No HP-specific documented local practice found. Flagged for farmer interviews."
            }
        ],
        "biological": []
    },
    "bacterial_wilt": {
        "name": "Bacterial Wilt",
        "cultural": [
            {
                "action": "IKS Research Gap Identified",
                "emoji": "🕵️",
                "theme": "lavender",
                "summary": "No specific local HP practice is documented yet for bacterial wilt.",
                "how": "Consult local elders or use the classical Vrikshayurveda treatments below."
            }
        ],
        "biological": [
            {
                "action": "Sweet Root Licorice Bath",
                "emoji": "🌿",
                "theme": "soft_pink",
                "summary": "The same calming licorice-honey drink used for stressed, sun-struggling plants!",
                "how": "Prepare a decoction of Yashtimadhu (licorice root) and Madhuca, mixed with milk and honey. Irrigate.",
                "frequency": "As needed"
            }
        ]
    },
    "root_knot_nematode": {
        "name": "Root-Knot Nematode",
        "cultural": [
            {
                "action": "Neem Cake Soil Snuggle",
                "emoji": "🪨",
                "theme": "mint_green",
                "summary": "Tuck neem cake into the soil to give roots a protective, worm-unfriendly bed!",
                "how": "Mix neem cake into the soil before planting.",
                "frequency": "Once at planting, refresh every 2-3 months"
            },
            {
                "action": "Marigold Buddy Border",
                "emoji": "🌼",
                "theme": "soft_yellow",
                "summary": "Plant cheerful marigolds nearby—their roots naturally shoo pesky nematodes away!",
                "how": "Plant marigold near or before the potato crop.",
                "frequency": "At or before planting time"
            }
        ],
        "biological": [
            {
                "action": "Seven-Day Cool Splash",
                "emoji": "🧊",
                "theme": "sky_blue",
                "summary": "A week of cool water baths helps calm irritated, wiggly-worm-troubled roots!",
                "how": "Irrigate the plant with cold water for seven consecutive days.",
                "frequency": "7 consecutive days"
            },
            {
                "action": "Milk & Dung Root Paste",
                "emoji": "🐄",
                "theme": "butter_yellow",
                "summary": "A gentle homemade paste tucked right at the roots to soothe worm troubles!",
                "how": "Apply a paste of cow dung, water, and milk to the affected root area.",
                "frequency": "As needed"
            },
            {
                "action": "Mustard-Spice Root Rub",
                "emoji": "🌶️",
                "theme": "peach",
                "summary": "A zesty herbal paste that gives pesky root worms a reason to move along!",
                "how": "Combine white mustard, Vacha (sweet flag), and Kushta into a paste. Apply directly to the affected part.",
                "frequency": "As needed"
            }
        ]
    },
    "potato_tuber_moth": {
        "name": "Potato Tuber Moth (Storage Pest)",
        "cultural": [
            {
                "action": "Leafy Storage Shield",
                "emoji": "🌿",
                "theme": "pastel_green",
                "summary": "Tuck fragrant local leaves in with stored potatoes to keep hungry moths away all season!",
                "how": "Layer leaves of Lantana, Eupatorium, and Eucalyptus in with or around stored potato tubers.",
                "frequency": "At storage time, refresh as leaves dry out"
            }
        ],
        "biological": []
    }
}

RICE_DISEASES = {
    "bacterial_leaf_blight": {
        "name": "Bacterial Leaf Blight & Blast",
        "cultural": [
            {
                "action": "Bana Border Bodyguard",
                "emoji": "🌿",
                "theme": "pastel_green",
                "summary": "Plant a friendly leafy hedge of Bana right beside your baby rice nursery to keep bugs and disease away!",
                "how": "Plant Bana (Vitex negundo) alongside the paddy nursery bed.",
                "frequency": "Once at nursery establishment"
            }
        ],
        "biological": [
            {
                "action": "Ramban River Gate Guardian",
                "emoji": "🌊",
                "theme": "sky_blue",
                "summary": "Crush spiky Ramban leaves and drop them right where water enters your paddy field!",
                "how": "Crush fresh Ramban (Agave americana) leaves and place them at the water channel inlet feeding the paddy field.",
                "frequency": "Test at each irrigation cycle"
            }
        ]
    },
    "rice_hispa": {
        "name": "Rice Hispa (Leaf-Feeding Beetle)",
        "cultural": [
            {
                "action": "Ankharein Leaf Shield",
                "emoji": "🍃",
                "theme": "mint_green",
                "summary": "A traditional leafy remedy farmers swear by to keep hungry hispa beetles off rice leaves!",
                "how": "Apply ankharein leaves to control rice hispa, following local farmer practice in Kangra and Hamirpur.",
                "frequency": "As needed"
            }
        ],
        "biological": []
    },
    "post_harvest_storage": {
        "name": "Post-Harvest Grain Storage Protection",
        "cultural": [
            {
                "action": "Perru Bamboo Basket Home",
                "emoji": "🧺",
                "theme": "peach",
                "summary": "Store harvested grain in a big spindle-shaped bamboo basket—a cozy, breathable, pest-proof home!",
                "how": "Store harvested paddy and finger millet grain in large spindle-shaped bamboo baskets, locally called 'Perru'.",
                "frequency": "At harvest/storage time"
            }
        ],
        "biological": []
    }
}

WHEAT_DISEASES = {
    "yellow_rust": {
        "name": "Yellow Rust / Stripe Rust",
        "cultural": [
            {
                "action": "IKS Research Gap Identified",
                "emoji": "🕵️",
                "theme": "soft_pink",
                "summary": "No traditional Himachal field-treatment is currently documented for Wheat Rust.",
                "how": "This is a great opportunity to interview local elders! For now, rely on modern resistant varieties."
            }
        ],
        "biological": []
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "cultural": [
            {
                "action": "IKS Research Gap Identified",
                "emoji": "🕵️",
                "theme": "soft_pink",
                "summary": "No traditional Himachal field-treatment is currently documented for Wheat Mildew.",
                "how": "Consult with local farmers to see if unrecorded traditional practices exist in your district."
            }
        ],
        "biological": []
    },
    "loose_smut": {
        "name": "Loose Smut",
        "cultural": [
            {
                "action": "IKS Research Gap Identified",
                "emoji": "🕵️",
                "theme": "lavender",
                "summary": "No traditional Himachal field-treatment is currently documented for Loose Smut.",
                "how": "Consult with local farmers to see if unrecorded traditional practices exist."
            }
        ],
        "biological": []
    },
    "karnal_bunt": {
        "name": "Karnal Bunt",
        "cultural": [
            {
                "action": "IKS Research Gap Identified",
                "emoji": "🕵️",
                "theme": "lavender",
                "summary": "No traditional Himachal field-treatment is currently documented for Karnal Bunt.",
                "how": "Consult with local farmers to see if unrecorded traditional practices exist."
            }
        ],
        "biological": []
    },
    "storage_and_harvest": {
        "name": "Post-Harvest Grain Storage Protection",
        "cultural": [
            {
                "action": "Bangru Mint Blanket",
                "emoji": "🌿",
                "theme": "mint_green",
                "summary": "Tuck dry wild mint leaves in with your stored wheat—bugs and mold hate it!",
                "how": "Mix dry Bangru (Mentha arvensis) leaves into stored wheat grain.",
                "frequency": "At storage time"
            },
            {
                "action": "Kali Basuti Leaf Layer",
                "emoji": "🍃",
                "theme": "pastel_green",
                "summary": "Layer in this traditional leafy herb to keep stored grain fungus-free and pest-free!",
                "how": "Mix dry Kali Basuti (Adhatoda vasica) leaves into stored wheat grain.",
                "frequency": "At storage time"
            },
            {
                "action": "Safeda Eucalyptus Hug",
                "emoji": "🍃",
                "theme": "sky_blue",
                "summary": "Fragrant eucalyptus leaves tucked into your grain bin, standing guard against sneaky storage fungi!",
                "how": "Mix dry Safeda (Eucalyptus citriodora) leaves into stored wheat grain.",
                "frequency": "At storage time"
            },
            {
                "action": "Walnut & Jugnu Wood Guard",
                "emoji": "🪵",
                "theme": "butter_yellow",
                "summary": "A traditional trio of walnut leaves, resin-rich wood, and wood ash tucked in for grain protection!",
                "how": "Combine walnut leaves, pieces of Jugnu wood, and wood ash with stored grain.",
                "frequency": "At storage time"
            },
            {
                "action": "Matchstick Mystery Guard",
                "emoji": "🔥",
                "theme": "peach",
                "summary": "An unusual old trick—tucking match sticks in with stored grain to keep pests away!",
                "how": "Place match box sticks in with stored wheat grain, following local farmer practice.",
                "frequency": "At storage time"
            },
            {
                "action": "Perru Bamboo Basket Home",
                "emoji": "🧺",
                "theme": "soft_yellow",
                "summary": "Store harvested wheat in a big spindle-shaped bamboo basket!",
                "how": "Store harvested wheat grain in large spindle-shaped bamboo baskets, locally called 'Perru'.",
                "frequency": "At harvest/storage time"
            }
        ],
        "biological": []
    }
}

MAIZE_DISEASES = {
    "banded_leaf_and_sheath_blight": {
        "name": "Banded Leaf and Sheath Blight (BLSB)",
        "cultural": [
            {
                "action": "Early Bird Sowing",
                "emoji": "🌱",
                "theme": "peach",
                "summary": "Plant a little earlier in the season to dodge the disease's favorite wet-weather window!",
                "how": "Sow around 30th May rather than late June field trials found disease severity greatest in late-June-sown crop and least in 30th-May-sown crop.",
                "frequency": "Once, at sowing choose the earliest sound date in your zone's window"
            },
            {
                "action": "Gentle Nitrogen Meal",
                "emoji": "⚖️",
                "theme": "soft_yellow",
                "summary": "Skip the extra-large nitrogen serving a lighter, balanced meal keeps disease away!",
                "how": "Avoid high nitrogen doses (150 kg/ha was found to increase disease severity and lower yield); use the recommended lower dose for your zone.",
                "frequency": "Split across top-dressing stages, avoiding the high-end rate"
            },
            {
                "action": "Ridge-Top Home",
                "emoji": "⛰️",
                "theme": "butter_yellow",
                "summary": "Give your maize a raised ridge to call home it grows happier and healthier there!",
                "how": "Sow maize on ridges rather than flat ground; ridge-sown crop showed lower disease severity and higher yield in field trials.",
                "frequency": "At sowing form ridges before planting"
            },
            {
                "action": "Room-to-Breathe Spacing",
                "emoji": "📏",
                "theme": "sky_blue",
                "summary": "Give each plant a little extra elbow room so disease can't sneak between them!",
                "how": "Avoid closer spacing (60cm x 15cm was found to increase disease severity); use the wider end of your variety's recommended spacing range.",
                "frequency": "At sowing"
            },
            {
                "action": "Weed Detective Patrol",
                "emoji": "🔍",
                "theme": "lavender",
                "summary": "Two sneaky weeds are secretly hosting the disease hunt them down first!",
                "how": "Prioritize removing Echinochloa colonum (barnyard grass) and Cyperus rotundus (nutgrass), which were found to specifically harbor and spread the pathogen.",
                "frequency": "Ongoing weeding, with extra attention to these two species"
            },
            {
                "action": "Lower Leaf Trim",
                "emoji": "✂️",
                "theme": "mint_green",
                "summary": "Snip away the lowest leaves during rainy season to keep the humid disease hideout away!",
                "how": "Physically pluck the lower leaves and their sheaths from the plant.",
                "frequency": "During the rainy season, once plants are established"
            }
        ],
        "biological": [
            {
                "action": "MDA-1 Fungus Fighter",
                "emoji": "🍄",
                "theme": "mint_green",
                "summary": "A specially selected friendly fungus strain that crushes disease growth in the lab!",
                "how": "Apply Trichoderma sp. isolate MDA-1 as seed treatment and/or soil application.",
                "frequency": "Once, at sowing"
            },
            {
                "action": "Twenty-Gram Seed Bath",
                "emoji": "🛁",
                "theme": "pastel_green",
                "summary": "Coat your seeds in a protective bio-bath before they even go in the ground!",
                "how": "Treat seed with Trichoderma viridi at 20g per kg of seed.",
                "frequency": "Once, as seed treatment at sowing"
            },
            {
                "action": "Dream Team Soil Duo",
                "emoji": "🤝",
                "theme": "soft_blue",
                "summary": "Two friendly microbes teaming up in the soil for extra-strong protection!",
                "how": "Apply Trichoderma asperellum + Bacillus subtilis, 200g/m² each, to soil before sowing.",
                "frequency": "Once, before sowing"
            },
            {
                "action": "Immune-Boost Bacteria Mist",
                "emoji": "🛡️",
                "theme": "soft_green",
                "summary": "A friendly bacteria spray that trains your plant's own immune system to fight back!",
                "how": "Apply Pseudomonas strains (AS19, AS21) as foliar spray to induce systemic resistance.",
                "frequency": "Starting at early vegetative stage, repeat every 10-14 days"
            }
        ],
        "botanical": [
            {
                "action": "Eucalyptus Power Splash",
                "emoji": "🌿",
                "theme": "sky_blue",
                "summary": "A strong eucalyptus leaf brew that knocked out disease growth by over 90% in the lab!",
                "how": "Spray Eucalyptus globulus aqueous leaf extract at 50% concentration.",
                "frequency": "Every 10-14 days starting at early vegetative stage",
                "confidence": "strong_92_percent_lab_inhibition"
            },
            {
                "action": "Eupatorium Total Knockout",
                "emoji": "🥊",
                "theme": "pastel_green",
                "summary": "A wild hillside weed brewed into a spray that completely stopped disease growth in the lab!",
                "how": "Spray Eupatorium adenophorum crude extract at 2.5% concentration.",
                "frequency": "Every 10-14 days",
                "confidence": "very_strong_100_percent_lab_inhibition_locally_abundant_in_HP"
            },
            {
                "action": "Bakain Leaf Mist",
                "emoji": "🍃",
                "theme": "mint_green",
                "summary": "A Persian lilac leaf extract that fights disease almost as well as the strongest options!",
                "how": "Spray Melia azedarach (Bakain) extract on foliage.",
                "frequency": "Following comparative trial pattern, suggest every 10-14 days",
                "confidence": "strong_87_percent_lab_inhibition"
            },
            {
                "action": "Vermicompost Soil Snuggle",
                "emoji": "🪱",
                "theme": "soft_yellow",
                "summary": "Rich worm-made compost that feeds your soil and fights disease at the same time!",
                "how": "Work vermicompost-enriched organic compost into soil at 50% concentration before sowing.",
                "frequency": "Once, before sowing",
                "confidence": "strong_84_percent_lab_inhibition_dual_purpose_soil_amendment"
            }
        ],
        "local_practice": [
            {
                "status": "gap_identified",
                "note": "No HP-district-specific traditional practice found specifically for BLSB. Worth asking directly in farmer interviews."
            }
        ]
    },
    "turcicum_leaf_blight": {
        "name": "Turcicum Leaf Blight (Northern Corn Leaf Blight)",
        "cultural": [
            {
                "action": "Tough Genotype Pick",
                "emoji": "💪",
                "theme": "lavender",
                "summary": "Grow HP-tested tough maize lines that naturally shrug off leaf blight!",
                "how": "Use resistant/tolerant genotypes identified in CSK HPKV's own Palampur field trials.",
                "frequency": "At sowing time"
            },
            {
                "action": "Room-to-Breathe Spacing",
                "emoji": "📏",
                "theme": "sky_blue",
                "summary": "Wider spacing and a lighter nitrogen meal both keep leaf blight pressure down!",
                "how": "Use wider spacing and avoid excess nitrogen at top-dressing.",
                "frequency": "At sowing and top-dressing"
            }
        ],
        "biological": [
            {
                "action": "Harzianum Triple Threat",
                "emoji": "🍄",
                "theme": "mint_green",
                "summary": "This friendly fungus shows up again and again in trials as a top disease fighter!",
                "how": "Apply Trichoderma harzianum as seed treatment at sowing, plus foliar spray during vegetative stage.",
                "frequency": "Seed treatment once; foliar spray during vegetative stage"
            },
            {
                "action": "Bacteria Bodyguard Duo",
                "emoji": "🛡️",
                "theme": "soft_green",
                "summary": "Two strong bacterial allies working together to fight off leaf blight fungus!",
                "how": "Apply Bacillus subtilis and Pseudomonas fluorescens as foliar spray or seed treatment.",
                "frequency": "Following standard bioagent application rates"
            }
        ],
        "botanical": [
            {
                "action": "Vacha Total Knockout",
                "emoji": "🌿",
                "theme": "pastel_green",
                "summary": "A traditional sweet flag extract that completely stopped fungus growth in the lab!",
                "how": "Spray Acorus calamus (Vacha) extract at 1% w/v concentration.",
                "frequency": "Following tested concentration",
                "confidence": "very_strong_100_percent_lab_inhibition"
            },
            {
                "action": "Artemisia Leaf Splash",
                "emoji": "🍃",
                "theme": "mint_green",
                "summary": "A strong herbal spray that knocks out three-quarters of the fungus growth!",
                "how": "Spray Artemisia indica extract at 2.5% w/v concentration.",
                "frequency": "Following tested concentration",
                "confidence": "strong_75_percent_lab_inhibition"
            },
            {
                "action": "Lantana Leaf Mist",
                "emoji": "🌸",
                "theme": "soft_pink",
                "summary": "A cheerful wildflower leaf spray that fights fungus nearly as well as Artemisia!",
                "how": "Spray Lantana camara extract at 2.5% w/v concentration.",
                "frequency": "Following tested concentration",
                "confidence": "strong_74_percent_lab_inhibition"
            },
            {
                "action": "Timru Spice Splash",
                "emoji": "🌶️",
                "theme": "peach",
                "summary": "A wild Himalayan spice plant, already growing on hillsides, that fights fungus too!",
                "how": "Spray Xanthoxylum armatum (Timru) extract at 2.5% w/v concentration.",
                "frequency": "Following tested concentration",
                "confidence": "moderate_44_percent_lab_inhibition_locally_abundant_in_HP_hills"
            },
            {
                "action": "Dhatura Leaf Brew",
                "emoji": "🌱",
                "theme": "lavender",
                "summary": "A strong herbal spray that performed as well as top treatments when paired with a friendly fungus seed treatment!",
                "how": "Apply Datura stramonium leaf extract at 50% concentration, combined with Trichoderma seed treatment.",
                "frequency": "Foliar spray at 50% concentration",
                "confidence": "strong_matched_best_integrated_treatment_in_field_trial"
            },
            {
                "action": "Tea Tree & Garlic Duo",
                "emoji": "🧄",
                "theme": "sky_blue",
                "summary": "Two essential oils that completely stopped fungus growth in a recent lab study!",
                "how": "Apply Tea Tree oil and Garlic oil, conservatively diluted, small-patch test before wider use.",
                "frequency": "Foliar application, exact field rate not yet confirmed",
                "confidence": "very_strong_100_percent_lab_inhibition_recent_2025_study"
            }
        ],
        "local_practice": [
            {
                "status": "gap_identified",
                "note": "No HP-district-specific traditional practice found specifically for turcicum leaf blight. Flagged for farmer interviews."
            }
        ]
    },
    "fall_armyworm": {
        "name": "Fall Armyworm (Currently Active Outbreak in HP, 19,000 hectares affected as of July 2026)",
        "cultural": [
            {
                "action": "Old-Seed Resistance Test",
                "emoji": "🌽",
                "theme": "butter_yellow",
                "summary": "Traditional local seeds might naturally resist this pest better than newer hybrids worth testing!",
                "how": "Plant indigenous/desi seed varieties; a natural-farming trainer reported this pest spreads much less in indigenous seeds compared to hybrid seeds.",
                "frequency": "At sowing consider a direct side-by-side comparison plot",
                "confidence": "unverified_field_observation_not_a_controlled_trial_high_research_value"
            },
            {
                "action": "HPKV Resistant Line Watch",
                "emoji": "👀",
                "theme": "mint_green",
                "summary": "Keep an eye out for HP-tested maize lines bred to resist this exact pest!",
                "how": "Use resistant inbred lines identified in CSK HPKV's 2023 Palampur screening trial, once publicly released.",
                "frequency": "At sowing, pending public release of specific lines"
            }
        ],
        "local_practice": [
            {
                "action": "Smoky Kitchen Cob Hang",
                "emoji": "💨",
                "theme": "peach",
                "summary": "Tie up your maize cobs in the kitchen where cooking smoke naturally keeps bugs away!",
                "how": "Tie maize cobs (along with pigeonpea and cowpea pods) in bundles and suspend them in the kitchen area, where smoke deters insect pests and moisture.",
                "frequency": "Applied at harvest/storage time",
                "documented_districts": ["Malan (Kangra) 50% adoption", "Sujanpur (Hamirpur) 74% adoption", "Palam valley", "Akrot", "Kotla"],
                "confidence": "high_directly_documented_maize_specific_storage_practice",
                "category_note": "This is a post-harvest storage practice, not a field-stage pest treatment. Recommend placing in storage module."
            }
        ]
    },
    "stalk_rot": {
        "name": "Stalk Rot (Bacterial and Fusarium)",
        "cultural": [
            {
                "action": "Gentle Nitrogen Meal",
                "emoji": "⚖️",
                "theme": "soft_yellow",
                "summary": "A balanced diet keeps stalks strong and standing tall against rot!",
                "how": "Avoid excess nitrogen combined with dense planting, both of which increase stalk rot susceptibility.",
                "frequency": "At top-dressing"
            },
            {
                "action": "Timely Harvest Habit",
                "emoji": "⏱️",
                "theme": "peach",
                "summary": "Harvest promptly once ready, don't let mature plants sit in wet fields!",
                "how": "Avoid leaving mature crop standing in wet field conditions.",
                "frequency": "At harvest time"
            },
            {
                "action": "Tough Genotype Pick",
                "emoji": "💪",
                "theme": "lavender",
                "summary": "Grow HP-tested maize lines specifically bred to resist stalk rot!",
                "how": "Use resistant genotypes identified in CSK HPKV mid-hill trials.",
                "frequency": "At sowing"
            }
        ],
        "biological": [
            {
                "status": "gap_identified",
                "note": "No dedicated bioagent trial specific to maize stalk rot found. Trichoderma/Pseudomonas evidence from BLSB and turcicum leaf blight above plausibly cross-applies but is unconfirmed for stalk rot specifically."
            }
        ],
        "botanical": [
            {
                "status": "gap_identified",
                "note": "No dedicated botanical trial specific to maize stalk rot found. Flagged as a research gap."
            }
        ]
    }
}

OKRA_DISEASES = {
    "yellow_vein_mosaic_virus": {
        "name": "Yellow Vein Mosaic Virus (YVMV)",
        "cultural": [
            {
                "action": "Champion Variety Pick",
                "emoji": "🏆",
                "theme": "lavender",
                "summary": "Grow a tough, ICAR-tested variety that naturally shrugs off the yellow vein virus!",
                "how": "Plant Parbhani Kranti or Ghana selection both found highly resistant in ICAR field screening of 14 okra cultivars.",
                "frequency": "At sowing time"
            },
            {
                "action": "Perfect Timing Sowing",
                "emoji": "⏱️",
                "theme": "peach",
                "summary": "Sow a little earlier to dodge the peak whitefly rush before it even begins!",
                "how": "Adjust sowing to an earlier date within the recommended window, since early sowing has shown reduced YVMV incidence in field trials.",
                "frequency": "At sowing time"
            },
            {
                "action": "Weed Patrol Sweep",
                "emoji": "🧹",
                "theme": "soft_yellow",
                "summary": "Clear out sneaky weeds around your field where whiteflies love to hide!",
                "how": "Remove weed hosts from in and around the field.",
                "frequency": "Every 2 weeks"
            },
            {
                "action": "Quick Goodbye Removal",
                "emoji": "👋",
                "theme": "soft_pink",
                "summary": "The moment a plant shows yellow veins, give it a swift, caring send-off to protect the rest!",
                "how": "Uproot and destroy infected plants immediately, away from the garden (not in compost).",
                "frequency": "Immediately when identified"
            }
        ],
        "biological": [
            {
                "action": "Yellow Sticky Watch Post",
                "emoji": "🟨",
                "theme": "butter_yellow",
                "summary": "Hang cheerful yellow traps to catch and count sneaky whiteflies before they spread trouble!",
                "how": "Hang yellow sticky traps around the field/canopy to trap and monitor whitefly.",
                "frequency": "Set once, replace every 2-3 weeks"
            }
        ],
        "botanical": [
            {
                "action": "Neem Shield Mist",
                "emoji": "🌿",
                "theme": "mint_green",
                "summary": "A gentle neem mist keeps whitefly numbers down and virus spread slower!",
                "how": "Apply a neem-based product spray around sowing time and repeat regularly.",
                "frequency": "Every 7-10 days"
            }
        ],
        "local_practice": [
            {
                "action": "Cow Urine Splash",
                "emoji": "🐄",
                "theme": "soft_yellow",
                "summary": "A traditional cow urine spray farmers trust to keep plants strong and pests away!",
                "how": "Spray 10% cow urine solution on the plant.",
                "frequency": "3 times, at 10-day intervals"
            }
        ],
        "iks": [
            {
                "action": "Nimastra Neem Ferment",
                "emoji": "🧪",
                "theme": "pastel_green",
                "summary": "A powerful fermented neem-and-cow-gift potion, brewed the traditional way!",
                "how": "Ferment 5kg crushed neem leaves + 100L water + 5L cow urine + 2kg fresh cow dung, stirring twice daily for 48 hours in shade, then strain. Makes enough for 1 acre.",
                "frequency": "Spray within 2 days of preparation",
                "confidence": "documented_traditional_formulation_general_pest_deterrent"
            }
        ]
    },
    "cercospora_leaf_spot": {
        "name": "Cercospora Leaf Spot",
        "cultural": [
            {
                "action": "Field Rest Rotation",
                "emoji": "🔄",
                "theme": "lavender",
                "summary": "Give your soil a break from okra every couple of years to starve out leftover fungus!",
                "how": "Avoid continuous okra cropping in the same field.",
                "frequency": "2+ years between plantings"
            },
            {
                "action": "Leafy Cleanup Duty",
                "emoji": "🧹",
                "theme": "soft_yellow",
                "summary": "Sweep away sick fallen leaves so spores don't get a second chance!",
                "how": "Remove and destroy infected leaf debris.",
                "frequency": "Post-harvest and as needed"
            },
            {
                "action": "Breezy Row Spacing",
                "emoji": "🌬️",
                "theme": "sky_blue",
                "summary": "Give each plant room to breathe so fresh air keeps fungus away!",
                "how": "Ensure adequate plant spacing at sowing time.",
                "frequency": "At sowing time"
            }
        ],
        "biological": [
            {
                "action": "Friendly Bacteria Splash",
                "emoji": "🦠",
                "theme": "mint_green",
                "summary": "The single most powerful microbe mist tested spray it on to keep leaf spots away!",
                "how": "Spray Pseudomonas fluorescens at 5% concentration on foliage.",
                "frequency": "Every 15 days from disease onset"
            },
            {
                "action": "Fungus-Fighting Fairy Mist",
                "emoji": "🧚",
                "theme": "pastel_green",
                "summary": "A gentle beneficial-fungus spray that keeps leaf spots from spreading!",
                "how": "Spray Trichoderma viride at 5% concentration on foliage.",
                "frequency": "Every 15 days"
            },
            {
                "action": "Dream Team Duo Spray",
                "emoji": "🤝",
                "theme": "soft_blue",
                "summary": "Two friendly microbes teaming up for the strongest leaf spot defense!",
                "how": "Combine Trichoderma (2%) + Pseudomonas fluorescens (2%) and spray together.",
                "frequency": "3 sprays at 15-day intervals"
            }
        ],
        "botanical": [
            {
                "action": "Neem Oil Leaf Wash",
                "emoji": "🍃",
                "theme": "mint_green",
                "summary": "A classic neem oil spray to keep leaf spots from taking hold!",
                "how": "Spray neem oil at 5% concentration on foliage.",
                "frequency": "Every 15 days"
            },
            {
                "action": "Garlic Punch Spray",
                "emoji": "🧄",
                "theme": "peach",
                "summary": "A zesty garlic oil mist that fungi really don't enjoy!",
                "how": "Spray garlic oil at 4% concentration on foliage.",
                "frequency": "Every 15 days"
            },
            {
                "action": "Onion Power Mist",
                "emoji": "🧅",
                "theme": "butter_yellow",
                "summary": "A sharp onion oil spray adding extra leaf spot protection!",
                "how": "Spray onion oil at 4% concentration on foliage.",
                "frequency": "Every 15 days"
            }
        ],
        "local_practice": [
            {
                "action": "Beejamrit & Panchagavya Combo",
                "emoji": "✨",
                "theme": "soft_pink",
                "summary": "The winning traditional combo! Seeds get a special bath, then leaves get a gentle five-gift spray!",
                "how": "Treat seeds with Beejamrit at 200ml/kg seed before sowing, then follow with 3 foliar sprays of Panchagavya at 10% concentration.",
                "frequency": "Seed treatment once; foliar spray 3 times at 15-day intervals from disease onset",
                "confidence": "high_best_performing_organic_combination_in_field_trial"
            }
        ]
    },
    "damping_off_root_rot": {
        "name": "Damping Off & Root Rot",
        "cultural": [
            {
                "action": "Dry Feet Planting",
                "emoji": "🏜️",
                "theme": "sky_blue",
                "summary": "Choose well-drained ground so little roots never sit in soggy soil!",
                "how": "Avoid waterlogged, poorly-drained sowing sites.",
                "frequency": "At sowing time"
            },
            {
                "action": "Just-Right Watering",
                "emoji": "💧",
                "theme": "soft_blue",
                "summary": "Check the soil before watering so seedlings get just what they need, not too much!",
                "how": "Avoid overwatering nursery beds; check soil moisture before each watering.",
                "frequency": "Every 1-2 days"
            },
            {
                "action": "Cozy Potting Mix",
                "emoji": "🪴",
                "theme": "pastel_green",
                "summary": "A fluffy vermicompost or farmyard-manure mix gives seedlings a healthy home!",
                "how": "Use vermicompost + soil or FYM + soil as potting media.",
                "frequency": "At sowing time"
            }
        ],
        "biological": [
            {
                "action": "Root-Guard Bacteria Bath",
                "emoji": "🛡️",
                "theme": "mint_green",
                "summary": "A soil treatment of friendly bacteria to keep tiny roots safe from rot!",
                "how": "Apply Pseudomonas fluorescens to the soil at sowing.",
                "frequency": "Once, at sowing time"
            },
            {
                "action": "Fungus-Fighter Seed Coat",
                "emoji": "🍄",
                "theme": "soft_green",
                "summary": "Coat seeds in a helpful fungus before planting to block disease from day one!",
                "how": "Treat seed with Trichoderma harzianum before sowing.",
                "frequency": "Once, at sowing time"
            }
        ],
        "botanical": [
            {
                "action": "Garlic Root Rescue",
                "emoji": "🧄",
                "theme": "peach",
                "summary": "Surprise! Garlic extract beat neem in real trials for protecting roots from rot!",
                "how": "Apply garlic clove extract at sowing/early seedling stage.",
                "frequency": "At sowing/early seedling stage"
            },
            {
                "action": "Neem Root Guard",
                "emoji": "🌿",
                "theme": "mint_green",
                "summary": "A trusty neem extract, second only to garlic in keeping seedlings safe!",
                "how": "Apply neem leaf/seed extract at sowing/early seedling stage.",
                "frequency": "At sowing/early seedling stage"
            }
        ],
        "local_practice": [
            {
                "status": "gap_identified",
                "note": "No documented local/IKS practice found specifically for okra damping-off. A strong candidate for direct farmer interviews."
            }
        ],
        "iks": []
    },
    "fusarium_wilt": {
        "name": "Fusarium Wilt",
        "cultural": [
            {
                "action": "Field Rest Rotation",
                "emoji": "🔄",
                "theme": "lavender",
                "summary": "Rotate away from okra and its relatives to break the wilt fungus's cycle!",
                "how": "Avoid okra/solanaceous crops in the same soil.",
                "frequency": "2-3 years between plantings"
            },
            {
                "action": "Moisture Balance Watch",
                "emoji": "⚖️",
                "theme": "sky_blue",
                "summary": "Keep soil moisture steady, since this fungus loves it too wet!",
                "how": "Control soil moisture, avoid excess humidity around roots.",
                "frequency": "Every 2-3 days"
            },
            {
                "action": "Quick Goodbye Removal",
                "emoji": "👋",
                "theme": "soft_pink",
                "summary": "Say goodbye to wilted plants right away to stop the fungus from spreading!",
                "how": "Destroy affected plants promptly when spotted.",
                "frequency": "Immediately when identified"
            }
        ],
        "biological": [
            {
                "action": "Fungus-Fighter Seed Coat",
                "emoji": "🍄",
                "theme": "mint_green",
                "summary": "The same helpful fungus seed coat used for damping-off also fights wilt!",
                "how": "Treat seed/soil with Trichoderma harzianum before sowing.",
                "frequency": "Once, at sowing time"
            }
        ],
        "botanical": [
            {
                "action": "Neem Leaf Splash",
                "emoji": "🍃",
                "theme": "pastel_green",
                "summary": "A neem leaf brew tested against wilt fungus, right alongside citrus extract!",
                "how": "Apply neem leaf aqueous extract at sowing and during early growth.",
                "frequency": "At sowing, repeat as needed during early growth"
            }
        ],
        "local_practice": [
            {
                "status": "gap_identified",
                "note": "No documented local/IKS practice found specifically for okra Fusarium wilt. Flagged for farmer interviews."
            }
        ],
        "iks": []
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "cultural": [
            {
                "action": "Breezy Row Spacing",
                "emoji": "🌬️",
                "theme": "sky_blue",
                "summary": "Good airflow between plants keeps powdery mildew from settling in!",
                "how": "Ensure good spacing between plants at sowing.",
                "frequency": "At sowing time"
            },
            {
                "action": "Gentle Fertilizer Meal",
                "emoji": "⚖️",
                "theme": "soft_yellow",
                "summary": "Feed plants a balanced diet, since too much nitrogen invites mildew!",
                "how": "Avoid excess nitrogen fertilizer.",
                "frequency": "At top-dressing stage"
            }
        ],
        "biological": [
            {
                "status": "gap_identified",
                "note": "No confirmed microbial bio-agent trial found specifically for okra powdery mildew. Worth testing Pseudomonas fluorescens/Trichoderma here too, since both are confirmed effective against Cercospora leaf spot in okra, but this hasn't been directly tested for powdery mildew yet."
            }
        ],
        "botanical": [
            {
                "action": "Neem Seed Kernel Mist",
                "emoji": "🌰",
                "theme": "mint_green",
                "summary": "A neem seed extract spray to keep white powdery spots from spreading!",
                "how": "Spray neem seed kernel extract (NSKE) at 5% concentration.",
                "frequency": "Every 10-14 days"
            },
            {
                "action": "Lime Water Splash",
                "emoji": "🍋",
                "theme": "soft_blue",
                "summary": "A simple lime water spray, a classic okra grower's trick against mildew!",
                "how": "Spray 10% lime water solution on affected leaves.",
                "frequency": "Repeat as needed"
            }
        ],
        "local_practice": [
            {
                "action": "Cow Urine Splash",
                "emoji": "🐄",
                "theme": "butter_yellow",
                "summary": "The same traditional cow urine spray, trusted here too for keeping mildew away!",
                "how": "Spray 10% cow urine solution on the plant.",
                "frequency": "3 times, at 10-day intervals"
            }
        ],
        "iks": [
            {
                "status": "not_confirmed",
                "note": "No classical-text-specific formula identified for okra powdery mildew (okra postdates Vrikshayurveda). General tonics like Panchagavya/Nimastra could reasonably be tested here as a hypothesis, but aren't confirmed against this disease specifically in our sources."
            }
        ]
    },
    "general_preventive_formulations": {
        "name": "General Preventive Traditional Formulations (Multi-Disease)",
        "iks": [
            {
                "action": "Nimastra Neem Ferment",
                "emoji": "🧪",
                "theme": "pastel_green",
                "summary": "A powerful fermented neem-and-cow-gift potion for all-around plant protection!",
                "how": "Ferment 5kg crushed neem leaves + 100L water + 5L cow urine + 2kg fresh cow dung, stirring twice daily for 48 hours in shade, then strain. Makes enough for 1 acre.",
                "frequency": "Spray within 2 days of preparation",
                "confidence": "scientist_corroborated_general_practice"
            },
            {
                "action": "Agneyastra Spice Ferment",
                "emoji": "🌶️",
                "theme": "peach",
                "summary": "A spicier fermented potion with chili and tobacco for extra pest-fighting power!",
                "how": "Ferment 5kg neem leaves + 20L cow urine + 500g tobacco leaves + 500g green chilies + ginger.",
                "frequency": "Same general application pattern as Nimastra",
                "confidence": "scientist_corroborated_general_practice"
            },
            {
                "action": "Jiwamrita Soil Tonic",
                "emoji": "🌱",
                "theme": "soft_yellow",
                "summary": "A simple four-ingredient tonic passed down for generations of healthy soil!",
                "how": "Ferment cow dung, cow urine, jaggery, and water together.",
                "frequency": "Applied as soil drench or diluted foliar spray",
                "confidence": "widely_documented_traditional_practice"
            },
            {
                "action": "Five-Gift Panchagavya Tonic",
                "emoji": "🎁",
                "theme": "soft_pink",
                "summary": "A gentle five-ingredient cow tonic no animal harmed, just cow-given gifts!",
                "how": "Ferment cow milk, curd, ghee, cow urine, and cow dung together, then dilute before use.",
                "frequency": "Soil drench or diluted foliar spray, typically 3-10% concentration",
                "confidence": "modern_field_trial_supported",
                "animal_product_flag": "dairy_and_urine_only_no_slaughter"
            }
        ]
    }
}

HEALTHY_TREATMENT = {
    "name": "Healthy Plant",
    "cultural": [
        {
            "action": "General Seed Health",
            "emoji": "🐄",
            "theme": "butter_yellow",
            "summary": "Keep seeds healthy with a traditional ash-and-dung blanket or cow urine soak!",
            "how": "Mix ash and cow dung together and apply to seeds, or soak in cow urine before sowing.",
            "frequency": "Once, before sowing"
        }
    ],
    "biological": []
}

DEFAULT_TREATMENT = {
    "name": "General Foliar Condition",
    "cultural": [
        {
            "action": "Five-Gift Cow Tonic (Panchagavya)",
            "emoji": "🐄",
            "theme": "soft_pink",
            "summary": "A gentle, nourishing tonic passed down through generations—no animal harmed!",
            "how": "Ferment cow milk, curd, ghee, cow urine, and cow dung. Dilute and use as a soil drench.",
            "frequency": "Every 10-14 days"
        }
    ],
    "biological": []
}

def get_treatment_data(predicted_class: str):
    """Normalize YOLO label, route to the correct crop dict, and retrieve matching treatment profile."""
    key = predicted_class.lower().strip()
    
    if "healthy" in key:
        return HEALTHY_TREATMENT
        
    parts = key.split("_", 1) 
    
    if len(parts) != 2:
        return DEFAULT_TREATMENT
        
    crop = parts[0]
    disease = parts[1]

    if crop == "tomato":
        if "yellow_virus" in disease or "mosaic_virus" in disease or "leaf_curl" in disease:
            return TOMATO_DISEASES.get("leaf_curl_virus", DEFAULT_TREATMENT)
        if "nematode" in disease:
            return TOMATO_DISEASES.get("root_knot_nematode", DEFAULT_TREATMENT)
        if "stem" in disease or "wound" in disease:
            return TOMATO_DISEASES.get("stem_wound_damage", DEFAULT_TREATMENT)
        for db_key in TOMATO_DISEASES:
            if db_key in disease:
                return TOMATO_DISEASES[db_key]
                
    elif crop == "potato":
        if "scurf" in disease or "scab" in disease:
            return POTATO_DISEASES.get("black_scurf_common_scab", DEFAULT_TREATMENT)
        if "wilt" in disease:
            return POTATO_DISEASES.get("bacterial_wilt", DEFAULT_TREATMENT)
        if "nematode" in disease:
            return POTATO_DISEASES.get("root_knot_nematode", DEFAULT_TREATMENT)
        if "moth" in disease:
            return POTATO_DISEASES.get("potato_tuber_moth", DEFAULT_TREATMENT)
        for db_key in POTATO_DISEASES:
            if db_key in disease:
                return POTATO_DISEASES[db_key]

    elif crop == "rice":
        if "hispa" in disease:
            return RICE_DISEASES.get("rice_hispa", DEFAULT_TREATMENT)
        if "storage" in disease or "post_harvest" in disease:
            return RICE_DISEASES.get("post_harvest_storage", DEFAULT_TREATMENT)
        for db_key in RICE_DISEASES:
            if db_key in disease:
                return RICE_DISEASES[db_key]
                
    elif crop == "wheat":
        if "leaf_rust" in disease or "stripe_rust" in disease:
            return WHEAT_DISEASES.get("yellow_rust", DEFAULT_TREATMENT)
        if "storage" in disease or "harvest" in disease:
            return WHEAT_DISEASES.get("storage_and_harvest", DEFAULT_TREATMENT)
        for db_key in WHEAT_DISEASES:
            if db_key in disease:
                return WHEAT_DISEASES[db_key]
                
    elif crop == "corn" or crop == "maize":
        for db_key in MAIZE_DISEASES:
            if db_key in disease:
                return MAIZE_DISEASES[db_key]
                
    elif crop == "okra" or crop == "pepper":
        for db_key in OKRA_DISEASES:
            if db_key in disease:
                return OKRA_DISEASES[db_key]

    return DEFAULT_TREATMENT

