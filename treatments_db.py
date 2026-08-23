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
    "blight": {
        "name": "Turcicum / Maydis Leaf Blight",
        "cultural": [
            {
                "action": "Ash Dusting",
                "emoji": "🪵",
                "theme": "soft_yellow",
                "summary": "Local farmers use wood ash to keep foliage dry and fungal spores away!",
                "how": "Dust wood ash over the affected maize leaves in the early morning.",
                "frequency": "Refresh after rain"
            }
        ],
        "biological": [
            {
                "action": "Sour Buttermilk Spray",
                "emoji": "🥛",
                "theme": "soft_blue",
                "summary": "A traditional fermented lassi spray to suppress fungal spots.",
                "how": "Dilute aged, sour buttermilk (khatta lassi) and spray on foliage.",
                "frequency": "Every 10-14 days"
            }
        ]
    },
    "fall_armyworm": {
        "name": "Fall Armyworm / Stem Borer",
        "cultural": [
            {
                "action": "Mixed Cropping",
                "emoji": "🌱",
                "theme": "peach",
                "summary": "Grow coriander or legumes alongside maize for natural pest control!",
                "how": "Plant Coriandrum sativum (Dhaniya) as a mixed crop.",
                "frequency": "At planting"
            }
        ],
        "biological": [
            {
                "action": "Aloe & Chili Extract",
                "emoji": "🌶️",
                "theme": "soft_pink",
                "summary": "A potent, traditional Himachali bio-pesticide to repel chewing caterpillars!",
                "how": "Mix Aloe barbadensis leaves and chili plant residue in water for 15 days. Filter and spray over the infested crop.",
                "frequency": "Every 2-3 weeks"
            },
            {
                "action": "Neem & Cow Urine Mix",
                "emoji": "🌿",
                "theme": "mint_green",
                "summary": "A trusted traditional spray combining neem's bitterness with cow urine.",
                "how": "Mix neem fruits/leaves with cow urine for 48-72 hours. Filter and spray.",
                "frequency": "As needed"
            }
        ]
    }
}

OKRA_DISEASES = {
    "yellow_vein_mosaic": {
        "name": "Yellow Vein Mosaic Virus (YVMV)",
        "cultural": [
            {
                "action": "Quick Plant Removal",
                "emoji": "✂️",
                "theme": "soft_pink",
                "summary": "Remove sick okra plants right away to stop whiteflies from spreading the virus!",
                "how": "Pull up and destroy infected plants immediately.",
                "frequency": "As soon as spotted"
            }
        ],
        "biological": [
            {
                "action": "Neem, Cow Urine & Garlic Spray",
                "emoji": "🧄",
                "theme": "mint_green",
                "summary": "A powerful local Himachali mix to repel the whiteflies that carry the virus!",
                "how": "Mix neem leaves, cow urine, and garlic. Filter and dilute before spraying.",
                "frequency": "Every 7-10 days"
            }
        ]
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "cultural": [
            {
                "action": "Ash Dusting",
                "emoji": "🪵",
                "theme": "soft_yellow",
                "summary": "A cheap and simple local trick to dry out powdery white fungi!",
                "how": "Dust wood ash over the plant leaves.",
                "frequency": "Refresh as needed"
            }
        ],
        "biological": [
            {
                "action": "Buttermilk Pest Trap & Spray",
                "emoji": "🥛",
                "theme": "peach",
                "summary": "Fermented dairy is locally documented to help manage both pests and mildew!",
                "how": "Set out buttermilk traps or use a diluted milk/lassi foliar spray in the morning sun.",
                "frequency": "Weekly"
            }
        ]
    },
    "fruit_borer": {
        "name": "Okra Fruit & Shoot Borer",
        "cultural": [
            {
                "action": "Marigold & Coriander Guard",
                "emoji": "🌼",
                "theme": "butter_yellow",
                "summary": "Intercrop with marigold and coriander to naturally ward off borer insects!",
                "how": "Plant these companions around the okra field.",
                "frequency": "At planting"
            }
        ],
        "biological": [
            {
                "action": "Siris Leaf Juice Spray",
                "emoji": "🍃",
                "theme": "sky_blue",
                "summary": "A natural repellent spray using local Siris (Albizia procera) leaves!",
                "how": "Ferment chopped Siris leaves with cow urine and jaggery for 10-15 days. Dilute and spray.",
                "frequency": "Every 2 weeks"
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

