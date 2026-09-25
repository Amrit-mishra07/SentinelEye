# Utility & Verification Scripts

This directory houses operational and verification scripts for the SentinelEye platform:

- `verify_offline_env.py` — Air-gap compliance validator: tests network isolation, verifies model weights presence, validates offline index access.
- `generate_synthetic_test_data.py` — Creates mock/synthetic bitemporal test pairs and schema-compliant JSONs for end-to-end testing before real imagery arrives.
- `toggle_replay_mode.sh` — Instantly toggles the system between live neural inference and cached replay demo mode.
- `verify_audit_chain.py` — Standalone cryptographic verifier for the BLAKE3 + Ed25519 audit log.
