# Cryptographic Audit Log Module

**Module Owner**: Priyanshu (LLM & Security)  
**Problem Statement**: Sovereign Offline Operation & Tamper-Evident Accountability

## Scope & Responsibilities
- Tamper-evident ledger recording all human analyst decisions (confirmations, rejections, overrides, classification modifications).
- Cryptographic hash chaining using `BLAKE3` (high speed, 256-bit security, tree-hashing capable).
- Digital signature verification using `Ed25519` (fast asymmetric signing via `PyNaCl` or `cryptography`).
- Chain integrity verification: guarantees that no analyst record can be backdated, modified, or omitted without breaking the hash chain.
- Export and import conforming to `schemas/analyst_decision.json`.

## Key Interfaces
- `init_genesis_block(analyst_id: str) -> AnalystDecision`
- `record_decision(decision: AnalystDecisionInput, signing_key: SigningKey) -> AnalystDecision`
- `verify_chain_integrity(log_path: str) -> Tuple[bool, List[str]]`
- `export_audit_trail(start_time: str, end_time: str) -> List[AnalystDecision]`

## Key & Log Storage
- Keys live in `audit/keys/` (gitignored).
- Ledger logs live in `audit/logs/` (gitignored).
