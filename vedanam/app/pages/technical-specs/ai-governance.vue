<script setup lang="ts">
import { ref } from 'vue'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'
import MathFormula from '~/components/MathFormula.vue'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

// Interactive Natural Language Query Tester
interface QueryPreset {
  prompt: string
  intent: string
  parameter: string
  generatedQuery: string
  mode: 'Deterministic (Rules Engine)' | 'Local Ollama SLM'
  groundedOutput: string
}

const queryPresets: QueryPreset[] = [
  {
    prompt: 'What is the blast radius and downstream spend if APP-010 goes down?',
    intent: 'BLAST_RADIUS_ANALYSIS',
    parameter: "app_id = 'APP-010'",
    generatedQuery: "MATCH (a:Application {id: 'APP-010'})<-[:DEPENDS_ON*1..10]-(downstream:Application) RETURN count(downstream), sum(downstream.tco)",
    mode: 'Deterministic (Rules Engine)',
    groundedOutput: 'APP-010 (Payments Gateway) has a transitive blast radius of 24 downstream applications across 3 business units, with $6,450,000 in operational spend at risk.'
  },
  {
    prompt: 'Identify all redundant applications supporting Order-to-Cash capability.',
    intent: 'CAPABILITY_REDUNDANCY',
    parameter: "capability_name = 'Order-to-Cash'",
    generatedQuery: "MATCH (c:BusinessCapability {name: 'Order-to-Cash'})<-[:PROVIDES]-(a:Application) RETURN a.id, a.name, a.tco, a.time_quadrant",
    mode: 'Deterministic (Rules Engine)',
    groundedOutput: '3 redundant applications detected: APP-005 (Global ERP OMS, $1.1M), APP-008 (Regional Legacy OMS, $480k, Eliminate), and APP-019 (Acquired Division OMS, $310k, Migrate).'
  },
  {
    prompt: 'Show all zombie applications with annual TCO over $200,000 and near-zero telemetry.',
    intent: 'ZOMBIE_DISCOVERY',
    parameter: "tco_threshold = 200000, utilization_percent < 10",
    generatedQuery: "SELECT app_id, name, tco, annual_avoidable_cost FROM v_applications WHERE quadrant = 'Zombie Systems' AND tco > 200000",
    mode: 'Deterministic (Rules Engine)',
    groundedOutput: 'Found 2 zombie systems: APP-007 (Legacy Regional CRM, TCO $425k, Net Avoidable $385k) and APP-022 (Deprecating Ledger Archive, TCO $240k, Net Avoidable $195k).'
  }
]

const activePresetIndex = ref(0)

const selectQueryPreset = (idx: number) => {
  activePresetIndex.value = idx
  playInteractChime(1.3)
}
</script>

