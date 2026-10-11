<script setup lang="ts">
import { ref } from 'vue'
import { useAudioSynth } from '~/composables/useAudioSynth'
import MathFormula from '~/components/MathFormula.vue'

export interface ExpeditionMilestone {
  number: number
  name: string
  altitude: number
  location: string
  phaseNumber: number
  business: {
    title: string
    executiveSummary: string
    businessImpact: string
    costImplications: string
    cfoTakeaway: string
    kpis: { label: string; value: string }[]
  }
  technical: {
    title: string
    formulaName: string
    formulaLatex: string
    formulaHtml?: string
    formulaExplanation: string
    moduleLineage: string
    inputContract: string
    outputContract: string
    latencySla: string
    memoryBudget: string
    codeSnippet: string
  }
}

const props = defineProps<{
  milestone: ExpeditionMilestone
  initialBook?: 'business' | 'technical'
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { playInteractChime } = useAudioSynth()

const activeBook = ref<'business' | 'technical'>(props.initialBook || 'business')
const copiedCode = ref(false)

const switchBook = (book: 'business' | 'technical') => {
  activeBook.value = book
  playInteractChime(book === 'business' ? 1.2 : 1.4)
}

const copySnippet = async () => {
  if (process.client && navigator.clipboard) {
    await navigator.clipboard.writeText(props.milestone.technical.codeSnippet)
    copiedCode.value = true
    playInteractChime(1.5)
    setTimeout(() => { copiedCode.value = false }, 1800)
  }
}
</script>

<template>
  <div class="notebook-modal-backdrop" @click.self="emit('close')">
    <div class="expedition-binder-case">
      <!-- Binder Top Leather Bar & Close -->
      <div class="binder-top-bar">
        <div class="binder-location">
          <span class="alt-flag">ALTITUDE: {{ milestone.altitude }}M</span>
          <span class="loc-name">{{ milestone.location }} · STAGE 0{{ milestone.number }}</span>
        </div>

        <!-- 2 Notebook Selector Tabs -->
        <div class="dual-notebook-tabs">
          <button
            type="button"
            class="tab-notebook-btn business-tab"
            :class="{ active: activeBook === 'business' }"
            @click="switchBook('business')"
          >
            <span class="book-icon">📖</span>
            <span class="book-name">Business Field Guide</span>
            <span class="book-badge">Executive & ROI</span>
          </button>

          <button
            type="button"
            class="tab-notebook-btn technical-tab"
            :class="{ active: activeBook === 'technical' }"
            @click="switchBook('technical')"
          >
            <span class="book-icon">📐</span>
            <span class="book-name">Technical Field Manual</span>
            <span class="book-badge">Math & Code</span>
          </button>
        </div>

        <button type="button" class="close-binder-btn" @click="emit('close')">✕</button>
      </div>

      <!-- Binder Interior Content (Open Journal Pages) -->
      <div class="journal-interior" :class="`theme-${activeBook}`">
        <!-- 1. BUSINESS FIELD GUIDE NOTEBOOK -->
        <div v-if="activeBook === 'business'" class="journal-view business-theme">
          <div class="journal-header">
            <span class="journal-tag">EXECUTIVE VALUE & STRATEGIC REALIZATION</span>
            <h2 class="journal-title">{{ milestone.business.title }}</h2>
            <p class="journal-lead">{{ milestone.business.executiveSummary }}</p>
          </div>

          <div class="journal-columns-grid">
            <!-- Left Page: Business Impact & Strategic Imperatives -->
            <div class="journal-page left-page">
              <span class="page-sec-hed">Enterprise Strategic Impact</span>
              <p class="body-text">{{ milestone.business.businessImpact }}</p>

              <span class="page-sec-hed mt-4">Cost Avoidance & Economic Rationale</span>
              <p class="body-text">{{ milestone.business.costImplications }}</p>

              <!-- CFO Takeaway Card -->
              <div class="cfo-takeaway-card">
                <span class="cfo-badge">CFO / CIO Core Takeaway</span>
                <p class="cfo-quote">“{{ milestone.business.cfoTakeaway }}”</p>
              </div>
            </div>

            <!-- Right Page: Target KPI Trajectories -->
            <div class="journal-page right-page">
              <span class="page-sec-hed">Monitored Business KPI Trajectories</span>
              <div class="kpi-cards-stack">
                <div v-for="kpi in milestone.business.kpis" :key="kpi.label" class="kpi-card">
                  <span class="kpi-label">{{ kpi.label }}</span>
                  <strong class="kpi-val">{{ kpi.value }}</strong>
                </div>
              </div>

              <!-- Expeditioner Note -->
              <div class="expeditioner-stamp">
                <div class="stamp-seal">VERIFIED</div>
                <div class="stamp-details">
                  <strong>Zero Spreadsheet Drift</strong>
                  <span>TBM ATUM 4.0 Standardized</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. TECHNICAL FIELD MANUAL NOTEBOOK -->
        <div v-else class="journal-view technical-theme">
          <div class="journal-header">
            <span class="journal-tag tech-tag">ENGINEERING SPECIFICATION & MATHEMATICAL PROOF</span>
            <h2 class="journal-title">{{ milestone.technical.title }}</h2>
            <div class="specs-pills-row">
              <span class="spec-pill">Execution SLA: <strong>{{ milestone.technical.latencySla }}</strong></span>
              <span class="spec-pill">Memory Budget: <strong>{{ milestone.technical.memoryBudget }}</strong></span>
              <span class="spec-pill">Reproducibility: <strong>Seed 42</strong></span>
            </div>
          </div>

          <div class="journal-columns-grid">
            <!-- Left Page: First-Principles Mathematical Proof -->
            <div class="journal-page left-page">
              <span class="page-sec-hed">First-Principles Mathematical Formulation</span>
              <div class="math-card-container">
                <MathFormula
                  :latex="milestone.technical.formulaLatex"
                  :formula-html="milestone.technical.formulaHtml"
                  :name="milestone.technical.formulaName"
                />
                <p class="formula-caption">{{ milestone.technical.formulaExplanation }}</p>
              </div>

              <div class="contracts-matrix">
                <div class="contract-item">
                  <span class="c-k">Input Data Contract:</span>
                  <span class="c-v mono">{{ milestone.technical.inputContract }}</span>
                </div>
                <div class="contract-item">
                  <span class="c-k">Output Artifact:</span>
                  <span class="c-v mono">{{ milestone.technical.outputContract }}</span>
                </div>
              </div>
            </div>

            <!-- Right Page: Python Source Code Lineage -->
            <div class="journal-page right-page">
              <div class="code-terminal-header">
                <span class="module-title">{{ milestone.technical.moduleLineage }}</span>
                <button type="button" class="copy-terminal-btn" @click="copySnippet">
                  {{ copiedCode ? 'Copied ✓' : 'Copy Code' }}
                </button>
              </div>
              <pre class="technical-pre"><code>{{ milestone.technical.codeSnippet }}</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notebook-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.5rem;
}

