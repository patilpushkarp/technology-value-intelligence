<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

const activeTab = ref<'why' | 'how' | 'what'>('why')
const docsPageRef = ref<HTMLElement | null>(null)
let gsapCtx: gsap.Context | null = null

const animateActiveChapter = () => {
  if (!process.client) return
  // Animate the newly active chapter card and its contents
  gsap.fromTo(
    '.docs-card-section',
    { opacity: 0, y: 35, scale: 0.98 },
    { opacity: 1, y: 0, scale: 1, duration: 0.75, ease: 'power3.out' }
  )
  gsap.fromTo(
    ['.chapter-badge', '.chapter-hed'],
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: 'power3.out' }
  )
  if (activeTab.value === 'why') {
    gsap.fromTo(
      '.callout-glass-card',
      { opacity: 0, y: 25, scale: 0.97 },
      { opacity: 1, y: 0, scale: 1, duration: 0.7, delay: 0.15, ease: 'power3.out' }
    )
    gsap.fromTo(
      '.pathology-card',
      { opacity: 0, y: 30, scale: 0.96 },
      { opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: 0.06, delay: 0.25, ease: 'power3.out' }
    )
  } else if (activeTab.value === 'how') {
    gsap.fromTo(
      '.guide-step',
      { opacity: 0, y: 35, x: -15 },
      { opacity: 1, y: 0, x: 0, duration: 0.7, stagger: 0.1, delay: 0.15, ease: 'power3.out' }
    )
  } else if (activeTab.value === 'what') {
    gsap.fromTo(
      '.arch-box',
      { opacity: 0, y: 25, scale: 0.96 },
      { opacity: 1, y: 0, scale: 1, duration: 0.65, stagger: 0.1, delay: 0.15, ease: 'power3.out' }
    )
    gsap.fromTo(
      '.notebook-table-wrap',
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.75, delay: 0.35, ease: 'power3.out' }
    )
  }
}

const setTab = (tab: 'why' | 'how' | 'what') => {
  if (activeTab.value === tab) return
  activeTab.value = tab
  playInteractChime(1.2)
  nextTick(() => {
    setTimeout(() => {
      ScrollTrigger.refresh()
      animateActiveChapter()
    }, 50)
  })
}

