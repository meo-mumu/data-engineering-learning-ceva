# Frequently Asked Questions

## Data Model Questions

### What is the difference between quantity_doses and quantity_units?

**Answer:**
These fields measure production volume differently based on Business Unit and product type:

**quantity_doses:**
- Used exclusively for Poultry Business Unit vaccine products
- Represents the total number of individual animal vaccinations in a batch
- Example: A batch might contain 100 vials, each with 1,000 doses = 100,000 total doses
- Relevant because poultry vaccines are administered to thousands of birds simultaneously via spray, drinking water, or in-ovo methods
- Other Business Units typically have NULL in this field

**quantity_units:**
- Used for Ruminants and Companion Animals Business Units
- Represents the total number of saleable packages or treatment units
- Example: A batch contains 5,000 bottles of pour-on antiparasitic = 5,000 units
- Each unit typically represents one animal treatment or one retail package
- More aligned with commercial/sales metrics

**Why the distinction?**
Poultry operations vaccinate thousands of birds at once using mass administration, making dose count more relevant than package count. In contrast, ruminant and companion animal products are typically administered individually, making unit count more meaningful.

### Why do some batches have NULL site_fk?

**Answer:**
NULL values in site_fk occur for several legitimate business reasons:

1. **Contract Manufacturing:** Some Companion Animal products are manufactured at Contract Manufacturing Organizations (CMOs) that are not in CEVA's owned site master data. These external facilities do not have site_fk records in the dimensional model.

2. **Legacy Data Migration:** Historical batches manufactured before the current data warehouse implementation may lack complete site attribution.

3. **Multi-Site Blending:** Occasionally, bulk product manufactured at one site is filled/finished at another. Business rules may assign the batch to the finishing site, leaving the bulk manufacturing site unrecorded.

4. **R&D or Pilot Batches:** Small-scale research or stability study batches manufactured in laboratory settings rather than commercial production sites.

**Data Quality:**
- Approximately 5-8% of Companion Animal batches have NULL site_fk
- Less than 1% of Poultry and Ruminants batches have NULL site_fk
- NULL site_fk batches are still valid production batches with complete quality and release information

### How to identify cold chain products?

**Answer:**
Cold chain products can be identified through multiple attributes:

**Primary Method - Therapeutic Class:**
All products with `therapeutic_class = 'vaccine'` require cold chain (+2°C to +8°C) regardless of Business Unit.

**Secondary Indicators:**
- Product names containing "vaccine" or specific vaccine terminology (Newcastle, Influenza, etc.)
- Business Unit context: All Poultry BU products are vaccines requiring cold chain
- Storage temperature specifications in product master data (when available)

**Cold Chain Requirements by BU:**
- **Poultry:** 100% of products require cold chain (all vaccines)
- **Ruminants:** Approximately 30% of products (vaccines only; antiparasitics and antibiotics are typically room temperature stable)
- **Companion Animals:** Approximately 25% of products (vaccines only; spot-ons and tablets are room temperature stable)

**Temperature Monitoring:**
Cold chain products require continuous temperature logging during storage and transport. Temperature excursions must be documented and assessed for product impact.

### What does a GMP deviation mean for a batch?

**Answer:**
A GMP (Good Manufacturing Practice) deviation indicates that something during the batch production did not follow the established, approved manufacturing procedure.

**Impact on Batch:**
- **has_gmp_deviation = TRUE** means a deviation was documented for this batch
- The batch status depends on deviation severity and investigation outcome
- Not all deviations result in batch rejection

**Deviation Outcomes:**
1. **Released with Deviation:** Minor deviations with no quality impact allow batch release after investigation (most common outcome)
2. **Quarantine:** Batch held pending investigation completion
3. **Released with Additional Testing:** Major deviations may require extra QC tests before release
4. **Rejected:** Critical deviations with proven quality impact result in rejection

**Key Point:**
A GMP deviation does NOT automatically mean the batch is defective. It means the manufacturing process varied from standard procedure and required documentation and investigation. Many batches with minor deviations are safely released after assessment.

**Business Context:**
CEVA maintains rigorous GMP standards. Even minor procedural variations (e.g., equipment calibration performed 1 day late) are documented as deviations to ensure comprehensive quality oversight.

