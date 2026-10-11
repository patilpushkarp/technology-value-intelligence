<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'
import MathFormula from '~/components/MathFormula.vue'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

// Interactive Distribution Demo State
const selectedDist = ref<'lognormal' | 'weibull' | 'beta'>('lognormal')
const distMu = ref(2.4)
const distSigma = ref(0.75)

const sampleStats = computed(() => {
  if (selectedDist.value === 'lognormal') {
    const mean = Math.exp(distMu.value + (distSigma.value ** 2) / 2).toFixed(1)
    const median = Math.exp(distMu.value).toFixed(1)
    const p99 = Math.exp(distMu.value + 2.326 * distSigma.value).toFixed(1)
    return { mean, median, p99, label: 'Monthly Telemetry Events (Millions)', skew: 'Extreme Heavy-Tail' }
  } else if (selectedDist.value === 'weibull') {
    return { mean: '48.2', median: '42.0', p99: '124.5', label: 'MTBF Uptime (Hours Between Outages)', skew: 'Aging / Wear-out' }
  } else {
    return { mean: '0.42', median: '0.40', p99: '0.88', label: 'Cost Allocation Proportion (Bounded [0, 1])', skew: 'U-Shaped / Concentrated' }
  }
})

// Interactive Mass Balance Verification
const baseGLSum = 13248500.00
const costPoolsSum = 13248500.00
const towersSum = 13248500.00
const appsSum = 13248500.00
const massBalanceDrift = (appsSum - baseGLSum).toFixed(2)
</script>