<template>
  <div class="subpage-wrapper">
    <div class="container subpage-container">
      <!-- Subpage Nav -->
      <div class="subpage-nav-header">
        <NuxtLink
          to="/technical-specs"
          class="back-pill-link"
          @mouseenter="setCursor('ALL SPECS', 'default')"
          @mouseleave="resetCursor"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          <span>Back to Technical Specs Hub</span>
        </NuxtLink>
        <div class="step-indexer">
          <span class="pastel-chip chip-lavender">Phase 06</span>
          <span class="indexer-text">Steps 11 & 12 of 12</span>
        </div>
      </div>

      <!-- Hero Header -->
      <header class="subpage-hero">
        <span class="section-tag">Autonomous Intelligence & Governance</span>
        <h1 class="subpage-main-title">AI & Governance: Dual-Mode Graph RAG & Executive Synthesis</h1>
        <p class="subpage-lead">
          Raw generative LLMs hallucinate numbers and expose enterprise databases to prompt injection vulnerabilities. TVI implements a decoupled Dual-Mode AI architecture: default deterministic rules mode for guaranteed zero-hallucination accuracy, with an optional local Ollama SLM mode strictly constrained by AST query firewalls.
        </p>
      </header>

      <!-- Step 11 Section -->
      <section class="spec-detail-block" id="step-11">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 11</span>
          <span class="pastel-chip chip-lavender">AI & Graph RAG</span>
          <span class="module-ref mono">src/tvi/llm.py</span>
        </div>
        <h2 class="block-heading">Dual-Mode AI Knowledge Graph Analyst & Zero-Hallucination Grounding</h2>
        <p class="block-intro">
          When a CFO asks "What happens if we shut down APP-010?", executing arbitrary generative code or unconstrained Text-to-SQL is high-risk. Step 11 decouples intent parsing from query execution.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">11.1</div>
              <div class="wf-content">
                <h4>Grounded Intent Classification & Entity Extraction</h4>
                <p>
                  Incoming natural language strings are matched against a compiled catalog of enterprise governance intents (e.g., <code>BLAST_RADIUS</code>, <code>CAPABILITY_TCO</code>, <code>ZOMBIE_DISCOVERY</code>, <code>PVM_DECOMPOSITION</code>). Entity IDs are extracted using regex and validated against the graph node registry.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">11.2</div>
              <div class="wf-content">
                <h4>Deterministic Mode Execution (Default, Sub-2ms)</h4>
                <p>
                  In default mode, the engine bypasses probabilistic neural networks entirely. The extracted parameters are bound to pre-compiled, audit-verified SQL and Cypher query templates. Results are returned in sub-2ms with zero hallucination guarantee.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">11.3</div>
              <div class="wf-content">
                <h4>Optional Local Ollama SLM Mode & AST Firewall</h4>
                <p>
                  When complex multi-intent questions require language generation, queries are routed to an on-device local Ollama model (e.g. Mistral 7B). The system strictly enforces read-only database connections and inspects all generated code through an Abstract Syntax Tree (AST) query firewall, preventing prompt and SQL injections.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive NL Query Sandbox -->
        <div class="interactive-tool-card">
          <div class="tool-header">
            <div class="tool-title-cluster">
              <span class="pastel-chip chip-lavender">Interactive NL-to-Graph Sandbox</span>
              <h3>Grounded Parameterized Query Execution Tester</h3>
            </div>
          </div>

          <div class="preset-queries-row">
            <button
              v-for="(preset, idx) in queryPresets"
              :key="idx"
              type="button"
              class="preset-btn"
              :class="{ active: activePresetIndex === idx }"
              @click="selectQueryPreset(idx)"
            >
              <span>Preset 0{{ idx + 1 }}</span>
            </button>
          </div>

          <div class="query-demo-box">
            <div class="demo-prompt-strip">
              <span class="prompt-icon">💬</span>
              <span class="prompt-text font-bold">"{{ queryPresets[activePresetIndex].prompt }}"</span>
              <span class="mode-badge mono">{{ queryPresets[activePresetIndex].mode }}</span>
            </div>

            <div class="query-flow-grid">
              <div class="flow-step-box">
                <span class="flow-hed">1. Extracted Intent & Entity</span>
                <div class="mono flow-code">
                  Intent: {{ queryPresets[activePresetIndex].intent }}<br />
                  Filter: {{ queryPresets[activePresetIndex].parameter }}
                </div>
              </div>

              <div class="flow-step-box">
                <span class="flow-hed">2. Parameterized Cypher / SQL Query</span>
                <div class="mono flow-code query-highlight">
                  {{ queryPresets[activePresetIndex].generatedQuery }}
                </div>
              </div>
            </div>

            <div class="grounded-result-card">
              <span class="result-label">Grounded Verified Answer (Zero Hallucination):</span>
              <p class="result-text">{{ queryPresets[activePresetIndex].groundedOutput }}</p>
            </div>

            <MathFormula
              latex="\mathcal{Q}(\text{Prompt}) \xrightarrow{\text{Regex / AST}} (\text{Intent}, \Theta) \xrightarrow{\text{Param Query}} \text{DuckDB} \times \text{NetworkX} \to \text{Grounded Answer}"
              formula-html="<span class='math-cal'>Q</span>(Prompt) <span class='math-arrow'>&xrarr;</span><sup>Regex / AST</sup> (Intent, &Theta;) <span class='math-arrow'>&xrarr;</span><sup>Param Query</sup> DuckDB &times; NetworkX <span class='math-arrow'>&xrarr;</span> Grounded Answer"
              name="Deterministic Grounded Intent Mapping Invariant"
            />
          </div>
        </div>
      </section>

      <!-- Step 12 Section -->
      <section class="spec-detail-block" id="step-12">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 12</span>
          <span class="pastel-chip chip-mint">Enterprise Synthesis & Validation</span>
          <span class="module-ref mono">src/tvi/reporting.py & validation.py</span>
        </div>
        <h2 class="block-heading">Unified Technology Value Chain & 4-Tier Automated Integrity Suite</h2>
        <p class="block-intro">
          The ultimate objective of Technology Value Intelligence is bridging operational IT with executive board governance. Step 12 synthesizes the entire enterprise dossier and validates all 4 analytical layers against automated regression benchmarks.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">12.1</div>
              <div class="wf-content">
                <h4>Unified Technology Value Chain Dossier Generation</h4>
                <p>
                  Assembles the complete enterprise multi-hop chain linking: General Ledger Transactions &rarr; IT Towers &rarr; Applications &rarr; Capabilities &rarr; Transformation Projects &rarr; Realized Business KPIs.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">12.2</div>
              <div class="wf-content">
                <h4>4-Tier Automated Integrity Validation Suite</h4>
                <p>
                  Executes the 4-tier verification protocol:
                  <strong>Tier 1:</strong> Data Quality & Null Checks,
                  <strong>Tier 2:</strong> General Ledger Mass Balance,
                  <strong>Tier 3:</strong> Graph Connectivity & Cycle Detection,
                  <strong>Tier 4:</strong> Analytical Guardrail Compliance.
                </p>
                <MathFormula
                  latex="\mathcal{V} = \mathcal{V}_{\text{Data}} \wedge \mathcal{V}_{\text{Database}} \wedge \mathcal{V}_{\text{Graph}} \wedge \mathcal{V}_{\text{Analytics}} \equiv \text{PASS}"
                  formula-html="<span class='math-cal'>V</span> = <span class='math-cal'>V</span><sub>Data</sub> &and; <span class='math-cal'>V</span><sub>Database</sub> &and; <span class='math-cal'>V</span><sub>Graph</sub> &and; <span class='math-cal'>V</span><sub>Analytics</sub> &equiv; <span class='math-pass'>PASS</span>"
                  name="4-Tier Integrity Validation Invariant"
                />
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">12.3</div>
              <div class="wf-content">
                <h4>Automated Board-Level Briefing Report Compilation</h4>
                <p>
                  Compiles a comprehensive 9-section Markdown briefing report containing executive summaries, portfolio TIME matrices, Single Point of Failure emergency alerts, and stage-gate investment recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 4-Tier Validation Audit Dashboard -->
        <div class="audit-dashboard-card">
          <div class="dash-top">
            <span class="dash-title">4-Tier Automated Integrity Suite (Repository Health)</span>
            <span class="dash-badge">ALL 4 TIERS PASSING · 83 PYTEST SUITES VERIFIED</span>
          </div>

          <div class="tiers-grid">
            <div class="tier-card">
              <div class="tier-card-top">
                <span class="tier-pill">Tier 1</span>
                <span class="check-icon">✓ PASS</span>
              </div>
              <h4>Data Quality Validation</h4>
              <p>11 CSV entities verified for non-null primary keys, referential integrity, and range bounds.</p>
            </div>

            <div class="tier-card">
              <div class="tier-card-top">
                <span class="tier-pill">Tier 2</span>
                <span class="check-icon">✓ PASS</span>
              </div>
              <h4>Database Mass Balance</h4>
              <p>DuckDB general ledger summation confirms 0.00% variance across all ATUM taxonomy layers.</p>
            </div>

            <div class="tier-card">
              <div class="tier-card-top">
                <span class="tier-pill">Tier 3</span>
                <span class="check-icon">✓ PASS</span>
              </div>
              <h4>Graph Connectivity & DAG</h4>
              <p>NetworkX graph verified with 102 nodes, 196 typed edges, and zero circular dependency loops.</p>
            </div>

            <div class="tier-card">
              <div class="tier-card-top">
                <span class="tier-pill">Tier 4</span>
                <span class="check-icon">✓ PASS</span>
              </div>
              <h4>Analytical Guardrails</h4>
              <p>Exit penalty deductions enforced, DiD causal language verified, zero-hallucination queries confirmed.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Bottom Navigation Cluster -->
      <div class="subpage-footer-nav">
        <NuxtLink to="/technical-specs/value-variance" class="nav-prev-btn">
          ← Previous: Value & Variance Analysis (Steps 09 & 10)
        </NuxtLink>
        <NuxtLink to="/technical-specs" class="nav-next-btn">
          Return to Technical Specs Hub ⮌
        </NuxtLink>
      </div>
    </div>

    <FooterSection />
  </div>
