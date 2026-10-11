<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'
import MathFormula from '~/components/MathFormula.vue'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

// Interactive TOPSIS & TIME Quadrant Explorer
interface RationalizationApp {
  id: string
  name: string
  tco: number
  annualAvoidable: number
  utilizationPercent: number
  techDebtScore: number
  timeQuadrant: 'Tolerate' | 'Invest' | 'Migrate' | 'Eliminate'
  exitPenalty: number
  topsisRank: number
}

const portfolioList: RationalizationApp[] = [
  {
    id: 'APP-007',
    name: 'Legacy Regional CRM Zombie',
    tco: 425000,
    annualAvoidable: 385000,
    utilizationPercent: 4.2,
    techDebtScore: 92,
    timeQuadrant: 'Eliminate',
    exitPenalty: 28000,
    topsisRank: 1
  },
  {
    id: 'APP-021',
    name: 'Document Archive Silo Matrix',
    tco: 310000,
    annualAvoidable: 220000,
    utilizationPercent: 18.5,
    techDebtScore: 78,
    timeQuadrant: 'Migrate',
    exitPenalty: 45000,
    topsisRank: 2
  },
  {
    id: 'APP-034',
    name: 'Supply Chain Procurement ERP',
    tco: 840000,
    annualAvoidable: 110000,
    utilizationPercent: 62.0,
    techDebtScore: 64,
    timeQuadrant: 'Tolerate',
    exitPenalty: 120000,
    topsisRank: 4
  },
  {
    id: 'APP-001',
    name: 'Customer Core Banking Ledger',
    tco: 1480000,
    annualAvoidable: 0,
    utilizationPercent: 91.5,
    techDebtScore: 18,
    timeQuadrant: 'Invest',
    exitPenalty: 0,
    topsisRank: 8
  },
  {
    id: 'APP-012',
    name: 'Omnichannel API Mesh Gateway',
    tco: 910000,
    annualAvoidable: 240000,
    utilizationPercent: 88.0,
    techDebtScore: 22,
    timeQuadrant: 'Invest',
    exitPenalty: 15000,
    topsisRank: 5
  }
]

const selectedQuadrant = ref<'All' | 'Eliminate' | 'Migrate' | 'Tolerate' | 'Invest'>('All')

const filteredApps = computed(() => {
  if (selectedQuadrant.value === 'All') return portfolioList
  return portfolioList.filter(a => a.timeQuadrant === selectedQuadrant.value)
})

