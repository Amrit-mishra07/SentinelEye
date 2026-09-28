#!/usr/bin/env bash
# ==============================================================================
# SentinelEye - Emergency Stage Recovery Script (20-Second SLA)
# Terminates hanging processes, flushes CUDA VRAM, and boots in Replay Mode.
# ==============================================================================

set -uo pipefail

echo "=========================================================="
echo " [EMERGENCY RECOVERY ACTIVATED] Commencing stage recovery..."
echo "=========================================================="

# 1. Kill any existing Streamlit or Python backend instances
echo "[1/4] Terminating existing dashboard and model processes..."
pkill -f "streamlit run" 2>/dev/null || true
pkill -f "uvicorn api.main:app" 2>/dev/null || true
sleep 1

# 2. Release VRAM / CUDA handles
echo "[2/4] Purging GPU memory and releasing CUDA device locks..."
python3 -c "
try:
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        print('      CUDA cache emptied successfully.')
except Exception:
    pass
" 2>/dev/null || true

# 3. Force Replay Mode in .env
echo "[3/4] Forcing REPLAY_MODE=true in .env..."
if [ -f ".env" ]; then
    sed -i 's/^REPLAY_MODE=.*/REPLAY_MODE=true/' .env || echo "REPLAY_MODE=true" >> .env
else
    echo "REPLAY_MODE=true" > .env
fi

# 4. Verify precomputed cache presence
if [ ! -d "data/precomputed/demo_pair_01_pangong" ]; then
    echo "      Generating missing precomputed cache..."
    python3 scripts/generate_synthetic_test_data.py
fi

# 5. Launch dashboard
echo "[4/4] Launching SentinelEye in Replay Mode..."
echo "=========================================================="
echo " Recovery complete! Launching dashboard on port 8501..."
echo " URL: http://localhost:8501"
echo "=========================================================="

export REPLAY_MODE=true
streamlit run frontend/app.py --server.headless=true --server.port=8501
