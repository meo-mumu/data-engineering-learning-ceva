# Génération de données CEVA Santé Animale

## Contexte
CEVA Santé Animale est un laboratoire pharmaceutique vétérinaire. On simule des données de production provenant de 3 Business Units différentes pour construire un POC de stack data lakehouse.

## Destination
Créer les fichiers dans `@work/data/a-sources/`

## BU 1 : Volaille (Poultry) — `bu_poultry_production.csv`

60 lignes de lots de production de vaccins aviaires.

| Colonne | Type | Description |
|---------|------|-------------|
| batch_id | string | Identifiant lot (format: "POL-2024-XXXXX") |
| product_code | string | Code produit (ex: "VAC-POL-001") |
| product_name | string | Nom commercial (ex: "Gallimune ND", "Cevac IBird", "Vectormune HVT") |
| target_species | string | Espèce cible : chicken, turkey, duck |
| production_date | date | Date production (2024, répartir sur l'année) |
| expiry_date | date | Date expiration (production_date + 18-24 mois) |
| quantity_doses | int | Nombre de doses (gros volumes : 10k à 500k) |
| site_code | string | Site production : "LIBOURNE-FR", "BUDAPEST-HU", "SUZHOU-CN" |
| storage_temp_min_c | int | Température stockage min (2 à -20 selon produit) |
| storage_temp_max_c | int | Température stockage max |
| qc_status | string | Statut QC : "released", "pending", "rejected" (95% released) |
| release_date | date | Date libération QC (NULL si pending/rejected) |

Contraintes métier :
- Les vaccins vivants ont des températures plus basses (2-8°C)
- Les vaccins inactivés peuvent être à température ambiante
- Quelques rejets QC réalistes (2-3 lignes)

## BU 2 : Ruminants — `bu_ruminants_production.csv`

100 lignes de production de médicaments et vaccins pour bovins/ovins.

| Colonne | Type | Description |
|---------|------|-------------|
| lot_number | string | Numéro de lot (format: "RUM-YYYYMM-XXXX") |
| product_ref | string | Référence produit (ex: "PARA-RUM-012") |
| product_label | string | Nom produit (ex: "Cevazuril", "Bovilis BVD", "Vecoxan") |
| therapeutic_class | string | Classe : "vaccine", "antiparasitic", "antibiotic", "anti-inflammatory" |
| target_species | string | Espèce : "bovine", "ovine", "caprine" |
| form | string | Forme galénique : "injectable", "oral_solution", "bolus", "pour-on" |
| unit_volume_ml | float | Volume par unité (10, 50, 100, 250, 500 ml) |
| quantity_units | int | Nombre d'unités produites (100 à 5000) |
| manufacturing_date | date | Date fabrication (2024) |
| expiration_date | date | Expiration (fabrication + 24-36 mois) |
| production_site | string | Site : "LIBOURNE-FR", "LENEXA-US", "ALGETE-ES" |
| batch_status | string | Statut : "in_production", "qc_testing", "released", "quarantine" |
| gmp_deviation | boolean | Déviation GMP signalée (5% des lots) |

Contraintes métier :
- Les antiparasitaires sont souvent en "pour-on" ou "oral_solution"
- Les vaccins sont injectables
- Les antibiotiques ont une forme variée
- Cohérence entre classe thérapeutique et forme

## BU 3 : Animaux de compagnie (Companion) — `bu_companion_catalog.json`

Structure JSON avec catalogue produits et derniers lots.
```json
{
  "bu_name": "Companion Animals",
  "last_updated": "2024-12-15T10:30:00Z",
  "products": [
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
        "light_sensitive": true
      }
    }
    // ... 8-10 produits variés (vaccins chien/chat, antiparasitaires, dentaire)
  ],
  "recent_batches": [
    {
      "batch_id": "COMP-2024-00123",
      "product_sku": "COMP-VAC-001",
      "produced_at": "2024-11-20",
      "quantity_units": 5000,
      "status": "released",
      "destination_market": "EU"
    }
    // ... 10-15 lots récents
  ]
}
```

Produits à inclure :
- Vaccins chien : maladie de Carré, parvovirose, leptospirose
- Vaccins chat : typhus, coryza, leucose
- Antiparasitaires : puces, tiques, vers
- Produits dentaires/hygiène

## Instructions techniques
- Utiliser des noms de produits réalistes CEVA (chercher sur leur site si besoin)
- Dates cohérentes (production < release < expiry)
- Encoder CSV en UTF-8
- JSON formaté lisible (indent 2)
- Seed aléatoire fixe pour reproductibilité