const filterByQuadrant = (quad: any) => {
  selectedQuadrant.value = quad
  playInteractChime(1.2)
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
          <span class="pastel-chip chip-sky">Phase 04</span>
          <span class="indexer-text">Steps 06 & 07 of 12</span>
        </div>
      </div>

      <!-- Hero Header -->
      <header class="subpage-hero">
        <span class="section-tag">Consumption Intelligence & Decision Optimization</span>
        <h1 class="subpage-main-title">Rationalization Engine: Telemetry Profiling, TIME & TOPSIS MCDA</h1>
        <p class="subpage-lead">
          Subjective IT committee voting on application retirement leads to political gridlock. TVI combines empirical telemetry median-split quadrant profiling with mathematical Multi-Criteria Decision Analysis (TOPSIS) and realistic contract exit penalty modeling.
        </p>
      </header>

      <!-- Step 06 Section -->
      <section class="spec-detail-block" id="step-06">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 06</span>
          <span class="pastel-chip chip-mint">Consumption Intelligence</span>
          <span class="module-ref mono">src/tvi/consumption_analytics.py</span>
        </div>
        <h2 class="block-heading">Telemetry Profiling, Quadrant Segmentation & GreenOps Rightsizing</h2>
        <p class="block-intro">
          Before deciding whether to invest in or eliminate software, the system evaluates real-world consumption telemetry. Applications that consume significant cloud infrastructure while registering zero user engagement are algorithmically quarantined.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">6.1</div>
              <div class="wf-content">
                <h4>Multivariate Telemetry Ingestion & Normalization</h4>
                <p>
                  Ingests hourly telemetry streams across CPU utilization, memory allocation, API request volume, and active authenticated sessions. Normalizes indicators using min-max bounds to form a composite utilization coefficient.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">6.2</div>
              <div class="wf-content">
                <h4>Median-Split 2x2 Quadrant Partitioning</h4>
                <p>
                  Partitions the portfolio across the median annual TCO ($P_{50}$) and median utilization ($P_{50}$) axes:
                  <strong>Workhorses</strong> (High Spend, High Use), <strong>Over-Provisioned</strong> (High Spend, Low Use), <strong>Efficient Supporting</strong> (Low Spend, High Use), and <strong>Zombie Systems</strong> (Low/Moderate Spend, Near-Zero Telemetry).
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">6.3</div>
              <div class="wf-content">
                <h4>Cloud Elasticity & GreenOps GHG Carbon Estimation</h4>
                <p>
                  Calculates elasticity coefficient &epsilon; comparing spend growth against workload activity. Derives Scope 2 GHG carbon emissions from total kWh consumption, data center Power Usage Effectiveness (PUE = 1.2), and regional grid carbon intensity (0.385 kg CO<sub>2</sub>e/kWh).
                </p>
                <MathFormula
                  latex="\epsilon = \frac{\% \Delta \text{Cost}}{\% \Delta \text{Workload}} = \frac{(C_1 - C_0) / C_0}{(W_1 - W_0) / W_0}"
                  formula-html="&epsilon; = <span class='math-frac'><span class='math-num'>% &Delta; Cost</span><span class='math-denom'>% &Delta; Workload</span></span> = <span class='math-frac'><span class='math-num'>(<i>C</i><sub>1</sub> &minus; <i>C</i><sub>0</sub>) / <i>C</i><sub>0</sub></span><span class='math-denom'>(<i>W</i><sub>1</sub> &minus; <i>W</i><sub>0</sub>) / <i>W</i><sub>0</sub></span></span>"
                  name="FinOps Elasticity Coefficient"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Step 07 Section -->
      <section class="spec-detail-block" id="step-07">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 07</span>
          <span class="pastel-chip chip-sky">Portfolio Rationalization</span>
          <span class="module-ref mono">src/tvi/rationalization.py</span>
        </div>
        <h2 class="block-heading">TOPSIS Multi-Criteria Decision Analysis & TIME Matrix Governance</h2>
        <p class="block-intro">
          Step 07 applies the Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) to rank rationalization candidates objectively, placing them into the Gartner TIME framework and calculating avoidable cost scenarios.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">7.1</div>
              <div class="wf-content">
                <h4>Decision Matrix Formulation & Criteria Weighting</h4>
                <p>
                  Constructs an <i>m</i> &times; <i>n</i> evaluation matrix across 5 weighted criteria: Annual TCO (weight 0.25), Technical Debt (0.20), Downstream Blast Radius (0.25), Capability Criticality (0.15), and Vendor Lock-in (0.15).
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">7.2</div>
              <div class="wf-content">
                <h4>TOPSIS Vector Normalization & Euclidean Closeness</h4>
                <p>
                  Normalizes vector scales and computes Euclidean distance to Positive Ideal Solution (<i>S</i><sub><i>i</i></sub><sup>*</sup>) and Negative Ideal Solution (<i>S</i><sub><i>i</i></sub><sup>&minus;</sup>). Computes the Relative Closeness index <i>R</i><sub><i>i</i></sub><sup>*</sup>.
                </p>
                <MathFormula
                  latex="R_i^* = \frac{S_i^-}{S_i^* + S_i^-} \quad \text{where} \quad S_i^* = \sqrt{\sum_{j=1}^n (v_{ij} - v_j^*)^2}"
                  formula-html="<i>R</i><sub><i>i</i></sub><sup>*</sup> = <span class='math-frac'><span class='math-num'><i>S</i><sub><i>i</i></sub><sup>&minus;</sup></span><span class='math-denom'><i>S</i><sub><i>i</i></sub><sup>*</sup> + <i>S</i><sub><i>i</i></sub><sup>&minus;</sup></span></span> &emsp;<span class='math-keyword'>where</span>&emsp; <i>S</i><sub><i>i</i></sub><sup>*</sup> = &radic;<span class='math-sqrt-body'><span class='math-op'>&sum;</span> (<i>v</i><sub><i>ij</i></sub> &minus; <i>v</i><sub><i>j</i></sub><sup>*</sup>)<sup>2</sup></span>"
                  name="TOPSIS Relative Closeness Score"
                />
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">7.3</div>
              <div class="wf-content">
                <h4>Avoidable Cost Modeling vs Fictional Gross Savings</h4>
                <p>
                  <strong>Analytical Guardrail 1 Enforced:</strong> TVI rejects claiming gross vendor contract amounts as immediate cash savings. The engine deducts contractual termination exit penalties and shared platform overhead amortization.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive TOPSIS & TIME Matrix Tool -->
        <div class="interactive-tool-card">
          <div class="tool-header">
            <div class="tool-title-cluster">
              <span class="pastel-chip chip-sky">Interactive Matrix Explorer</span>
              <h3>Gartner TIME Matrix & TOPSIS Rationalization Ranking</h3>
            </div>
            <div class="quadrant-filter-buttons">
              <button
                v-for="q in ['All', 'Eliminate', 'Migrate', 'Tolerate', 'Invest']"
                :key="q"
                type="button"
                class="q-btn"
                :class="{ active: selectedQuadrant === q }"
                @click="filterByQuadrant(q)"
              >
                {{ q }}
              </button>
            </div>
          </div>

          <!-- Filtered Table -->
          <div class="matrix-table-wrap">
            <table class="matrix-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Application Name</th>
                  <th>Annual TCO</th>
                  <th>Net Avoidable Cost</th>
                  <th>Exit Penalty</th>
                  <th>Utilization</th>
                  <th>TIME Quadrant</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in filteredApps" :key="app.id">
                  <td class="mono font-bold">#{{ app.topsisRank }}</td>
                  <td>
                    <strong>{{ app.name }}</strong>
                    <span class="app-sub-id mono">{{ app.id }}</span>
                  </td>
                  <td class="mono">${{ app.tco.toLocaleString() }}</td>
                  <td class="mono highlight-mint">${{ app.annualAvoidable.toLocaleString() }}</td>
                  <td class="mono highlight-rose">${{ app.exitPenalty.toLocaleString() }}</td>
                  <td class="mono">{{ app.utilizationPercent }}%</td>
                  <td>
                    <span
                      class="time-pill"
                      :class="{
                        'pill-elim': app.timeQuadrant === 'Eliminate',
                        'pill-migr': app.timeQuadrant === 'Migrate',
                        'pill-tol': app.timeQuadrant === 'Tolerate',
                        'pill-inv': app.timeQuadrant === 'Invest'
                      }"
                    >
                      {{ app.timeQuadrant }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="formula-footer-box">
            <span class="footer-title">Analytical Guardrail Note:</span>
            <p>
              Notice how for <strong>APP-007 (Legacy Regional CRM Zombie)</strong>, gross spend is $425,000, but net avoidable cost is accurately reported as $385,000 after accounting for $28,000 in contractual early exit fees and $12,000 in shared compliance archive overhead.
            </p>
          </div>
        </div>
      </section>

      <!-- Bottom Navigation Cluster -->
      <div class="subpage-footer-nav">
        <NuxtLink to="/technical-specs/cost-attribution" class="nav-prev-btn">
          ← Previous: 5-Layer Cost Stack & Capabilities (Steps 04 & 05)
        </NuxtLink>
        <NuxtLink to="/technical-specs/value-variance" class="nav-next-btn">
          Next: TVR Value & PVM Variance Analysis (Steps 09 & 10) →
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

.quadrant-filter-buttons {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.q-btn {
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-pill);
  border: 1px solid #dcdfe6;
  background: #ffffff;
  font-size: 0.82rem;
  font-weight: 600;
  color: #4b4f5d;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.q-btn.active {
  background: #121316;
  color: #ffffff;
  border-color: #121316;
}

.matrix-table-wrap {
  overflow-x: auto;
  margin-bottom: 1.25rem;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.matrix-table th {
  background: #ffffff;
  padding: 0.85rem 1rem;
  text-align: left;
  font-size: 0.76rem;
  text-transform: uppercase;
  color: #7b8090;
  border-bottom: 1px solid #e6e9f0;
}

.matrix-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #e9ecf2;
}

.app-sub-id {
  display: block;
  font-size: 0.72rem;
  color: #8c909e;
}

.highlight-mint {
  color: #047857;
  font-weight: 700;
}

.highlight-rose {
  color: #b91c1c;
  font-weight: 700;
}

.time-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-pill);
  display: inline-block;
}

.pill-elim { background: var(--pastel-rose-soft); color: #be123c; }
.pill-migr { background: var(--pastel-sky-soft); color: #0369a1; }
.pill-tol { background: var(--pastel-peach-soft); color: #c2410c; }
.pill-inv { background: var(--pastel-mint-soft); color: #047857; }

.formula-footer-box {
  background: #ffffff;
  border: 1px solid #e5e8f0;
  border-radius: 14px;
  padding: 1rem 1.25rem;
}

.footer-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #121316;
  display: block;
  margin-bottom: 0.3rem;
}

.formula-footer-box p {
  font-size: 0.84rem;
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
</style>
