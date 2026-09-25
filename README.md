# SentinelEye 🛰️👁️

**Semantic Retrieval and Multi-Temporal Change Analysis of Satellite Imagery**  
*Smart India Hackathon (SIH) 2026 | Problem Statement PS26227 (DGIS / Indian Army, Space Technology Theme)*  
**Team Ulysses**

---

## 1. Overview & Problem Statement

**Problem Statement PS26227**: Military and geospatial intelligence analysts must monitor vast territorial expanses across thousands of square kilometers to detect tactical changes (border infrastructure, surface clearances, track development, outpost expansions) across heterogeneous satellite sensors over time. Current workflows suffer from manual image comparison bottlenecks, high false alarm rates from seasonal/lighting variations, and network vulnerabilities.

**SentinelEye Solution**: SentinelEye is a **sovereign, air-gapped satellite intelligence platform** designed for defence analysts. It couples cross-modal semantic retrieval (`RemoteCLIP` + `FAISS`) with multi-temporal change detection (`BIT` with `CVA` fallback) and an offline, hallucination-constrained language model (`Qwen-2.5-7B` / `Gemma-2-9B` via GBNF grammar) that generates verifiable intelligence briefings strictly anchored to a structured **Facts Dictionary**. All analyst validation decisions are permanently anchored into a tamper-evident `BLAKE3` hash chain signed with `Ed25519`.

### Core Engineering Principles
- **Precision Over Recall**: Minimizing false alarms from seasonal vegetation, snow cover, and illumination angle deltas to avoid operational fatigue.
- **Sovereign Air-Gapped Operation**: 100% offline execution; zero external network or cloud API calls at runtime.
- **Tamper-Evident Audit Trails**: Cryptographic proof of who confirmed, rejected, or re-classified every intelligence event.
- **Multi-Sensor Harmonization**: Optical (`Sentinel-2`, `Landsat`, `Bhuvan`) and SAR (`Sentinel-1`) cross-registration and feature alignment.

---

## 2. Team Ulysses (Module Ownership)

| Member | Focus Area | Core Modules / Models | Key Deliverables |
|---|---|---|---|
| **Gargi** | Semantic Retrieval & Change Detection | RemoteCLIP, FAISS, BIT, CVA, BAN, BFAST | Vector retrieval index, change masks, BIT-to-CVA fallback pipeline |
| **Anuj** | Data Sourcing & Preprocessing | Sentinel-1/2, Landsat, Bhuvan, Fmask, GDAL | Coregistered before/after pairs, metadata extraction, `docs/DATA.md` |
| **Priyanshu** | LLM Briefings & Security Audit | Qwen/Gemma, llama.cpp, GBNF, BLAKE3, Ed25519 | Constrained briefings, tamper-evident audit ledger, `docs/LLM_SCHEMA.md` |
| **Ram** | Frontend & Spatial UI | Streamlit / React Geospatial Dashboard | Search -> Results -> Swipe Slider -> Overlay -> Attribution -> Brief |
| **Sachin** | Defence Presentation & Strategy | Domain Strategy, Operational Pitch | Tactical pitch deck, evaluation rubrics, presentation flow |
| **Amritanshu** | Integration, Schemas & QA | Repo Architecture, Schemas, CI/QA | Shared schemas (`/schemas`), `INTEGRATION.md`, `DEMO_FALLBACK.md` |

---

## 3. Architecture & Data Flow