</template>

<style scoped>
.subpage-wrapper {
  padding-top: 7.5rem;
  background-color: var(--bg-canvas);
  min-height: 100vh;
}

.subpage-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 var(--container-padding) 5rem;
}

.subpage-nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-pill-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 1.1rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 0.84rem;
  font-weight: 600;
  color: #33363f;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.back-pill-link:hover {
  background: #ffffff;
  color: #121316;
  transform: translateX(-2px);
}

.step-indexer {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.indexer-text {
  font-size: 0.84rem;
  font-weight: 600;
  color: #6c7180;
}

.subpage-hero {
  max-width: 1050px;
  margin-bottom: 3.5rem;
}

.subpage-main-title {
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 4vw, 3.4rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: #121316;
  margin: 0.6rem 0 1rem;
}

.subpage-lead {
  font-size: 1.15rem;
  line-height: 1.65;
  color: #4b4f5d;
}

.spec-detail-block {
  background: #ffffff;
  border-radius: var(--radius-container);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 12px 40px -10px rgba(0, 0, 0, 0.05);
  padding: 2.5rem;
  margin-bottom: 3.5rem;
}

.block-badge-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 1.2rem;
}

.step-num-badge {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 800;
  background: #17181d;
  color: #ffffff;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-pill);
}

.module-ref {
  font-size: 0.78rem;
  background: #f1f3f7;
  color: #474b59;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-pill);
}

