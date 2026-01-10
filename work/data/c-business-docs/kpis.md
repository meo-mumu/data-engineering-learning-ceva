# Key Performance Indicators

## Production Volume Metrics

### Batches Produced per Month
**Definition:** Total number of batches manufactured per month, segmented by Business Unit.

**Measurement:**
- Count of batches with production_date in the reporting month
- Segmented by business_unit_name
- Tracked at site level for multi-site BUs

**Typical Targets:**
- Poultry BU: 80-120 batches/month (seasonal variation)
- Ruminants BU: 60-90 batches/month
- Companion Animals BU: 100-150 batches/month

**Reporting Frequency:** Monthly

**Business Context:**
Production volume reflects market demand and manufacturing capacity utilization. Poultry shows strong seasonality aligned with agricultural cycles.

### Production Volume by Quantity Units
**Definition:** Total quantity units manufactured per month by Business Unit.

**Measurement:**
- Sum of quantity_units for all batches produced in reporting month
- Excludes rejected batches
- Segmented by business_unit_name

**Typical Targets:**
- Ruminants BU: 500,000-800,000 units/month
- Companion Animals BU: 1,200,000-1,800,000 units/month

**Reporting Frequency:** Monthly

### Production Volume by Quantity Doses
**Definition:** Total vaccine doses manufactured per month (Poultry BU specific).

**Measurement:**
- Sum of quantity_doses for poultry batches in reporting month
- Only applicable to Poultry Business Unit

**Typical Target:**
- Poultry BU: 250-400 million doses/month

**Reporting Frequency:** Monthly

**Business Context:**
Poultry vaccines are measured in doses because a single vial contains hundreds or thousands of doses for mass vaccination in commercial poultry operations.

### Production by Site
**Definition:** Production volume distributed across manufacturing sites.

**Measurement:**
- Count of batches per site_name
- Sum of quantity_units or quantity_doses per site
- Month-over-month comparison

**Target Distribution:**
- Libourne (France): 40% of total production (multi-BU site)
- Budapest (Hungary): 25% (primarily Poultry)
- Suzhou (China): 15% (Poultry for APAC market)
- Lenexa (USA): 10% (Ruminants for North America)
- Algete (Spain): 10% (Ruminants for EU market)

**Reporting Frequency:** Monthly

### Production by Product
**Definition:** Top performing products by batch count and volume.

**Measurement:**
- Batch count per product_name
- Total quantity produced per product

**Business Context:**
Identifies high-volume products requiring dedicated production lines and inventory management focus. Used for capacity planning and forecasting.

**Reporting Frequency:** Quarterly

## Quality Metrics

### Batch Rejection Rate
**Definition:** Percentage of batches rejected after QC testing.

**Formula:**
```
Rejection Rate = (Number of batches with qc_status = 'rejected' / Total batches produced) × 100
```

**Measurement Period:** Rolling 12 months

**Target Thresholds:**
- Acceptable: < 2%
- Warning: 2-5%
- Critical: > 5%

**Reporting Frequency:** Monthly

**Business Impact:**
High rejection rates indicate manufacturing quality issues, result in financial losses, and may trigger regulatory investigations. Each percentage point increase represents significant cost impact.

### GMP Deviation Rate
**Definition:** Frequency of GMP deviations per 100 batches produced.

**Formula:**
```
GMP Deviation Rate = (Count of batches with has_gmp_deviation = TRUE / Total batches produced) × 100
```

**Measurement Period:** Rolling 12 months

**Target Thresholds by Severity:**
- Critical deviations: < 0.5% (less than 1 in 200 batches)
- Major deviations: < 3%
- Minor deviations: < 10%

**Reporting Frequency:** Monthly

**Business Impact:**
GMP deviation trends are monitored by regulatory authorities. High rates may trigger regulatory inspections and impact manufacturing license renewal.

### First Pass Release Rate
**Definition:** Percentage of batches released without requiring additional testing or investigation.

**Formula:**
```
First Pass Rate = (Batches released without quarantine or deviation / Total batches released) × 100
```

**Target:** > 95%

**Reporting Frequency:** Monthly

