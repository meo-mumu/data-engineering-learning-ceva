# Specifications

 - Tool: Polars (pure Python)                                                                                                                                                                 
 - Strategy: Full refresh, no validation                                                                                                                                                      
 - SK Generation: Sequential integers starting at 1                                                                                                                                           
 - Output: Single parquet per table in /work/data/b-silver-star-schema/                                                                                                                       
 - Architecture: Single script (user preference)                                                                                                                                              
                                                  
                                                  
## dim_product
- Add a bu_source column
- Add therapeutic_class attribute (nullable: vaccine, antiparasitic, antibiotic, anti-inflammatory, dental/hygiene)
- For attributes like temp_min_c, temp_max_c, light_sensitive, target_species, form, ... make nullable columns

## dim_specie
- Add a bu_source column

## dim_site
- Add a bu_source column

## fact_batch_production
- One for all. Add a bu_source column
- Granularity: lot / batch
- batch_status attribute (qc_status/batch_status/status from sources)
- targeted_species is an array of species


---

# Star Schema Model

## dim_product
| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| product_sk | INTEGER | Surrogate key | NO |
| product_code | VARCHAR | Business key (product_code/product_ref/sku) | NO |
| product_name | VARCHAR | Product name (product_name/product_label/name) | NO |
| therapeutic_class | VARCHAR | vaccine, antiparasitic, antibiotic, anti-inflammatory, dental | YES |
| category | VARCHAR | Product category | YES |
| form | VARCHAR | injectable, oral_solution, bolus, pour-on | YES |
| temp_min_c | INTEGER | Minimum storage temperature | YES |
| temp_max_c | INTEGER | Maximum storage temperature | YES |
| light_sensitive | BOOLEAN | Light sensitivity | YES |
| dose_ml | FLOAT | Dose volume in ml | YES |
| unit_volume_ml | FLOAT | Unit volume in ml | YES |
| bu_source | VARCHAR | Source BU: poultry, ruminants, companion | NO |

## dim_specie
| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| specie_sk | INTEGER | Surrogate key | NO |
| specie_code | VARCHAR | chicken, turkey, duck, bovine, ovine, caprine, dog, cat | NO |
| specie_name | VARCHAR | Specie name | NO |
| animal_type | VARCHAR | poultry, ruminant, companion | NO |
| bu_source | VARCHAR | Source BU | NO |

## dim_site
| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| site_sk | INTEGER | Surrogate key | NO |
| site_code | VARCHAR | LIBOURNE-FR, BUDAPEST-HU, SUZHOU-CN, LENEXA-US, ALGETE-ES | NO |
| country | VARCHAR | Country code | NO |
| region | VARCHAR | Geographic region | YES |
| bu_source | VARCHAR | Source BU | NO |

## fact_batch_production
| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| batch_production_sk | INTEGER | Surrogate key | NO |
| batch_id | VARCHAR | Business key (batch_id/lot_number) | NO |
| product_fk | INTEGER | FK to dim_product | NO |
| site_fk | INTEGER | FK to dim_site | NO |
| production_date | DATE | Production/manufacturing date | NO |
| expiry_date | DATE | Expiration date | NO |
| release_date | DATE | QC release date | YES |
| quantity_doses | INTEGER | Quantity in doses (Poultry) | YES |
| quantity_units | INTEGER | Quantity in units (Ruminants/Companion) | YES |
| batch_status | VARCHAR | released, pending, rejected, in_production, qc_testing, quarantine | NO |
| gmp_deviation | BOOLEAN | GMP deviation flag | YES |
| destination_market | VARCHAR | Destination market (e.g., EU) | YES |
| bu_source | VARCHAR | Source BU: poultry, ruminants, companion | NO |
| targeted_species | INTEGER[] | Array of FKs to dim_specie | NO |