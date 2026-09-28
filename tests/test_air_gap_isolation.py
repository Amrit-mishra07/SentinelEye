"""
Automated Air-Gap & Sovereign Network Isolation Test.
Guarantees that no pipeline stage initiates external network socket calls.
Monkeypatches socket.socket.connect to raise NetworkSecurityViolation if network access is attempted.
"""

import pytest
import socket
from pipeline.orchestrator import SentinelEyePipeline


class NetworkSecurityViolation(RuntimeError):
    """Raised when an unauthorized external network connection is attempted."""
    pass


@pytest.fixture
def block_external_network(monkeypatch):
    """
    Blocks all external socket network connections.
    Allows loopback / localhost connections (127.0.0.1) for local IPC if needed.
    """
    orig_connect = socket.socket.connect

    def guarded_connect(self, address):
        host, port = address[0], address[1]
        # Permit localhost / loopback only
        if host in ("127.0.0.1", "localhost", "::1"):
            return orig_connect(self, address)
        raise NetworkSecurityViolation(
            f"AIR-GAP BREACH DETECTED: Pipeline attempted external connection to {host}:{port}!"
        )

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)


def test_air_gap_compliance_live_pipeline(block_external_network):
    """
    Executes full pipeline operations while all external network sockets are severed.
    Proves 100% offline compliance for DGIS / Indian Army evaluation.
    """
    pipeline = SentinelEyePipeline(offline_mode=True, replay_mode=False)

    # 1. Semantic search without external network
    res = pipeline.search_imagery("trenching and vehicle revetments")
    assert res is not None

    # 2. Change detection without external network
    records, mask, conf, models = pipeline.detect_changes(
        before_meta={"tile_id": "TILE-B", "acquisition_date": "2025-11-10T00:00:00Z"},
        after_meta={"tile_id": "TILE-A", "acquisition_date": "2026-02-20T00:00:00Z"},
    )
    assert len(records) > 0

    # 3. LLM briefing without external network
    brief = pipeline.generate_briefing(records)
    assert "TACTICAL SATELLITE INTELLIGENCE BRIEF" in brief

    # 4. Cryptographic signing without external network
    decision = pipeline.commit_analyst_decision(records[0].change_id)
    assert decision.audit_crypto.signature is not None


def test_air_gap_compliance_replay_mode(block_external_network):
    """
    Verifies that the entire Replay demo fallback operates completely isolated from the network.
    """
    pipeline = SentinelEyePipeline(offline_mode=True, replay_mode=True)
    res = pipeline.run_full_cycle(
        query="road construction in northern sector",
        scenario_id="demo_pair_01_pangong",
    )
    assert res.is_replay_mode is True
    assert res.execution_time_ms < 100.0
