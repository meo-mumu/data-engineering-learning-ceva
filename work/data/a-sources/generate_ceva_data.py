"""
Générateur de données simulées pour CEVA Santé Animale
Génère des données pour 3 Business Units : Volaille, Ruminants, Animaux de compagnie
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import random
import numpy as np

# Seed fixe pour reproductibilité
random.seed(42)
np.random.seed(42)

# =============================================================================
# BU 1 : VOLAILLE (Poultry) - 60 lignes
# =============================================================================

def generate_poultry_data():
    """Génère 60 lignes de production de vaccins aviaires"""

    products = [
        {"code": "VAC-POL-001", "name": "Gallimune ND", "temp_min": 2, "temp_max": 8, "shelf_months": 18},
        {"code": "VAC-POL-002", "name": "Cevac IBird", "temp_min": 2, "temp_max": 8, "shelf_months": 24},
        {"code": "VAC-POL-003", "name": "Vectormune HVT", "temp_min": -20, "temp_max": -15, "shelf_months": 24},
        {"code": "VAC-POL-004", "name": "Cevac Transmune", "temp_min": 2, "temp_max": 8, "shelf_months": 18},
        {"code": "VAC-POL-005", "name": "Nobilis IB Multi", "temp_min": 2, "temp_max": 8, "shelf_months": 24},
        {"code": "VAC-POL-006", "name": "Cevac Vitabron", "temp_min": 2, "temp_max": 8, "shelf_months": 18},
        {"code": "VAC-POL-007", "name": "Gallimune SE", "temp_min": 2, "temp_max": 8, "shelf_months": 24},
        {"code": "VAC-POL-008", "name": "Nobilis Gumboro", "temp_min": -20, "temp_max": -15, "shelf_months": 24},
    ]

    species = ["chicken", "turkey", "duck"]
    sites = ["LIBOURNE-FR", "BUDAPEST-HU", "SUZHOU-CN"]

    data = []
    batch_counter = 10000

    for i in range(60):
        product = random.choice(products)

        # Date de production répartie sur 2024
        prod_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))

        # Date d'expiration
        expiry_date = prod_date + timedelta(days=product["shelf_months"] * 30)

        # Statut QC : 95% released
        qc_status = random.choices(
            ["released", "pending", "rejected"],
            weights=[0.95, 0.03, 0.02]
        )[0]

        # Date de release (NULL si not released)
        if qc_status == "released":
            release_date = prod_date + timedelta(days=random.randint(7, 21))
        else:
            release_date = None

        batch_id = f"POL-2024-{batch_counter + i:05d}"

        data.append({
            "batch_id": batch_id,
            "product_code": product["code"],
            "product_name": product["name"],
            "target_species": random.choice(species),
            "production_date": prod_date.strftime("%Y-%m-%d"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "quantity_doses": random.randint(10000, 500000),
            "site_code": random.choice(sites),
            "storage_temp_min_c": product["temp_min"],
            "storage_temp_max_c": product["temp_max"],
            "qc_status": qc_status,
            "release_date": release_date.strftime("%Y-%m-%d") if release_date else None
        })

    df = pd.DataFrame(data)
    return df


# =============================================================================
# BU 2 : RUMINANTS - 100 lignes
# =============================================================================

def generate_ruminants_data():
    """Génère 100 lignes de production de médicaments pour ruminants"""

    products = [
        # Vaccins
        {"ref": "VAC-RUM-001", "label": "Bovilis BVD", "class": "vaccine", "form": "injectable", "volume": [50, 100]},
        {"ref": "VAC-RUM-002", "label": "Coglavax", "class": "vaccine", "form": "injectable", "volume": [50, 100]},
        {"ref": "VAC-RUM-003", "label": "Bovilis IBR", "class": "vaccine", "form": "injectable", "volume": [50, 100]},
        {"ref": "VAC-RUM-004", "label": "Ovivac P Plus", "class": "vaccine", "form": "injectable", "volume": [50, 100]},

        # Antiparasitaires
        {"ref": "PARA-RUM-001", "label": "Cevazuril", "class": "antiparasitic", "form": "oral_solution", "volume": [100, 250, 500]},
        {"ref": "PARA-RUM-002", "label": "Vecoxan", "class": "antiparasitic", "form": "oral_solution", "volume": [250, 500]},
        {"ref": "PARA-RUM-003", "label": "Eprinex", "class": "antiparasitic", "form": "pour-on", "volume": [250, 500]},
        {"ref": "PARA-RUM-004", "label": "Supaverm", "class": "antiparasitic", "form": "pour-on", "volume": [500]},
        {"ref": "PARA-RUM-005", "label": "Cevamec", "class": "antiparasitic", "form": "injectable", "volume": [50, 100, 250]},

        # Antibiotiques
        {"ref": "AB-RUM-001", "label": "Shotapen", "class": "antibiotic", "form": "injectable", "volume": [50, 100]},
        {"ref": "AB-RUM-002", "label": "Bovoxyl", "class": "antibiotic", "form": "injectable", "volume": [100, 250]},
        {"ref": "AB-RUM-003", "label": "Rilexine", "class": "antibiotic", "form": "bolus", "volume": [10]},

        # Anti-inflammatoires
        {"ref": "AI-RUM-001", "label": "Finadyne", "class": "anti-inflammatory", "form": "injectable", "volume": [50, 100, 250]},
        {"ref": "AI-RUM-002", "label": "Metacam", "class": "anti-inflammatory", "form": "oral_solution", "volume": [100, 250]},
    ]

    species_list = ["bovine", "ovine", "caprine"]
    sites = ["LIBOURNE-FR", "LENEXA-US", "ALGETE-ES"]
    statuses = ["in_production", "qc_testing", "released", "quarantine"]

    data = []

    for i in range(100):
        product = random.choice(products)

        # Date de fabrication en 2024
        year_month = random.choice(range(1, 13))
        day = random.randint(1, 28)
        manuf_date = datetime(2024, year_month, day)

        # Date d'expiration (24-36 mois)
        shelf_months = random.randint(24, 36)
        expiry_date = manuf_date + timedelta(days=shelf_months * 30)

        # Lot number format: RUM-YYYYMM-XXXX
        lot_number = f"RUM-{manuf_date.strftime('%Y%m')}-{random.randint(1000, 9999):04d}"

        # Statut batch
        batch_status = random.choices(statuses, weights=[0.15, 0.20, 0.60, 0.05])[0]

        # Déviation GMP (5%)
        gmp_deviation = random.random() < 0.05

        # Volume unitaire
        unit_volume = random.choice(product["volume"])

        # Espèce cible
        target_sp = random.choice(species_list)

        data.append({
            "lot_number": lot_number,
            "product_ref": product["ref"],
            "product_label": product["label"],
            "therapeutic_class": product["class"],
            "target_species": target_sp,
            "form": product["form"],
            "unit_volume_ml": float(unit_volume),
            "quantity_units": random.randint(100, 5000),
            "manufacturing_date": manuf_date.strftime("%Y-%m-%d"),
            "expiration_date": expiry_date.strftime("%Y-%m-%d"),
            "production_site": random.choice(sites),
            "batch_status": batch_status,
            "gmp_deviation": gmp_deviation
        })

    df = pd.DataFrame(data)
    return df


# =============================================================================
# BU 3 : ANIMAUX DE COMPAGNIE (Companion) - JSON
# =============================================================================

def generate_companion_data():
    """Génère le catalogue JSON pour animaux de compagnie"""

    products = [
        {
            "sku": "COMP-VAC-001",
            "name": "Canigen DHP",
            "category": "vaccine",
            "target_species": ["dog"],
            "form": "injectable",
            "dose_ml": 1.0,
            "storage_requirements": {
                "min_temp_c": 2,
                "max_temp_c": 8,
                "light_sensitive": True
            }
        },
        {
            "sku": "COMP-VAC-002",
            "name": "Canigen L",
            "category": "vaccine",
            "target_species": ["dog"],
            "form": "injectable",
            "dose_ml": 1.0,
            "storage_requirements": {
                "min_temp_c": 2,
                "max_temp_c": 8,
                "light_sensitive": True
            }
        },
        {
            "sku": "COMP-VAC-003",
            "name": "Feligen CRP",
            "category": "vaccine",
            "target_species": ["cat"],
            "form": "injectable",
            "dose_ml": 1.0,
            "storage_requirements": {
                "min_temp_c": 2,
                "max_temp_c": 8,
                "light_sensitive": True
            }
        },
        {
            "sku": "COMP-VAC-004",
            "name": "Purevax RCP",
            "category": "vaccine",
            "target_species": ["cat"],
            "form": "injectable",
            "dose_ml": 1.0,
            "storage_requirements": {
                "min_temp_c": 2,
                "max_temp_c": 8,
                "light_sensitive": True
            }
        },
        {
            "sku": "COMP-PARA-001",
            "name": "Vectra 3D",
            "category": "antiparasitic",
            "target_species": ["dog"],
            "form": "spot-on",
            "dose_ml": 2.5,
            "storage_requirements": {
                "min_temp_c": 15,
                "max_temp_c": 25,
                "light_sensitive": False
            }
        },
        {
            "sku": "COMP-PARA-002",
            "name": "Broadline",
            "category": "antiparasitic",
            "target_species": ["cat"],
            "form": "spot-on",
            "dose_ml": 0.9,
            "storage_requirements": {
                "min_temp_c": 15,
                "max_temp_c": 25,
                "light_sensitive": False
            }
        },
        {
            "sku": "COMP-PARA-003",
            "name": "Milbemax",
            "category": "antiparasitic",
            "target_species": ["dog", "cat"],
            "form": "tablet",
            "dose_ml": None,
            "storage_requirements": {
                "min_temp_c": 15,
                "max_temp_c": 25,
                "light_sensitive": False
            }
        },
        {
            "sku": "COMP-DENT-001",
            "name": "Orozyme Gel",
            "category": "dental",
            "target_species": ["dog", "cat"],
            "form": "gel",
            "dose_ml": 70.0,
            "storage_requirements": {
                "min_temp_c": 5,
                "max_temp_c": 25,
                "light_sensitive": False
            }
        },
        {
            "sku": "COMP-DENT-002",
            "name": "Plaque Off",
            "category": "dental",
            "target_species": ["dog", "cat"],
            "form": "powder",
            "dose_ml": None,
            "storage_requirements": {
                "min_temp_c": 15,
                "max_temp_c": 25,
                "light_sensitive": False
            }
        },
        {
            "sku": "COMP-HYGI-001",
            "name": "Douxo S3 Calm",
            "category": "hygiene",
            "target_species": ["dog"],
            "form": "shampoo",
            "dose_ml": 200.0,
            "storage_requirements": {
                "min_temp_c": 5,
                "max_temp_c": 30,
                "light_sensitive": False
            }
        }
    ]

    # Générer 15 lots récents
    batches = []
    markets = ["EU", "US", "APAC", "LATAM"]
    statuses = ["released", "in_transit", "distributed"]

    for i in range(15):
        product = random.choice(products)

        # Date de production (novembre-décembre 2024)
        prod_month = random.choice([11, 12])
        prod_day = random.randint(1, 28)
        prod_date = datetime(2024, prod_month, prod_day)

        batch = {
            "batch_id": f"COMP-2024-{10100 + i:05d}",
            "product_sku": product["sku"],
            "produced_at": prod_date.strftime("%Y-%m-%d"),
            "quantity_units": random.randint(2000, 15000),
            "status": random.choice(statuses),
            "destination_market": random.choice(markets)
        }
        batches.append(batch)

    catalog = {
        "bu_name": "Companion Animals",
        "last_updated": "2024-12-15T10:30:00Z",
        "products": products,
        "recent_batches": batches
    }

    return catalog


# =============================================================================
# MAIN - Génération des fichiers
# =============================================================================

if __name__ == "__main__":
    print("🏭 Génération des données CEVA Santé Animale...")

    # BU 1 : Volaille
    print("\n📦 BU 1 : Volaille (Poultry)...")
    df_poultry = generate_poultry_data()
    output_path_poultry = "work/data/a-sources/bu_poultry_production.csv"
    df_poultry.to_csv(output_path_poultry, index=False, encoding='utf-8')
    print(f"   ✓ {len(df_poultry)} lignes générées → {output_path_poultry}")

    # BU 2 : Ruminants
    print("\n🐄 BU 2 : Ruminants...")
    df_ruminants = generate_ruminants_data()
    output_path_ruminants = "work/data/a-sources/bu_ruminants_production.csv"
    df_ruminants.to_csv(output_path_ruminants, index=False, encoding='utf-8')
    print(f"   ✓ {len(df_ruminants)} lignes générées → {output_path_ruminants}")

    # BU 3 : Animaux de compagnie
    print("\n🐕 BU 3 : Animaux de compagnie (Companion)...")
    catalog_companion = generate_companion_data()
    output_path_companion = "work/data/a-sources/bu_companion_catalog.json"
    with open(output_path_companion, 'w', encoding='utf-8') as f:
        json.dump(catalog_companion, f, indent=2, ensure_ascii=False)
    print(f"   ✓ {len(catalog_companion['products'])} produits + {len(catalog_companion['recent_batches'])} lots → {output_path_companion}")

    print("\n✅ Génération terminée avec succès !")
    print("\nRésumé :")
    print(f"  - Volaille     : {len(df_poultry)} lots")
    print(f"  - Ruminants    : {len(df_ruminants)} lots")
    print(f"  - Companion    : {len(catalog_companion['products'])} produits, {len(catalog_companion['recent_batches'])} lots")
