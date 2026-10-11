<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'
import MathFormula from '~/components/MathFormula.vue'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

// Interactive Price-Volume-Mix (PVM) Simulator State
const baseUnitRate = ref(120.00) // $ per compute unit (P0)
const currUnitRate = ref(135.00) // P1 (Rate hike)
const baseVolume = ref(1000)     // V0 (Workload units)
const currVolume = ref(1250)     // V1 (Traffic growth)

const pvmBreakdown = computed(() => {
  const p0 = baseUnitRate.value
  const p1 = currUnitRate.value
  const v0 = baseVolume.value
  const v1 = currVolume.value

  const baseSpend = p0 * v0
  const currSpend = p1 * v1
  const totalVariance = currSpend - baseSpend

  // Exact algebraic decomposition
  const priceEffect = (p1 - p0) * v0
  const volumeEffect = p0 * (v1 - v0)
  const mixEffect = (p1 - p0) * (v1 - v0)

  return {
    baseSpend,
    currSpend,
    totalVariance,
    priceEffect,
    volumeEffect,
    mixEffect,
    pricePct: totalVariance !== 0 ? ((priceEffect / totalVariance) * 100).toFixed(1) : '0',
    volumePct: totalVariance !== 0 ? ((volumeEffect / totalVariance) * 100).toFixed(1) : '0',
    mixPct: totalVariance !== 0 ? ((mixEffect / totalVariance) * 100).toFixed(1) : '0'
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
          <span class="pastel-chip chip-rose">Phase 05</span>
          <span class="indexer-text">Steps 09 & 10 of 12</span>
        </div>
      </div>

      <!-- Hero Header -->
      <header class="subpage-hero">
        <span class="section-tag">Value Realization & Variance Intelligence</span>
        <h1 class="subpage-main-title">Value & Variance: TVR Realization, DiD Econometrics & PVM Math</h1>
        <p class="subpage-lead">
          Technology transformations frequently claim victory upon deployment ("on time and on budget") while failing to deliver business value. TVI implements longitudinal post-delivery benefit realization tracking with Difference-in-Differences econometrics, alongside pure algebraic Price-Volume-Mix variance decomposition.
        </p>
      </header>

      <!-- Step 09 Section -->
      <section class="spec-detail-block" id="step-09">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 09</span>
          <span class="pastel-chip chip-peach">TVR Benefit Realization</span>
          <span class="module-ref mono">src/tvi/value_realization.py</span>
        </div>
        <h2 class="block-heading">Technology Value Realization (TVR) & Difference-in-Differences Econometrics</h2>
        <p class="block-intro">
          Traditional accounting treats technology projects as CapEx line items that end upon release. The Technology Value Realization (TVR) philosophy audits whether targeted business KPI shifts actually occurred in subsequent operational quarters.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">9.1</div>
              <div class="wf-content">
                <h4>Longitudinal Benefit Tracking & VRR Calculation</h4>
                <p>
                  Connects transformation projects to operational KPIs via <code>DELIVERS</code> and <code>TRACKS</code> graph edges. Computes the Value Realization Ratio $\text{VRR} = \frac{\text{Actual Realized Benefit}}{\text{Target Business Case Benefit}}$ across quarters $Q_1$ through $Q_8$.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">9.2</div>
              <div class="wf-content">
                <h4>Difference-in-Differences (DiD) Causal Econometrics</h4>
                <p>
                  To isolate authentic IT efficiency from macroeconomic trends (e.g., industry-wide transaction surges), TVI executes Difference-in-Differences estimation comparing modernized departments against untreated control units.
                </p>
                <MathFormula
                  latex="\hat{\beta}_{\text{DiD}} = (\bar{Y}_{\text{Post}, T} - \bar{Y}_{\text{Pre}, T}) - (\bar{Y}_{\text{Post}, C} - \bar{Y}_{\text{Pre}, C})"
                  formula-html="<span class='math-hat'>&beta;&#770;</span><sub>DiD</sub> = (<i>Y&#772;</i><sub>Post, <i>T</i></sub> &minus; <i>Y&#772;</i><sub>Pre, <i>T</i></sub>) &minus; (<i>Y&#772;</i><sub>Post, <i>C</i></sub> &minus; <i>Y&#772;</i><sub>Pre, <i>C</i></sub>)"
                  name="Difference-in-Differences Causal Estimator"
                />
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">9.3</div>
              <div class="wf-content">
                <h4>Enforcement of Analytical Guardrail 2 (Association vs Causality)</h4>
                <p>
                  <strong>Analytical Guardrail 2 Enforced:</strong> All reports strictly state financial benefits as <em>associated with</em> KPI movements rather than claiming ungrounded single-factor causation, protecting IT leadership during financial audit examinations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Step 10 Section -->
      <section class="spec-detail-block" id="step-10">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 10</span>
          <span class="pastel-chip chip-rose">Variance Decomposition</span>
          <span class="module-ref mono">src/tvi/variance.py</span>
        </div>
        <h2 class="block-heading">Price-Volume-Mix (PVM) Variance Decomposition & Automated SLA Credits</h2>
        <p class="block-intro">
          When cloud bills rise by $180,000 MoM, finance teams often demand across-the-board cuts. Step 10 mathematically isolates whether the spike was caused by vendor rate hikes (Price), legitimate business traffic growth (Volume), or inefficient architectural tier shifting (Mix).
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">10.1</div>
              <div class="wf-content">
                <h4>Pure Algebraic PVM Variance Decomposition</h4>
                <p>
                  Applies the 3-factor algebraic identity: Price Effect + Volume Effect + Mix Effect matches total variance with 0.00% remainder.
                </p>
                <MathFormula
                  latex="\Delta C = \underbrace{\sum (P_1 - P_0) V_0}_{\text{Price Effect}} + \underbrace{\sum P_0 (V_1 - V_0)}_{\text{Volume Effect}} + \underbrace{\sum (P_1 - P_0)(V_1 - V_0)}_{\text{Mix Effect}}"
                  formula-html="&Delta;<i>C</i> = <span class='math-term'><span class='math-brace'>(<i>P</i><sub>1</sub> &minus; <i>P</i><sub>0</sub>)<i>V</i><sub>0</sub></span><span class='math-label'>Price Effect</span></span> + <span class='math-term'><span class='math-brace'><i>P</i><sub>0</sub>(<i>V</i><sub>1</sub> &minus; <i>V</i><sub>0</sub>)</span><span class='math-label'>Volume Effect</span></span> + <span class='math-term'><span class='math-brace'>(<i>P</i><sub>1</sub> &minus; <i>P</i><sub>0</sub>)(<i>V</i><sub>1</sub> &minus; <i>V</i><sub>0</sub>)</span><span class='math-label'>Mix Effect</span></span>"
                  name="Algebraic PVM 3-Factor Decomposition"
                />
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">10.2</div>
              <div class="wf-content">
                <h4>Non-Parametric Anomaly Detection (Modified Z-Score via MAD)</h4>
                <p>
                  Replaces sensitive Gaussian standard deviations with the Median Absolute Deviation (MAD). Outliers with |<i>M</i><sub><i>i</i></sub>| &gt; 3.5 are automatically flagged for FinOps forensic review:
                </p>
                <MathFormula
                  latex="M_i = \frac{0.6745(x_i - \tilde{x})}{\text{MAD}} \quad \text{where} \quad \text{MAD} = \text{median}(|x_i - \tilde{x}|)"
                  formula-html="<i>M</i><sub><i>i</i></sub> = <span class='math-frac'><span class='math-num'>0.6745(<i>x</i><sub><i>i</i></sub> &minus; <i>x&#771;</i>)</span><span class='math-denom'>MAD</span></span> &emsp;<span class='math-keyword'>where</span>&emsp; MAD = median(|<i>x</i><sub><i>i</i></sub> &minus; <i>x&#771;</i>|)"
                  name="Modified Z-Score Outlier Detection"
                />
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">10.3</div>
              <div class="wf-content">
                <h4>Automated Contractual SLA Breach Penalty Claims</h4>
                <p>
                  Cross-references outage events against vendor master services agreements (MSAs). When vendor availability drops below contractual commitments (e.g., 99.99%), the system generates audit-ready credit claim documentation.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive PVM Decomposition Sandbox -->
        <div class="interactive-tool-card">
          <div class="tool-header">
            <div class="tool-title-cluster">
              <span class="pastel-chip chip-rose">Interactive Simulator</span>
              <h3>Algebraic Price-Volume-Mix Variance Decomposer</h3>
            </div>
            <div class="variance-badge mono" :class="{ 'pos': pvmBreakdown.totalVariance >= 0, 'neg': pvmBreakdown.totalVariance < 0 }">
              Total Spend Variance: ${{ pvmBreakdown.totalVariance >= 0 ? '+' : '' }}{{ pvmBreakdown.totalVariance.toLocaleString() }}
            </div>
          </div>

          <div class="tool-body-grid">
            <div class="controls-column">
              <div class="pvm-input-row">
                <label>
                  <span>Base Unit Rate ($/Unit, P0):</span>
                  <input v-model.number="baseUnitRate" type="number" step="5" class="pvm-num-input" />
                </label>
                <label>
                  <span>Current Unit Rate ($/Unit, P1):</span>
                  <input v-model.number="currUnitRate" type="number" step="5" class="pvm-num-input" />
                </label>
              </div>

              <div class="pvm-input-row">
                <label>
                  <span>Base Workload Volume (V0):</span>
                  <input v-model.number="baseVolume" type="number" step="50" class="pvm-num-input" />
                </label>
                <label>
                  <span>Current Workload Volume (V1):</span>
                  <input v-model.number="currVolume" type="number" step="50" class="pvm-num-input" />
                </label>
              </div>

              <div class="baseline-spend-box">
                <div class="sp-row">
                  <span>Prior Month Baseline Spend:</span>
                  <strong class="mono">${{ pvmBreakdown.baseSpend.toLocaleString() }}</strong>
                </div>
                <div class="sp-row">
                  <span>Current Month Spend:</span>
                  <strong class="mono">${{ pvmBreakdown.currSpend.toLocaleString() }}</strong>
                </div>
              </div>
            </div>

            <div class="waterfall-display-column">
              <h4>Three-Factor Decomposition Waterfall</h4>
              <div class="waterfall-cards">
                <div class="wf-card wf-price">
                  <div class="wf-card-hed">
                    <span>1. Price Effect (Rate Change)</span>
                    <span class="mono">{{ pvmBreakdown.pricePct }}%</span>
                  </div>
                  <strong class="wf-card-val mono">
                    ${{ pvmBreakdown.priceEffect >= 0 ? '+' : '' }}{{ pvmBreakdown.priceEffect.toLocaleString() }}
                  </strong>
                  <p class="wf-card-desc">Variance caused strictly by vendor rate shifts: $(P_1 - P_0) \times V_0$.</p>
                </div>

                <div class="wf-card wf-vol">
                  <div class="wf-card-hed">
                    <span>2. Volume Effect (Demand Change)</span>
                    <span class="mono">{{ pvmBreakdown.volumePct }}%</span>
                  </div>
                  <strong class="wf-card-val mono">
                    ${{ pvmBreakdown.volumeEffect >= 0 ? '+' : '' }}{{ pvmBreakdown.volumeEffect.toLocaleString() }}
                  </strong>
                  <p class="wf-card-desc">Variance caused strictly by business scale: $P_0 \times (V_1 - V_0)$.</p>
                </div>

                <div class="wf-card wf-mix">
                  <div class="wf-card-hed">
                    <span>3. Mix / Interaction Effect</span>
                    <span class="mono">{{ pvmBreakdown.mixPct }}%</span>
                  </div>
                  <strong class="wf-card-val mono">
                    ${{ pvmBreakdown.mixEffect >= 0 ? '+' : '' }}{{ pvmBreakdown.mixEffect.toLocaleString() }}
                  </strong>
                  <p class="wf-card-desc">Compound interaction term: $(P_1 - P_0) \times (V_1 - V_0)$.</p>
                </div>
              </div>

              <div class="proof-note mono">
                Proof of Conservation: Price + Volume + Mix = Total Variance (Exact 0.00% Residual).
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Bottom Navigation Cluster -->
      <div class="subpage-footer-nav">
        <NuxtLink to="/technical-specs/portfolio-rationalization" class="nav-prev-btn">
          ← Previous: Rationalization Engine & TIME (Steps 06 & 07)
        </NuxtLink>
        <NuxtLink to="/technical-specs/ai-governance" class="nav-next-btn">
          Next: Dual-Mode AI & Executive Synthesis (Steps 11 & 12) →
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

.variance-badge {
  font-size: 0.94rem;
  font-weight: 700;
  padding: 0.45rem 1.1rem;
  border-radius: var(--radius-pill);
}
.variance-badge.pos { background: #fee2e2; color: #991b1b; }
.variance-badge.neg { background: #dcfce7; color: #166534; }

.tool-body-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.controls-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.pvm-input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.pvm-input-row label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.82rem;
  color: #4b4f5d;
}

.pvm-num-input {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 700;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d0d4dd;
  border-radius: 10px;
  background: #ffffff;
  color: #121316;
}

.baseline-spend-box {
  background: #ffffff;
  border: 1px solid #e2e5eb;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sp-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.88rem;
  color: #4c505e;
}

.waterfall-display-column h4 {
  font-size: 0.98rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.85rem;
}

.waterfall-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.wf-card {
  background: #ffffff;
  border: 1px solid #e2e5eb;
  border-radius: 12px;
  padding: 0.85rem 1rem;
}

.wf-card-hed {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: #6b707f;
  margin-bottom: 0.2rem;
}

.wf-card-val {
  font-size: 1.15rem;
  display: block;
  margin-bottom: 0.2rem;
}

.wf-card-desc {
  font-size: 0.76rem;
  color: #7b8090;
}

.wf-price .wf-card-val { color: #dc2626; }
.wf-vol .wf-card-val { color: #2563eb; }
.wf-mix .wf-card-val { color: #d97706; }

.proof-note {
  font-size: 0.78rem;
  color: #047857;
  background: var(--pastel-mint-soft);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
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
