# Local LLM + Knowledge Graph AI Analyst

**Purpose:** Provides a guarded, zero-hallucination natural language analytical interface. Operates in deterministic rules mode by default (or optional local Ollama Llama-3 mode). Parses intent/slots, executes safe deterministic database/graph queries (zero arbitrary code execution), and synthesizes grounded executive explanations with cited entities.  
**Series Index:** Notebook 11 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Provides a guarded, zero-hallucination natural language analytical interface. Operates in deterministic rules mode by default (or optional local Ollama Llama-3 mode). Parses intent/slots, executes safe deterministic database/graph queries (zero arbitrary code execution), and synthesizes grounded executive explanations with cited entities.

### Core Methodology
Deterministic intent and slot extraction; conversational session memory with pronoun anaphora resolution; expanded domain intent routing (blast radius gating, SLA penalties, decommissioning roadmap, capability maturity); guarded parameter validation; zero arbitrary code execution; grounded contextual synthesis with entity citation and executive briefing slide generation.

---

## 2. Key Scenarios & Focus Areas
- Answering questions on August spend spike, TechNova vendor dependencies, and out-of-domain rejection.
- Multi-turn conversational memory resolving context ("What about its blast radius?", "How does this compare?").
- Automated gating decisions, penalty tracking, and decommissioning milestones via natural language.
- Executive briefing slide generation directly from analytical intent outputs.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `Natural language queries`
- `Knowledge Graph`
- `DuckDB analytical database`

### Primary Outputs
- `Grounded conversational answers`
- `Cited entity links`
- `Analytical evidence records`
- `Executive Markdown briefing slides`

---

## 4. File Structure & Versioning

```text
11_local_llm_knowledge_graph_analyst/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: The active development canvas where new algorithms, visualizations, and modular extensions can be developed without touching the baseline.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Expand intent vocabulary and slot extraction for complex multi-hop queries.
- [x] Add conversational session memory and context tracking across turns.
- [x] Integrate LangChain / LlamaIndex agentic tooling with strict verification sandboxes.
- [x] Generate automatic executive summary briefing slides directly from Q&A outputs.
