# SentinelEye Integration Checklist & Module Contracts (INTEGRATION.md)

**Integration Lead**: Amritanshu  
**Target Completion**: Smart India Hackathon 2026 Integration Day  
**Status**: Ready for Execution

---

## 1. End-to-End Pipeline Wiring Sequence

To prevent integration collisions, modules must be wired strictly in this sequential order:

```
[Step 1] Ingestion (Anuj)
   │  Output: schemas/tile_metadata.json + Preprocessed TIFs
   ▼
[Step 2] Feature Extraction & Indexing (Gargi)
   │  Input: Preprocessed TIFs
   │  Output: Local FAISS Index + SQLite Metadata Cache
   ▼
[Step 3] Semantic Retrieval (Gargi)
   │  Input: Text prompt / Visual crop
   │  Output: schemas/retrieval_result.json
   ▼
[Step 4] Change Detection & Fallback Pipeline (Gargi)
   │  Input: Before/After Tile Pair
   │  Output: Change Masks + Confidence Scores
   ▼
[Step 5] Facts Dictionary Synthesis (Amritanshu / Gargi)
   │  Input: Change Masks + Metadata + Provenance
   │  Output: schemas/change_record.json (The Facts Dictionary)
   ▼
[Step 6] Constrained LLM Briefing Engine (Priyanshu)
   │  Input: schemas/change_record.json
   │  Output: Structured Hallucination-Proof Briefing Text
   ▼
[Step 7] Frontend Dashboard Visualization (Ram)
   │  Input: All previous schemas
   │  Features: Search -> Results -> Swipe -> Heatmap -> Briefing
   ▼
[Step 8] Cryptographic Audit Ledger Commit (Priyanshu & Ram)
   │  Input: schemas/analyst_decision.json
   │  Output: Signed BLAKE3 + Ed25519 Audit Log Entry
```

---

## 2. Module Interface Contracts & Signatures

### Module 1: Ingestion & Preprocessing (Anuj)
- **Primary Function**: `ingest_and_tile_scene`
  ```python
  def ingest_and_tile_scene(
      scene_dir: str,
      sensor: str,
      tile_size: int = 512,
      output_dir: str = "data/preprocessed/tiles_512"
  ) -> List[TileMetadata]:
      """
      Ingests optical or SAR raw product, runs atmospheric correction,
      orthorectification, Fmask cloud screening, and writes 512x512 GeoTIFF tiles.
      Returns list of TileMetadata objects conforming to schemas/tile_metadata.json.
      """
  ```
- **Pair Preparation Function**: `prepare_coregistered_pair`
  ```python
  def prepare_coregistered_pair(
      before_tile_id: str,
      after_tile_id: str
  ) -> Tuple[np.ndarray, np.ndarray, TileMetadata, TileMetadata, np.ndarray]:
      """
      Loads two temporal tiles, coregisters them (<0.5 px RMSE),
      and computes combined valid pixel mask (1 = valid, 0 = cloud/gap).
      Returns (before_arr, after_arr, before_meta, after_meta, valid_mask).
      """
  ```
- **Reads**: Raw satellite scenes from `data/raw/{sensor}/`.
- **Writes**: Preprocessed tiles in `data/preprocessed/tiles_512/` and metadata in `data/preprocessed/tiles_512/metadata/`.

---

### Module 2: Semantic Retrieval & Indexing (Gargi)
- **Offline Embedder Function**: `extract_tile_embeddings`
  ```python
  def extract_tile_embeddings(
      tile_paths: List[str],
      weights_path: str = "models/remoteclip/remoteclip_vit_b32.pt",
      batch_size: int = 32
  ) -> np.ndarray:
      """
      Generates 512-dim L2-normalized float32 embeddings using offline RemoteCLIP.
      """
  ```
- **Search Query Endpoint / Function**: `semantic_search`
  ```python
  def semantic_search(
      query: str,
      query_type: QueryType = QueryType.TEXT,
      filters: Optional[RetrievalFilters] = None,
      top_k: int = 10
  ) -> RetrievalResult:
      """
      Executes hybrid spatial/temporal filter via SQLite metadata DB,
      performs FAISS inner-product similarity search on candidate IDs,
      and returns schema-compliant RetrievalResult.
      """
  ```
- **Reads**: Preprocessed tiles, local weights `models/remoteclip/`, `retrieval/indexes/`.
- **Writes**: `schemas/retrieval_result.json`.

---

