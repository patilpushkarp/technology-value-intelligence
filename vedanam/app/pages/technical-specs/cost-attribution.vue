<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'
import MathFormula from '~/components/MathFormula.vue'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

// Interactive 5-Layer Cost Stack Calculator State
const infraCost = ref(380000)
const softwareCost = ref(480000)
const personnelCost = ref(420000)
const vendorCost = ref(120000)
const overheadCost = ref(200000)

const activeUsers = ref(8400)
const monthlyTransactions = ref(3500000)

const totalTco = computed(() => {
  return infraCost.value + softwareCost.value + personnelCost.value + vendorCost.value + overheadCost.value
})

const costPerUser = computed(() => {
  return (totalTco.value / Math.max(1, activeUsers.value)).toFixed(2)
})

const costPer1kEvents = computed(() => {
  const annualEvents = monthlyTransactions.value * 12
  return ((totalTco.value / Math.max(1, annualEvents)) * 1000).toFixed(4)
})

const layerShares = computed(() => {
  const total = Math.max(1, totalTco.value)
  return {
    infra: ((infraCost.value / total) * 100).toFixed(1),
    software: ((softwareCost.value / total) * 100).toFixed(1),
    personnel: ((personnelCost.value / total) * 100).toFixed(1),
    vendor: ((vendorCost.value / total) * 100).toFixed(1),
    overhead: ((overheadCost.value / total) * 100).toFixed(1)
  }
})
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
          <span class="pastel-chip chip-peach">Phase 03</span>
          <span class="indexer-text">Steps 04 & 05 of 12</span>
        </div>
      </div>

      <!-- Hero Header -->
      <header class="subpage-hero">
        <span class="section-tag">Cost Intelligence & Unit Economics</span>
        <h1 class="subpage-main-title">Cost Attribution: 5-Layer TCO Stack & Capability Lineage</h1>
        <p class="subpage-lead">
          Enterprise IT leaders frequently mistake direct vendor invoices for true application cost. TVI establishes a 5-layer Activity-Based Costing stack to uncover fully burdened TCO and projects costs onto business capabilities with mathematical double-counting prevention.
        </p>
      </header>

      <!-- Step 04 Section -->
      <section class="spec-detail-block" id="step-04">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 04</span>
          <span class="pastel-chip chip-peach">TCO Disaggregation</span>
          <span class="module-ref mono">src/tvi/cost_analytics.py</span>
        </div>
        <h2 class="block-heading">5-Layer Fully Burdened Cost Stack & FinOps Unit Economics</h2>
        <p class="block-intro">
          A cloud invoice of $10,000/month for an application reveals only a tiny fraction of its corporate burden. Full TCO requires absorbing software license maintenance, dedicated engineering personnel, vendor integration contracts, and shared IT facilities.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">4.1</div>
              <div class="wf-content">
                <h4>5-Layer Cost Disaggregation</h4>
                <p>
                  Every application's annual expenditure is partitioned into 5 discrete tiers:
                  Layer 1 (Direct Infrastructure), Layer 2 (Software Licenses), Layer 3 (Internal Personnel FTEs), Layer 4 (Vendor Contractors), and Layer 5 (Shared Enterprise Overhead & SOC).
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">4.2</div>
              <div class="wf-content">
                <h4>Unit Economic Rate Calculation</h4>
                <p>
                  Computes standardized FinOps unit rates: Fully Burdened Cost per Monthly Active User ($\$/\text{MAU}$) and Fully Burdened Cost per 1,000 Transaction Events ($\$/1\text{k Events}$). This normalizes multi-million dollar platforms against lean services.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">4.3</div>
              <div class="wf-content">
                <h4>Lorenz Spend Concentration & Gini Coefficient</h4>
                <p>
                  Ranks all enterprise applications by TCO and plots the Lorenz curve. Computes the portfolio Gini coefficient ($G \approx 0.62$), exposing that the top 20% of workhorse platforms account for over 68% of total IT operating cash outflow.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive 5-Layer Burdened Cost Calculator -->
        <div class="interactive-tool-card">
          <div class="tool-header">
            <div class="tool-title-cluster">
              <span class="pastel-chip chip-peach">Interactive Calculator</span>
              <h3>5-Layer Burdened TCO & Unit Economics Sandbox</h3>
            </div>
            <div class="total-badge mono">
              Total Annual TCO: ${{ totalTco.toLocaleString() }}
            </div>
          </div>

          <div class="tool-body-grid">
            <div class="sliders-col">
              <div class="cost-slider-item">
                <div class="slider-hed">
                  <span>Layer 1: Direct Infrastructure (Cloud/Hardware)</span>
                  <strong class="mono">${{ infraCost.toLocaleString() }} ({{ layerShares.infra }}%)</strong>
                </div>
                <input v-model.number="infraCost" type="range" min="50000" max="1500000" step="10000" />
              </div>

              <div class="cost-slider-item">
                <div class="slider-hed">
                  <span>Layer 2: Software Licenses & Subscriptions</span>
                  <strong class="mono">${{ softwareCost.toLocaleString() }} ({{ layerShares.software }}%)</strong>
                </div>
                <input v-model.number="softwareCost" type="range" min="20000" max="1200000" step="10000" />
              </div>

              <div class="cost-slider-item">
                <div class="slider-hed">
                  <span>Layer 3: Internal Personnel FTE Salaries</span>
                  <strong class="mono">${{ personnelCost.toLocaleString() }} ({{ layerShares.personnel }}%)</strong>
                </div>
                <input v-model.number="personnelCost" type="range" min="50000" max="1200000" step="10000" />
              </div>

              <div class="cost-slider-item">
                <div class="slider-hed">
                  <span>Layer 4: External Vendor & Contractor Services</span>
                  <strong class="mono">${{ vendorCost.toLocaleString() }} ({{ layerShares.vendor }}%)</strong>
                </div>
                <input v-model.number="vendorCost" type="range" min="0" max="600000" step="10000" />
              </div>

              <div class="cost-slider-item">
                <div class="slider-hed">
                  <span>Layer 5: Shared Enterprise Overhead (SOC/DR)</span>
                  <strong class="mono">${{ overheadCost.toLocaleString() }} ({{ layerShares.overhead }}%)</strong>
                </div>
                <input v-model.number="overheadCost" type="range" min="20000" max="500000" step="5000" />
              </div>
            </div>

            <div class="economics-col">
              <h4>Derived FinOps Unit Economics</h4>
              <div class="unit-readouts-grid">
                <div class="readout-card">
                  <span class="k">Active Enterprise Users</span>
                  <input v-model.number="activeUsers" type="number" min="10" max="50000" step="100" class="mini-input" />
                </div>
                <div class="readout-card highlight-mint">
                  <span class="k">Burdened Cost / User</span>
                  <strong class="v">${{ costPerUser }} / yr</strong>
                </div>
                <div class="readout-card">
                  <span class="k">Monthly Transactions</span>
                  <input v-model.number="monthlyTransactions" type="number" min="10000" max="100000000" step="100000" class="mini-input" />
                </div>
                <div class="readout-card highlight-lavender">
                  <span class="k">Burdened Cost / 1k Events</span>
                  <strong class="v">${{ costPer1kEvents }}</strong>
                </div>
              </div>

              <MathFormula
                latex="\text{TCO}_i = C_{\text{Infra},i} + C_{\text{Soft},i} + C_{\text{Pers},i} + C_{\text{Vend},i} + C_{\text{Overhead},i}"
                formula-html="TCO<sub><i>i</i></sub> = <i>C</i><sub>Infra,<i>i</i></sub> + <i>C</i><sub>Soft,<i>i</i></sub> + <i>C</i><sub>Pers,<i>i</i></sub> + <i>C</i><sub>Vend,<i>i</i></sub> + <i>C</i><sub>Overhead,<i>i</i></sub>"
                name="5-Layer Activity-Based TCO Stack"
              />
              <p class="formula-caption">
                Notice how doubling direct infrastructure often impacts total TCO by only 15% because human maintenance and enterprise overhead dominate true system economics.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Step 05 Section -->
      <section class="spec-detail-block" id="step-05">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 05</span>
          <span class="pastel-chip chip-rose">Capability Intelligence</span>
          <span class="module-ref mono">src/tvi/cost_analytics.py</span>
        </div>
        <h2 class="block-heading">Proportional Capability Attribution & Redundancy Quantification</h2>
        <p class="block-intro">
          CIOs and CFOs think in terms of business capabilities (e.g., "What does Order-to-Cash or Regulatory Compliance cost?"). Mapping applications to business capabilities often causes double-counting in corporate finance. Step 05 enforces mathematical weight conservation.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">5.1</div>
              <div class="wf-content">
                <h4>Bipartite Graph Projection (Applications to Capabilities)</h4>
                <p>
                  Extracts bipartite subgraph edges between Applications and Business Capabilities connected by <code>PROVIDES</code> relationships. An application providing <i>k</i> capabilities has edge weights initially defined as <i>w</i><sub><i>ij</i></sub> = 1 / <i>k</i>.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">5.2</div>
              <div class="wf-content">
                <h4>Weight Conservation & Double-Counting Prevention Proof</h4>
                <p>
                  Enforces strict mathematical normalization: For any application <i>A</i><sub><i>i</i></sub>, the sum of attribution weights across all fulfilled capabilities must equal exactly 1.00 (&sum; <i>w</i><sub><i>ij</i></sub> &equiv; 1.00). This guarantees that total attributed capability costs match total application TCO with zero variance.
                </p>
                <MathFormula
                  latex="C(k) = \sum_{a \in \text{Apps}(k)} w_{a,k} \cdot \text{TCO}(a) \quad \text{where} \quad \sum_{j} w_{a,j} \equiv 1.00"
                  formula-html="<i>C</i>(<i>k</i>) = <span class='math-op'>&sum;</span><sub><i>a</i> &isin; Apps(<i>k</i>)</sub> <i>w</i><sub><i>a</i>,<i>k</i></sub> &middot; TCO(<i>a</i>) &emsp;<span class='math-keyword'>where</span>&emsp; <span class='math-op'>&sum;</span><sub><i>j</i></sub> <i>w</i><sub><i>a</i>,<i>j</i></sub> &equiv; 1.00"
                  name="Capability Attribution Conservation Invariant"
                />
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">5.3</div>
              <div class="wf-content">
                <h4>Capability Redundancy Scoring & Sankey Value Flows</h4>
                <p>
                  Flags capabilities supported by 3 or more disparate legacy applications fulfilling overlapping functions (e.g., Scenario C duplicate Order Management systems). Generates multi-tier Sankey value flow graphs mapping spend from GL to business outcomes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Bottom Navigation Cluster -->
      <div class="subpage-footer-nav">
        <NuxtLink to="/technical-specs/graph-topology" class="nav-prev-btn">
          ← Previous: Graph Topology & Blast Radius (Steps 03 & 08)
        </NuxtLink>
        <NuxtLink to="/technical-specs/portfolio-rationalization" class="nav-next-btn">
          Next: Portfolio Rationalization & TIME (Steps 06 & 07) →
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.tool-title-cluster h3 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #121316;
  margin-top: 0.3rem;
}

