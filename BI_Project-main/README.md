# Phishing URL Detection & Analysis - BI Solution

## Project Overview

This is a comprehensive Business Intelligence solution for detecting and analyzing phishing URLs. The project includes:
- **Data extraction** from raw CSV files
- **Data transformation** with feature engineering
- **Star schema** data warehouse (SQLite + MySQL)
- **Power BI dashboards** with  DAX measures

---

## Dataset

**Source File:** `data/raw/urls.csv`
- **235,795 URLs** (100,945 phishing + 134,850 benign)
- **Columns:** URL, Domain, label, length

**Processed Data:** `data/processed/fact_phishing_incident.csv`
- **11 columns** with engineered features

---

## Data Structure

### Fact Table: `fact_phishing_incident`
| Column | Type | Description |
|--------|------|-------------|
| URL | string | Full URL |
| Domain | string | Domain name |
| label | string | benign/phishing |
| length | int | URL character length |
| is_phishing | int | 0=benign, 1=phishing |
| has_ip | int | 1 if URL contains IP address |
| special_char_count | int | Count of special characters |
| has_suspicious_keyword | int | 1 if contains phishing keywords |
| length_category | string | Very Short/Short/Medium/Long/Very Long |
| special_char_range | string | None/Low/Medium/High/Very High |
| characteristic_key | string | Composite key for linking |

### Dimension Tables
- **dim_label** (2 rows): benign, phishing classifications
- **dim_domain** (220,086 rows): domain statistics & phishing rates
- **dim_url_characteristics** (38 rows): feature combinations & risk profiles
- **dim_url_length** (5 rows): URL length categories

---

## Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Processing Pipeline
Run scripts in order:

```bash
# Extract & transform raw data
python scripts/extract/read_data.py

# Create aggregations
python scripts/aggregate.py

# Enrich fact table
python scripts/enrich_fact_table.py

# Add composite keys
python scripts/add_composite_key.py

# Load to SQLite
python scripts/load/load.py

# Export dimensions from MySQL
python scripts/export_dimensions.py
```

---

## Project Structure

```
BI_Phising/
├── data/
│   ├── raw/
│   │   └── urls.csv                          # Raw data (235,795 rows)
│   └── processed/
│       ├── fact_phishing_incident.csv        # Main fact table
│       ├── dim_label.csv                     # Label dimension
│       ├── dim_domain.csv                    # Domain dimension
│       ├── dim_url_characteristics.csv       # Characteristics dimension
│       ├── dim_url_length.csv                # Length dimension
│       ├── agg_incidents_per_label.csv       # Aggregations
│       ├── agg_length_stats.csv
│       └── phishing.db                       # SQLite database
├── scripts/
│   ├── extract/
│   │   └── read_data.py                      # Data extraction & cleaning
│   ├── transform/
│   │   └── transform.py                      # Feature engineering
│   ├── load/
│   │   └── load.py                           # Load to SQLite
│   ├── aggregate.py                          # Create aggregations
│   ├── enrich_fact_table.py                  # Add length_category
│   ├── add_composite_key.py                  # Add composite keys
│   ├── add_risk_profile_to_fact.py           # Optional enhancement
│   ├── export_dimensions.py                  # MySQL export
│   └── clean_dim_characteristics.py          # Clean dimension table
├── modeling/                                  # Reserved for ML models
├── requirements.txt                          # Python dependencies
└── README.md                                 # This file
```

---

## Features Engineered

### 1. **is_phishing** (Target Variable)
- 0 = benign/legitimate URLs
- 1 = phishing/malicious URLs

