# SMA-Project-of-Tongji-University

## Quick Start

1. Please install **Maven** and **JDK 25**.

2. Create `.env` under the root path, and write the following lines into `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=<your_api_key>
OPENAI_BASE_URL=<model_api_url>
OPENAI_MODEL=<your_model>
EMBEDDING_MODEL=text-embedding-3-small
MILVUS_MODE=lite
RAG_MILVUS_URI=.run/milvus/canvas_ai.db
MILVUS_TOKEN=
MILVUS_COLLECTION_PREFIX=canvas_rag_
MILVUS_VECTOR_DIM=1536
```

3. Just run:

```bash
bash ./run_services.sh
```