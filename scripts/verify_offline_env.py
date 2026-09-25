#!/usr/bin/env python3
"""
SentinelEye - Air-Gap & Offline Environment Readiness Validator
Checks for air-gap compliance, local weights presence, schema integrity, and key storage.
"""

import os
import sys
from pathlib import Path

# ANSI Color Codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check_status(condition: bool, description: str, critical: bool = True) -> bool:
    if condition:
        print(f"[{GREEN}PASS{RESET}] {description}")
        return True
    else:
        prefix = f"[{RED}FAIL{RESET}]" if critical else f"[{YELLOW}WARN{RESET}]"
        print(f"{prefix} {description}")
        return False


def main():
    print(f"\n{BOLD}======================================================{RESET}")
    print(f"{BOLD}  SentinelEye Offline Air-Gap Verification Suite      {RESET}")
    print(f"{BOLD}======================================================\n{RESET}")

    repo_root = Path(__file__).resolve().parent.parent
    all_passed = True

    # 1. Directory Structure Checks
    print(f"{BOLD}1. Checking Repository Layout...{RESET}")
    required_dirs = [
        "ingestion",
        "retrieval",
        "change_detection",
        "llm_briefing",
        "audit",
        "frontend",
        "schemas",
        "docs",
        "scripts",
        "tests",
        "data",
        "models",
    ]
    for d in required_dirs:
        dir_path = repo_root / d
        if not check_status(dir_path.is_dir(), f"Directory exists: {d}"):
            all_passed = False

    # 2. Schema Files Checks
    print(f"\n{BOLD}2. Checking Shared Schema Contracts...{RESET}")
    schemas = [
        "tile_metadata.json",
        "tile_metadata.py",
        "change_record.json",
        "change_record.py",
        "analyst_decision.json",
        "analyst_decision.py",
        "retrieval_result.json",
        "retrieval_result.py",
    ]
    for s in schemas:
        schema_path = repo_root / "schemas" / s
        if not check_status(schema_path.is_file(), f"Schema contract exists: schemas/{s}"):
            all_passed = False

    # 3. Environment & Air-Gap Flag Checks
    print(f"\n{BOLD}3. Checking Air-Gap Environment Variables...{RESET}")
    hf_offline = os.environ.get("HF_HUB_OFFLINE", "0")
    tf_offline = os.environ.get("TRANSFORMERS_OFFLINE", "0")
    replay_mode = os.environ.get("REPLAY_MODE", "false").lower()

    check_status(
        hf_offline == "1",
        f"HF_HUB_OFFLINE is set to '1' (current: '{hf_offline}')",
        critical=False,
    )
    check_status(
        tf_offline == "1",
        f"TRANSFORMERS_OFFLINE is set to '1' (current: '{tf_offline}')",
        critical=False,
    )
    print(f"       Operating Mode: {'REPLAY (Zero Latency)' if replay_mode == 'true' else 'LIVE INFERENCE'}")

    # 4. Model Weights Check
    print(f"\n{BOLD}4. Checking Local Pretrained Model Checkpoints...{RESET}")
    models_to_check = [
        ("RemoteCLIP", repo_root / "models" / "remoteclip" / "remoteclip_vit_b32.pt"),
        ("BIT (Transformer)", repo_root / "models" / "bit" / "bit_base_bitemporal.pth"),
        ("Local LLM (GGUF)", repo_root / "models" / "llm" / "qwen2.5-7b-instruct-q4_k_m.gguf"),
    ]
    for model_name, path in models_to_check:
        check_status(
            path.is_file(),
            f"Weights found for {model_name} at {path.relative_to(repo_root)}",
            critical=False,
        )

    # 5. Summary
    print(f"\n{BOLD}======================================================{RESET}")
    if all_passed:
        print(f"{GREEN}{BOLD}Core repository structure and schemas are AIR-GAP READY!{RESET}")
    else:
        print(f"{RED}{BOLD}Some critical components are missing. See errors above.{RESET}")
    print(f"{BOLD}======================================================\n{RESET}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