.expedition-binder-case {
  width: 100%;
  max-width: 1180px;
  max-height: 88vh;
  background: #ffffff;
  border-radius: 28px;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

/* Binder Top Bar */
.binder-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.8rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.binder-location {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.alt-flag {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 800;
  background: #0284c7;
  color: #ffffff;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  letter-spacing: 0.05em;
}

.loc-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
}

.dual-notebook-tabs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #e2e8f0;
  padding: 0.25rem;
  border-radius: var(--radius-pill);
}

.tab-notebook-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.1rem;
  border-radius: var(--radius-pill);
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.book-icon {
  font-size: 1rem;
}

.book-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
}

.book-badge {
  font-size: 0.66rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.06);
  color: #64748b;
}

.tab-notebook-btn.active.business-tab {
  background: #b45309; /* Warm expedition leather */
  box-shadow: 0 4px 14px rgba(180, 83, 9, 0.25);
}
.tab-notebook-btn.active.business-tab .book-name,
.tab-notebook-btn.active.business-tab .book-badge {
  color: #ffffff;
}
.tab-notebook-btn.active.business-tab .book-badge {
  background: rgba(255, 255, 255, 0.2);
}

.tab-notebook-btn.active.technical-tab {
  background: #0284c7; /* Glacial alpine blue */
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
}
.tab-notebook-btn.active.technical-tab .book-name,
.tab-notebook-btn.active.technical-tab .book-badge {
  color: #ffffff;
}
.tab-notebook-btn.active.technical-tab .book-badge {
  background: rgba(255, 255, 255, 0.2);
}

