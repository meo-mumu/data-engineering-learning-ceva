"""
ELT Script: Transform CEVA Animal Health source data into star schema
Outputs 4 parquet files: dim_product, dim_specie, dim_site, fact_batch_production
"""
import polars as pl
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
SOURCES_DIR = BASE_DIR / "data" / "a-sources"
OUTPUT_DIR = BASE_DIR / "data" / "b-silver-star-schema"

# Mappings
ANIMAL_TYPE_MAP = {
    'chicken': 'poultry', 'turkey': 'poultry', 'duck': 'poultry',
    'bovine': 'ruminant', 'ovine': 'ruminant', 'caprine': 'ruminant',
    'dog': 'companion', 'cat': 'companion'
}

REGION_MAP = {
    'FR': 'Europe', 'HU': 'Europe', 'ES': 'Europe',
    'US': 'North America', 'CN': 'Asia'
}


def extract_sources():
    """Load 3 source files"""
    print("EXTRACT: Loading sources...")

    # Poultry CSV
    poultry = pl.read_csv(SOURCES_DIR / "bu_poultry_production.csv")
    print(f"  Poultry: {len(poultry)} rows")

    # Ruminants CSV
    ruminants = pl.read_csv(SOURCES_DIR / "bu_ruminants_production.csv")
    print(f"  Ruminants: {len(ruminants)} rows")

    # Companion JSON
    companion_json = pl.read_json(SOURCES_DIR / "bu_companion_catalog.json")
    companion_products = companion_json.select(pl.col("products")).explode("products").unnest("products")
    companion_batches = companion_json.select(pl.col("recent_batches")).explode("recent_batches").unnest("recent_batches")
    print(f"  Companion: {len(companion_products)} products, {len(companion_batches)} batches")

    return poultry, ruminants, companion_products, companion_batches


def build_dim_specie(poultry, ruminants, companion_products):
    """Build dim_specie from all unique species"""
    print("\nTRANSFORM: Building dim_specie...")

    # Extract species from each source
    poultry_species = poultry.select(pl.col("target_species")).unique()
    ruminants_species = ruminants.select(pl.col("target_species")).unique()
    companion_species = companion_products.select(pl.col("target_species")).explode("target_species").unique()

    # Union all species
    all_species = pl.concat([
        poultry_species,
        ruminants_species,
        companion_species
    ]).unique().rename({"target_species": "specie_code"})

    # Map to animal_type and bu_source
    dim_specie = all_species.with_columns([
        pl.col("specie_code").replace(ANIMAL_TYPE_MAP).alias("animal_type"),
        pl.col("specie_code").str.to_titlecase().alias("specie_name")
    ])

    # Derive bu_source from animal_type
    dim_specie = dim_specie.with_columns(
        pl.when(pl.col("animal_type") == "poultry").then(pl.lit("poultry"))
          .when(pl.col("animal_type") == "ruminant").then(pl.lit("ruminants"))
          .when(pl.col("animal_type") == "companion").then(pl.lit("companion"))
          .alias("bu_source")
    )

    # Generate surrogate keys
    dim_specie = dim_specie.sort(["animal_type", "specie_code"]).with_row_index(name="specie_sk", offset=1)

    # Reorder columns
    dim_specie = dim_specie.select(["specie_sk", "specie_code", "specie_name", "animal_type", "bu_source"])

    print(f"  Created {len(dim_specie)} species")
    return dim_specie