```
+----------------------------------------------------------------------------------------------------+
|                                    SENTINELEYE PIPELINE ARCHITECTURE                               |
+----------------------------------------------------------------------------------------------------+

 [ SATELLITE IMAGERY ]
  Sentinel-1/2, Landsat, Bhuvan
          |
          v
 [ 1. INGESTION & PREPROCESSING ]  (Anuj)
  - Radiometric Calibration & Atmospheric Correction (BOA)
  - Coregistration (<0.5 px RMSE) + Fmask Cloud Masking
  - Tile Metadata Generation (schemas/tile_metadata.json)
          |
          +------------------------------------------+
          |                                          |
          v                                          v
 [ 2. RETRIEVAL PIPELINE ] (Gargi)          [ 3. CHANGE DETECTION PIPELINE ] (Gargi)
  - RemoteCLIP Feature Extraction            - Primary: Bitemporal Image Transformer (BIT)
  - Offline FAISS Vector Index               - Fallback: Change Vector Analysis (CVA) + BFAST
  - Pre/Post Metadata Filters (AOI, Time)    - SAHI + YOLO for Small Object Detection
  - Ranked Candidates (retrieval_result.json) - Confidence & Multi-Model Scoring
          |                                          |
          +--------------------+---------------------+
                               |
                               v
               [ 4. FACTS DICTIONARY SYNTHESIS ]
                - Deduplicated Tactical Events
                - Gap-fill & Reconstructed Pixel Flagging
                - Output: schemas/change_record.json
                               |
                               v
               [ 5. CONSTRAINED LLM BRIEFING ] (Priyanshu)
                - Local Qwen-2.5 / Gemma via llama.cpp
                - GBNF Grammar (Logit Constraints to Prevent Hallucinations)
                - Output: Military Tactical Briefing
                               |
                               v
               [ 6. ANALYST REVIEW & AUDIT LOG ] (Priyanshu & Ram)
                - Interactive Geospatial Dashboard (Ram)
                - Analyst Decision: Confirm / Reject / Reclassify
                - BLAKE3 Cryptographic Hash Chain
                - Ed25519 Asymmetric Digital Signature
                - Output: schemas/analyst_decision.json
```

---

## 4. Repository Structure

```
SentinelEye/
├── .env.example              # Template environment variables (air-gap, paths, keys)
├── .gitignore                 # Strict rules excluding large rasters, weights, and keys
├── requirements.txt           # Pinned production dependencies
├── INTEGRATION.md             # Integration checklist, contracts, and risk registry
├── DEMO_FALLBACK.md           # Stage presentation backup and replay mode plan
├── README.md                  # This file
│
├── ingestion/                 # Satellite imagery preprocessing (Anuj)
│   ├── coregistration.py
│   ├── fmask_filter.py
│   └── tiler.py
│
├── retrieval/                 # Semantic retrieval and vector search (Gargi)
│   ├── embedder.py            # RemoteCLIP offline wrapper
│   ├── indexer.py             # FAISS / SQLite index management
│   └── indexes/               # Local vector index files (gitignored)
│
├── change_detection/          # Multi-temporal change models (Gargi)
│   ├── bit_model.py           # BIT transformer inference
│   ├── cva_fallback.py        # Deterministic Change Vector Analysis fallback
│   ├── fusion.py              # Confidence scoring and candidate synthesis
│   └── sahi_yolo.py           # Fine-grained asset detection
│
├── llm_briefing/              # Hallucination-proof LLM briefings (Priyanshu)
│   ├── grammar/               # GBNF grammars for strict structured output
│   ├── facts_parser.py        # Facts dictionary ingest & validator
│   └── generator.py           # Local llama.cpp / Ollama inference client
│
├── audit/                     # Cryptographic audit ledger (Priyanshu)
│   ├── hash_chain.py          # BLAKE3 chaining logic
│   ├── signer.py              # Ed25519 key management and signature validation
│   └── logs/                  # Audit ledger logs (gitignored)
│
├── frontend/                  # Tactical analyst dashboard (Ram)
│   ├── app.py                 # Streamlit / Web UI main entrypoint
│   └── components/            # Sliders, overlays, maps, briefing viewers
│
├── schemas/                   # Shared Pydantic models & JSON Schemas (Amritanshu)
│   ├── tile_metadata.json     # Satellite tile metadata schema
│   ├── change_record.json     # Facts dictionary change record schema
│   ├── analyst_decision.json  # Tamper-evident analyst decision schema
│   └── retrieval_result.json  # Semantic retrieval response schema
│
├── docs/                      # Technical specifications & team documentation
│   ├── DATA.md                # Satellite data specifications (Anuj)
│   ├── LLM_SCHEMA.md          # LLM grammar & facts specification (Priyanshu)
│   ├── INTEGRATION.md          # Integration checklist & contracts
│   └── DEMO_FALLBACK.md       # Contingency & replay procedures
│
├── scripts/                   # Operational and verification utilities
│   ├── verify_offline_env.py  # Air-gap and model presence validator
│   ├── generate_synthetic_test_data.py # Mock test data generator
│   └── toggle_replay_mode.sh  # Instant demo replay mode toggle
│
├── tests/                     # Unit and integration test suite
│   ├── test_schemas.py        # Schema validation test cases
│   └── test_audit_chain.py    # BLAKE3 & Ed25519 hash chain tests
│
├── data/                      # Local raster tiles & demo pairs (gitignored)
│   └── precomputed/           # Cached demo scenarios for zero-latency fallback
│
└── models/                    # Pretrained model weights (gitignored)
    └── MODEL_CATALOG.md       # Upstream licenses, paths, and checksums
```