### How are targeted_species stored in the fact table?

**Answer:**
The `targeted_species` field in the fact_production table stores animal species as a comma-separated string when a product targets multiple species.

**Format:**
- Single species: `"bovine"` or `"canine"`
- Multiple species: `"bovine,ovine,caprine"` or `"chicken,turkey"`

**Common Values by Business Unit:**

**Poultry BU:**
- `"chicken"` (most common)
- `"turkey"`
- `"duck"`
- `"chicken,turkey"` (combination products)

**Ruminants BU:**
- `"bovine"` (cattle only)
- `"ovine"` (sheep only)
- `"caprine"` (goat only)
- `"bovine,ovine"` (dual registration)
- `"bovine,ovine,caprine"` (tri-species registration)

**Companion Animals BU:**
- `"canine"` (dogs only)
- `"feline"` (cats only)
- `"canine,feline"` (rare, some antiparasitics)

**Querying Considerations:**
To find all batches for a specific species when multiple species exist:
- Use string matching: `WHERE targeted_species LIKE '%bovine%'`
- Parse the comma-separated list in your analytics tool
- Note: Exact match (`targeted_species = 'bovine'`) will miss multi-species products

### What is the typical timeline from production to release?

**Answer:**
The production-to-release timeline varies by Business Unit and product complexity:

**Poultry Business Unit:**
- Typical: 7-14 days
- Range: 5-21 days
- Fastest: Live vaccines with simplified testing (5-7 days)
- Slowest: Inactivated vaccines requiring sterility confirmation (14-21 days)

**Ruminants Business Unit:**
- Typical: 12-18 days
- Range: 10-25 days
- Fastest: Generic antibiotics with established testing (10-12 days)
- Slowest: Novel vaccines or products with potency challenges (18-25 days)

**Companion Animals Business Unit:**
- Typical: 10-15 days
- Range: 7-21 days
- Fastest: Dental/hygiene products with simple testing (7-10 days)
- Slowest: Vaccines and injectable products (14-21 days)

**Factors Affecting Timeline:**
1. Sterility testing: 7-14 days incubation required
2. Potency testing: Complex assays may take 3-7 days
3. Deviation investigations: Can add 5-15 days
4. Quarantine status: Investigation period varies
5. Laboratory backlog: Peak production periods may extend timelines

**Business Impact:**
Shorter cycle times improve cash flow but cannot compromise quality. Extended timelines may indicate quality issues requiring attention.

### Why do some batches show production_date but no release_date?

**Answer:**
Batches with production_date but NULL release_date fall into several categories:

**1. Batches Still in Process (Most Common):**
- Status = 'in_production': Batch is currently being manufactured
- Status = 'qc_testing': Manufacturing complete, QC testing underway
- Status = 'pending': Awaiting QC test initiation
- These batches will receive release_date when testing completes

**2. Batches in Quarantine:**
- Status = 'quarantine': On hold pending investigation
- May eventually be released or rejected
- Investigation timeline varies (typically 7-30 days)

**3. Rejected Batches:**
- Status = 'rejected': Failed QC testing or critical GMP deviation
- Will never receive release_date
- Batch destroyed or reprocessed

**4. Recent Production:**
- Batches produced in current reporting period
- Still within normal QC cycle time
- Expected to show release_date in subsequent data refresh

**Data Quality Check:**
If a batch shows production_date older than 30 days with NULL release_date and status NOT in ('rejected', 'quarantine'), this may indicate:
- Data pipeline issue requiring investigation
- Exceptional delay in QC process
- Missing status update in source system

### How to calculate batch rejection rate correctly?

**Answer:**
Calculating batch rejection rate requires careful definition to avoid misleading metrics:

**Correct Formula:**
```
Rejection Rate = (Count of batches with qc_status = 'rejected') /
                 (Count of batches with qc_status IN ('released', 'rejected')) × 100
```

**Key Points:**

**Denominator Should Include:**
- Only batches that have completed QC testing (released or rejected)
- Excludes batches still in production, pending, or qc_testing status
- Typically filter to batches older than 21 days to ensure QC completion