.total-badge {
  font-size: 0.92rem;
  font-weight: 700;
  background: #17181d;
  color: #ffffff;
  padding: 0.45rem 1rem;
  border-radius: var(--radius-pill);
}

.tool-body-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 2rem;
}

.sliders-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cost-slider-item {
  background: #ffffff;
  border: 1px solid #e5e8f0;
  border-radius: 12px;
  padding: 0.85rem;
}

.slider-hed {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: #4b4f5d;
  margin-bottom: 0.4rem;
}

.cost-slider-item input[type='range'] {
  width: 100%;
}

.economics-col {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.economics-col h4 {
  font-size: 0.98rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.75rem;
}

.unit-readouts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.readout-card {
  background: #ffffff;
  border: 1px solid #e2e5eb;
  border-radius: 12px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
}

.readout-card.highlight-mint {
  background: #f0fdf4;
  border-color: #86efac;
}

.readout-card.highlight-lavender {
  background: #f5f3ff;
  border-color: #c4b5fd;
}

.readout-card .k {
  font-size: 0.74rem;
  color: #7b8090;
  margin-bottom: 0.25rem;
}

.readout-card .v {
  font-size: 1.15rem;
  color: #121316;
}

.mini-input {
  font-family: var(--font-mono);
  font-size: 0.95rem;
  font-weight: 700;
  padding: 0.25rem 0.45rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #121316;
}

.formula-box-sm {
  background: #17181d;
  color: #fed7aa;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.78rem;
  margin-bottom: 0.5rem;
}

.formula-caption {
  font-size: 0.82rem;
  line-height: 1.5;
  color: #555968;
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
  .tool-body-grid {
    grid-template-columns: 1fr;
  }
}
</style>