### Module 3: Change Detection & Scoring Pipeline (Gargi)
- **Primary Inference Function**: `run_change_detection`
  ```python
  def run_change_detection(
      before_img: np.ndarray,
      after_img: np.ndarray,
      valid_mask: np.ndarray,
      use_cva_fallback: bool = False
  ) -> Tuple[np.ndarray, float, List[str]]:
      """
      Runs BIT model (or CVA fallback if specified or low confidence).
      Returns:
        - change_mask: uint8 binary mask (0 = no change, 1 = change)
        - model_confidence: float [0.0 - 1.0]
        - models_activated: e.g. ['BIT'] or ['CVA', 'BFAST']
      """
  ```
- **Candidate Polygonization & Attribution**: `synthesize_change_records`
  ```python
  def synthesize_change_records(
      change_mask: np.ndarray,
      before_meta: TileMetadata,
      after_meta: TileMetadata,
      valid_mask: np.ndarray,
      confidence: float,
      models_activated: List[str]
  ) -> List[ChangeRecord]:
      """
      Converts connected components to GeoJSON polygons, extracts area,
      checks if any footprint pixel overlaps with valid_mask == 0
      (setting is_reconstructed_or_gap_filled = True), and constructs ChangeRecord objects.
      """
  ```
- **Reads**: Coregistered image arrays, `TileMetadata`.
- **Writes**: List of `schemas/change_record.json` entries (Facts Dictionary).

---

### Module 4: Constrained LLM Briefing Engine (Priyanshu)
- **Briefing Generator Function**: `generate_briefing_from_facts`
  ```python
  def generate_briefing_from_facts(
      facts: List[ChangeRecord],
      model_path: str = "models/llm/qwen2.5-7b-instruct-q4_k_m.gguf",
      grammar_path: str = "llm_briefing/grammar/briefing.gbnf"
  ) -> str:
      """
      Feeds verified change records into local quantized LLM via llama.cpp.
      Applies GBNF grammar constraints so the model cannot invent coordinates,
      dates, or unauthorized change classifications.
      """
  ```
- **Fact Verifier / Anti-Hallucination Guardrail**: `verify_briefing_integrity`
  ```python
  def verify_briefing_integrity(
      briefing_text: str,
      facts: List[ChangeRecord]
  ) -> Tuple[bool, List[str]]:
      """
      Validates that every coordinate, date, and metric in the text
      corresponds strictly to an input ChangeRecord fact.
      """
  ```
- **Reads**: List of `ChangeRecord` objects.
- **Writes**: Structured text brief + validation report.

---

### Module 5: Cryptographic Audit Ledger (Priyanshu)
- **Hash Chaining & Signing Function**: `commit_analyst_decision`
  ```python
  def commit_analyst_decision(
      change_record_id: str,
      analyst_id: str,
      decision: DecisionType,
      notes: str,
      signing_key_path: str,
      audit_log_path: str = "audit/logs/analyst_audit_chain.log"
  ) -> AnalystDecision:
      """
      1. Reads last line of audit log to get previous_block_hash.
      2. Computes BLAKE3 hash of decision payload.
      3. Computes cumulative chain_hash = BLAKE3(previous_block_hash + payload_hash).
      4. Signs chain_hash using analyst's Ed25519 private key.
      5. Appends serialized AnalystDecision JSON to audit log.
      """
  ```
- **Ledger Verification Function**: `verify_audit_log`
  ```python
  def verify_audit_log(audit_log_path: str) -> Tuple[bool, int, str]:
      """
      Traverses the entire ledger from genesis to tail:
      validates all BLAKE3 hash links and verifies all Ed25519 public key signatures.
      """
  ```
- **Reads**: `schemas/change_record.json` ID, Analyst actions.
- **Writes**: `audit/logs/analyst_audit_chain.log`.

---

### Module 6: Frontend & Dashboard (Ram)
- **Streamlit App Entrypoint**: `frontend/app.py`
  - Loads configuration from `.env` (`REPLAY_MODE` toggle).
  - Component 1: Search bar (calls `semantic_search`).
  - Component 2: Retrieval gallery (renders `ScoredTileCandidate` items).
  - Component 3: Bitemporal swipe comparison map (using Folium / Leaflet).
  - Component 4: Change polygon overlay with provenance tooltip (`is_reconstructed_or_gap_filled` alert badge).
  - Component 5: Intelligence briefing viewer.
  - Component 6: Review & Sign-Off button panel (calls `commit_analyst_decision`).

---

## 3. Concrete Integration Checklist