.close-binder-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #64748b;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-binder-btn:hover {
  background: #0f172a;
  color: #ffffff;
}

/* Journal Interior Pages */
.journal-interior {
  padding: 2.2rem;
  overflow-y: auto;
  flex: 1;
}

.journal-header {
  margin-bottom: 1.8rem;
}

.journal-tag {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #b45309;
}

.tech-tag {
  color: #0284c7;
}

.journal-title {
  font-family: var(--font-display);
  font-size: 1.65rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.3rem 0 0.5rem;
}

.journal-lead {
  font-size: 0.95rem;
  color: #475569;
  line-height: 1.55;
  max-width: 900px;
}

.specs-pills-row {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.6rem;
}

.spec-pill {
  font-size: 0.75rem;
  padding: 0.3rem 0.75rem;
  background: #f1f5f9;
  border-radius: var(--radius-pill);
  color: #334155;
}

.journal-columns-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 2.2rem;
}

.journal-page {
  display: flex;
  flex-direction: column;
}

.page-sec-hed {
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #64748b;
  display: block;
  margin-bottom: 0.4rem;
}

.mt-4 { margin-top: 1.2rem; }

.body-text {
  font-size: 0.88rem;
  line-height: 1.6;
  color: #334155;
}

.cfo-takeaway-card {
  margin-top: 1.5rem;
  padding: 1.1rem;
  border-radius: 16px;
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
}

.cfo-badge {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #b45309;
  display: block;
  margin-bottom: 0.3rem;
}

.cfo-quote {
  font-size: 0.88rem;
  font-style: italic;
  color: #78350f;
  line-height: 1.5;
  margin: 0;
}

.kpi-cards-stack {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
}

.kpi-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
}

.kpi-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
}

.expeditioner-stamp {
  margin-top: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
}

.stamp-seal {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 800;
  color: #059669;
  border: 2px solid #059669;
  padding: 0.35rem 0.65rem;
  border-radius: 8px;
  transform: rotate(-5deg);
}

.stamp-details {
  display: flex;
  flex-direction: column;
  font-size: 0.76rem;
  color: #64748b;
}

.math-card-container {
  margin-bottom: 1.2rem;
}

.formula-caption {
  font-size: 0.78rem;
  color: #64748b;
  margin-top: 0.4rem;
  line-height: 1.45;
}

.contracts-matrix {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
}

.contract-item {
  display: flex;
  flex-direction: column;
  font-size: 0.75rem;
}

.c-k {
  color: #64748b;
  font-weight: 700;
}

.c-v {
  color: #0f172a;
}

.code-terminal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1rem;
  background: #0f172a;
  border-radius: 14px 14px 0 0;
}

.module-title {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #94a3b8;
}

.copy-terminal-btn {
  font-size: 0.7rem;
  font-weight: 700;
  color: #38bdf8;
  background: transparent;
  border: none;
  cursor: pointer;
}

.technical-pre {
  margin: 0;
  padding: 1rem;
  background: #020617;
  border-radius: 0 0 14px 14px;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  color: #93c5fd;
  line-height: 1.5;
  max-height: 320px;
  overflow-y: auto;
}

@media (max-width: 950px) {
  .journal-columns-grid {
    grid-template-columns: 1fr;
  }
}
</style>