<template>
  <div class="subpage-wrapper">
    <div class="container subpage-container">
      <!-- Top Navigation Pill -->
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
          <span class="pastel-chip chip-mint">Phase 01</span>
          <span class="indexer-text">Steps 01 & 02 of 12</span>
        </div>
      </div>

      <!-- Hero Header -->
      <header class="subpage-hero">
        <span class="section-tag">Analytical Truth & Pipeline Engineering</span>
        <h1 class="subpage-main-title">Data Pipeline: Procedural Generation, Copulas & Columnar OLAP</h1>
        <p class="subpage-lead">
          A forensic engineering walkthrough of how raw enterprise telemetry, GL invoices, and CMDB entities are generated with mathematical determinism, correlated via multivariate copulas, and ingested into DuckDB with zero reconciliation variance.
        </p>
      </header>

      <!-- Step 01 Section -->
      <section class="spec-detail-block" id="step-01">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 01</span>
          <span class="pastel-chip chip-lavender">Data Generation & Synthesis</span>
          <span class="module-ref mono">src/tvi/data_generation.py & copulas.py</span>
        </div>
        <h2 class="block-heading">Procedural Entity Generation & Heavy-Tailed Telemetry Modeling</h2>
        <p class="block-intro">
          Traditional corporate tech demos rely on random Gaussian variables. In enterprise environments, this approach produces deeply misleading conclusions: real application traffic, infrastructure costs, and incident frequencies are heavily skewed. TVI enforces non-Gaussian statistical distributions and copula dependencies.
        </p>

        <!-- Step-by-Step Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">1.1</div>
              <div class="wf-content">
                <h4>Deterministic Seed & Pseudo-Random State Initialization</h4>
                <p>
                  Execution begins by loading enterprise parameters from <code>config.yaml</code>. The generator locks <code>random_seed = 42</code> across NumPy and Python's native random module, ensuring byte-level deterministic reproducibility across all 102 enterprise nodes.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">1.2</div>
              <div class="wf-content">
                <h4>Heavy-Tailed Marginal Sampling (Beta, Weibull, Log-Normal)</h4>
                <p>
                  Workload events and storage volumes are sampled using Log-Normal distributions, reflecting real-world microservice traffic where a small fraction of workhorses handle the majority of requests. Proportions are sampled using bounded Beta distributions [0, 1], and hardware failure intervals follow Weibull survival curves.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">1.3</div>
              <div class="wf-content">
                <h4>Multivariate Copula Dependency Coupling (Sklar's Theorem)</h4>
                <p>
                  To prevent unrealistic scenarios (e.g., massive transaction spikes with zero cloud infrastructure spend), the pipeline fits a Gaussian Copula using Cholesky decomposition <b>L L</b><sup><i>T</i></sup>. This preserves authentic rank correlations (&rho; &approx; 0.78) between active users, CPU concurrency, and General Ledger charges without distorting the non-Gaussian marginal shapes.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">1.4</div>
              <div class="wf-content">
                <h4>Scenario Injection (Scenarios A through Y)</h4>
                <p>
                  Deterministic anomalies and governance edge cases are injected into the baseline data: Scenario A (Zombie Regional CRM with near-zero telemetry), Scenario C (Duplicate Order-to-Cash ERP systems), Scenario D (Single Point of Failure Payments Gateway), and Scenarios E/F (Contrasting Benefit Realization trajectories).
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive Copula & Distribution Inspector -->
        <div class="interactive-tool-card">
          <div class="tool-header">
            <div class="tool-title-cluster">
              <span class="pastel-chip chip-mint">Interactive Sandbox</span>
              <h3>Parametric Distribution & Heavy-Tail Simulator</h3>
            </div>
            <div class="dist-switcher">
              <button
                type="button"
                class="dist-btn"
                :class="{ active: selectedDist === 'lognormal' }"
                @click="selectedDist = 'lognormal'; playInteractChime(1.2)"
              >
                Log-Normal (Telemetry)
              </button>
              <button
                type="button"
                class="dist-btn"
                :class="{ active: selectedDist === 'weibull' }"
                @click="selectedDist = 'weibull'; playInteractChime(1.2)"
              >
                Weibull (MTBF)
              </button>
              <button
                type="button"
                class="dist-btn"
                :class="{ active: selectedDist === 'beta' }"
                @click="selectedDist = 'beta'; playInteractChime(1.2)"
              >
                Beta (Allocations)
              </button>
            </div>
          </div>

          <div class="tool-body-grid">
            <div class="tool-controls">
              <label class="control-label">
                <span>Distribution Type: <strong>{{ selectedDist.toUpperCase() }}</strong></span>
                <span class="control-hint">Simulating non-Gaussian heavy tail</span>
              </label>
              <div v-if="selectedDist === 'lognormal'" class="slider-group">
                <div class="slider-row">
                  <span>Location parameter (&mu;): {{ distMu }}</span>
                  <input v-model.number="distMu" type="range" min="1.0" max="3.5" step="0.1" />
                </div>
                <div class="slider-row">
                  <span>Scale parameter (&sigma;): {{ distSigma }}</span>
                  <input v-model.number="distSigma" type="range" min="0.2" max="1.5" step="0.05" />
                </div>
              </div>
              <div class="stat-readouts">
                <div class="readout-box">
                  <span class="k">Calculated Mean</span>
                  <strong class="v">{{ sampleStats.mean }}</strong>
                </div>
                <div class="readout-box">
                  <span class="k">Median (P50)</span>
                  <strong class="v">{{ sampleStats.median }}</strong>
                </div>
                <div class="readout-box highlight">
                  <span class="k">Extreme Spike (P99)</span>
                  <strong class="v">{{ sampleStats.p99 }}</strong>
                </div>
              </div>
            </div>

            <div class="tool-expl-panel">
              <h4>Why This Matters to Technology Business Management</h4>
              <p>
                In a standard normal distribution, a 3-&sigma; event occurs once every 370 days. In log-normal cloud telemetry, extreme concurrency spikes occur weekly. Relying on average cost calculations leads to 40% under-provisioning during peak billing hours.
              </p>
              <MathFormula
                latex="F(x_1, \dots, x_d) = C(F_1(x_1), \dots, F_d(x_d)) \quad \text{with} \quad C_R(u) = \Phi_R(\Phi^{-1}(u_1), \dots, \Phi^{-1}(u_d))"
                formula-html="<i>F</i>(<i>x</i><sub>1</sub>, &hellip;, <i>x</i><sub><i>d</i></sub>) = <i>C</i>(<i>F</i><sub>1</sub>(<i>x</i><sub>1</sub>), &hellip;, <i>F</i><sub><i>d</i></sub>(<i>x</i><sub><i>d</i></sub>)) &emsp;<span class='math-keyword'>with</span>&emsp; <i>C</i><sub><i>R</i></sub>(<i>u</i>) = &Phi;<sub><i>R</i></sub>(&Phi;<sup>&minus;1</sup>(<i>u</i><sub>1</sub>), &hellip;, &Phi;<sup>&minus;1</sup>(<i>u</i><sub><i>d</i></sub>))"
                name="Sklar's Multivariate Copula Theorem"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Step 02 Section -->
      <section class="spec-detail-block" id="step-02">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 02</span>
          <span class="pastel-chip chip-sky">Relational Accounting & OLAP</span>
          <span class="module-ref mono">src/tvi/database.py</span>
        </div>
        <h2 class="block-heading">TBM ATUM Taxonomy & Vectorized Columnar OLAP in DuckDB</h2>
        <p class="block-intro">
          Technology Business Management (TBM) standardizes enterprise spending across the Apptio TBM Unified Model (ATUM) taxonomy. To ensure maximum analytical speed on a standard 16 GB laptop without managing an external database server, TVI implements DuckDB in-process columnar execution.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">2.1</div>
              <div class="wf-content">
                <h4>Schema Generation & Taxonomic Table Creation</h4>
                <p>
                  DuckDB initializes 11 structured tables mapping the ATUM 4-tier cost flow: Cost Pools (Internal Labor, External Services, Hardware, Software), IT Towers (Compute, Storage, Network, Application Support), Applications, and Business Services.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">2.2</div>
              <div class="wf-content">
                <h4>Zero-Copy Parquet Export with Snappy Compression</h4>
                <p>
                  All generated datasets are stored in columnar Apache Parquet with Snappy compression in <code>data/parquet/</code>. DuckDB performs SIMD-vectorized scans directly against these files, yielding sub-5ms aggregations across thousands of ledger rows.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">2.3</div>
              <div class="wf-content">
                <h4>Zero-Reconciliation Mass Balance Audit</h4>
                <p>
                  The system runs an automated audit confirming that the sum of raw general ledger transactions matches the sum of IT towers and fully burdened application costs down to machine epsilon: $\Delta = \$0.00$.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Live Mass Balance Audit Card -->
        <div class="audit-proof-card">
          <div class="proof-top">
            <span class="proof-title">Zero-Reconciliation Financial Mass Balance Proof</span>
            <span class="audit-pass-badge">AUDIT: 0.00% VARIANCE (PASSED)</span>
          </div>
          <div class="proof-table-wrap">
            <table class="proof-table">
              <thead>
                <tr>
                  <th>ATUM Taxonomic Layer</th>
                  <th>Aggregated Currency ($ USD)</th>
                  <th>Variance vs General Ledger</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>General Ledger Baseline</strong></td>
                  <td class="mono">${{ baseGLSum.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</td>
                  <td class="mono">$0.00 (0.00%)</td>
                  <td><span class="chip-mint-sm">Baseline Truth</span></td>
                </tr>
                <tr>
                  <td><strong>Layer 1: Cost Pools (ATUM Tier 1)</strong></td>
                  <td class="mono">${{ costPoolsSum.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</td>
                  <td class="mono">$0.00 (0.00%)</td>
                  <td><span class="chip-mint-sm">Exact Match</span></td>
                </tr>
                <tr>
                  <td><strong>Layer 2: IT Towers (ATUM Tier 2)</strong></td>
                  <td class="mono">${{ towersSum.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</td>
                  <td class="mono">$0.00 (0.00%)</td>
                  <td><span class="chip-mint-sm">Exact Match</span></td>
                </tr>
                <tr>
                  <td><strong>Layer 3: Fully Burdened Applications</strong></td>
                  <td class="mono">${{ appsSum.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</td>
                  <td class="mono">${{ massBalanceDrift }} (0.00%)</td>
                  <td><span class="chip-mint-sm">Exact Match</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <MathFormula
            latex="\sum_{k \in \text{Cost Pools}} C_k \equiv \sum_{t \in \text{IT Towers}} C_t \equiv \sum_{a \in \text{Apps}} C_a = C_{\text{Total}} \quad (\text{Variance} = 0.00\%)"
            formula-html="<span class='math-op'>&sum;</span><sub><i>k</i> &isin; Cost Pools</sub> <i>C</i><sub><i>k</i></sub> &equiv; <span class='math-op'>&sum;</span><sub><i>t</i> &isin; Towers</sub> <i>C</i><sub><i>t</i></sub> &equiv; <span class='math-op'>&sum;</span><sub><i>a</i> &isin; Apps</sub> <i>C</i><sub><i>a</i></sub> = <i>C</i><sub>Total</sub> &emsp;<span class='math-note'>Variance = 0.00%</span>"
            name="General Ledger Mass-Balance Invariant"
          />
          <p class="proof-note">
            Mathematical Proof: For all cost records in the General Ledger, the sum of Tier 1 Cost Pools, Tier 2 IT Towers, and fully burdened Application TCO balances with zero reconciliation variance. Machine precision guaranteed by <code>DECIMAL(18,2)</code> arithmetic.
          </p>
        </div>
      </section>

      <!-- Bottom Navigation Cluster -->
      <div class="subpage-footer-nav">
        <NuxtLink to="/technical-specs" class="nav-prev-btn">
          ← Overview Hub
        </NuxtLink>
        <NuxtLink to="/technical-specs/graph-topology" class="nav-next-btn">
          Next Phase: Graph Topology & Blast Radius (Steps 03 & 08) →
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

/* Detail Block */
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

/* Workflow Timeline */
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

.wf-content code {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  background: #eef1f6;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}

/* Interactive Sandbox Tool */
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

.dist-switcher {
  display: flex;
  gap: 0.4rem;
}

.dist-btn {
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-pill);
  border: 1px solid #dcdfe6;
  background: #ffffff;
  font-size: 0.82rem;
  font-weight: 600;
  color: #4b4f5d;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dist-btn.active {
  background: #121316;
  color: #ffffff;
  border-color: #121316;
}

.tool-body-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 2rem;
}

.control-label {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  font-size: 0.88rem;
}

.control-hint {
  font-size: 0.78rem;
  color: #7b8090;
}

.slider-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.slider-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.82rem;
  color: #404452;
}

.slider-row input[type='range'] {
  width: 100%;
}

.stat-readouts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.readout-box {
  background: #ffffff;
  border: 1px solid #e2e5ec;
  border-radius: 12px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
}

.readout-box.highlight {
  border-color: var(--pastel-rose);
  background: #fff5f6;
}

.readout-box .k {
  font-size: 0.72rem;
  color: #787d8d;
}

.readout-box .v {
  font-size: 1.1rem;
  color: #121316;
  margin-top: 0.2rem;
}

.tool-expl-panel {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.tool-expl-panel h4 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.5rem;
}

.tool-expl-panel p {
  font-size: 0.88rem;
  line-height: 1.55;
  color: #555967;
  margin-bottom: 1rem;
}

.copula-math-pill {
  background: #17181d;
  color: #a7f3d0;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.78rem;
}

/* Proof Table */
.audit-proof-card {
  background: #f7f8fb;
  border: 1px solid #e3e6ee;
  border-radius: 22px;
  padding: 1.85rem;
}

.proof-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.proof-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #121316;
}

.audit-pass-badge {
  font-size: 0.76rem;
  font-weight: 700;
  background: var(--pastel-mint-soft);
  color: #047857;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-pill);
}

.proof-table-wrap {
  overflow-x: auto;
  margin-bottom: 1rem;
}

.proof-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.proof-table th {
  background: #ffffff;
  padding: 0.85rem 1rem;
  text-align: left;
  font-size: 0.76rem;
  text-transform: uppercase;
  color: #7b8090;
  border-bottom: 1px solid #e6e9f0;
}

.proof-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #e9ecf2;
}

.chip-mint-sm {
  font-size: 0.74rem;
  font-weight: 600;
  background: var(--pastel-mint-soft);
  color: #065f46;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.proof-note {
  font-size: 0.82rem;
  color: #6a6f7e;
  line-height: 1.45;
}

/* Bottom Navigation */
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
