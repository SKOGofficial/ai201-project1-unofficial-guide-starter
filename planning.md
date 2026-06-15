# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Laptops and Mini-PCs: Use-Case Analysis and Recommendation Engine. This knowledge is valuable because official manufacturer spec sheets completely hide real-world trade-offs like thermal throttling, fan noise, upgradeability limits, and cost-per-token efficiencies for local AI. There isn’t a lot of information out there on selection of the right laptop based on specific needs of the consumer, for example if a user wants to know if a certain laptop meets the base requirements of a video game or if a mini PC can manage local LLM work loads.

---

## Documents

| #   | Source                                    | Description                                                                                                                                                 | URL or location                                                                                         |
| --- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 1   | TerminalBytes Technical Editorial         | An in-depth 2026 text guide breaking down hardware tiers (like AMD Strix Halo vs Apple Silicon) for running massive 70B local AI models completely offline. | https://terminalbytes.com/best-mini-pc-for-local-llm-2026/                                              |
| 2   | TerminalBytes OpenClaw Guide              | Text comparison evaluating upgradeable DDR5 RAM limits versus soldered RAM configurations when running local AI orchestration frameworks.                   | https://terminalbytes.com/openclaw-mini-pc-alternatives-mac-mini/                                       |
| 3   | TerminalBytes Hardware Review             | Dense, text-heavy breakdown outlining RAM requirements and CPU/iGPU processing limits for quantized local models like Gemma 4.                              | https://terminalbytes.com/run-gemma-4-mini-pc-without-gpu/                                              |
| 4   | Tom's Hardware Tier List                  | Comprehensive buying guide ranking high-end vs budget gaming laptops based on real-world frame rates, thermal efficiency, and chassis engineering.          | https://www.tomshardware.com/laptops/gaming-laptops/best-gaming-laptops                                 |
| 5   | Tom's Hardware MSI & Alienware Deep-Dives | Text-heavy performance reviews detailing CPU power limits (TDP), cooling fan acoustics, and hardware upgrade paths.                                         | https://www.tomshardware.com/laptops/gaming-laptops/raider-crosshair-performance-upgrade-arrow-lake-msi |
| 6   | Lenovo Hardware Glossary Guide            | Text comparing stationary small-form-factor mini-PCs versus all-in-one laptops for standard multi-display office productivity and space optimization.       | https://www.lenovo.com/us/en/glossary/mini-pc/                                                          |
| 7   | r/TechNook Long-form Essay                | Community-sourced text analysis comparing the long-term cost trajectories, component lifespan, and hardware obsolescence of laptops vs mini-PCs.            | https://www.reddit.com/r/TechNook/comments/1s11d2z/mini_pcs_vs_full_pcs_vs_laptops_what_actually/       |
| 8   | r/MiniPCs Technical Deep-Dive             | Dense forum text thread highlighting why mini-PCs outperform identically-specced laptops due to larger cooling arrays and stable wall power profiles.       | https://www.reddit.com/r/MiniPCs/comments/1raptft/whats_an_advantage_of_a_mini_pc_over_a_laptop/        |
| 9   | ServeTheHome TinyMiniMicro Series         | Text-heavy editorial analyzing how to repurpose low-power mini-PCs into virtualization nodes (Proxmox, Docker, and local automation).                       | https://www.servethehome.com/tag/tinyminimicro/                                                         |
| 10  | PCMag Productivity Roundup                | A clean text-based buying guide comparing battery lifespans, keyboard ergonomics, chassis weight, and display aspect ratios for business users.             | https://www.pcmag.com/picks/the-best-laptops                                                            |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
450
**Overlap:**
100
**Reasoning:**
I will choose a character window of 450 characters and an over lap of 100 characters, this is because most information in these texts are organised in paragraphs that compare and contrast features of Laptops and MiniPC's making them important for a lot of different user querires while seperating them into smaller chunks will lose the comparisons made in the same chunk.