**Business Context:**
Measures manufacturing consistency and quality system effectiveness. Batches requiring quarantine or extensive investigation delay time-to-market and increase costs.

### QC Testing Backlog
**Definition:** Number of batches in qc_testing status for more than 14 days.

**Measurement:**
- Count of batches with qc_status = 'qc_testing'
- Filtered by days_since_production > 14

**Target:** < 5 batches in backlog at any time

**Reporting Frequency:** Weekly

**Business Impact:**
Testing backlog delays product availability and may cause stockouts. Extended testing periods may also indicate laboratory capacity issues.

## Operational Metrics

### Average Release Cycle Time
**Definition:** Mean number of days from production date to release date.

**Formula:**
```
Avg Cycle Time = Mean(release_date - production_date) for batches with qc_status = 'released'
```

**Target by Business Unit:**
- Poultry: 7-10 days
- Ruminants: 12-16 days
- Companion Animals: 10-14 days

**Reporting Frequency:** Monthly

**Business Context:**
Shorter cycle times improve cash flow and reduce inventory holding costs. However, cycle time cannot compromise testing thoroughness.

### Batch Size Efficiency
**Definition:** Average quantity per batch compared to theoretical maximum capacity.

**Measurement:**
- Mean quantity_units per batch by product
- Compared to production line rated capacity

**Target:** > 85% of theoretical capacity

**Reporting Frequency:** Quarterly

**Business Context:**
Low batch sizes indicate inefficient capacity utilization. Very high batch sizes may increase quality risk.

### Quarantine Resolution Time
**Definition:** Average days batches spend in quarantine status before disposition.

**Measurement:**
- Mean duration in quarantine status
- Segmented by resolution outcome (released vs rejected)

**Target:** < 7 days average quarantine duration

**Reporting Frequency:** Monthly

**Business Impact:**
Extended quarantine periods tie up working capital and warehouse space. Rapid resolution improves operational efficiency.

### Cold Chain Compliance Rate
**Definition:** Percentage of vaccine batches maintaining required temperature throughout storage.

**Measurement:**
- Count of cold chain products without temperature excursions
- Based on continuous temperature monitoring data

**Target:** > 99.5%

**Reporting Frequency:** Monthly

**Business Impact:**
Cold chain failures compromise product efficacy and may require batch destruction. Critical for vaccine products.

### Production Schedule Adherence
**Definition:** Percentage of planned batches produced within scheduled week.

**Measurement:**
- Batches produced on schedule / Total planned batches × 100

**Target:** > 90%

**Reporting Frequency:** Weekly

**Business Context:**
Measures production reliability and planning effectiveness. Low adherence indicates capacity constraints or planning issues.

## Business Unit Specific Metrics

### Poultry BU: Seasonal Demand Fulfillment
**Definition:** Ability to meet peak seasonal demand (Q2-Q3 in Northern Hemisphere).

**Measurement:**
- Production volume in peak months vs planned volume
- Inventory availability during high-demand periods

**Target:** 100% of forecasted seasonal demand

### Ruminants BU: Multi-Site Coordination
**Definition:** Production distribution efficiency across three sites.

**Measurement:**
- Variance in production volume across sites
- Inter-site product transfer frequency

**Target:** ± 15% variance from planned site allocation

### Companion Animals BU: Portfolio Diversity
**Definition:** Production coverage across therapeutic classes and pharmaceutical forms.

**Measurement:**
- Number of distinct products manufactured per quarter
- Production volume distribution across therapeutic classes

**Target:** Minimum 80% of product portfolio manufactured at least once per quarter

## Financial Impact Metrics

### Cost of Quality (Rejection)
**Definition:** Financial loss from rejected batches.

**Measurement:**
- Sum of rejected batch values (materials + labor)
- Expressed as percentage of total production value

**Target:** < 1% of total production value

**Reporting Frequency:** Quarterly

### Deviation Investigation Cost
**Definition:** Resource cost of investigating and resolving GMP deviations.

**Measurement:**
- Labor hours × average hourly rate
- Includes investigation, documentation, and CAPA implementation

**Benchmark:** < €5,000 per major deviation; < €1,000 per minor deviation

**Reporting Frequency:** Quarterly