### 2. **has_ip** (IP Address Detection)
- 1 if URL contains IP address (e.g., http://192.168.1.1)
- 0 otherwise

### 3. **special_char_count** (Suspicious Patterns)
Counts these characters: `@`, `-`, `?`, `_`, `=`, `%`, `&`
- Phishing URLs often use special chars to obfuscate domains

### 4. **has_suspicious_keyword** (Phishing Keywords)
Detects: login, verify, update, secure, bank, confirm, account, password
- Common in phishing URLs targeting user credentials

### 5. **length_category** (URL Length Bins)
- Very Short (<20 chars)
- Short (20-29 chars)
- Medium (30-49 chars)
- Long (50-99 chars)
- Very Long (100+ chars)

### 6. **special_char_range** (Character Density)
- None (0 chars)
- Low (1-3 chars)
- Medium (4-7 chars)
- High (8-15 chars)
- Very High (15+ chars)

### 7. **characteristic_key** (Composite Key)
Links fact table to dim_url_characteristics for multi-dimensional analysis

---

## Database Connections

### SQLite (Power BI Ready)
```
Location: data/processed/phishing.db
Tables: 5 (1 fact + 4 dimensions)
```

### MySQL (Optional Sync)
```
Database: bi-project
Tables: Same structure as SQLite
```

---

## Power BI Setup

### Import Data
1. Open Power BI Desktop
2. Get Data → SQLite (via ODBC) or CSV files
3. Load all 5 tables

### Create Relationships
1. Go to Model view
2. Create 4 relationships:
   - `fact[label]` → `dim_label[label_name]` (Many-to-One)
   - `fact[Domain]` → `dim_domain[domain_name]` (Many-to-One)
   - `fact[length_category]` → `dim_url_length[length_category]` (Many-to-One)
   - `fact[characteristic_key]` → `dim_url_characteristics[characteristic_key]` (Many-to-One)

### Add DAX Measures
Copy all measures from the DAX section into your Power BI model.

---

## DAX Measures (46 Total)

### Fact Table (26 measures)
- Basic counts: Total Incidents, Total Phishing, Total Benign
- Percentages: Phishing %, Benign %
- Features: URLs with IP, URLs with Suspicious Keywords
- Length analysis: Avg URL Length, Max/Min Length
- Risk scoring: Critical Risk URLs, Critical Risk %

### Dimension Tables (20 measures)
- Domain analytics: Avg Phishing Rate, Domains by Risk Level
- Characteristic profiles: Risk profile distributions
- Length statistics: Category counts and ranges

---

## Dashboards (3 Total)

### Dashboard 1: Executive Summary
- 8 visuals
- KPI cards (Total Incidents, Phishing, Benign)
- Top 10 phishing domains
- Phishing distribution pie chart

### Dashboard 2: Deep Dive Analysis
- 8 visuals
- Feature impact analysis (IP, Keywords)
- URL length comparisons
- Special character analysis
- Risk profile distribution

### Dashboard 3: Advanced Insights
- 8 visuals
- Domain risk categorization
- Drill-through capability
- Risk profile breakdown
- Feature correlations

**Total:** 24 visuals across 3 dashboards

---

## Star Schema Design

```
                    dim_label
                        ↑
                        │ (label)
                        │
fact_phishing_incident ─┼─→ dim_domain
       (235,795 rows)  │ (Domain)
                        │
                        ├─→ dim_url_length
                        │ (length_category)
                        │
                        └─→ dim_url_characteristics
                          (characteristic_key)
```

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Total URLs | 235,795 |
| Phishing URLs | 100,945 (42.8%) |
| Benign URLs | 134,850 (57.2%) |
| Unique Domains | 220,086 |
| Domains with 100% Phishing | ~5,000 |
| Avg URL Length (Phishing) | 46.24 chars |
| Avg URL Length (Benign) | 27.23 chars |
| Special Char Avg | 2.5 per URL |

---

## Running the Full Pipeline

```bash
# One-command execution of entire ETL
.\venv\Scripts\activate
python scripts/extract/read_data.py && python scripts/aggregate.py && python scripts/enrich_fact_table.py && python scripts/add_composite_key.py && python scripts/load/load.py
```

---

## Troubleshooting

### SQLite Not Found in Power BI
- Install SQLite ODBC Driver from: https://www.ch-werner.de/sqliteodbc/
- Create DSN pointing to `phishing.db`

### MySQL Connection Issues
- Update credentials in `scripts/export_dimensions.py`
- Ensure MySQL service is running
- Check database exists: `SHOW DATABASES;`

### DAX Measure Errors
- Ensure base measures are created before dependent measures
- Check table relationships are active (solid lines in Model view)

---

## Technologies Used

- **Python 3.13** - Data processing
- **Pandas** - Data transformation
- **SQLite** - Local database
- **MySQL** - Optional enterprise database
- **Power BI** - Business Intelligence & visualization
- **DAX** - Data Analysis Expressions

---

## Author
Chaima khoualdia Ranim Aloui  - BI Phishing Detection Project


