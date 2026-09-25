#!/usr/bin/env bash
# ==============================================================================
# SentinelEye - Replay Mode Fast Toggle Utility
# Quickly switches between Live Neural Inference and Cached Replay Demo Mode.
# ==============================================================================

set -euo pipefail

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
    else
        echo "Error: Neither .env nor .env.example found."
        exit 1
    fi
fi

TARGET_MODE="${1:-toggle}"

CURRENT_MODE=$(grep -E "^REPLAY_MODE=" "$ENV_FILE" | cut -d '=' -f2 | tr '[:upper:]' '[:lower:]' || echo "false")

if [ "$TARGET_MODE" = "on" ] || [ "$TARGET_MODE" = "true" ]; then
    NEW_MODE="true"
elif [ "$TARGET_MODE" = "off" ] || [ "$TARGET_MODE" = "false" ]; then
    NEW_MODE="false"
else
    # Toggle
    if [ "$CURRENT_MODE" = "true" ]; then
        NEW_MODE="false"
    else
        NEW_MODE="true"
    fi
fi

# Replace in .env
if grep -q "^REPLAY_MODE=" "$ENV_FILE"; then
    sed -i "s/^REPLAY_MODE=.*/REPLAY_MODE=${NEW_MODE}/" "$ENV_FILE"
else
    echo "REPLAY_MODE=${NEW_MODE}" >> "$ENV_FILE"
fi

echo "======================================================="
if [ "$NEW_MODE" = "true" ]; then
    echo " [REPLAY MODE ACTIVATED] "
    echo " Fast stage demo enabled: using cached precomputed outputs."
    echo " Zero heavy GPU/model compute required."
else
    echo " [LIVE INFERENCE MODE ACTIVATED] "
    echo " Pipeline will execute full neural inference (RemoteCLIP, BIT, LLM)."
fi
echo "======================================================="