onMounted(() => {
  if (!process.client || !docsPageRef.value) return
  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    // 1. Docs Hero Arrival Entry
    const heroTl = gsap.timeline({ delay: 0.1 })
    heroTl
      .fromTo('.back-pill-link', { opacity: 0, x: -25 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power3.out' })
      .fromTo('.docs-hero .section-tag', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }, '-=0.4')
      .fromTo('.docs-main-hed', { opacity: 0, y: 35, filter: 'blur(5px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.9, ease: 'power4.out' }, '-=0.3')
      .fromTo('.docs-subhed', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
      .fromTo('.docs-tab-bar', { opacity: 0, y: 20, scale: 0.95 }, { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'back.out(1.4)' }, '-=0.4')

    // 2. Hero Exit on Scroll Down into Content
    gsap.to('.docs-hero', {
      scrollTrigger: {
        trigger: '.docs-hero',
        start: 'top top',
        end: 'bottom top',
        scrub: 0.6
      },
      y: -50,
      opacity: 0.2,
      ease: 'power2.in'
    })

    // 3. Initial Active Chapter Entrance
    animateActiveChapter()
  }, docsPageRef.value)
})

onUnmounted(() => {
  gsapCtx?.revert()
})
</script>

<template>
  <div ref="docsPageRef" class="docs-page">
    <div class="container docs-container">
      <!-- Top Meta & Navigation -->
      <div class="docs-hero">
        <NuxtLink
          to="/"
          class="back-pill-link"
          @mouseenter="setCursor('BACK HOME', 'default')"
          @mouseleave="resetCursor"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          <span>Return to Vedanam Experience</span>
        </NuxtLink>

        <span class="section-tag">System Documentation</span>
        <h1 class="docs-main-hed">Governance & Technology Value Realization</h1>
        <p class="docs-subhed">
          The comprehensive guide to Vedanam: exploring why this application exists, how to navigate its sensory and analytical instruments, and what subsystems power its core.
        </p>

        <!-- Chapter Navigation Pills in Frosted Glass Capsule (ledup.pt style) -->
        <div class="docs-tab-bar">
          <button
            type="button"
            class="tab-pill"
            :class="{ active: activeTab === 'why' }"
            @click="setTab('why')"
          >
            <span>01. Why This App</span>
          </button>
          <button
            type="button"
            class="tab-pill"
            :class="{ active: activeTab === 'how' }"
            @click="setTab('how')"
          >
            <span>02. How to Use</span>
          </button>
          <button
            type="button"
            class="tab-pill"
            :class="{ active: activeTab === 'what' }"
            @click="setTab('what')"
          >
            <span>03. What Is Inside</span>
          </button>
        </div>
      </div>

      <!-- Chapter 1: WHY THIS APP -->
      <section v-if="activeTab === 'why'" class="docs-card-section" id="why">
        <div class="chapter-badge pastel-chip chip-lavender">Chapter 01 · Epistemology & Motivation</div>
        <h2 class="chapter-hed">Why Vedanam? The Collapse of Accounting Fiction</h2>

        <div class="prose-content">
          <h3>The Philosophical Genesis</h3>
          <p>
            In ancient Vedic epistemology, <strong>Vedanā</strong> (वेदना) denotes sensory perception, affective discernment, and the direct intuitive cognition of reality prior to conceptual distortion.
            Contemporary IT Financial Management (ITFM) and Technology Business Management (TBM) suffer from the opposite affliction: they are drowning in intellectual abstractions, disconnected ERP accounts, and inert spreadsheets.
          </p>
          <p>
            When an executive reviews an annual IT budget, they are reading <em>accounting fiction</em>. A general ledger row says "FinSys ERP: $4,200,000". It tells you nothing about the 14 revenue-critical services depending on that software, the single point of failure lurking in its database cluster, or the fact that a $620,000 legacy CRM system has registered near-zero user telemetry over the past quarter.
          </p>

          <div class="callout-glass-card">
            <span class="callout-title">The Core Thesis of Vedanam</span>
            <p>
              Technology value cannot be comprehended through isolated financial rows. It is a living, topological phenomenon. Vedanam bridges deterministic analytical truth (<strong>DuckDB OLAP</strong>) with relational intelligence (<strong>NetworkX Semantic Graph</strong>) to create a transparent, proactive governance platform for technology and financial executives.
            </p>
          </div>

          <h3>The Eight Pathologies of Enterprise Technology Spend</h3>
          <div class="pathologies-grid">
            <div class="pathology-card">
              <span class="pastel-chip chip-rose">01</span>
              <h4>The Zombie System Pathology</h4>
              <p>Applications that run silently with zero real user telemetry but immortal annual vendor maintenance renewals, draining 10% to 18% of IT operating budgets.</p>
            </div>
            <div class="pathology-card">
              <span class="pastel-chip chip-peach">02</span>
              <h4>Topological Blindness</h4>
              <p>Decommissioning an apparently secondary service only to trigger cascading outages across core consumer payment gateways because dependencies were undocumented.</p>
            </div>
            <div class="pathology-card">
              <span class="pastel-chip chip-sky">03</span>
              <h4>Attribution Double-Counting</h4>
              <p>Shared infrastructure and cloud lakehouses being billed at 100% to multiple departments simultaneously, creating artificial spend inflation and distorted ROI.</p>
            </div>
            <div class="pathology-card">
              <span class="pastel-chip chip-mint">04</span>
              <h4>Spreadsheet Hallucination</h4>
              <p>Manual spreadsheets with broken formulas exhibiting 12% to 18% reconciliation variance against audited General Ledgers.</p>
            </div>
            <div class="pathology-card">
              <span class="pastel-chip chip-lavender">05</span>
              <h4>Uncaptured Benefit Drift</h4>
              <p>Transformation projects declared "successful" simply because they shipped on-schedule, despite failing to move target operational and commercial KPIs.</p>
            </div>
            <div class="pathology-card">
              <span class="pastel-chip chip-rose">06</span>
              <h4>Single Point of Failure (SPOF) Lock-in</h4>
              <p>Concealed vendor concentration where a single technology provider controls multiple non-substitutable tier-1 business capabilities.</p>
            </div>
            <div class="pathology-card">
              <span class="pastel-chip chip-mint">07</span>
              <h4>Elasticity Overhead Waste</h4>
              <p>Cloud workloads provisioned for maximum peak concurrency 24/7/365 rather than scaling dynamically, generating massive FinOps waste.</p>
            </div>
            <div class="pathology-card">
              <span class="pastel-chip chip-peach">08</span>
              <h4>Fictional Gross Savings Illusion</h4>
              <p>Treating gross contract spend as immediate cash savings upon rationalization, ignoring contract exit penalties and retained shared platform overhead.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Chapter 2: HOW TO USE -->
      <section v-if="activeTab === 'how'" class="docs-card-section" id="how">
        <div class="chapter-badge pastel-chip chip-sky">Chapter 02 · Operator Runbook</div>
        <h2 class="chapter-hed">How to Navigate & Operate Vedanam</h2>

        <div class="prose-content">
          <p>
            Vedanam is designed to enable seamless transitions between macro executive portfolio oversight and forensic technical deep-dives into any individual component.
          </p>

          <div class="guide-steps">
            <div class="guide-step">
              <div class="step-num pastel-chip chip-lavender">Step 01</div>
              <div class="step-info">
                <h3>Visual Inspection via Hotspot Rooms</h3>
                <p>Navigate to the Projects section and click the pulsating circular white pins positioned across architectural spaces. Each hotspot instantly reveals burdened annual TCO, dependency counts, and operational risk tiers.</p>
              </div>
            </div>

            <div class="guide-step">
              <div class="step-num pastel-chip chip-mint">Step 02</div>
              <div class="step-info">
                <h3>Analytical Deep-Dive via the Bento Grid</h3>
                <p>Examine the Highlights bento grid to inspect DuckDB and NetworkX engine telemetry, active production node counts (102 enterprise nodes), and the 2026 Governance Catalog.</p>
              </div>
            </div>

            <div class="guide-step">
              <div class="step-num pastel-chip chip-sky">Step 03</div>
              <div class="step-info">
                <h3>Strategic Pillar Evaluation</h3>
                <p>Interact with the 5-pillar accordion container (Innovation, Quality, Efficiency, Expertise, Sustainability) to deconstruct multi-criteria decision models and month-over-month variance drivers.</p>
              </div>
            </div>

            <div class="guide-step">
              <div class="step-num pastel-chip chip-peach">Step 04</div>
              <div class="step-info">
                <h3>Fuzzy Search via Floating Glass Navbar</h3>
                <p>Click the circular magnifying glass button in the floating header to launch instant search across all enterprise applications, capabilities, and criticality tiers in real time.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Chapter 3: WHAT IS INSIDE -->
      <section v-if="activeTab === 'what'" class="docs-card-section" id="what">
        <div class="chapter-badge pastel-chip chip-mint">Chapter 03 · Architecture & Codebase</div>
        <h2 class="chapter-hed">What Powers the Core of Vedanam</h2>

        <div class="prose-content">
          <h3>Strict Three-Layer Architecture</h3>
          
          <div class="architecture-flow-box">
            <div class="arch-box arch-box-top">
              <span class="box-title">Presentation & Local AI Interface</span>
              <span class="box-sub">Nuxt 4 · Three.js 3D Luminaire · GSAP Animations · Deterministic NL Analyst (Optional Local Ollama)</span>
            </div>
            <div class="arch-arrow-down">↓</div>
            <div class="arch-box arch-box-mid">
              <span class="box-title">TVI Analytics Engine</span>
              <span class="box-sub">Burdened TCO · Capability Allocation · MCDA Rationalization · Transitive Blast Radius</span>
            </div>
            <div class="arch-arrow-down">↓</div>
            <div class="arch-bottom-split">
              <div class="arch-box arch-box-half">
                <span class="box-title">Analytical Truth (DuckDB)</span>
                <span class="box-sub">Columnar OLAP · General Ledger Aggregations · MoM Variance Decomposition</span>
              </div>
              <div class="arch-box arch-box-half">
                <span class="box-title">Relationship Intelligence (NetworkX)</span>
                <span class="box-sub">Typed Semantic Property Graph · Multi-Hop Traversals · Dependency Subgraphs</span>
              </div>
            </div>
          </div>

          <div class="callout-glass-card">
            <span class="callout-title">Complete Forensic Technical Specifications</span>
            <p>
              Looking for mathematical proofs, input/output data contracts, latency SLAs, and line-by-line source lineage?
              <NuxtLink to="/technical-specs" class="specs-inline-link">
                <strong>Explore the Technical Specifications & Execution Engine Guide ↗</strong>
              </NuxtLink>
            </p>
          </div>

          <h3>The 12-Notebook Research Curriculum</h3>
          <div class="notebook-table-wrap">
            <table class="notebook-table">
              <thead>
                <tr>
                  <th>Notebook</th>
                  <th>Module</th>
                  <th>Core Objective & Output</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>01_generate_enterprise_data</code></td>
                  <td>Data Generation</td>
                  <td>Deterministic generation of 102 nodes, GL ledger rows, CMDB, and telemetry (Seed 42)</td>
                </tr>
                <tr>
                  <td><code>02_tbm_itfm_data_model</code></td>
                  <td>Data Modeling</td>
                  <td>DuckDB schema design for TBM taxonomy, general ledger sums, and burdened cost models</td>
                </tr>
                <tr>
                  <td><code>03_build_knowledge_graph</code></td>
                  <td>Knowledge Graph</td>
                  <td>Semantic property graph construction with typed nodes and directed edges in NetworkX</td>
                </tr>
                <tr>
                  <td><code>04_application_cost_intelligence</code></td>
                  <td>Application TCO</td>
                  <td>5-layer burdened cost calculation, unit economics, and general ledger reconciliation</td>
                </tr>
                <tr>
                  <td><code>05_capability_cost_intelligence</code></td>
                  <td>Capability Attribution</td>
                  <td>Proportional cost allocation across business capabilities without double-counting</td>
                </tr>
                <tr>
                  <td><code>06_consumption_intelligence</code></td>
                  <td>Consumption Analytics</td>
                  <td>Telemetry profiling, quadrant split, and automated discovery of zombie applications</td>
                </tr>
                <tr>
                  <td><code>07_application_rationalization</code></td>
                  <td>MCDA Rationalization</td>
                  <td>TIME matrix placement with realistic avoidable cost scenarios and contract exit penalties</td>
                </tr>
                <tr>
                  <td><code>08_dependency_and_impact_analysis</code></td>
                  <td>Blast Radius Analysis</td>
                  <td>Transitive dependency tracing, single points of failure, and revenue-at-risk simulation</td>
                </tr>
                <tr>
                  <td><code>09_investment_benefit_realization</code></td>
                  <td>Benefit Realization</td>
                  <td>Tracking post-delivery KPI progress, target vs actual variances, and benefit drift</td>
                </tr>
                <tr>
                  <td><code>10_cost_driver_and_variance_analysis</code></td>
                  <td>Variance Decomposition</td>
                  <td>Month-over-month cost driver decomposition across rate, volume, and mix effects</td>
                </tr>
                <tr>
                  <td><code>11_local_llm_knowledge_graph_analyst</code></td>
                  <td>Local AI Analyst</td>
                  <td>Deterministic natural-language-to-graph queries with optional local Ollama LLM integration</td>
                </tr>
                <tr>
                  <td><code>12_end_to_end_technology_value_intelligence</code></td>
                  <td>Executive Synthesis</td>
                  <td>End-to-end governance synthesis, portfolio briefing, and 4-tier validation audit</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer matching ledup.pt in English -->
    <FooterSection />
  </div>
</template>

<style scoped>
.docs-page {
  padding-top: 8rem;
  background-color: var(--bg-canvas);
  min-height: 100vh;
}

.docs-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 var(--container-padding) 5rem;
}

.docs-hero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 3.5rem;
}

