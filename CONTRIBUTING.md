# Contributing to SentinelEye 🛰️

Welcome to **SentinelEye**! We are thrilled that you are interested in contributing to this open-source sovereign satellite intelligence platform. 

SentinelEye was created by **Team Ulysses** for the **Smart India Hackathon (SIH) 2026** under **Problem Statement PS26227** (DGIS / Indian Army, Space Technology theme): *"Semantic Retrieval and Multi-Temporal Change Analysis of Satellite Imagery"*.

Whether you are a beginner taking your first steps in open source, a student passionate about geospatial data or remote sensing, or an experienced developer skilled in PyTorch, vector search, or local LLMs—**you are warmly welcome here!**

This guide provides a comprehensive, step-by-step walkthrough to get you from zero to your first merged Pull Request.

---

## Table of Contents
1. [Core Principles & Air-Gap Rules](#1-core-principles--air-gap-rules)
2. [Code of Conduct](#2-code-of-conduct)
3. [Architecture Overview & Module Map](#3-architecture-overview--module-map)
4. [Step-by-Step Setup Guide for Beginners](#4-step-by-step-setup-guide-for-beginners)
   - [Prerequisites & System Libraries](#prerequisites--system-libraries)
   - [Forking and Cloning](#forking-and-cloning)
   - [Python Virtual Environment](#python-virtual-environment)
   - [Installing Dependencies](#installing-dependencies)
   - [Configuring Environment Variables](#configuring-environment-variables)
   - [Generating Synthetic Test Data](#generating-synthetic-test-data)
   - [Verifying Offline Readiness](#verifying-offline-readiness)
   - [Running the Test Suite](#running-the-test-suite)
5. [Finding Something to Work On](#5-finding-something-to-work-on)
   - [Good First Issues for Beginners](#good-first-issues-for-beginners)
   - [Module-by-Module Ideas](#module-by-module-ideas)
6. [Development Workflow & Git Guidelines](#6-development-workflow--git-guidelines)
   - [Creating a Feature Branch](#creating-a-feature-branch)
   - [Conventional Commit Messages](#conventional-commit-messages)
   - [Keeping Your Fork Synced](#keeping-your-fork-synced)
7. [Coding Standards & Conventions](#7-coding-standards--conventions)
   - [Python Style & Typing](#python-style--typing)
   - [Shared Schemas Contract](#shared-schemas-contract)
8. [Testing & Quality Assurance](#8-testing--quality-assurance)
9. [Submitting Your Pull Request (PR)](#9-submitting-your-pull-request-pr)
10. [Troubleshooting & FAQ](#10-troubleshooting--faq)

---

## 1. Core Principles & Air-Gap Rules

Before writing any code, it is critical to understand the engineering constraints that define SentinelEye:

> [!IMPORTANT]
> **Strict Sovereign Air-Gap Constraint**
> SentinelEye is designed for defence analysts in secure, air-gapped operations. The entire platform must operate with **zero network connectivity at runtime**.
> 
> 1. **No External Network Calls**: Never introduce runtime calls to external cloud APIs, external CDNs, Hugging Face Hub downloads, or remote telemetry.
> 2. **Local Models Only**: All pretrained models (RemoteCLIP, BIT, Qwen/Gemma GGUF, YOLO) must be loaded from local paths in `models/` with licenses documented in `models/MODEL_CATALOG.md`.
> 3. **Precision Over Recall**: False alarms in defence intelligence create critical operational fatigue. Filter out natural/seasonal illumination and vegetation shifts.
> 4. **No Sensitive Data in Git**: Never commit `.tif`, `.tiff`, `.pth`, `.pt`, `.gguf`, `.key`, or `.env` files to git. Strictly respect `.gitignore`.

---

## 2. Code of Conduct

We are committed to providing a welcoming, inspiring, and harassment-free community for everyone.

### Our Standards
- **Be Respectful**: Treat all contributors, regardless of experience level, background, or identity, with respect and kindness.
- **Be Constructive**: Offer helpful, empathetic code review feedback. If you disagree with an architectural decision, explain the technical trade-offs objectively.
- **Ask Questions Cheerfully**: There are no "silly questions"—if something in the setup or documentation is unclear, that is a documentation bug we want to fix!

---

## 3. Architecture Overview & Module Map

SentinelEye is organized into decoupled modules with clear interfaces:

```
[ Ingestion (Anuj) ] ──> [ Retrieval Index (Gargi) ] ──> [ Change Detection (Gargi) ]
         │                                                            │
         ▼                                                            ▼
[ Tile Metadata ]                                            [ Change Records (Facts) ]
                                                                      │
                                                                      ▼
[ Cryptographic Audit (Priyanshu) ] <── [ Frontend (Ram) ] <── [ Constrained LLM Briefing ]
```

### Module Responsibilities:
- [`ingestion/`](ingestion/): Satellite scene radiometric calibration, orthorectification, coregistration, Fmask cloud screening, and standardized tiling.
- [`retrieval/`](retrieval/): Offline `RemoteCLIP` image/text embeddings, local `FAISS` vector index, and metadata filtering.
- [`change_detection/`](change_detection/): Bitemporal Image Transformer (`BIT`), Change Vector Analysis (`CVA`) fallback, confidence scoring, and candidate polygonization.
- [`llm_briefing/`](llm_briefing/): Offline quantized LLM inference (`Qwen-2.5-7B` / `Gemma-2-9B` via `llama.cpp`), GBNF grammar constraints ensuring zero hallucination.
- [`audit/`](audit/): Tamper-evident ledger using `BLAKE3` cryptographic hash chaining and `Ed25519` asymmetric digital signatures.
- [`frontend/`](frontend/): Streamlit geospatial dashboard: search bar, swipe slider, change heatmap overlay, attribution inspector, and intelligence report viewer.
- [`schemas/`](schemas/): Central Pydantic v2 and JSON Schema data contracts (`tile_metadata`, `change_record`, `analyst_decision`, `retrieval_result`).
- [`scripts/`](scripts/): Offline verification scripts, synthetic test data generators, and demo toggle utilities.
- [`tests/`](tests/): Automated pytest suite validating schemas, crypto logic, and pipeline steps.

---

## 4. Step-by-Step Setup Guide for Beginners

Follow these steps sequentially to set up your local development environment.

### Prerequisites & System Libraries

SentinelEye requires **Python 3.10 or 3.11** and system geospatial libraries (GDAL, GEOS, PROJ).

#### On Ubuntu / Debian / WSL2:
```bash
sudo apt-get update && sudo apt-get install -y \
    python3-dev \
    python3-venv \
    python3-pip \
    git \
    libgdal-dev \
    gdal-bin \
    libgl1-mesa-glx \
    libglib2.0-0
```

#### On macOS (Homebrew):
```bash
brew install gdal git
```

---

### Step 1: Forking and Cloning

1. Navigate to the SentinelEye GitHub repository: [https://github.com/Amrit-mishra07/SentinelEye](https://github.com/Amrit-mishra07/SentinelEye)
2. Click the **Fork** button (top right) to create your own copy under your GitHub account.
3. Open your terminal and clone your fork to your computer:
   ```bash
   git clone https://github.com/<YOUR-GITHUB-USERNAME>/SentinelEye.git
   cd SentinelEye
   ```
4. Set up the `upstream` remote to keep track of changes from the main repository:
   ```bash
   git remote add upstream https://github.com/Amrit-mishra07/SentinelEye.git
   git remote -v
   ```
   *(You should see `origin` pointing to your fork and `upstream` pointing to the main project).*

---

### Step 2: Python Virtual Environment

Always use an isolated virtual environment to avoid package version conflicts:

```bash
# Create virtual environment named 'venv'
python3 -m venv venv

# Activate it:
# On Linux / macOS / WSL:
source venv/bin/activate

# On Windows (cmd):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

*(Your terminal prompt should now be prefixed with `(venv)`).*

---

### Step 3: Installing Dependencies

Upgrade package managers and install the pinned dependencies:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

> [!TIP]
> If you are on an architecture without GPU (CUDA), `requirements.txt` installs CPU-compatible packages (`faiss-cpu`, standard torch). Everything in SentinelEye runs completely fine in CPU mode for development and testing!

---

### Step 4: Configuring Environment Variables

Create your local `.env` configuration file from the provided template:

```bash
cp .env.example .env
```

Open `.env` in your code editor. By default, it is configured for safe local testing:
- `DEVICE=cpu` (change to `cuda` if you have an NVIDIA GPU)
- `OFFLINE_MODE=true`
- `REPLAY_MODE=false`

---

### Step 5: Generating Synthetic Test Data

Because satellite rasters and model checkpoints are large (gigabytes), you do **not** need them to start developing! 

Run the synthetic data generator to create realistic, schema-valid mock pairs:

```bash
python scripts/generate_synthetic_test_data.py
```

This creates mock tiles, metadata, change records, and audit logs in `data/precomputed/demo_pair_01_pangong/`.

---

### Step 6: Verifying Offline Readiness

Run the automated offline air-gap and environment validator:

```bash
python scripts/verify_offline_env.py
```

You should see a clean green output indicating all 12 core directories and 8 schema contracts exist.

---

### Step 7: Running the Test Suite

Execute the test suite using `pytest`:

```bash
pytest
```

Expected output:
```text
============================= test session starts ==============================
rootdir: /path/to/SentinelEye
collected 6 items

tests/test_audit_chain.py .                                              [ 16%]
tests/test_schemas.py .....                                              [100%]

============================== 6 passed in 0.09s ===============================
```

🎉 **Congratulations! Your development environment is completely set up and ready!**

---

## 5. Finding Something to Work On

Not sure where to start? Here are great ways for beginners to jump in:

### Good First Issues for Beginners
1. **Add Unit Tests**: Write unit tests in `tests/test_schemas.py` for edge cases in schemas (e.g., negative resolutions, malformed bounding boxes, invalid MGRS grid coordinates).
2. **Improve Error Messages**: Add helpful exceptions and user-friendly error messages when files or model weights are missing.
3. **Enhance Documentation**: Fix typos, add docstrings (`Google` or `NumPy` style) to undocumented functions, or write tutorials in `docs/`.
4. **Synthetic Test Scenarios**: Extend `scripts/generate_synthetic_test_data.py` to generate Scenario 2 (Desert Outpost) and Scenario 3 (Eastern Mountain Valley).
5. **Streamlit UI Polish**: Add custom CSS or status badges in `frontend/` to display whether the app is currently in `LIVE INFERENCE` or `REPLAY (CACHED)` mode.

### Module-by-Module Ideas
| Module | Beginner-Friendly Opportunity | Relevant Files |
|---|---|---|
| **Schemas** | Add serialization helper methods (`to_geojson()`, `to_dict()`) | `schemas/*.py` |
| **Ingestion** | Add coordinate conversion utility between Lat/Lon and UTM/MGRS | `ingestion/` |
| **Retrieval** | Add helper function to compute cosine similarity without PyTorch | `retrieval/` |
| **Audit** | Add a command-line audit trail verifier script | `audit/`, `scripts/` |
| **Frontend** | Build a Folium side-by-side tile viewer component | `frontend/` |

---

## 6. Development Workflow & Git Guidelines

To keep the repository clean and maintainable, please follow these Git workflows.

### Step 1: Sync with Upstream
Before starting new work, always pull the latest changes from the main project:
```bash
git checkout main
git fetch upstream
git merge upstream/main
```

### Step 2: Create a Feature Branch
Never make changes directly on `main`. Create a descriptive feature branch:
```bash
# Pattern: <type>/<short-description>
git checkout -b feat/add-mgrs-coordinate-converter
# or
git checkout -b fix/tile-metadata-bbox-validation
# or
git checkout -b docs/clarify-gdal-installation
```

### Step 3: Make Your Changes & Commit
Follow the **Conventional Commits** specification:

| Prefix | Usage | Example |
|---|---|---|
| `feat:` | A new feature or capability | `feat(schemas): add coordinate conversion helper to GeoCoordinates` |
| `fix:` | A bug fix | `fix(audit): correct previous block hash verification edge case` |
| `docs:` | Documentation changes only | `docs: add troubleshooting steps for GDAL on Windows WSL2` |
| `test:` | Adding or updating tests | `test(schemas): add validation tests for invalid sensor enums` |
| `refactor:` | Code restructuring without feature or bug changes | `refactor(retrieval): separate sqlite queries into helper module` |
| `chore:` | Build tasks, package updates, formatting | `chore: update .gitignore to exclude mypy cache` |

Commit your changes:
```bash
git add schemas/tile_metadata.py tests/test_schemas.py
git commit -m "feat(schemas): add MGRS coordinate validator to GeoCoordinates"
```

### Step 4: Push to Your Fork
```bash
git push -u origin feat/add-mgrs-coordinate-converter
```

---

## 7. Coding Standards & Conventions

### Python Guidelines
- **Python Version**: Write code compatible with Python 3.10+.
- **Type Annotations**: Use Python type hints (`from typing import Optional, List, Dict, Tuple`).
- **Docstrings**: Provide clear docstrings explaining arguments, return types, and exceptions.
- **Imports Order**:
  1. Standard library imports (`os`, `sys`, `pathlib`, `json`)
  2. Third-party packages (`numpy`, `pydantic`, `torch`)
  3. Local module imports (`from schemas import TileMetadata`)

### Shared Schemas Rule
- Whenever creating or modifying inter-module data structures, **update both the Pydantic model (`.py`) and the JSON Schema (`.json`)** in `schemas/`.
- Run `pytest tests/test_schemas.py` to ensure existing contracts remain unviolated.

---

## 8. Testing & Quality Assurance

Every Pull Request must pass the automated test suite before it can be merged.

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_schemas.py

# Run offline readiness check
python scripts/verify_offline_env.py
```

If you add a new function or schema field, **always add corresponding unit tests** in `tests/`.

---

## 9. Submitting Your Pull Request (PR)

Once your code is pushed to your fork:

1. Go to the SentinelEye repository on GitHub: [https://github.com/Amrit-mishra07/SentinelEye](https://github.com/Amrit-mishra07/SentinelEye)
2. You will see a banner: *"feat/add-mgrs-coordinate-converter had recent pushes"*. Click **Compare & pull request**.
3. Fill out the PR title and description using this format:

```markdown
## Description
Brief summary of what this PR does and why it was needed.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Documentation update
- [ ] Test addition / improvement

## Testing
- [ ] Ran `pytest` locally and all tests passed.
- [ ] Ran `python scripts/verify_offline_env.py`.

## Air-Gap Compliance
- [ ] Confirmed zero external network calls added.
- [ ] Confirmed no large binary files (.tif, .pth, .gguf) committed.
```

4. Click **Create pull request**.
5. The maintainers will review your PR, suggest any refinements, and merge it!

---

## 10. Troubleshooting & FAQ

### Q: `ModuleNotFoundError: No module named 'gdal'` or `osgeo`
**Solution**: GDAL Python bindings must match your system GDAL installation.
```bash
# Check system gdal version:
gdal-config --version
# Output e.g.: 3.8.4

# Install matching python gdal:
pip install GDAL==$(gdal-config --version)
```

### Q: `torch.cuda.is_available()` returns `False`
**Solution**: This is normal if you do not have an NVIDIA GPU. The entire test suite and demo replay mode run seamlessly on CPU. In `.env`, ensure:
```ini
DEVICE=cpu
```

### Q: How do I test without downloading 5GB model weights?
**Solution**: Use **Replay Mode**! Run `python scripts/generate_synthetic_test_data.py` and set `REPLAY_MODE=true` in your `.env`. The frontend and pipeline will run instantly on mock data without needing neural network checkpoints.

### Q: Git says `Your branch is behind 'upstream/main'`
**Solution**: Update your branch from upstream:
```bash
git fetch upstream
git rebase upstream/main
git push -f origin <your-branch-name>
```

---

## Need Help?
- Open an [Issue on GitHub](https://github.com/Amrit-mishra07/SentinelEye/issues) labeled `question`.
- Tag **Amritanshu** or any member of **Team Ulysses** in your PR comments.

Thank you for helping us build sovereign, air-gapped satellite intelligence for India! 🇮🇳🛰️