### Stage A: Environment & Model Verification (09:00 - 10:30)
- [ ] Run `python scripts/verify_offline_env.py` to confirm all dependencies install without network.
- [ ] Verify all model checkpoints exist in `./models` with valid SHA256 checksums:
  - [ ] `models/remoteclip/remoteclip_vit_b32.pt`
  - [ ] `models/bit/bit_base_bitemporal.pth`
  - [ ] `models/llm/qwen2.5-7b-instruct-q4_k_m.gguf`
- [ ] Generate Ed25519 test keypair: `audit/keys/analyst_ed25519.key`.

### Stage B: Data Ingestion & Index Pipeline (10:30 - 12:30)
- [ ] Anuj places 3 verified before/after demonstration pairs into `data/precomputed/`.
- [ ] Run `ingest_and_tile_scene` to produce standardized 512x512 tiles.
- [ ] Gargi runs embedding generation with RemoteCLIP; writes FAISS index and SQLite metadata DB.
- [ ] Execute `tests/test_retrieval.py` to verify top-K recall on queries like "road construction".

### Stage C: Change Detection & Facts Dictionary (13:30 - 15:30)
- [ ] Gargi runs BIT model on demo pair #1; verifies change mask generation.
- [ ] Test BIT -> CVA fallback trigger by introducing noisy/low-confidence inputs.
- [ ] Verify `synthesize_change_records` populates `is_reconstructed_or_gap_filled` correctly when Fmask has masked pixels.
- [ ] Validate generated records against `schemas/change_record.json`.

### Stage D: Constrained LLM Briefing & Audit Log (15:30 - 17:30)
- [ ] Priyanshu loads Qwen-2.5 GGUF using `llama-cpp-python` with `n_gpu_layers=33` (or CPU mode if GPU full).
- [ ] Compile GBNF grammar and test constrained generation on sample `ChangeRecord`.
- [ ] Test anti-hallucination guardrail: intentionally alter a coordinate to ensure validator raises `SecurityException`.
- [ ] Priyanshu & Ram test decision sign-off; verify `AnalystDecision` appends to audit log and passes BLAKE3 verification.

### Stage E: Full System Dry Run & Stage Fallback Test (17:30 - 19:00)
- [ ] Execute complete end-to-end flow from UI: Search -> Detect -> Brief -> Sign.
- [ ] Test Replay Mode: toggle `REPLAY_MODE=true` in `.env`; ensure dashboard runs identically with zero GPU compute.
- [ ] Disable Wi-Fi / Ethernet adapter on demo laptop and verify zero network crashes.

---

## 4. Known Integration Risks & Mitigations

| # | Risk Description | Technical Impact | Mitigation Strategy |
|---|---|---|---|
| **R1** | **FAISS lacks native metadata filtering** | Cannot filter by AOI coordinates or date range directly inside vector search. | **Two-Tier Filter**: First query SQLite metadata table for matching tile IDs within the spatial/temporal window; retrieve candidates; if candidate count < 5,000, perform FAISS `search_by_id` or compute inner product directly. Alternatively, post-filter FAISS top-K results. |
| **R2** | **GPL-licensed component isolation** | BFAST or certain geospatial tools carry GPL/AGPL licenses, posing IP contamination risks. | **Process Boundary Isolation**: Any GPL component (such as BFAST or YOLO-SAHI) runs exclusively as an isolated command-line subprocess or containerized service communicating strictly via JSON over standard streams. |
| **R3** | **GPU VRAM exhaustion (OOM)** | Running RemoteCLIP (ViT-B), BIT transformer, and Qwen-2.5-7B simultaneously exceeds 8GB-12GB VRAM. | **Sequential Execution / Offloading**: Unload RemoteCLIP from CUDA (`torch.cuda.empty_cache()`) before running BIT. For the LLM, use 4-bit quantized GGUF (`Q4_K_M`) executed with llama.cpp hybrid CPU/GPU layers (`n_gpu_layers=20`). |
| **R4** | **Air-gapped framework connection attempts** | Hugging Face Transformers or PyTorch Hub trying to check online endpoints at startup causes hanging or crashes. | Enforce system environment variables `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and load weights strictly from explicit local file paths with no model name strings. |
| **R5** | **Cloud and shadow false alarms** | High false-positive rate in mountain/snow terrain (Ladakh / Pangong sectors) degrading analyst trust. | Integrate Fmask validity mask directly into the loss/scoring function. When pixel validity is ambiguous, set `is_reconstructed_or_gap_filled = True` and lower confidence score. |
| **R6** | **LLM latency on stage** | Local LLM text generation taking >25 seconds during a 5-minute pitch. | Pre-generate and cache the briefing text for the 3 demo pairs in `data/precomputed/`. Live demo streams tokens from local cache or pre-warmed llama.cpp context. |
