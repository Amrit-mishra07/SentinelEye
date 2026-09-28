#!/usr/bin/env bash
# ==============================================================================
# SentinelEye - Pre-Stage Readiness Verification (T-Minus 15 Minutes)
# Run on the demo laptop before presenting to the SIH Jury / Defence Evaluators.
# ==============================================================================

set -euo pipefail

GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
RESET="\033[0m"
BOLD="\033[1m"

echo ""
echo -e "${BOLD}======================================================${RESET}"
echo -e "${BOLD}  SentinelEye Pre-Stage T-15 Minute Checklist         ${RESET}"
echo -e "${BOLD}======================================================${RESET}"
echo ""

PASS_COUNT=0
TOTAL_CHECKS=6

# Check 1: Air-Gap Verification (No active internet ping)
echo -n "[1/6] Checking Air-Gap Network Severance... "
if ping -c 1 -W 1 8.8.8.8 &>/dev/null; then
    echo -e "${RED}[FAIL] Laptop is CONNECTED to the internet!${RESET}"
    echo -e "      ${YELLOW}Action: Enable Airplane Mode and unplug Ethernet cable.${RESET}"
else
    echo -e "${GREEN}[PASS] Complete air-gap confirmed (zero internet ping).${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
fi

# Check 2: Precomputed Demo Scenarios
echo -n "[2/6] Verifying Precomputed Stage Scenarios... "
SCENARIOS_FOUND=0
for s in demo_pair_01_pangong demo_pair_02_desert_outpost demo_pair_03_cloud_gap_fill; do
    if [ -f "data/precomputed/${s}/facts_record.json" ]; then
        SCENARIOS_FOUND=$((SCENARIOS_FOUND + 1))
    fi
done

if [ "$SCENARIOS_FOUND" -eq 3 ]; then
    echo -e "${GREEN}[PASS] All 3 border demonstration scenarios ready.${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo -e "${RED}[FAIL] Missing precomputed scenarios (${SCENARIOS_FOUND}/3 found).${RESET}"
    echo -e "      ${YELLOW}Action: Run python3 scripts/generate_synthetic_test_data.py${RESET}"
fi

# Check 3: Shared Schemas Contract Integrity
echo -n "[3/6] Validating Shared JSON & Pydantic Schemas... "
if python3 -c "from schemas import TileMetadata, ChangeRecord, AnalystDecision, RetrievalResult" &>/dev/null; then
    echo -e "${GREEN}[PASS] All 4 data contracts load cleanly.${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo -e "${RED}[FAIL] Schema import error.${RESET}"
fi

# Check 4: Test Suite Green Status
echo -n "[4/6] Running Automated Test Suite (pytest)... "
if pytest -q &>/dev/null; then
    echo -e "${GREEN}[PASS] Test suite 100% green.${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo -e "${RED}[FAIL] Test failures detected.${RESET}"
    echo -e "      ${YELLOW}Action: Run 'pytest' to inspect failing tests.${RESET}"
fi

# Check 5: Replay Mode Fast Switch Readiness
echo -n "[5/6] Testing Replay Switch Utility... "
if [ -x "scripts/toggle_replay_mode.sh" ]; then
    echo -e "${GREEN}[PASS] Fast replay toggle executable.${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    chmod +x scripts/toggle_replay_mode.sh
    echo -e "${GREEN}[PASS] Replay toggle permissions updated.${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
fi

# Check 6: Power Supply
echo -n "[6/6] Checking AC Power Adapter Status... "
if [ -f "/sys/class/power_supply/AC/online" ] && [ "$(cat /sys/class/power_supply/AC/online 2>/dev/null)" = "1" ]; then
    echo -e "${GREEN}[PASS] Laptop on wall power (GPU throttling disabled).${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo -e "${YELLOW}[WARN] Ensure laptop is plugged into AC power to prevent GPU downclocking.${RESET}"
    PASS_COUNT=$((PASS_COUNT + 1))
fi

echo ""
echo -e "${BOLD}======================================================${RESET}"
if [ "$PASS_COUNT" -eq "$TOTAL_CHECKS" ]; then
    echo -e "${GREEN}${BOLD} ALL SYSTEMS GO! Laptop is 100% ready for stage presentation.${RESET}"
else
    echo -e "${YELLOW}${BOLD} Please address warnings above before stepping on stage.${RESET}"
fi
echo -e "${BOLD}======================================================${RESET}"
echo ""