.back-pill-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 1.1rem;
  border-radius: var(--radius-pill);
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 0.82rem;
  font-weight: 600;
  color: #121316;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.back-pill-link:hover {
  background: #f7f7f9;
  transform: translateX(-3px);
}

.docs-main-hed {
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 3.4vw, 2.75rem);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 1rem;
  max-width: 24ch;
}

.docs-subhed {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #555966;
  font-weight: 400;
  max-width: 75ch;
  margin-bottom: 2.5rem;
}

/* Tabs */
.docs-tab-bar {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-pill);
  padding: 0.35rem;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.05);
}

.tab-pill {
  padding: 0.55rem 1.35rem;
  border-radius: var(--radius-pill);
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.125rem;
  color: #555966;
  background: transparent;
  transition: all 0.2s ease;
}

.tab-pill:hover {
  color: #121316;
}

.tab-pill.active {
  background: #121316;
  color: #ffffff;
}

/* Section Cards */
.docs-card-section {
  background: #ffffff;
  border-radius: var(--radius-card);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: var(--glass-card-shadow);
  padding: clamp(2rem, 5vw, 4rem);
  margin-bottom: 3rem;
  will-change: transform, opacity;
}

.chapter-badge {
  margin-bottom: 1rem;
}

.chapter-hed {
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 2.4vw, 1.85rem);
  font-weight: 500;
  line-height: 1.25;
  color: #121316;
  letter-spacing: -0.02em;
  margin-bottom: 1.6rem;
}

