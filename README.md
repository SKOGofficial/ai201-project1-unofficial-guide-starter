# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Laptops and Mini-PCs: use-case analysis and a recommendation engine. The system covers
real-world hardware trade-offs for choosing between laptops and mini-PCs — thermal
throttling, fan noise, RAM upgradeability, TDP/power limits, and cost-per-token efficiency
for running local AI models.

This knowledge is valuable because official manufacturer spec sheets hide these real-world
trade-offs. There isn't much consolidated information on selecting the right machine for a
specific need — for example, whether a given laptop meets the baseline requirements of a
particular video game, or whether a mini-PC can comfortably handle local LLM workloads.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| #   | Source                                    | Type                     | URL or file path                                                                                                                      |
| --- | ----------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | TerminalBytes Technical Editorial         | Technical editorial      | `data/Terminal_Bytes_1.txt` — https://terminalbytes.com/best-mini-pc-for-local-llm-2026/                                              |
| 2   | TerminalBytes OpenClaw Guide              | Comparison guide         | `data/Terminal_Bytes_2.txt` — https://terminalbytes.com/openclaw-mini-pc-alternatives-mac-mini/                                       |
| 3   | TerminalBytes Hardware Review             | Hardware review          | `data/Terminal_Bytes_3.txt` — https://terminalbytes.com/run-gemma-4-mini-pc-without-gpu/                                              |
| 4   | Tom's Hardware Tier List                  | Buying guide / tier list | `data/Tom's_Hardware_1.txt` — https://www.tomshardware.com/laptops/gaming-laptops/best-gaming-laptops                                 |
| 5   | Tom's Hardware MSI & Alienware Deep-Dives | Performance review       | `data/Tom's_Hardware_2.txt` — https://www.tomshardware.com/laptops/gaming-laptops/raider-crosshair-performance-upgrade-arrow-lake-msi |
| 6   | Lenovo Hardware Glossary Guide            | Vendor glossary / guide  | `data/Lenovo_1.txt` — https://www.lenovo.com/us/en/glossary/mini-pc/                                                                  |
| 7   | r/TechNook Long-form Essay                | Community forum essay    | `data/Reddit_1.txt` — https://www.reddit.com/r/TechNook/comments/1s11d2z/mini_pcs_vs_full_pcs_vs_laptops_what_actually/               |
| 8   | r/MiniPCs Technical Deep-Dive             | Community forum thread   | `data/Reddit_2.txt` — https://www.reddit.com/r/MiniPCs/comments/1raptft/whats_an_advantage_of_a_mini_pc_over_a_laptop/                |
| 9   | ServeTheHome TinyMiniMicro Series         | Editorial series         | `data/Serve_The_Home_1.txt` — https://www.servethehome.com/tag/tinyminimicro/                                                         |
| 10  | PCMag Productivity Roundup                | Buying guide             | `data/Pcmag_1.txt` — https://www.pcmag.com/picks/the-best-laptops                                                                     |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
450 characters (split with LangChain `RecursiveCharacterTextSplitter`, `length_function=len`).

**Overlap:**
100 characters.

**Why these choices fit your documents:**
Most information in these texts is organized in paragraphs that compare and contrast features
of laptops and mini-PCs, which makes them relevant to many different user queries. A 450-character
window keeps a complete comparison together within a single chunk; splitting into smaller chunks
would lose the contrast made within the same passage. The 100-character overlap preserves context
across chunk boundaries so a comparison isn't cut in half. This window size also works well for the
forum-style sources, where 450 characters captures a meaningful slice of an interactive discussion,
giving the LLM condensed points from both sides.

**Preprocessing before chunking:**
Each source file begins with a `MetaData:` header block followed by a `Text:` marker. During
ingestion (`ingest.py` → `parse_metadata`), the metadata header is parsed into structured fields
(e.g. website name / title) and stripped from the body, so only the clean article/forum text is
chunked. A `source`, `file`, and approximate `line` number are attached to every chunk as metadata.

**Final chunk count:**
526 chunks across 10 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
`all-MiniLM-L6-v2`, run locally via `sentence-transformers`. Vectors are stored in a local
ChromaDB collection (`hardware_guide`) using cosine distance, and retrieval returns the top-k = 5
chunks per query.

**Production tradeoff reflection:**
If I were deploying this for real users and cost weren't a constraint, I would choose a more
detailed embedding model — likely higher-dimensional vectors — to capture finer relationships
between pieces of information. A lot of this content is based on model names and numbers that can
sit very close together in vector space, which makes specific details hard to distinguish. Because
a larger model is heavier, it would also need to run on hardware that can embed text quickly and
comfortably. For general scalability, if a user asks for information that isn't yet in the vector
database, having an AI agent or a developer automatically update the database with that information
would help keep the system adaptive over time.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

The generator (`generator.py`) is backed by Groq running `llama-3.3-70b-versatile`. Grounding is
enforced through both the system prompt and structural choices in how context is assembled:

- **Low-relevance filtering:** Retrieved chunks with a cosine distance above `MAX_DISTANCE = 0.7`
  are dropped before generation. The remaining chunks are sorted by ascending distance and capped
  at the top 5.
- **Hard fallback:** If retrieval returns nothing (or every chunk is filtered out as a weak match),
  the system returns a fixed message — `"Cannot respond to the query based on the information
provided."` — without ever calling the LLM.
- **Structured context block:** Each surviving chunk is injected into the user message labeled with
  its content, source file, line number, and distance, so the model has explicit, attributable
  context to cite from.

**System prompt grounding instruction:**
The model is given a "Hardware Recommendation Expert" persona and these grounding rules (verbatim
from `generator.py`):

> Answer the user's question using ONLY the information in the retrieved chunks provided in the user
> message. ... Grounding Rules:
>
> 1. Use ONLY the provided context. Do not use outside knowledge.
> 2. If the context doesn't contain the answer, respond with exactly: "Cannot respond to the query
>    based on the information provided."
> 3. Be technical and precise regarding hardware specs.

**How source attribution is surfaced in the response:**
The system prompt instructs the model to cite using each chunk's metadata (file and line number)
and to place the citation at the end of its response in the format `[File-name: line-number]`
(e.g. `[Lenovo_1.txt: 42]`). Those file and line values are supplied to the model in the context
block built from the retrieved chunk metadata.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| #   | Question                                                                                                                           | Expected answer                                                                                                                     | System response (summarized)                                                                       | Retrieval quality                                                  | Response accuracy |
| --- | ---------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------- |
| 1   | What chip has the best single core performance?                                                                                    | M5                                                                                                                                  | Cannot respond to the query based on the information provided.                                     | Terrible                                                           | 0%                |
| 2   | Why do mini-PCs typically maintain higher sustained performance than laptops sharing the exact same processor?                     | They utilize larger cooling arrays and stable wall power profiles (higher sustained TDP) to completely avoid thermal throttling.    | They can pull as much power as the want and cool much better, leading to better performance        | good, pulled from an active reddit dicussion                       | 90%               |
| 3   | What primary architectural limitation does the OpenClaw guide highlight when running large local AI models on a Mac Mini?          | It is constrained by non-upgradeable soldered RAM configurations, unlike modular mini-PCs that support high-capacity DDR5 upgrades. | OpenClaw guide shows that Memory is soldered on Mac-Minis making it hard to updgrade RAM in future | Great, pulled from a blog post about Mac Mini usage with open claw | 90%               |
| 4   | According to hardware buying guides, what is the minimum memory footprint required to run a 4-bit quantized Gemma 4 26B MoE model? | A minimum of 16–18 GB of available combined memory (RAM, VRAM, or Unified Memory).                                                  | Minimum is 24GB ram while 32GB is recomended                                                       | yes pulled from a direct FAQ about Gemma 4                         | 90%               |
| 5   | In the ServeTheHome TinyMiniMicro series, what platforms are heavily utilized to turn mini-PCs into homelab nodes?                 | Virtualization hypervisors and container orchestration stacks like Proxmox and Docker.                                              | Cannot respond to the query based on the information provided. [Lenovo_1.txt: 34]                  | Terrible, sources did not include information on this              | 0%                |

**Retrieval quality:** Relevant
**Response accuracy:** Partially accurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

What chip has the best single core performance?

**What the system returned:**

Cannot answer from the information given.

**Root cause (tied to a specific pipeline stage):**

Ingesting step, I did not have any data sources on single core performance, but several on how good the M5 was.

**What you would change to fix it:**

Include more sources on chip performance details.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The spec helped organise my thought before begining development, it also helped guid the development process as the AI agent could easily follow along the planning documet.

**One way your implementation diverged from the spec, and why:**

I changed the UI later on as I wanted it to look different, I also ended up using a slightly different embedding modle: lang chain, because the AI recomened it for larger sources.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Embedding and retrieval (Milestone 4)**

- _What I gave the AI:_ I asked Gemini to adapt the embedding and retrieval strategy from Lab 1 to
  this project's context, and gave it the `retrieve` function from Lab 1.
- _What it produced:_ Small edits to that logic so the retrieval matched my new metadata schema
  (source, file, line, distance).
- _What I changed or overrode:_ I I chaned the meta data so that the chunks could chunks could be mapped a little easier, especially based on title of blog post or reddit post.

**Instance 2 — Generation and interface (Milestone 5)**

- _What I gave the AI:_ I used Gemini and Claude to customize the generation step and the UI, giving
  them the Lab 1 UI and the `planning.md` document.
- _What it produced:_ A reworked Gradio UI that surfaces the default test questions from the
  planning doc, plus the grounded generation logic.
- _What I changed or overrode:_ Gemini Messed up the usage of gradio, and I had to debug it using claude.
<!-- Additional AI usage from planning.md (Milestone 3 — Ingestion):
     Used Gemini to research sources. Input was the domain and project context; expected sources
     broad enough to cover the laptop/mini-PC decision-making market. Verified by skimming each
     source; it took three attempts to land on the right set. -->
