# SentinelEye Demo Contingency & Fallback Plan (DEMO_FALLBACK.md)

**Classification**: RESTRICTED / INTERNAL TEAM PLAYBOOK  
**Applicability**: Smart India Hackathon 2026 Stage Presentation & Jury Evaluation  
**Integration Lead**: Amritanshu

---

## 1. Contingency Philosophy: The 3-Tier Defense

Live machine learning presentations on edge laptops in air-gapped auditoriums carry known risks: GPU thermal throttling, CUDA driver faults, out-of-memory errors, or OS lockups. 

SentinelEye incorporates a **zero-delay, 3-tier fallback architecture** to ensure the presentation succeeds under any failure condition without the jury noticing an interruption.

```
       [ JURY EVALUATION COMMENCES ]
                    │
                    ▼
     ┌─────────────────────────────┐
     │   TIER 1: LIVE INFERENCE    │ ── (Failure / High Latency) ──┐
     │   Full neural pipeline      │                               │
     └─────────────────────────────┘                               ▼
                                                    ┌─────────────────────────────┐
                                                    │    TIER 2: REPLAY MODE      │
                                                    │   Hot switch: zero compute  │
                                                    │   Precomputed JSONs & tiles │
                                                    └─────────────────────────────┘
                                                                   │
                                                                   │ ── (Total OS / UI Crash) ──┐
                                                                   ▼                            ▼
                                                    ┌─────────────────────────────┐
                                                    │  TIER 3: BACKUP VIDEO & MP4 │
                                                    │  4K high-res recorded run   │
                                                    └─────────────────────────────┘
```

---

## 2. Tier 2: Hot Replay Mode Specification

### What is Replay Mode?
Replay Mode freezes all heavy model calls (`RemoteCLIP`, `BIT`, `llama.cpp`) and redirects the backend to serve pre-calculated, verified JSON files and pre-rendered mask PNGs stored under `data/precomputed/`. The frontend UI (Streamlit / React) operates **identically**—the user can click buttons, move the swipe slider, inspect the change attribution, read the intelligence briefing, and commit to the audit log. Latency drops from ~8 seconds to <50 milliseconds.

### Activating Replay Mode
There are three simple ways to activate Replay Mode:

#### Option A: Dashboard UI Toggle (Fastest on stage)
In the top right corner of the dashboard, flip the toggle:
`Mode: [ Live Inference ] ────> [ Replay (Cached) ]`

#### Option B: Environment Variable (Before starting app)
```bash
export REPLAY_MODE=true
streamlit run frontend/app.py
```

#### Option C: Instant Terminal Switch Script
```bash
./scripts/toggle_replay_mode.sh on
```

---

## 3. Precomputed Demonstration Scenarios (Prepared by Anuj)

Three high-priority border and tactical scenarios are stored permanently in `data/precomputed/`:

### Scenario 1: Northern Border - Pangong Lake Sector
- **Location**: Pangong Tso North Ridge (33.7291° N, 78.6812° E) | MGRS: `43RER12345678`
- **Sensors**: Sentinel-2 (Bitemporal Optical: Nov 2025 vs Feb 2026)
- **Detected Event**: Rapid road widening (1,420m length) and heavy machinery staging area.
- **Precomputed Artifacts**:
  - `data/precomputed/demo_pair_01_pangong/tile_before.tif` & `thumbnail_before.png`
  - `data/precomputed/demo_pair_01_pangong/tile_after.tif` & `thumbnail_after.png`
  - `data/precomputed/demo_pair_01_pangong/change_mask.png`
  - `data/precomputed/demo_pair_01_pangong/facts_record.json`
  - `data/precomputed/demo_pair_01_pangong/briefing.txt`