.prose-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  color: #383a42;
  font-size: 0.875rem;
  line-height: 1.65;
}

.prose-content h3 {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: #121316;
  margin-top: 1rem;
}

.callout-glass-card {
  background: #f7f7fa;
  border-left: 4px solid var(--pastel-lavender);
  border-radius: 16px;
  padding: 1.5rem 1.8rem;
  margin: 1rem 0;
}

.callout-title {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #5b21b6;
  display: block;
  margin-bottom: 0.4rem;
}

/* Pathologies Grid */
.pathologies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
  margin-top: 0.5rem;
}

.pathology-card {
  background: #fafafc;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 18px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  will-change: transform, opacity;
}

.pathology-card h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #121316;
}

.pathology-card p {
  font-size: 0.84rem;
  color: #555966;
  line-height: 1.55;
}

/* Guide Steps */
.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.guide-step {
  display: flex;
  gap: 1.5rem;
  background: #fafafc;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 18px;
  padding: 1.75rem;
  align-items: flex-start;
  will-change: transform, opacity;
}

.step-num {
  font-size: 0.8rem;
  white-space: nowrap;
}

.step-info h3 {
  margin-top: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.35rem;
}

.step-info p {
  color: #555966;
  font-size: 0.95rem;
  line-height: 1.55;
}

/* Architecture Diagram */
.architecture-flow-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
  margin: 1.5rem 0;
}

.arch-box {
  background: #f7f7fa;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
}

.arch-arrow-down {
  font-size: 1.2rem;
  color: #8c909e;
}

.arch-bottom-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  width: 100%;
}

.box-title {
  font-weight: 700;
  color: #121316;
}

.box-sub {
  font-size: 0.82rem;
  color: #717582;
}

/* Notebook Table */
.notebook-table-wrap {
  overflow-x: auto;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  margin-top: 1rem;
}

.notebook-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.notebook-table th,
.notebook-table td {
  padding: 0.9rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.notebook-table th {
  background: #f7f7fa;
  font-weight: 700;
  color: #121316;
  text-transform: uppercase;
  font-size: 0.74rem;
  letter-spacing: 0.05em;
}

.notebook-table tr:last-child td {
  border-bottom: none;
}
</style>