This also works well for forum style data sources since 450 characters encapuslate a lot interactive discussions giving the llm condensed points from boths sides.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2
**Top-k:**
5
**Production tradeoff reflection:**
I think I would choose an embedding model that is more detailed, maybe higher demension vectors to capture better realtionships between the information. This ie because a lot of the information is based on model names and numbers which may appear very close to each other in vector database making details hard to show up. I think being that its a larger model, it will also have to run on hardware that can comfertably embedd information quickly. And for general scalling if the user request information that isn't available in the existing vector database, having an AI agent or a developer update the data base with that information automatically would help keep our system adaptive over time.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                                                                           | Expected answer                                                                                                                     |
| --- | ---------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 1   | What chip has the best single core performance?                                                                                    | M5                                                                                                                                  |
| 2   | Why do mini-PCs typically maintain higher sustained performance than laptops sharing the exact same processor?                     | They utilize larger cooling arrays and stable wall power profiles (higher sustained TDP) to completely avoid thermal throttling.    |
| 3   | What primary architectural limitation does the OpenClaw guide highlight when running large local AI models on a Mac Mini?          | It is constrained by non-upgradeable soldered RAM configurations, unlike modular mini-PCs that support high-capacity DDR5 upgrades. |
| 4   | According to hardware buying guides, what is the minimum memory footprint required to run a 4-bit quantized Gemma 4 26B MoE model? | A minimum of 16–18 GB of available combined memory (RAM, VRAM, or Unified Memory).                                                  |
| 5   | In the ServeTheHome TinyMiniMicro series, what platforms are heavily utilized to turn mini-PCs into homelab nodes?                 | Virtualization hypervisors and container orchestration stacks like Proxmox and Docker.                                              |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. I think that the data base being so large could have an impact in latency and general development life cycle since it will take a long time to embbed every time I need to embed anything.

2. I think that the mix of Form based data sources and blog-post based data sources are going to pose a challenge with compatability. Also there are concerns with the formating of the documents as not all of the documents may transfer over as clean text.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

+------------------------------------------------------------+
| 1. DOCUMENT INGESTION |
| - Manually copy and paste text from chosen data sources |
| - Saved locally as structured text files (.txt / .md) |
+------------------------------------------------------------+
|
v
+------------------------------------------------------------+
| 2. CHUNKING |
| - Processes files using a universal chunking rule |
| - Split text using LangChain RecursiveCharacterSplitter |
+------------------------------------------------------------+
|
v
+------------------------------------------------------------+
| 3. EMBEDDING + VECTOR STORE |
| - Generate text embeddings locally via embedding model |
| - Insert and index vectors inside local ChromaDB |
+------------------------------------------------------------+
|
v
+------------------------------------------------------------+
| 4. RETRIEVAL |
| - System takes incoming user hardware query |
| - Queries ChromaDB to retrieve top relevant text chunks |
+------------------------------------------------------------+
|
v
+------------------------------------------------------------+
| 5. GENERATION |
| - Formulate structural System Prompt + User Message |
| - Inject retrieved context chunks directly into the prompt|
| - Transmit payload to Groq API to process via Llama |
| - Receive final output and surface response to the user |
+------------------------------------------------------------+

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

Used Gemini to research sources.
My input was the domain and project context.
I expect the AI to give me sources that are wide enough to encapsulate the Laptop and MiniPC decision making market.
I will be skimming through each source to verify.
it took three attempts to get the right sources for this step.

**Milestone 4 — Embedding and retrieval:**

I asked Gemini to canabalise the embedding and retrival strategy used in the Lab 1 and apply it to this context.
I gave it the retrive function from Lab1.
I excpect it to make small edits to this logic and make it so that it matches my new metadata schema.
I verified by reading through the code and making sure the metadata meets my schema.

**Milestone 5 — Generation and interface:**

I used Gemini and Calude to cusotmize the generation and interface.
For input I gave it the UI from Lab 1 and planning.md doc.
I'm expecting it to rehash the UI to include the default questions from the planning doc.
I'm verifying by testing the generation and UI by running the app.
