# Detailed Execution Plan: The Unofficial Guide (Laptop & Mini-PC Advisor)

This plan outlines the surgical changes required to transform the "RulesBot" codebase into a specialized RAG system for hardware recommendations.

## Phase 1: Environment & Configuration
1.  **Dependencies**:
    *   Verify `requirements.txt` includes `langchain-text-splitters`.
    *   Ensure `gradio` and `chromadb` versions are compatible.
2.  **Global Settings (`config.py`)**:
    *   Change `CHROMA_COLLECTION` to `"hardware_advisor"`.
    *   Set `DOCS_PATH` to `"./data"` (as per user instruction).
    *   Set `N_RESULTS` to `5` (as per `planning.md`).

## Phase 2: Data Ingestion Refactoring (`ingest.py`)
1.  **Document Loading**:
    *   Modify `load_documents()` to support both `.txt` and `.md` files.
    *   Change dictionary key `game` to `source` for better domain fit.
2.  **Advanced Chunking**:
    *   Replace the manual sliding window in `chunk_document()` with `RecursiveCharacterSplitter`.
    *   Configure `chunk_size=450` and `chunk_overlap=100`.
    *   Ensure metadata includes `source`, `file`, and `line` (using `start_index` for line calculation).

## Phase 3: Retrieval & Vector Store (`retriever.py`)
1.  **Metadata Alignment**:
    *   Update `embed_and_store()` to handle the `source` field in metadata.
    *   Update `retrieve()` to extract `source` from the retrieved chunks' metadata.
2.  **Distance Metrics**:
    *   Confirm `cosine` similarity is optimal (default in current setup).

## Phase 4: Persona & Generation (`generator.py`)
1.  **System Prompt Rebuild**:
    *   Persona: "Hardware Selection Expert".
    *   Context: Expert in thermal throttling, TDP, RAM upgradeability, and local AI hardware requirements.
    *   Constraint: Answer *only* using provided context; if unsure, state "Cannot respond to the query based on the information provided."
2.  **Context Formatting**:
    *   Update the context block to label sources as "Hardware Source" instead of "Game".
    *   Maintain the strict distance threshold (`MAX_DISTANCE = 0.7`).

## Phase 5: UI & Branding (`app.py`)
1.  **Visual Rebranding**:
    *   Change title to "The Unofficial Guide".
    *   Update HTML header: "💻 The Unofficial Guide: Hardware Recommendation Engine".
    *   Update description to focus on Laptops, Mini-PCs, and thermal/upgradeability trade-offs.
2.  **Examples & Interaction**:
    *   Replace board game examples with the 5 evaluation questions from `planning.md`:
        *   "What chip has the best single core performance?"
        *   "Why do mini-PCs typically maintain higher sustained performance than laptops?"
        *   "What architectural limitation does the OpenClaw guide highlight for Mac Mini?"
        *   "Minimum memory footprint for 4-bit quantized Gemma 4 26B?"
        *   "What platforms turn mini-PCs into homelab nodes in ServeTheHome series?"
3.  **Sidebar Update**:
    *   Update the "Loaded Sources" list to dynamically or statically reflect the hardware guides.

## Phase 6: Validation & Testing
1.  **Clean Slate**: Delete `./chroma_db` to ensure a clean re-ingestion of the hardware data.
2.  **Ingestion Test**: Run `app.py` and verify terminal output for "Loaded X document(s)" from the `./data` folder.
3.  **Accuracy Check**: Run the 5 evaluation questions through the UI and compare against the "Expected Answer" column in `planning.md`.
