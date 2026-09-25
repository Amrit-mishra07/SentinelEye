"""
Unit tests for cryptographic audit hash chaining logic (BLAKE3 simulation & chain verification).
"""

import hashlib
import json


def compute_hash(data: str) -> str:
    """Uses SHA-256 for test environment fallback if blake3 package is not yet compiled."""
    try:
        import blake3
        return blake3.blake3(data.encode()).hexdigest()
    except ImportError:
        return hashlib.sha256(data.encode()).hexdigest()


def test_hash_chain_tamper_detection():
    # Genesis block
    genesis_prev = "0" * 64
    entry1_payload = json.dumps({"decision_id": "DEC-001", "decision": "CONFIRMED"}, sort_keys=True)
    entry1_payload_hash = compute_hash(entry1_payload)
    entry1_chain_hash = compute_hash(genesis_prev + entry1_payload_hash)

    # Second block linked to first
    entry2_payload = json.dumps({"decision_id": "DEC-002", "decision": "REJECTED"}, sort_keys=True)
    entry2_payload_hash = compute_hash(entry2_payload)
    entry2_chain_hash = compute_hash(entry1_chain_hash + entry2_payload_hash)

    # Verification passes
    assert entry2_chain_hash == compute_hash(entry1_chain_hash + entry2_payload_hash)

    # Tampering test: modify entry 1 payload retroactively
    tampered_entry1_payload = json.dumps({"decision_id": "DEC-001", "decision": "REJECTED"}, sort_keys=True)
    tampered_payload_hash = compute_hash(tampered_entry1_payload)
    tampered_chain_hash = compute_hash(genesis_prev + tampered_payload_hash)

    # Verification fails on subsequent block!
    recalculated_entry2_chain_hash = compute_hash(tampered_chain_hash + entry2_payload_hash)
    assert recalculated_entry2_chain_hash != entry2_chain_hash
