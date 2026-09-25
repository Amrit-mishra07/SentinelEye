# Model Catalog & Local Packaging Manifest

**Constraint**: Offline, Air-Gapped Operation (No runtime network calls, no cloud APIs).  
All pretrained model weights must be pre-packaged locally in this `/models` directory with licenses explicitly declared and verified.

---

## 1. RemoteCLIP (Semantic Retrieval)
- **Model**: `RemoteCLIP-ViT-B-32` (or `RemoteCLIP-ViT-L-14`)
- **Weights File**: `models/remoteclip/remoteclip_vit_b32.pt`
- **Architecture**: Vision Transformer dual-encoder trained on remote sensing image-text pairs.
- **Upstream License**: Apache 2.0 / MIT
- **Intended Use**: Natural-language text prompt and visual crop semantic feature embedding (512-dim).
- **Offline Loading**: Loaded directly via `torch.load()` or `open_clip.create_model_and_transforms()` with local weights file path.

---

## 2. BIT — Bitemporal Image Transformer (Change Detection)
- **Model**: `BIT_base`
- **Weights File**: `models/bit/bit_base_bitemporal.pth`
- **Architecture**: Dual-branch ResNet/Transformer encoder with bitemporal difference decoder for high-resolution change mask generation.
- **Upstream License**: MIT License
- **Intended Use**: Pixel-level change detection on coregistered optical before/after pairs.
- **Offline Loading**: Direct PyTorch state dict load (`torch.load(..., map_location='cpu')`).

---

## 3. BAN — Bi-temporal Adapter Network
- **Model**: `BAN_Adapter_v1`
- **Weights File**: `models/ban/ban_adapter.pth`
- **Architecture**: Lightweight foundation model adapter for multi-temporal feature harmonization.
- **Upstream License**: MIT License
- **Intended Use**: Harmonizing multi-sensor feature distributions (e.g. cross-sensor Sentinel-2 vs Landsat-8 pairs).

---

## 4. Prithvi-EO-2.0 (Foundation Model - Optional / Advanced Feature Extractor)
- **Model**: `Prithvi-EO-2.0-300M`
- **Weights File**: `models/prithvi/prithvi_eo_2_300m.pt`
- **Architecture**: Geospatial foundation model pre-trained on multi-spectral satellite imagery.
- **Upstream License**: Apache 2.0
- **Intended Use**: Self-supervised multi-spectral representations.

---

## 5. Local LLM (Constrained Intelligence Briefing)
- **Model**: `Qwen2.5-7B-Instruct-GGUF` (or `Gemma-2-9B-It-GGUF`)
- **Weights File**: `models/llm/qwen2.5-7b-instruct-q4_k_m.gguf`
- **Quantization**: 4-bit Medium (`Q4_K_M`) — optimized for 8GB-16GB CPU/GPU demo laptop execution.
- **Upstream License**: Apache 2.0 (Qwen) / Gemma Terms of Use (Gemma)
- **Intended Use**: Reading structured Facts Dictionary JSON and generating military-standard tactical briefings under GBNF grammar constraints.
- **Offline Loading**: Loaded via `llama_cpp.Llama(model_path=...)` or local Ollama daemon.

---

## 6. Lightweight YOLO + SAHI (Tactical Asset Detection)
- **Model**: `yolov8n-sahi.pt`
- **Weights File**: `models/yolo/yolov8n_sahi.pt`
- **Architecture**: Slicing Aided Hyper Inference on 512x512 sub-crops for small military vehicles, aircraft, and encampments.
- **Upstream License**: AGPL-3.0 (Isolated execution wrapper to ensure core pipeline modularity).

---

## Verification Checklist for Deployment Team
- [ ] Ensure all weight files exist in their respective directories before entering venue.
- [ ] Verify SHA256 checksums match `scripts/checksums.sha256`.
- [ ] Test offline loading with `scripts/verify_offline_env.py` with Wi-Fi disabled.