def build_dim_product(poultry, ruminants, companion_products):
    """Build dim_product from 3 sources"""
    print("\nTRANSFORM: Building dim_product...")

    # Normalize Poultry products
    poultry_products = poultry.select([
        pl.col("product_code"),
        pl.col("product_name"),
        pl.lit(None, dtype=pl.String).alias("therapeutic_class"),
        pl.lit(None, dtype=pl.String).alias("category"),
        pl.lit(None, dtype=pl.String).alias("form"),
        pl.col("storage_temp_min_c").alias("temp_min_c"),
        pl.col("storage_temp_max_c").alias("temp_max_c"),
        pl.lit(None, dtype=pl.Boolean).alias("light_sensitive"),
        pl.lit(None, dtype=pl.Float64).alias("dose_ml"),
        pl.lit(None, dtype=pl.Float64).alias("unit_volume_ml"),
        pl.lit("poultry").alias("bu_source")
    ]).unique(subset=["product_code"])

    # Normalize Ruminants products
    ruminants_products = ruminants.select([
        pl.col("product_ref").alias("product_code"),
        pl.col("product_label").alias("product_name"),
        pl.col("therapeutic_class"),
        pl.lit(None, dtype=pl.String).alias("category"),
        pl.col("form"),
        pl.lit(None, dtype=pl.Int64).alias("temp_min_c"),
        pl.lit(None, dtype=pl.Int64).alias("temp_max_c"),
        pl.lit(None, dtype=pl.Boolean).alias("light_sensitive"),
        pl.lit(None, dtype=pl.Float64).alias("dose_ml"),
        pl.col("unit_volume_ml"),
        pl.lit("ruminants").alias("bu_source")
    ]).unique(subset=["product_code"])

    # Normalize Companion products (unnest storage_requirements)
    companion_products_norm = companion_products.select([
        pl.col("sku").alias("product_code"),
        pl.col("name").alias("product_name"),
        pl.lit(None, dtype=pl.String).alias("therapeutic_class"),
        pl.col("category"),
        pl.col("form"),
        pl.col("storage_requirements").struct.field("min_temp_c").alias("temp_min_c"),
        pl.col("storage_requirements").struct.field("max_temp_c").alias("temp_max_c"),
        pl.col("storage_requirements").struct.field("light_sensitive").alias("light_sensitive"),
        pl.col("dose_ml"),
        pl.lit(None, dtype=pl.Float64).alias("unit_volume_ml"),
        pl.lit("companion").alias("bu_source")
    ])

    # Union all products
    dim_product = pl.concat([
        poultry_products,
        ruminants_products,
        companion_products_norm
    ])

    # Generate surrogate keys
    dim_product = dim_product.sort(["bu_source", "product_code"]).with_row_index(name="product_sk", offset=1)

    # Reorder columns
    dim_product = dim_product.select([
        "product_sk", "product_code", "product_name", "therapeutic_class", "category",
        "form", "temp_min_c", "temp_max_c", "light_sensitive", "dose_ml", "unit_volume_ml", "bu_source"
    ])

    print(f"  Created {len(dim_product)} products")
    return dim_product


def build_dim_site(poultry, ruminants):
    """Build dim_site from poultry + ruminants"""
    print("\nTRANSFORM: Building dim_site...")

    # Extract sites
    poultry_sites = poultry.select([
        pl.col("site_code"),
        pl.lit("poultry").alias("bu_source")
    ]).unique()

    ruminants_sites = ruminants.select([
        pl.col("production_site").alias("site_code"),
        pl.lit("ruminants").alias("bu_source")
    ]).unique()

    # Union sites
    all_sites = pl.concat([poultry_sites, ruminants_sites]).unique(subset=["site_code"])

    # Extract country from site_code
    dim_site = all_sites.with_columns([
        pl.col("site_code").str.split("-").list.get(1).alias("country")
    ])

    # Map country to region
    dim_site = dim_site.with_columns(
        pl.col("country").replace(REGION_MAP).alias("region")
    )

    # Generate surrogate keys
    dim_site = dim_site.sort(["country", "site_code"]).with_row_index(name="site_sk", offset=1)

    # Reorder columns
    dim_site = dim_site.select(["site_sk", "site_code", "country", "region", "bu_source"])

    print(f"  Created {len(dim_site)} sites")
    return dim_site


