# Semantic Retrieval Module

**Module Owner**: Gargi (RemoteCLIP + FAISS / Qdrant)  
**Problem Statement**: PS26227 — Semantic Retrieval

## Scope & Responsibilities
- Generate semantic image embeddings using locally packaged `RemoteCLIP` (ViT-B/32 or ViT-L/14).
- Maintain offline vector index (`FAISS` index file + embedded SQLite metadata store, or embedded Qdrant).
- Provide natural-language text-to-image semantic search (e.g., "airfield with hardened aircraft shelters", "trench construction along ridgeline").
- Support image-to-image similarity search using visual crop queries.
- Support spatial (AOI bounding box), temporal (date window), and sensor filtering before/after vector search.
- Produce retrieval outputs conforming to `schemas/retrieval_result.json`.

## Key Interfaces
- `encode_text(query: str) -> np.ndarray` (512-d normalized embedding)
- `encode_image(image_path: str) -> np.ndarray` (512-d normalized embedding)
- `search(query: str, filters: RetrievalFilters, top_k: int = 10) -> RetrievalResult`
- `build_index(tile_embeddings: np.ndarray, metadata_records: List[TileMetadata]) -> None`

## Index Artifacts
Local indices live under `retrieval/indexes/` (gitignored).
