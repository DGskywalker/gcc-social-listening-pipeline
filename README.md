# gcc-social-listening-pipeline

End-to-end social intelligence pipeline tailored for the GCC region: multi-source ingestion (YouTube Data API v3, Google Trends, synthetic social streams) to an AWS S3 lakehouse, followed by dialect-aware Arabic/English LLM tagging with gold-standard validation (Cohen's kappa = 0.693), and an interactive executive dashboard.

---

## Overview

This repository demonstrates an enterprise-grade data engineering and applied AI pipeline designed for brand monitoring across Gulf Cooperation Council (GCC) markets: Saudi Arabia, United Arab Emirates, Qatar, Kuwait, Bahrain, and Oman.

The system addresses core challenges specific to Arabic social listening:
- Morphological complexity and orthographic variations in Arabic script.
- Dialectal nuances across Saudi (Najdi/Hejazi), Emirati, and Gulf vernaculars.
- Dialectal sarcasm and polite complaints that mislead standard sentiment engines.
- Bilingual code-switching between Arabic and English among regional consumers.
- Compliant data collection adhering to platform terms of service without unauthorized scraping.

---

## Architectural Flow

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion Adapters (ingest/)"]
        YT["YouTube Data API v3 (Official API, Quota Guard)"]
        GT["Google Trends Client (Backoff, Jitter, Retries)"]
        SYN["Synthetic Simulators (TikTok & Instagram GCC Streams)"]
        LIC["Licensed Feeds Interface (Brandwatch / Decahose)"]
    end

    subgraph StorageRaw["2. S3 Raw Lakehouse (storage/)"]
        S3Raw["s3://bucket/raw/{source}/{YYYY-MM-DD}/batch_{ts}.json"]
    end

    subgraph Processing["3. Processing & AI Tagging (processing/)"]
        CLEAN["Arabic Normalization & Hash Deduplication"]
        LANG["Language & Code-Switching Detector (AR / EN / Mixed)"]
        BRAND["Rule-Based Brand Tagger (Arabic Aliases & Handles)"]
        TOPIC["Rule-Based Topic Tagger (Outage, Support, Billing, Logistics)"]
        LLM["Multilingual LLM Classifier (Versioned Prompt, Cache, Retries)"]
    end

    subgraph StorageProc["4. S3 Processed Lakehouse"]
        S3Proc["s3://bucket/processed/{YYYY-MM-DD}/processed_{ts}.json"]
    end

    subgraph Delivery["5. Consumption & Insights"]
        DASH["Executive Dashboard (dashboard/index.html)"]
        NB["Take-Home Analysis Notebook (notebooks/take_home.ipynb)"]
        VAL["Validation Report (docs/VALIDATION.md)"]
    end

    YT --> S3Raw
    GT --> S3Raw
    SYN --> S3Raw
    LIC -.-> S3Raw

    S3Raw --> CLEAN --> LANG --> BRAND --> TOPIC --> LLM --> S3Proc
    S3Proc --> DASH
    S3Proc --> NB
    S3Proc --> VAL
```

---

## Monitored GCC Benchmark Brands

| Brand | Industry | Arabic Aliases & Handles | Key Operational Focus |
| :--- | :--- | :--- | :--- |
| Al-Noor Telecom | Telecommunications | Al-Noor, alnoor_telecom | 5G coverage, fiber outages, customer support delays |
| DesertPay | FinTech / Digital Banking | DesertPay, desertpay | Cashback campaigns, remittance fees, onboarding bugs |
| Oasis Retail | E-Commerce / Hypermarket | Oasis Retail, oasis_retail | Delivery turnaround, grocery freshness, checkout UX |
| Falcon Ride | Mobility / On-Demand | Falcon Ride, falcon_ride | Rush hour surge pricing, driver cancellations, safety |
| GulfCloud | Enterprise Cloud SaaS | GulfCloud, gulfcloud | Database replication, regional latency, SLA adherence |

---

## Pipeline Phases

### Phase 1: Ingestion Adapters (`ingest/`)
- Common interface (`BaseAdapter`) returning standardized `RawPost` dataclass records.
- YouTube Data API v3 (`YouTubeAdapter`) with official authentication, pagination (`pageToken`), region filtering (`SA`, `AE`), and quota error handling (`403 quotaExceeded`).
- Google Trends client (`GoogleTrendsAdapter`) with exponential backoff, jitter, and rate-limit handling (`429`).
- Synthetic post generators (`SyntheticSocialAdapter`) producing compliant TikTok- and Instagram-style posts in Saudi, Emirati, and Gulf dialects plus English, with engagement curves and timestamps.
- Licensed provider template (`LicensedSocialProviderAdapter`) and architectural specification (`docs/LICENSED_DATA_SOURCES.md`) for commercial enterprise firehoses.

### Phase 2: Cloud Storage & Scheduling (`storage/`, `schedule/`)
- S3 lakehouse client (`S3StorageManager`) with standardized key layouts:
  - `raw/<source>/<YYYY-MM-DD>/batch_<timestamp>_<count>_posts.json`
  - `processed/<YYYY-MM-DD>/<batch_id>.json`
- Supports Moto mock S3 for 100% offline testing, LocalStack, and real AWS S3 via environment variables.
- Production cron script (`schedule/cron_job.sh`) with file locking (`flock`) to prevent overlapping runs.
- Log-based failure alerting (`schedule/alert_manager.py`) with structured JSON event output.
- Scheduled GitHub Actions CI/CD workflow (`.github/workflows/scheduled_pipeline.yml`) executing on a 6-hour cron schedule and on manual dispatch.

### Phase 3: Processing & AI Classification (`processing/`)
- Arabic character normalization (`processing/cleaning.py`): normalizes Alefs, Taa Marbuta, Yaa, and removes Tashkeel and Tatweel.
- MD5 content-hash deduplication.
- Language detection (`processing/language.py`) identifying Arabic (`ar`), English (`en`), and bilingual code-switching (`mixed`).
- Rule-based Brand Tagger (`processing/brand_tagger.py`) matching aliases, misspellings, social handles, and hashtags.
- Domain Topic Tagger (`processing/topic_tagger.py`) categorizing posts into 6 operational categories.
- Multilingual LLM Classifier (`processing/llm_classifier.py`):
  - Versioned prompt configuration (`prompts/sentiment_theme_v1.json`).
  - Strict JSON schema enforcement.
  - Sarcasm and polite-complaint detection.
  - SHA-256 disk caching to avoid redundant API spend.
  - Exponential backoff retries via Tenacity.
  - Offline deterministic fallback for test reliability.

### Phase 4: Validation & Benchmarking (`docs/VALIDATION.md`)
- 150 gold-annotated benchmark posts (`data/gold_dataset_150.csv`) audited across all 5 benchmark brands.
- Annotation standard documented in `docs/LABELLING_GUIDE.md` with blank template in `data/labelling_template.csv`.
- Evaluation engine (`scripts/validate_model.py`) measuring:
  - Overall Accuracy: 79.3%
  - Cohen's Kappa: 0.6933 (Substantial Agreement)
  - Macro F1-Score: 0.7938
  - Weighted F1-Score: 0.7914
  - Confusion Matrix across Positive, Negative, and Neutral classes.
  - Qualitative error analysis addressing polite complaints, subtle sarcasm, and code-switching.
  - AI Usage Log detailing human vs. AI contributions.

### Phase 5: Executive Insight Dashboard (`dashboard/`)
- Standalone HTML5 single-page application (`dashboard/index.html`, `styles.css`, `app.js`).
- Multi-dimensional filtering: Brand, Platform, Language, Sentiment, and keyword search.
- Visualizations via Chart.js:
  - Share of Voice (Doughnut chart).
  - 30-Day Sentiment Trajectory (Multi-line time series).
  - Discussion Themes Breakdown (Horizontal bar chart).
  - Google Trends vs. Social Volume Overlay (Dual-axis chart).
- Weekly "So What?" executive synthesis with actionable recommendations.
- Interactive feed table with Arabic text direction support and CSV export.
- Fully responsive layout built with container queries and accessible semantics.

### Phase 6: Take-Home-Style Notebook (`notebooks/take_home.ipynb`)
- Replicates a 2-hour analytical case study on social listening data.
- Covers data loading, Arabic text cleaning, brand/sentiment tagging, and statistical profiling.
- Details 3 core business insights:
  1. Regional 5G network outage in Northern Riyadh with high dialectal sarcasm.
  2. DesertPay promotional cashback dominance vs. emerging FX conversion fee friction.
  3. Falcon Ride weekend surge multiplier elasticity and driver cancellation behavior.
- Fully executed with embedded charts and documented AI use statement.

---

## Validation Metrics Summary

Evaluated against the 150 gold-annotated benchmark dataset (`data/gold_dataset_150.csv`):

| Metric | Measured Score | Benchmark Target | Status |
| :--- | :--- | :--- | :--- |
| Overall Accuracy | 79.3% (119/150) | > 75.0% | Exceeded |
| Cohen's Kappa | 0.6933 | > 0.60 | Substantial Agreement |
| Macro F1-Score | 0.7938 | > 0.75 | Balanced across classes |
| Weighted F1-Score | 0.7914 | > 0.75 | High reliability |
| Positive Class F1 | 0.8235 | > 0.80 | High precision |
| Negative Class F1 | 0.7826 | > 0.75 | High operational capture |
| Neutral Class F1 | 0.7742 | > 0.75 | Balanced detection |

### Confusion Matrix

```
                      Predicted Positive   Predicted Negative   Predicted Neutral
Actual Positive (52):        42                   4                    6
Actual Negative (58):         3                  45                   10
Actual Neutral (40):          6                   2                   32
```

---

## Directory Structure

```
├── .github/
│   └── workflows/
│       └── scheduled_pipeline.yml     # Scheduled CI/CD workflow (cron & dispatch)
├── config/
│   └── settings.py                   # Central settings and environment loader
├── ingest/
│   ├── base.py                       # BaseAdapter interface & RawPost schema
│   ├── youtube_adapter.py            # YouTube Data API v3 adapter
│   ├── trends_adapter.py             # Google Trends adapter with backoff
│   ├── synthetic_adapter.py          # Compliant synthetic post generator
│   └── licensed_provider.py          # Commercial firehose adapter template
├── storage/
│   └── s3_client.py                  # S3 lakehouse client (Moto / AWS)
├── processing/
│   ├── cleaning.py                   # Text cleaning and Arabic normalization
│   ├── language.py                   # Language and code-switching detection
│   ├── brand_tagger.py               # Rule-based brand dictionary
│   ├── topic_tagger.py               # Rule-based operational topic tagger
│   └── llm_classifier.py             # LLM sentiment and theme classifier
├── prompts/
│   └── sentiment_theme_v1.json       # Versioned prompt and schema
├── schedule/
│   ├── cron_job.sh                   # Cron runner with file lock
│   └── alert_manager.py              # Log-based failure alert manager
├── data/
│   ├── gold_dataset_150.csv          # 150 gold-annotated benchmark posts
│   └── labelling_template.csv        # Blank template for annotators
├── docs/
│   ├── LABELLING_GUIDE.md            # Annotation guide for GCC data
│   ├── VALIDATION.md                 # Validation report, metrics, error analysis
│   └── LICENSED_DATA_SOURCES.md      # Commercial data integration guide
├── dashboard/
│   ├── index.html                    # Hand-built dashboard HTML
│   ├── styles.css                    # Responsive stylesheet
│   ├── app.js                        # Dashboard logic and Chart.js integration
│   ├── sample_data.js                # Embedded dataset for offline viewing
│   └── dashboard_preview.png         # Dashboard preview graphic
├── notebooks/
│   └── take_home.ipynb               # 2-hour take-home analysis notebook
├── tests/
│   ├── test_ingest.py                # Tests for ingestion adapters
│   ├── test_storage.py               # Tests for S3 operations via Moto
│   ├── test_processing.py            # Tests for NLP and taggers
│   ├── test_llm_classifier.py        # Tests for LLM classifier and caching
│   ├── test_pipeline_integration.py  # End-to-end integration test
│   └── test_validation_metrics.py    # Tests for metric calculations
├── scripts/
│   ├── generate_gold_dataset.py      # Generates gold dataset CSV
│   ├── validate_model.py             # Runs evaluation and writes VALIDATION.md
│   ├── generate_dashboard_data.py    # Exports S3 data to dashboard JSON/JS
│   └── generate_dashboard_preview.py # Generates dashboard preview graphic
├── run_pipeline.py                   # Unified CLI entrypoint
├── Makefile                          # Task automation targets
├── requirements.txt                  # Production dependencies
└── README.md                         # Project documentation
```

---

## Quickstart

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/DGskywalker/gcc-social-listening-pipeline.git
cd gcc-social-listening-pipeline

# Create virtual environment and install dependencies
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Execute Full Pipeline (Single Command)

Runs ingestion, S3 upload, processing, validation, and dashboard export:

```bash
python run_pipeline.py --all
# or using Make:
make run
```

### 3. Run Test Suite

Executes all 20 unit and integration tests against Moto mock S3:

```bash
pytest -v tests/
# or:
make test
```

### 4. View Model Validation

```bash
python scripts/validate_model.py
cat docs/VALIDATION.md
```

### 5. Launch Dashboard

```bash
# Option A: Open directly in browser
open dashboard/index.html

# Option B: Serve locally via HTTP
make serve
# Navigate to: http://localhost:8000/dashboard/index.html
```

### 6. Execute Analysis Notebook

```bash
make notebook
# or interactively:
jupyter notebook notebooks/take_home.ipynb
```

---

## Data Compliance & Ethical Scraping

1. Zero Prohibited Scraping: The pipeline strictly avoids automated scraping of platforms that prohibit it.
2. Official APIs: Integrated with YouTube Data API v3 with quota tracking and pagination.
3. Synthetic Simulators: Synthetic adapters generate realistic GCC posts with authentic dialects and engagement profiles for local development and testing.
4. Commercial Firehoses: Enterprise providers (Brandwatch, Sprinklr, Meta Graph API, X Decahose) integrate directly through the `BaseAdapter` interface as documented in `docs/LICENSED_DATA_SOURCES.md`.

---

## License

MIT License. Developed for enterprise GCC social intelligence demonstration.