### Scenario 2: Western Sector - Desert Forward Outpost
- **Location**: Thar Sector Border Post (27.1845° N, 70.8921° E)
- **Sensors**: Sentinel-1 SAR (IW VV/VH Coherence Difference)
- **Detected Event**: New vehicle revetments and defensive trenching detected under darkness/dust.
- **Precomputed Artifacts**:
  - `data/precomputed/demo_pair_02_desert_outpost/facts_record.json`
  - `data/precomputed/demo_pair_02_desert_outpost/briefing.txt`

### Scenario 3: Eastern Sector - Cloud-Covered Mountain Ridge
- **Location**: Arunachal Mountain Valley (27.5810° N, 92.1245° E)
- **Sensors**: Multi-Sensor Cross-Modal (Landsat-8 + Sentinel-2 with Fmask gap-fill)
- **Key Feature**: Demonstrates sovereign data integrity warning (`is_reconstructed_or_gap_filled = True`).
- **Precomputed Artifacts**:
  - `data/precomputed/demo_pair_03_cloud_gap_fill/facts_record.json`
  - `data/precomputed/demo_pair_03_cloud_gap_fill/briefing.txt`

---

## 4. Tier 3: Emergency Backup Video Playbook

If the laptop encounters complete hardware or operating system failure:
- **Location of Video**: Stored locally on Desktop AND on two independent FAT32 USB drives in Sachin and Amritanshu's badges.
- **File Name**: `SentinelEye_Demo_Walkthrough_1080p.mp4`
- **Duration**: Exactly 3 minutes 45 seconds (aligned with Sachin's presentation timing).

### Video Chapter Cue Points
| Timestamp | Presentation Topic | Visual Shown on Screen |
|---|---|---|
| `00:00 - 00:45` | Problem & Air-Gapped Search | Query input -> RemoteCLIP sub-second retrieval across 10,000 km² |
| `00:45 - 01:45` | Change Detection & Slider | Bitemporal swipe -> BIT change detection heatmap -> CVA fallback comparison |
| `01:45 - 02:30` | Facts Dictionary & Gap-fill | Attribution tooltip highlighting valid vs gap-filled pixels (`Fmask`) |
| `02:30 - 03:15` | Zero-Hallucination Brief | GBNF constrained LLM generating tactical report from structured facts |
| `03:15 - 03:45` | Audit Log & Non-Repudiation | Analyst confirms decision -> BLAKE3 hash chain update -> Ed25519 signature |

---

## 5. Rapid 20-Second Automated Stage Recovery

If the dashboard freezes while waiting for jury, run the automated emergency recovery script:

```bash
./scripts/emergency_restart.sh
```
This automatically:
1. Terminates hanging Streamlit and Python backend processes.
2. Purges GPU CUDA memory handles (`torch.cuda.empty_cache()`).
3. Enforces `REPLAY_MODE=true` in `.env`.
4. Relaunches the dashboard with precomputed scenarios in **under 20 seconds**.

---

## 6. Pre-Stage Readiness Verification (T-Minus 15 Minutes)

Run the automated pre-stage validator before stepping on the presentation dais:

```bash
./scripts/pre_stage_check.sh
```
This automatically validates:
- [x] **Air-Gap Check**: Verifies zero internet socket connection (flags if Wi-Fi is on).
- [x] **Scenario Presence**: Validates all 3 precomputed demonstration scenarios in `data/precomputed/`.
- [x] **Schema Integrity**: Validates all 4 Pydantic v2 data contracts.
- [x] **Test Suite**: Confirms 100% green test status (`pytest`).
- [x] **Replay Switch**: Confirms `scripts/toggle_replay_mode.sh` is executable.
- [x] **AC Power**: Checks wall power status to ensure GPU is unthrottled.

---

## 7. Air-Gapped Docker Severance Demonstration

To prove sovereign offline isolation to the military jury beyond any technical doubt:

```bash
# 1. Build self-contained demo image
docker build -t sentineleye:demo .

# 2. Run with Docker networking completely disabled (--net none)
docker run --rm --net none -p 8501:8501 sentineleye:demo
```
Access the dashboard at `http://localhost:8501` with zero network interfaces attached to the container.

