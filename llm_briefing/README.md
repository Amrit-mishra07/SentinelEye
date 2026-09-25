# LLM Intelligence Briefing Module

**Module Owner**: Priyanshu (LLM & Security)  
**Problem Statement**: PS26227 — Intelligence Briefing & Hallucination-Proof Reporting

## Scope & Responsibilities
- Offline LLM inference using local quantized models (`Qwen-2.5-7B-Instruct` or `Gemma-2-9B` via `llama.cpp` / `llama-cpp-python` / `Ollama`).
- Input ingestion: Consumes the structured **Facts Dictionary** (`schemas/change_record.json`), which contains verified, high-precision detected changes.
- Constrained generation / GBNF Grammars: Strict grammar enforcement ensuring the LLM cannot hallucinate coordinates, dates, or change types that do not exist in the facts dictionary.
- Output generation: Produces military-standard formatted tactical intelligence summaries (Situation, Changes Observed, Timeline, Confidence & Verification Status, Analyst Recommendations).
- Pixel Provenance awareness: Highlights when any observation relied on gap-filled or reconstructed pixels (`is_reconstructed_or_gap_filled == True`).

## Key Interfaces
- `load_local_llm(model_path: str, n_ctx: int = 4096) -> Llama`
- `generate_intelligence_brief(facts: List[ChangeRecord], context_notes: str = "") -> BriefingOutput`
- `validate_against_facts(briefing_text: str, facts: List[ChangeRecord]) -> ValidationReport`

## Grammar & Constraints
Refer to `docs/LLM_SCHEMA.md` for the formal GBNF grammar definition and fact dictionary constraints.