.block-heading {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 0.8rem;
}

.block-intro {
  font-size: 1.05rem;
  line-height: 1.65;
  color: #4c505f;
  margin-bottom: 2rem;
}

.workflow-steps-box {
  background: #fafafc;
  border: 1px solid #ebedf3;
  border-radius: 20px;
  padding: 1.85rem;
  margin-bottom: 2.25rem;
}

.wf-title {
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #121316;
  margin-bottom: 1.25rem;
}

.wf-timeline {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.wf-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.wf-num {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 800;
  background: #17181d;
  color: #ffffff;
  padding: 0.3rem 0.65rem;
  border-radius: 8px;
  flex-shrink: 0;
}

.wf-content h4 {
  font-size: 0.98rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.35rem;
}

.wf-content p {
  font-size: 0.92rem;
  line-height: 1.55;
  color: #555968;
}

.interactive-tool-card {
  background: #f7f8fb;
  border: 1px solid #e3e6ee;
  border-radius: 22px;
  padding: 1.85rem;
}

.tool-header {
  margin-bottom: 1.25rem;
}

.tool-title-cluster h3 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #121316;
  margin-top: 0.3rem;
}

.preset-queries-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.preset-btn {
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-pill);
  border: 1px solid #d4d7e0;
  background: #ffffff;
  font-size: 0.82rem;
  font-weight: 600;
  color: #4b4f5d;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.preset-btn.active {
  background: #121316;
  color: #ffffff;
  border-color: #121316;
}

.query-demo-box {
  background: #ffffff;
  border: 1px solid #e2e5eb;
  border-radius: 16px;
  padding: 1.5rem;
}

.demo-prompt-strip {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #f8f9fb;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  margin-bottom: 1.25rem;
  font-size: 0.92rem;
  color: #121316;
}

.mode-badge {
  font-size: 0.72rem;
  background: var(--pastel-lavender-soft);
  color: #5b21b6;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-pill);
  margin-left: auto;
}

.query-flow-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.flow-step-box {
  background: #fafafc;
  border: 1px solid #eaedf3;
  border-radius: 12px;
  padding: 1rem;
}

.flow-hed {
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #7b8090;
  display: block;
  margin-bottom: 0.4rem;
}

.flow-code {
  font-size: 0.78rem;
  color: #3b3f4d;
  line-height: 1.5;
}

.query-highlight {
  color: #0369a1;
  background: #f0f9ff;
  padding: 0.5rem;
  border-radius: 6px;
}

.grounded-result-card {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
}

.result-label {
  font-size: 0.76rem;
  font-weight: 700;
  color: #166534;
  display: block;
  margin-bottom: 0.35rem;
  text-transform: uppercase;
}

.result-text {
  font-size: 0.92rem;
  line-height: 1.55;
  color: #14532d;
}

/* 4-Tier Dashboard */
.audit-dashboard-card {
  background: #f7f8fb;
  border: 1px solid #e3e6ee;
  border-radius: 22px;
  padding: 1.85rem;
}

.dash-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.dash-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #121316;
}

.dash-badge {
  font-size: 0.76rem;
  font-weight: 700;
  background: var(--pastel-mint-soft);
  color: #047857;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-pill);
}

.tiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.tier-card {
  background: #ffffff;
  border: 1px solid #e2e5eb;
  border-radius: 14px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
}

.tier-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.tier-pill {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  font-weight: 700;
  background: #17181d;
  color: #ffffff;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-pill);
}

.check-icon {
  font-size: 0.74rem;
  font-weight: 800;
  color: #059669;
}

.tier-card h4 {
  font-size: 0.94rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.35rem;
}

.tier-card p {
  font-size: 0.8rem;
  line-height: 1.5;
  color: #636877;
}

.subpage-footer-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e4e7ee;
}

.nav-prev-btn, .nav-next-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.65rem 1.4rem;
  border-radius: var(--radius-pill);
  font-size: 0.88rem;
  font-weight: 700;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.nav-prev-btn {
  background: #ffffff;
  color: #3b3f4d;
  border: 1px solid #d8dbe2;
}

.nav-prev-btn:hover {
  background: #f1f3f7;
  color: #121316;
}

.nav-next-btn {
  background: #121316;
  color: #ffffff;
}

.nav-next-btn:hover {
  background: #2b2e38;
  transform: translateX(3px);
}

.mono {
  font-family: var(--font-mono);
}

@media (max-width: 900px) {
  .query-flow-grid {
    grid-template-columns: 1fr;
  }
}
</style>