**Denominator Should NOT Include:**
- Batches currently in quarantine (outcome unknown)
- Batches still in production or QC testing
- R&D or stability batches not intended for commercial release

**Time Period:**
- Use rolling 12-month period for trend analysis
- Monthly snapshots can be volatile due to small sample sizes
- Align to production_date, not release_date

**Segmentation:**
Rejection rates vary significantly by:
- Business Unit (Poultry typically lower than Ruminants)
- Production site (newer facilities may have higher initial rates)
- Product complexity (vaccines higher than simple formulations)
- Always segment analysis accordingly

**Example Query Logic:**
```sql
WHERE qc_status IN ('released', 'rejected')
  AND production_date >= DATE_ADD(CURRENT_DATE, INTERVAL -12 MONTH)
  AND production_date <= CURRENT_DATE
```

### What does pharmaceutical_form tell us about the product?

**Answer:**
The pharmaceutical_form field indicates how the product is formulated and administered, which has significant implications:

**Quality Control Requirements:**
- **Injectable:** Requires sterility testing, endotoxin testing, particulate matter testing
- **Oral solution:** Requires stability testing, pH testing, microbial limits testing
- **Powder:** Requires moisture content testing, reconstitution testing
- **Spot-on/Pour-on:** Requires dermal penetration testing, stability in packaging

**Storage and Handling:**
- **Injectable:** Often requires refrigeration, always requires protection from light
- **Tablet/Bolus:** Requires humidity control, room temperature stable
- **Gel:** Temperature-sensitive, viscosity changes with temperature
- **Powder:** Must remain dry, often requires reconstitution before use

**Manufacturing Complexity:**
- **Injectable:** Highest complexity, requires aseptic processing or terminal sterilization
- **Spot-on:** Specialized filling equipment for small volumes (0.5-3ml)
- **Powder:** Requires specialized blending and particle size control
- **Tablet:** Requires compression equipment and coating capabilities

**Business Unit Patterns:**
- **Poultry:** Primarily injectable (vaccines)
- **Ruminants:** Diverse (injectable, pour-on, bolus, oral solution)
- **Companion Animals:** Diverse (spot-on, tablet, injectable, gel)

**Market Preferences:**
- **European markets:** Preference for spot-on antiparasitics
- **US markets:** Shift toward oral tablets (chewables) for dogs
- **Livestock markets:** Prefer easy administration (pour-on vs injectable)

### How to identify batches at risk of expiry?

**Answer:**
Identifying batches approaching expiry requires calculating remaining shelf life:

**Key Calculations:**

**Remaining Shelf Life (Days):**
```
Days_to_Expiry = expiry_date - CURRENT_DATE
```

**Percentage of Shelf Life Remaining:**
```
Shelf_Life_Remaining_Pct = (expiry_date - CURRENT_DATE) /
                           (expiry_date - production_date) × 100
```

**Risk Categories:**

**Critical Risk (Immediate Action Required):**
- Less than 60 days to expiry
- Less than 20% shelf life remaining
- Batch should be moved to clearance or destruction

**Medium Risk (Monitoring Required):**
- 60-180 days to expiry
- 20-40% shelf life remaining
- Prioritize for distribution to high-turnover customers

**Low Risk (Normal Inventory):**
- More than 180 days to expiry
- More than 40% shelf life remaining
- Normal inventory management

**Business Unit Considerations:**

**Poultry (24-month shelf life):**
- Critical: < 2 months remaining
- Medium: 2-6 months remaining

**Ruminants (30-36 month shelf life):**
- Critical: < 3 months remaining
- Medium: 3-9 months remaining

**Companion Animals (24-30 month shelf life):**
- Critical: < 2 months remaining
- Medium: 2-6 months remaining

**Special Cases:**
- Batches in quarantine status: Assess shelf life impact before release decision
- Rejected batches: Expiry irrelevant, will be destroyed
- Cold chain products: May have accelerated expiry if temperature excursions occurred

**Inventory Management:**
Use FEFO (First Expiry, First Out) rather than FIFO (First In, First Out) for distribution prioritization.

### What drives the difference in batch size across Business Units?

**Answer:**
Batch size (quantity_units or quantity_doses) varies significantly across Business Units due to multiple factors:

**Market Demand Patterns:**

