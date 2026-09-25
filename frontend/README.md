# Frontend Analyst Dashboard

**Module Owner**: Ram (Frontend & UI)  
**Problem Statement**: PS26227 — Analyst Interaction & Visualization

## Scope & Responsibilities
- Interactive military geospatial dashboard for defence intelligence analysts.
- Workflow pipeline implementation:
  1. **Search**: Natural-language text prompt / visual crop input with spatial AOI bounding box & date range selector.
  2. **Results**: Ranked image tile retrieval gallery with similarity scores & sensor badges.
  3. **Before / After**: Side-by-side split screen and interactive swipe slider for temporal scene comparison.
  4. **Change Overlay**: Heatmap and vector polygon overlay of detected changes (BIT / CVA detections).
  5. **Attribution & Provenance**: Hover tooltips showing confidence score, sensor provenance, Fmask gap-fill warnings, and detection model breakdown.
  6. **Intelligence Brief**: Display hallucination-constrained military briefing generated from the Facts Dictionary.
  7. **Review & Sign-Off**: Analyst confirmation/rejection action bar triggering the BLAKE3/Ed25519 audit chain commit.
- Toggle between **Live Inference Mode** and **Replay / Demo Fallback Mode** (`REPLAY_MODE=true`).

## Technology Options
- Streamlit application (`frontend/app.py`) for rapid offline demo execution, or React/Next.js offline SPA consuming local FastAPI backend (`frontend/web`).
