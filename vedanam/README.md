# VEDANAM — Architectural Glassmorphism Web Application

> **Sensory & Architectural Intelligence for Technology Value Realization (TVR)**  
> Built with **Nuxt 4**, **Three.js**, **GSAP & ScrollTrigger**, and **pure Vanilla CSS**, faithfully replicating the clean architectural design system of [ledup.pt](https://ledup.pt/).

---

## 🏛️ Application Architecture & Design System

Vedanam is the executive and architectural presentation layer for the **Technology Value Intelligence (TVI)** engine. It presents relationship-aware IT Financial Management (TBM/ITFM) as a living, spatial digital twin of the enterprise technology portfolio.

### 1. Visual Foundations (Ledup Style)
- **Canvas Foundation:** Light architectural studio canvas (`#f5f5f7`, `#fafafc`) paired with optical white cards (`#ffffff`) and deep obsidian/charcoal containers (`#14151a`, `#17181d`, `#1e1f26`).
- **Black & White Dominance:** Primary typography in optical carbon black (`#121316`) and pure white (`#ffffff`).
- **Sophisticated Pastel Palette:**
  - `Pastel Mint` (`#a7f3d0`) — Optimized TCO and healthy realization.
  - `Pastel Lavender` (`#c4b5fd`) — Semantic graph topology and active focus.
  - `Pastel Sky` (`#7dd3fc`) — DuckDB analytical truth core and runbooks.
  - `Pastel Peach` (`#fed7aa`) — Volume and enterprise scale metrics.
  - `Pastel Rose` (`#fecdd3`) — Risk tiers, rationalization alerts, and single points of failure.
- **100% Viewport Utilization:** Full-width expansive responsive layouts (`clamp(1.5rem, 3.5vw, 4.5rem)`), eliminating arbitrary width boxing on ultrawide screens.

---

## 🎬 Story-Driven Scroll Entry & Exit Animation Engine

Every section on the home page (`app/pages/index.vue`) loads as per its architectural narrative story, dynamically responding to user scroll position with choreographed entry and exit transitions powered by **GSAP** and **ScrollTrigger**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. HERO VIEW (The Illumination)                                        │
│    • Entry: 3D constellation + optical blur headline + spring badges   │
│    • Exit: Scrubbed upward drift (y: -80px) & 3D depth recession       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (scroll down)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. BENTO GRID HIGHLIGHTS (The Architectural Arsenal)                   │
│    • Entry: Header reveal -> Row 1 Archetypes -> Row 2 Engines         │
│    • Exit: Reverse exit when scrolling out; re-entry when returning   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (scroll down)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. PROJECTS & HOTSPOTS (Operational Landscape)                         │
│    • Entry: Left meta -> Spinning drag stamp -> Sonar radar pins       │
│    • Manifesto: Commitment to Excellence card lifts into view          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (scroll down)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. STRATEGIC PILLARS (Executive Tenets)                                │
│    • Entry: Giant dark container scale-lift + dual render cards        │
│    • Cascade: 5 foundation tabs (01 Innovation to 05 Sustainability)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (scroll down)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 5. CULMINATING FOOTER (The Sanctuary & Gateway)                        │
│    • Entry: Monumental rounded container rise + 4-column directory     │
│    • Exit: Smooth downward slide on upward scroll                      │
└────────────────────────────────────────────────────────────────────────┘
```

### Page-by-Page Animation Details:

#### 1. Home Page (`app/pages/index.vue`):
- **Hero View (`HeroSection.vue`):** Arrival choreography with Three.js 3D constellation canvas, optical text unblurring (`filter: blur(6px)` to `0px`), subtitle glide, and elastic telemetry badge popping (`back.out(1.5)`). Exit scrub translates pinned typography up (`y: -80px`), disperses telemetry chips, and pushes graph into depth (`z: -2.2`).
- **Highlights Bento Grid (`BentoGridSection.vue`):** Two-phase progressive loading: header reveal, Row 1 (Reference Architecture, ATHENA vector core pop, 102 Nodes stat scale, Governance Portal), and Row 2 (ONYX columnar execution slices expand, CATALOG 2026 banner expands, ORBIS graph topology constellation nodes pop). Reverse exit when scrolled out of view.
- **Projects & Hotspots (`HotspotShowcase.vue`):** Left meta narrative, rotating drag stamp badge (`• DRAG TO EXPLORE MORE VALUE INITIATIVES`), room card slide-in, and 4 sequential sonar radar pins (`scale: 0 -> 1`, stagger `0.1s`). Bottom "Commitment to Excellence" card elevates into place.
- **Strategic Pillars Accordion (`AccordionSection.vue`):** Dark container scale-lift (`#1e1f26`), white manifesto and dual render cards glide in, followed by a cascading staircase reveal of the 5 horizontal foundation tabs (`01. INNOVATION` through `05. SUSTAINABILITY`).
- **Culminating Footer (`FooterSection.vue`):** Massive curved dark container rises from the bottom (`y: 70px -> 0, scale: 0.98 -> 1`), headline unveil, 4-column directory cascade, and copyright strip fade.

#### 2. System Documentation Page (`app/pages/docs.vue`):
- **Docs Hero:** Arrival entry with back pill link slide (`x: -25px -> 0`), optical headline unblurring (`filter: blur(5px) -> blur(0px)`), subtitle glide, and chapter tab capsule pop (`back.out(1.4)`). Scrubbed upward exit on scroll down into chapters.
- **Active Chapter Cards:** Dynamic entrance on tab switch and scroll, elevating the chapter card (`y: 35px -> 0, scale: 0.98 -> 1`) with chapter badge and heading.
- **Pathologies & Guide Steps:**
  - *Chapter 1 (Why This App):* Glass callout thesis card lifts in, followed by an 8-card pathology grid cascade (`stagger: 0.06s`).
  - *Chapter 2 (How to Use):* 4 guide steps slide in sequentially from the bottom-left (`stagger: 0.1s`).
  - *Chapter 3 (What Is Inside):* Architecture 3-layer flow boxes cascade, followed by the 12-notebook research curriculum table reveal.

#### 3. Reference Application Architecture Page (`app/pages/reference-application.vue`):
- **Ref Hero Header:** Eyebrow chips slide in (`x: -20px -> 0`), title unveils (`filter: blur(5px) -> blur(0px)`), and 3 canonical archetype selector tab cards cascade in with spring ease (`stagger: 0.1s, back.out(1.4)`).
- **Application Overview:** Glass overview card lifts and scales into view (`y: 45px -> 0, scale: 0.98 -> 1`), code pill and health badge pop in.
- **Unit Economics Grid:** 4 metric cards (TCO, Cost/User, Cost/1k Txn, Blast Radius) cascade in with staggered upward pop (`stagger: 0.1s, scale: 0.94 -> 1`).
- **3D Subgraph & Cost Stack Split:** Left 3D WebGL knowledge graph card slides in from left (`x: -45px -> 0`), right DuckDB cost card slides in from right (`x: 45px -> 0`), segmented cost bar expands (`scaleX: 0 -> 1`), and cost breakdown rows cascade.
- **Capability Attribution & Governance Matrix:** Left capability progress bars fill from 0% to target width, and right governance scorecard audit cells pop in with back-easing (`stagger: 0.06s`).
- **What-If Scenario Simulator:** Interactive sandbox card expands into view (`y: 50px -> 0, scale: 0.98 -> 1`), sliders column slides in from left, and real-time results box slides in from right.
- **25 Enterprise Scenarios Grid:** Section header and tier filter bar unveil, followed by the 25 scenario cards (Scenarios A through Y) cascading into view with rapid fluid stagger (`stagger: 0.035s`).
- **Archetype Switch Animation:** Switching between canonical archetypes triggers a soft fluid refresh pulse across the overview card and unit economic metrics.

#### 4. Immersive 3D Technical Specifications Experience (`app/pages/technical-specs/index.vue`):
- **3 Mountain Expedition 3D Mocks on Pristine White Canvas (`#f8fafc` / `#ffffff`):** Designed around the unifying metaphor of **discovering an ice-capped mountain range**, where the 6 stages of the TVI architecture are milestones along the ascent from Valley Basecamp (1,400m) to Apex Summit (8,848m).
- **Mandatory Dual Field Notebooks Architecture at Every Milestone:** At each milestone along the climb, the user interacts with two distinct field notebooks:
  - **1. Business Field Guide (`ExpeditionNotebookModal.vue` / `useExpeditionMilestones.ts`):** Leather-bound expedition guide detailing executive ROI, strategic value realization, cost avoidance scenarios, TBM ATUM 4.0 standards, target KPI trajectories, and CFO/CIO core takeaways.
  - **2. Technical Field Manual (`ExpeditionNotebookModal.vue` / `useExpeditionMilestones.ts`):** Glacial-blue engineering blueprint detailing first-principles KaTeX mathematical formulation (`MathFormula.vue`), execution latency SLAs, memory budgets, input/output data contracts, and Python source code lineage with one-click clipboard copying.
- **The 3 Distinct Mountain Ascent Mocks:**
  - **Mock 01: The Summit Ridge Ascent (`MockMountainAscent.vue` / `/technical-specs/mock-ascent` or `?mock=ascent`):** First-person scrolly-climb up a crystalline 3D mountain slope with snow flurry particles. Features a live vertical Altimeter & Barometric HUD (1,400m to 8,848m, hPa, temperature, O₂ levels), expedition waypoint cairns, and 3D field books resting on the snow ledge of each camp.
  - **Mock 02: Topographic Relief Desk (`MockTopographicRelief.vue` / `/technical-specs/mock-relief` or `?mock=relief`):** High-altitude expedition cartography studio featuring a physical 3D stepped contour relief table on a surveyor's drafting desk. Users drag an elevation slice plane slider across the 14-tier massif to illuminate contour isolines, inspect surveyor beacon pins, and examine the dual open notebooks resting on the drafting desk blotter.
  - **Mock 03: Dual Codex Observatory (`MockDualBookObservatory.vue` / `/technical-specs/mock-observatory` or `?mock=observatory`):** Panoramic glass summit overlook perched above distant snowy mountain peaks. Centerpiece features two massive 3D books resting side-by-side on a crystalline ice lectern with animated 3D page-turn transitions synced to milestone progression, and an interactive side-by-side open dual-journal spread.
- **Floating Alpine Studio Switcher Dock (`MockSwitcherBar.vue`):** Minimalist frosted glass capsule on light alpine canvas allowing instant 1-click toggling between Mock 01 (Ascent), Mock 02 (Relief Desk), and Mock 03 (Observatory) with Web Audio API harmonic chimes, plus an interactive "Compare 3 Mocks" evaluation drawer.
- **Zero Memory Leaks & 60–120 FPS:** Full WebGL renderer cleanup and requestAnimationFrame cancellation on unmount.
- **Hardware & Benchmark Guarantees:** 100% offline, local-first 16 GB RAM laptop budget, fixed Seed 42 determinism, 0.00% General Ledger drift, and 83/83 passing Pytest test suites.

#### 5. Forensic Technical Specs Sub-Pages (`app/pages/technical-specs/*.vue`):
- **Data Pipeline (`technical-specs/data-pipeline.vue`):** Steps 01 & 02 walkthrough covering procedural entity generation, non-Gaussian Beta/Weibull/Log-Normal distributions, Sklar's multivariate Copula math, DuckDB vectorized OLAP, and live Zero-Reconciliation mass-balance proofs.
- **Graph Topology (`technical-specs/graph-topology.vue`):** Steps 03 & 08 walkthrough detailing NetworkX typed property graph schema, Brandes betweenness centrality, DAG cycle validation (Tarjan SCC & Kahn), transitive closure reachability, and interactive Single Point of Failure (SPOF) cascade outage simulation.
- **Cost Attribution (`technical-specs/cost-attribution.vue`):** Steps 04 & 05 walkthrough disaggregating fully burdened TCO across a 5-layer Activity-Based Costing stack, unit economics modeling, Lorenz curves / Gini spend concentration, and bipartite capability attribution with double-counting prevention proofs.
- **Portfolio Rationalization (`technical-specs/portfolio-rationalization.vue`):** Steps 06 & 07 walkthrough covering workload telemetry profiling, 2x2 median-split quadrants (Workhorses vs Zombies), Cloud Elasticity, GreenOps Scope 2 GHG math, TOPSIS MCDA vector normalization, and Gartner TIME matrix decommissioning runbooks with exit penalty amortization.
- **Value & Variance (`technical-specs/value-variance.vue`):** Steps 09 & 10 walkthrough detailing Technology Value Realization (TVR) post-delivery tracking, Difference-in-Differences (DiD) causal econometrics, 3-factor algebraic Price-Volume-Mix (PVM) variance decomposition, and automated SLA breach penalty claims.
- **AI & Governance (`technical-specs/ai-governance.vue`):** Steps 11 & 12 walkthrough deconstructing the Dual-Mode AI architecture (deterministic zero-hallucination rules vs local Ollama SLM), Graph RAG topological grounding, AST query security firewalls, Unified Technology Value Chain dossier compilation, and 4-tier automated integrity validation.

#### 6. Terms of Service & Operational Governance Page (`app/pages/terms.vue`):
- **Executive Governance & Analytical Guardrails Hub:** Comprehensive 8-article enterprise governance constitution covering operational boundaries, avoidance modeling, and mass-balance mandates.
- **Avoidable Cost vs. Guaranteed Cash Savings:** Formal codification of Guardrail 01 specifying that rationalization recommendations (MCDA, TIME matrix, decommissioning runbooks) represent *potential avoidable cost scenarios*, strictly acknowledging contractual vendor lock-ins, termination penalties, and shared platform overhead.
- **Associative Causality in Value Realization (TVR):** Codification of Guardrail 02 requiring that benefit realizations and KPI linkage waterfalls represent *statistical and temporal associations*, preventing ungrounded single-factor causal claims in complex corporate ecosystems.
- **Algorithmic Determinism & Mass Balance Mandate:** Mandatory conservation of General Ledger mass balance ($\Delta = \$0.00$), Seed 42 reproducibility, and zero-code execution hallucination security rules.
- **Dual-Mode AI & Human Oversight Governance:** Strict operational rules defining deterministic rules vs. advisory local Ollama generation, requiring human executive authorization for critical system decommissioning.
- **Interactive UI & Real-Time Filter Engine:** Category tab pill filter (`All Articles`, `Scope & IP`, `Analytical Guardrails`, `Deterministic Truth`, `Liability & Custody`), real-time search input filter, one-click permalink clipboard copying with Web Audio harmonic chime feedback, and GSAP arrival choreography.

#### 7. Privacy Policy & Telemetry Governance Page (`app/pages/privacy.vue`):
- **Local-First & Zero-Exfiltration Core Manifesto:** Formal architectural guarantee that *"Your Enterprise Data Never Leaves Your Device."* No cloud telemetry beacons, zero third-party tracking cookies, no Google Analytics, no session heatmaps, and 100% air-gappable operation.
- **Data Classification & Non-PII Prohibition Matrix:** Side-by-side demarcation table verifying permissible system-level telemetry (application IDs, GL cost records, vCPU/RAM metrics) versus strictly prohibited Personally Identifiable Information (individual employee data, personal browsing history, customer credentials).
- **Local AI & Loopback Insulation Protocol:** Establishes that AI interactions execute either through offline deterministic rules or via local Ollama models routed exclusively to `http://localhost:11434` over the loopback interface (`127.0.0.1`), with zero prompt data transmitted to external multi-tenant cloud LLM APIs.
- **Sensory Hardware & Browser API Permissions:** Transparent disclosure of procedural Web Audio API synthesis (432Hz sine waves on CPU without microphone access) and client-side GPU WebGL rendering without canvas fingerprinting.
- **Instant Sovereign Data Destruction:** Documented verification of zero cloud remanence, enabling instantaneous and total data destruction via standard local filesystem commands (`rm -rf database/ data/`).
- **Interactive UI & Filtering:** Category filter tabs, instant search, copyable clause permalinks with audio chime feedback, 4-tier architectural data flow diagram, and direct Data Protection Officer communication channels.

### Technical Safeguards:
- **Zero Memory Leaks:** Scoped to `gsap.context(..., rootRef.value)` with complete teardown on `onUnmounted` via `ctx?.revert()`.
- **Hardware Acceleration:** All animated elements use `will-change: transform, opacity;` for 60–120 FPS performance.
- **Trigger Calibration:** `ScrollTrigger.refresh()` scheduled on mount and tab switches to guarantee exact trigger thresholds after asset hydration.

---

## 🚀 Development & Commands

```bash
# Install dependencies
npm install

# Start local development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```