def build_fact_batch_production(poultry, ruminants, companion_products, companion_batches, dim_product, dim_specie, dim_site):
    """Build fact_batch_production from 3 sources"""
    print("\nTRANSFORM: Building fact_batch_production...")

    # Create species lookup dict
    species_lookup = dict(zip(dim_specie["specie_code"], dim_specie["specie_sk"]))

    # Normalize Poultry batches
    fact_poultry = poultry.select([
        pl.col("batch_id"),
        pl.col("product_code"),
        pl.col("site_code"),
        pl.col("production_date").str.strptime(pl.Date, "%Y-%m-%d"),
        pl.col("expiry_date").str.strptime(pl.Date, "%Y-%m-%d"),
        pl.col("release_date").str.strptime(pl.Date, "%Y-%m-%d", strict=False),
        pl.col("quantity_doses"),
        pl.lit(None, dtype=pl.Int64).alias("quantity_units"),
        pl.col("qc_status").alias("batch_status"),
        pl.lit(None, dtype=pl.Boolean).alias("gmp_deviation"),
        pl.lit(None, dtype=pl.String).alias("destination_market"),
        pl.col("target_species"),
        pl.lit("poultry").alias("bu_source")
    ])

    # Convert target_species to array
    fact_poultry = fact_poultry.with_columns(
        pl.col("target_species").map_elements(
            lambda x: [species_lookup[x]] if x in species_lookup else [],
            return_dtype=pl.List(pl.Int64)
        ).alias("targeted_species")
    )

    # Normalize Ruminants batches
    fact_ruminants = ruminants.select([
        pl.col("lot_number").alias("batch_id"),
        pl.col("product_ref").alias("product_code"),
        pl.col("production_site").alias("site_code"),
        pl.col("manufacturing_date").str.strptime(pl.Date, "%Y-%m-%d").alias("production_date"),
        pl.col("expiration_date").str.strptime(pl.Date, "%Y-%m-%d").alias("expiry_date"),
        pl.lit(None, dtype=pl.Date).alias("release_date"),
        pl.lit(None, dtype=pl.Int64).alias("quantity_doses"),
        pl.col("quantity_units"),
        pl.col("batch_status"),
        pl.col("gmp_deviation"),
        pl.lit(None, dtype=pl.String).alias("destination_market"),
        pl.col("target_species"),
        pl.lit("ruminants").alias("bu_source")
    ])

    # Convert target_species to array
    fact_ruminants = fact_ruminants.with_columns(
        pl.col("target_species").map_elements(
            lambda x: [species_lookup[x]] if x in species_lookup else [],
            return_dtype=pl.List(pl.Int64)
        ).alias("targeted_species")
    )

    # Normalize Companion batches (need to join with products for target_species)
    companion_batches_with_species = companion_batches.join(
        companion_products.select(["sku", "target_species"]),
        left_on="product_sku",
        right_on="sku",
        how="left"
    )

    fact_companion = companion_batches_with_species.select([
        pl.col("batch_id"),
        pl.col("product_sku").alias("product_code"),
        pl.lit(None, dtype=pl.String).alias("site_code"),
        pl.col("produced_at").str.strptime(pl.Date, "%Y-%m-%d").alias("production_date"),
        pl.lit(None, dtype=pl.Date).alias("expiry_date"),
        pl.lit(None, dtype=pl.Date).alias("release_date"),
        pl.lit(None, dtype=pl.Int64).alias("quantity_doses"),
        pl.col("quantity_units"),
        pl.col("status").alias("batch_status"),
        pl.lit(None, dtype=pl.Boolean).alias("gmp_deviation"),
        pl.col("destination_market"),
        pl.col("target_species"),
        pl.lit("companion").alias("bu_source")
    ])

    # Convert target_species array to targeted_species
    fact_companion = fact_companion.with_columns(
        pl.col("target_species").map_elements(
            lambda arr: [species_lookup[s] for s in arr if s in species_lookup],
            return_dtype=pl.List(pl.Int64)
        ).alias("targeted_species")
    )

    # Union all facts
    fact = pl.concat([
        fact_poultry.drop("target_species"),
        fact_ruminants.drop("target_species"),
        fact_companion.drop("target_species")
    ])

    # Lookup product_fk
    fact = fact.join(
        dim_product.select(["product_sk", "product_code"]),
        on="product_code",
        how="left"
    ).rename({"product_sk": "product_fk"})

    # Lookup site_fk (left join - companion has NULL)
    fact = fact.join(
        dim_site.select(["site_sk", "site_code"]),
        on="site_code",
        how="left"
    ).rename({"site_sk": "site_fk"})

    # Generate surrogate keys
    fact = fact.sort(["bu_source", "production_date", "batch_id"]).with_row_index(name="batch_production_sk", offset=1)

    # Reorder columns
    fact = fact.select([
        "batch_production_sk", "batch_id", "product_fk", "site_fk",
        "production_date", "expiry_date", "release_date",
        "quantity_doses", "quantity_units", "batch_status",
        "gmp_deviation", "destination_market", "bu_source", "targeted_species"
    ])

    print(f"  Created {len(fact)} batches")
    return fact


def load_parquet(dim_product, dim_specie, dim_site, fact):
    """Write 4 parquet files"""
    print("\nLOAD: Writing parquet files...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dim_product.write_parquet(OUTPUT_DIR / "dim_product.parquet")
    print(f"  Written: dim_product.parquet ({len(dim_product)} rows)")

    dim_specie.write_parquet(OUTPUT_DIR / "dim_specie.parquet")
    print(f"  Written: dim_specie.parquet ({len(dim_specie)} rows)")

    dim_site.write_parquet(OUTPUT_DIR / "dim_site.parquet")
    print(f"  Written: dim_site.parquet ({len(dim_site)} rows)")

    fact.write_parquet(OUTPUT_DIR / "fact_batch_production.parquet")
    print(f"  Written: fact_batch_production.parquet ({len(fact)} rows)")


def main():
    print("=" * 60)
    print("ELT: CEVA Animal Health - Star Schema")
    print("=" * 60)

    # Extract
    poultry, ruminants, companion_products, companion_batches = extract_sources()

    # Transform Dimensions
    dim_specie = build_dim_specie(poultry, ruminants, companion_products)
    dim_product = build_dim_product(poultry, ruminants, companion_products)
    dim_site = build_dim_site(poultry, ruminants)

    # Transform Fact
    fact = build_fact_batch_production(
        poultry, ruminants, companion_products, companion_batches,
        dim_product, dim_specie, dim_site
    )

    # Load
    load_parquet(dim_product, dim_specie, dim_site, fact)

    print("\n" + "=" * 60)
    print("ELT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