**Poultry:**
- Very large batches (10-50 million doses)
- Justification: Commercial poultry farms vaccinate thousands of birds simultaneously
- Large-scale production matches large-scale customer demand
- Economies of scale are critical for low-margin vaccine market

**Ruminants:**
- Medium batches (20,000-100,000 units)
- Justification: More fragmented customer base (individual farmers)
- Product variety requires smaller, more frequent batches
- Balances production efficiency with inventory turnover

**Companion Animals:**
- Smaller batches (5,000-50,000 units)
- Justification: High product variety (multiple sizes, species, pack configurations)
- Veterinary channel requires diverse SKU availability
- Premium pricing supports smaller batch economics

**Manufacturing Constraints:**

**Equipment Capacity:**
- Filling line capacity limits maximum batch size
- Poultry high-speed lines: 10,000+ vials/hour
- Companion animal spot-on lines: 2,000-4,000 units/hour

**Sterility Requirements:**
- Larger batches require longer sterility testing sample sizes
- Very large batches may be split into sub-batches for testing efficiency

**Quality Risk:**
- Larger batches increase financial risk if rejection occurs
- Complex products may use smaller batches to minimize loss potential

**Shelf Life Considerations:**
- Products with shorter shelf life require smaller, more frequent batches
- Long shelf-life products can support larger batch production

**Typical Batch Sizes by Product Type:**

- Poultry vaccines: 20-50 million doses
- Ruminant vaccines: 30,000-80,000 units
- Ruminant antiparasitics: 50,000-150,000 units
- Companion vaccines: 10,000-30,000 units
- Companion spot-ons: 15,000-60,000 units
- Companion tablets: 25,000-100,000 units

**Trend:**
Increasing automation and demand forecasting accuracy enable larger batch sizes across all BUs, improving manufacturing efficiency.

### How are GMP deviations categorized and what triggers each severity level?

**Answer:**
GMP deviations are classified into three severity levels based on potential impact to product quality:

**Critical Deviations:**

**Definition:** Deviations likely to affect product quality, safety, or efficacy.

**Examples:**
- Sterility test failure or contamination during aseptic processing
- Out-of-specification test results for critical quality attributes
- Use of expired raw materials in formulation
- Equipment malfunction during critical process step (e.g., autoclave failure)
- Environmental monitoring exceeding alert limits in sterile areas
- Temperature excursion outside validated range for cold chain products

**Immediate Actions:**
- Batch automatically placed in quarantine
- Senior management notification within 8 hours
- Investigation must begin immediately
- Batch cannot be released until full investigation complete

**Target Rate:** < 0.5% of batches (less than 1 in 200)

**Major Deviations:**

**Definition:** Deviations that may affect product quality but unlikely to reach the end user or with uncertain quality impact.

**Examples:**
- Equipment calibration performed outside scheduled window (but still within grace period)
- Documentation errors requiring correction (e.g., missing signature corrected within 24 hours)
- Environmental monitoring exceeding action limits in non-sterile areas
- Deviation from in-process test timing (e.g., test performed 30 minutes late)
- Minor equipment malfunction with no proven process impact
- Procedural step performed out of sequence but with no quality consequence

**Immediate Actions:**
- QA notification within 24 hours
- Batch may continue with QA oversight and approval
- Investigation required within 10 working days
- Additional testing may be required before release

**Target Rate:** < 3% of batches

**Minor Deviations:**

**Definition:** Procedural deviations with no quality impact, typically documentation or timing issues.

**Examples:**
- Administrative documentation errors (typos, formatting)
- Cleaning performed slightly outside scheduled window but within validated limits
- Training documentation completed late (but person was qualified)
- Logbook entries made retrospectively within same shift
- Procedural variations that do not affect critical process parameters

**Immediate Actions:**
- Documentation required but no immediate escalation
- Investigation within 30 days
- Typically no impact on batch release timeline
- May be batched for trending analysis

**Target Rate:** < 10% of batches

**Classification Responsibility:**
Initial classification by Quality Assurance department within 4 hours of deviation report. May be reclassified during investigation if additional information emerges.

**Key Principle:**
"When in doubt, classify higher." It is better to over-investigate than to miss a potential quality issue.
