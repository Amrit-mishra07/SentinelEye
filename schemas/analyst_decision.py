"""
SentinelEye - Analyst Decision & Tamper-Evident Audit Record Schema
Defines human verification decisions chained cryptographically with BLAKE3 and signed via Ed25519.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    FLAGGED_FOR_REVISIT = "FLAGGED_FOR_REVISIT"
    DOWNGRADED = "DOWNGRADED"


class TacticalPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    ROUTINE = "ROUTINE"


class AuditCryptoBlock(BaseModel):
    block_index: int = Field(..., ge=0, description="Sequential index of the record in the chain (0 = genesis)")
    previous_block_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="BLAKE3 256-bit hash of the previous record in the chain (64 hex characters)",
    )
    payload_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="BLAKE3 256-bit hash of the current entry canonical payload (excluding audit_crypto block)",
    )
    chain_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="BLAKE3 hash of (previous_block_hash + payload_hash) linking the chain",
    )
    analyst_public_key: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="Ed25519 public key of the signing analyst (hex encoded)",
    )
    signature: str = Field(
        ...,
        min_length=128,
        max_length=128,
        description="Ed25519 digital signature over the chain_hash (hex encoded)",
    )


class AnalystDecision(BaseModel):
    schema_version: str = Field(default="1.0.0", description="Schema specification version")
    decision_id: str = Field(
        ...,
        description="Unique identifier for the review action (e.g., DEC-2026-0105)",
    )
    change_record_id: str = Field(
        ...,
        description="Foreign reference to the change_id evaluated in the Facts Dictionary",
    )
    analyst_id: str = Field(
        ...,
        description="Identifier of the duty analyst (e.g., ANALYST-DEF-712)",
    )
    analyst_station_id: str = Field(
        default="STATION-ALPHA-AIRGAP",
        description="Identifier of the offline terminal or workstation",
    )
    decision: DecisionType = Field(
        ...,
        description="Formal validation outcome (CONFIRMED, REJECTED, FLAGGED_FOR_REVISIT, DOWNGRADED)",
    )
    tactical_priority: TacticalPriority = Field(
        default=TacticalPriority.MEDIUM,
        description="Assigned tactical threat or surveillance priority",
    )
    notes: Optional[str] = Field(
        default="",
        description="Analyst reasoning, collateral intelligence context, or rejection justification",
    )
    timestamp: str = Field(
        ...,
        description="UTC ISO 8601 timestamp at which decision was finalized",
    )
    audit_crypto: AuditCryptoBlock = Field(
        ...,
        description="Cryptographic proof block securing chain integrity and non-repudiation",
    )