---

## 5. Offline & Air-Gapped Operation

> [!IMPORTANT]
> **Strict Air-Gap Compliance**: SentinelEye is engineered to run in environments completely severed from the public internet. At demo time, all network interfaces can be disabled.

- **Zero Cloud Runtime Calls**: No calls to external embedding APIs, LLM endpoints, or cloud tile servers.
- **Local Model Weights**: All neural network checkpoints live in `./models` with their licenses explicitly declared in [MODEL_CATALOG.md](file:///home/amritm/Projects/open-source/SentinelEye/models/MODEL_CATALOG.md).
- **Offline Framework Flags**: The environment enforces `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` to prevent any implicit connection attempts.
- **Embedded Storage**: Vector searches use local `faiss-cpu` with an embedded SQLite database for spatial/temporal metadata filtering.
- **Local LLM Execution**: Briefings run locally via quantized GGUF weights on `llama.cpp`.

---

## 6. Setup & Installation

### Step 1: Clone and Create Virtual Environment
```bash
git clone https://github.com/Amrit-mishra07/SentinelEye.git
cd SentinelEye

# Recommended: Python 3.10 or 3.11
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install System Dependencies (Ubuntu / Debian)
For GDAL and OpenCV support:
```bash
sudo apt-get update && sudo apt-get install -y \
    libgdal-dev \
    gdal-bin \
    libgl1-mesa-glx \
    libglib2.0-0
```

### Step 3: Install Python Packages
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
# Edit .env if custom model paths or data directories are used
```

### Step 5: Verify Model Weights Placement
Place pretrained model checkpoints in the `models/` directory:
- `models/remoteclip/remoteclip_vit_b32.pt`
- `models/bit/bit_base_bitemporal.pth`
- `models/llm/qwen2.5-7b-instruct-q4_k_m.gguf`

Verify readiness using the offline validator:
```bash
python scripts/verify_offline_env.py
```

---

## 7. Running the Demo End-to-End

### Mode A: Live Pipeline (Normal Mode)
Launch the interactive defence dashboard:
```bash
streamlit run frontend/app.py
```
1. **Search**: Enter query `"military outpost expansion with surface clearance"` or upload a visual crop.
2. **Select Pair**: Choose the retrieved bitemporal satellite pair.
3. **Change Detection**: Trigger BIT model with automatic CVA fallback.
4. **Inspect Attribution**: Review Fmask cloud/gap warnings and confidence scores.
5. **Briefing**: Read the hallucination-proof military intelligence summary.
6. **Sign-Off**: Confirm or reject findings to record a signed entry in the BLAKE3 audit chain.

### Mode B: Zero-Latency Demo Replay (Fallback Mode)
If GPU resources are constrained or stage time is limited:
```bash
# In .env set REPLAY_MODE=true or run:
export REPLAY_MODE=true
streamlit run frontend/app.py
```
This loads precomputed and verified scenarios instantly from `data/precomputed/` with identical dashboard UI behavior. See [DEMO_FALLBACK.md](file:///home/amritm/Projects/open-source/SentinelEye/DEMO_FALLBACK.md) for full contingency steps.
