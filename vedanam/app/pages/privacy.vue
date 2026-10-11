<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'

useHead({
  title: 'Privacy Policy & Data Sovereignty — VEDANAM',
  meta: [
    {
      name: 'description',
      content: 'Local-first privacy architecture, zero-tracking commitments, and data sovereignty policies for the Vedanam Technology Value Intelligence platform.'
    }
  ]
})

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

type CategoryKey = 'all' | 'architecture' | 'telemetry' | 'ai' | 'sovereignty'

const activeCategory = ref<CategoryKey>('all')
const searchQuery = ref('')
const privacyPageRef = ref<HTMLElement | null>(null)
const copiedClause = ref<string | null>(null)
let gsapCtx: gsap.Context | null = null

interface PrivacyArticle {
  id: string
  number: string
  title: string
  category: CategoryKey
  badge: string
  badgeClass: string
  summary: string
  clauses: {
    heading: string
    text: string
    isHighlight?: boolean
    isWarning?: boolean
  }[]
  keyTakeaway: string
}

const articles: PrivacyArticle[] = [
  {
    id: 'privacy-01',
    number: 'Article 01',
    title: 'The Local-First & Zero-Exfiltration Core Architecture',
    category: 'architecture',
    badge: 'Zero Exfiltration',
    badgeClass: 'chip-mint',
    summary: 'Establishes the fundamental architectural contract: your enterprise financial ledger, topology, and telemetry never leave your machine.',
    clauses: [
      {
        heading: '1.1 Local-First Execution Paradigm',
        text: 'Vedanam and the Technology Value Intelligence (TVI) engine are engineered under a strict local-first architectural paradigm. Analytical truth operations execute through an in-process DuckDB columnar database stored on your local disk; topological relationship graph traversals execute through an in-memory NetworkX engine; and user interface rendering is powered entirely by client-side browser technologies.',
        isHighlight: true
      },
      {
        heading: '1.2 Total Absence of Remote Telemetry Beacons',
        text: 'The Vedanam web application transmits ZERO telemetry beacons, usage analytics, clickstream heatmaps, or diagnostic payloads to remote cloud servers. We do not integrate Google Analytics, Segment, Mixpanel, Datadog RUM, Sentry, or third-party marketing pixels.'
      },
      {
        heading: '1.3 100% Offline & Air-Gapped Capability',
        text: 'The entire application suite is 100% operational in disconnected, air-gapped corporate environments. No outbound internet connection is required to generate synthetic data, ingest general ledger invoices, run portfolio rationalizations, or traverse dependency graphs.'
      }
    ],
    keyTakeaway: 'All computation and storage occur within your machine; zero outbound telemetry packets are transmitted.'
  },
  {
    id: 'privacy-02',
    number: 'Article 02',
    title: 'Enterprise Telemetry Ingestion & PII Prohibition Standard',
    category: 'telemetry',
    badge: 'Non-PII Telemetry',
    badgeClass: 'chip-lavender',
    summary: 'Classifies permissible operational telemetry and strictly prohibits the ingestion of Personally Identifiable Information (PII).',
    clauses: [
      {
        heading: '2.1 Categories of Permissible Enterprise Telemetry',
        text: 'TVI is designed to model systemic architectural and financial relationships. Authorized ingested data is restricted to: (a) Application metadata (name, criticality tier, hosting model, life-cycle phase); (b) Financial GL line items (cost pool, IT tower, vendor name, burdened monthly invoice amounts); (c) Hardware and cloud telemetry (vCPU counts, RAM allocations, storage gigabytes, aggregate transaction volumes); and (d) Business capability maps.'
      },
      {
        heading: '2.2 Strict Prohibition of Personally Identifiable Information (PII)',
        text: 'Vedanam DOES NOT require, ingest, or process Personally Identifiable Information (PII). This includes, without limitation: individual employee names, government identification numbers, personal email addresses, home addresses, payroll specifics, customer credit card records, patient health information (PHI), or end-user surveillance telemetry.',
        isWarning: true
      },
      {
        heading: '2.3 Role & System-Level Aggregation',
        text: 'All resource consumption and capacity metrics are processed exclusively as system-level or department-level aggregates. Individual user activity tracking is strictly unsupported by design.'
      }
    ],
    keyTakeaway: 'The platform processes only systemic enterprise infrastructure and ledger metadata—never personal human data.'
  },
  {
    id: 'privacy-03',
    number: 'Article 03',
    title: 'Browser Storage, Cookies & Ephemeral Client State',
    category: 'architecture',
    badge: 'Cookie-Free Policy',
    badgeClass: 'chip-sky',
    summary: 'Guarantees a 100% tracking-cookie-free experience and details the strictly utilitarian use of client browser storage.',
    clauses: [
      {
        heading: '3.1 Zero Third-Party & Tracking Cookies',
        text: 'Vedanam sets ZERO third-party cookies, zero cross-site advertising cookies, and zero behavioral tracking cookies. You will never encounter a cookie consent wall on Vedanam because we do not engage in any user surveillance.'
      },
      {
        heading: '3.2 Utilitarian Browser Local Storage Usage',
        text: 'The application utilizes the browser\'s standard localStorage API solely for state preservation of user interface preferences across page reloads. These keys include: (a) audio synthesizer active/muted state; (b) active application archetype selection in the decision workspace; and (c) UI color scheme defaults.'
      },
      {
        heading: '3.3 Ephemeral In-Memory State',
        text: 'Fuzzy search queries, real-time what-if scenario slider positions, and temporary graph filters reside entirely in client RAM and are immediately discarded upon closing or refreshing the browser tab.'
      }
    ],
    keyTakeaway: 'Zero tracking cookies; localStorage is used solely to remember your audio preference and active view.'
  },
  {
    id: 'privacy-04',
    number: 'Article 04',
    title: 'Artificial Intelligence & Local LLM Data Insulation',
    category: 'ai',
    badge: 'Local AI Insulation',
    badgeClass: 'chip-rose',
    summary: 'Codifies the strict data insulation protocols governing natural language queries and local Ollama model interactions.',
    clauses: [
      {
        heading: '4.1 Air-Gapped Deterministic Mode',
        text: 'In standard operational mode, the natural language query analyst runs as a deterministic rules engine. Input phrases are resolved through grounded semantic matching against local database views and graph nodes. Zero external API calls are dispatched.'
      },
      {
        heading: '4.2 Localhost Loopback Ollama Protocol',
        text: 'When local generative AI mode is enabled, prompt payloads and context schemas are routed exclusively to the local Ollama daemon at http://localhost:11434 via the loopback network adapter (127.0.0.1). Traffic never traverses the public internet.'
      },
      {
        heading: '4.3 Zero Cloud LLM Data Leakage',
        text: 'Vedanam guarantees that enterprise general ledger figures, dependency graphs, vendor contracts, and vulnerability topologies are NEVER transmitted to multi-tenant cloud AI APIs (such as OpenAI ChatGPT, Anthropic Claude, Google Gemini API, or AWS Bedrock) without explicit, custom out-of-band user configuration.',
        isHighlight: true
      }
    ],
    keyTakeaway: 'AI operates on local loopback (localhost:11434); financial records and topologies are never shared with cloud models.'
  },
  {
    id: 'privacy-05',
    number: 'Article 05',
    title: 'Sensory Hardware & Browser API Permissions Policy',
    category: 'architecture',
    badge: 'Sensory APIs',
    badgeClass: 'chip-peach',
    summary: 'Explains the technical operation of the Web Audio API and WebGL 3D rendering engines without invasive device permissions.',
    clauses: [
      {
        heading: '5.1 Web Audio API Harmonic Synthesizer',
        text: 'Vedanam features an interactive 432Hz harmonic ambient synthesizer and spatial interaction chime engine. All sound waveforms are synthesized procedurally in browser memory using the Web Audio API. Vedanam NEVER requests microphone access, records ambient audio, or transmits sound data.'
      },
      {
        heading: '5.2 WebGL 3D Constellation Shaders',
        text: 'The 3D topological luminaire and constellation views utilize Three.js and hardware-accelerated WebGL. Graphics rendering executes entirely on the user\'s local GPU. Vedanam does not perform canvas fingerprinting or capture screen recordings.'
      },
      {
        heading: '5.3 Standalone Typography & Formula Rendering',
        text: 'KaTeX mathematical typesetting scripts and Google Fonts are loaded directly into the DOM and cached locally. No keystroke data or equation queries are logged or reported.'
      }
    ],
    keyTakeaway: 'Audio synthesis and 3D graphics execute purely on client hardware; no microphone or recording access is ever requested.'
  },
  {
    id: 'privacy-06',
    number: 'Article 06',
    title: 'Data Sovereignty, Open Formats & Instant Purge',
    category: 'sovereignty',
    badge: 'Data Sovereignty',
    badgeClass: 'chip-mint',
    summary: 'Affirms that enterprises own 100% of their data in open standard formats and possess unconstrained local deletion capabilities.',
    clauses: [
      {
        heading: '6.1 Unrestricted Data Portability',
        text: 'All datasets generated or ingested by TVI are stored in transparent, non-proprietary industry formats: Apache Parquet (.parquet), Comma-Separated Values (.csv), standard DuckDB files (.duckdb), and GraphML (.graphml). Enterprises are never trapped in proprietary vendor databases.'
      },
      {
        heading: '6.2 Instant Sovereign Data Destruction (Zero Remanence)',
        text: 'Because data is stored exclusively on local disks, an organization retains complete sovereign authority to delete, purge, or shred all data instantly using standard operating system commands (e.g. rm -rf database/ data/). There are no remote cloud shadow copies, multi-region backups, or hidden database logs to decommission.'
      },
      {
        heading: '6.3 Zero Reconciliation Audit Retention',
        text: 'Financial audit trails (financial_audit_log.parquet) exist solely on local storage to facilitate internal corporate compliance, SOX readiness, and ITFM reconciliation checks.'
      }
    ],
    keyTakeaway: 'You own your data in open Parquet/DuckDB formats; you can delete everything instantly with zero remote remnants.'
  },
  {
    id: 'privacy-07',
    number: 'Article 07',
    title: 'Enterprise Regulatory Alignment & Data Protection Contacts',
    category: 'sovereignty',
    badge: 'Regulatory Compliance',
    badgeClass: 'chip-sky',
    summary: 'Maps Vedanam\'s zero-exfiltration posture to global privacy frameworks including GDPR, CCPA/CPRA, and SOC 2.',
    clauses: [
      {
        heading: '7.1 GDPR Article 25: Privacy by Design & Default',
        text: 'Vedanam natively fulfills the mandate of Article 25 of the General Data Protection Regulation (EU GDPR) by enforcing data minimization, storage limitation, and local-first edge execution by default from the initial software release.'
      },
      {
        heading: '7.2 CCPA / CPRA "Do Not Sell or Share" Compliance',
        text: 'Vedanam does not sell, share, rent, or monetize enterprise or personal information. The platform contains no advertising technology or commercial broker data pipelines.'
      },
      {
        heading: '7.3 Data Protection Officer & Security Inquiries',
        text: 'For questions regarding architectural data protection audits, source-code verification reviews, or cryptographic checksum confirmations, contact our Data Protection and Governance team at privacy@vedanam.pt.'
      }
    ],
    keyTakeaway: 'Privacy by Design is built into the architecture; compliant with GDPR, CCPA, and enterprise audit regimes.'
  }
]

const filteredArticles = computed(() => {
  return articles.filter(art => {
    const matchesCategory = activeCategory.value === 'all' || art.category === activeCategory.value
    if (!matchesCategory) return false
    if (!searchQuery.value.trim()) return true
    const q = searchQuery.value.toLowerCase()
    return (
      art.title.toLowerCase().includes(q) ||
      art.summary.toLowerCase().includes(q) ||
      art.number.toLowerCase().includes(q) ||
      art.clauses.some(c => c.heading.toLowerCase().includes(q) || c.text.toLowerCase().includes(q))
    )
  })
})

const setCategory = (cat: CategoryKey) => {
  if (activeCategory.value === cat) return
  activeCategory.value = cat
  playInteractChime(1.2)
  nextTick(() => {
    ScrollTrigger.refresh()
    animateCards()
  })
}

const copyAnchor = async (id: string) => {
  if (process.client && navigator.clipboard) {
    const url = `${window.location.origin}/privacy#${id}`
    await navigator.clipboard.writeText(url)
    copiedClause.value = id
    playInteractChime(1.5)
    setTimeout(() => {
      copiedClause.value = null
    }, 2000)
  }
}

const animateCards = () => {
  if (!process.client) return
  gsap.fromTo(
    '.privacy-article-card',
    { opacity: 0, y: 30, scale: 0.98 },
    { opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: 0.08, ease: 'power3.out' }
  )
}

onMounted(() => {
  if (!process.client || !privacyPageRef.value) return
  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    const heroTl = gsap.timeline({ delay: 0.1 })
    heroTl
      .fromTo('.back-pill-link', { opacity: 0, x: -25 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power3.out' })
      .fromTo('.privacy-hero .section-tag', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }, '-=0.4')
      .fromTo('.privacy-main-hed', { opacity: 0, y: 35, filter: 'blur(5px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.9, ease: 'power4.out' }, '-=0.3')
      .fromTo('.privacy-subhed', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
      .fromTo('.vitals-badges-strip', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, '-=0.4')
      .fromTo('.privacy-filter-bar', { opacity: 0, y: 20, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'back.out(1.4)' }, '-=0.3')

    animateCards()
  }, privacyPageRef.value)
})

onUnmounted(() => {
  gsapCtx?.revert()
})
</script>

<template>
  <div ref="privacyPageRef" class="privacy-page">
    <div class="container privacy-container">
      <!-- 1. Hero & Breadcrumbs -->
      <header class="privacy-hero">
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

        <span class="section-tag">Privacy & Data Sovereignty</span>
        <h1 class="privacy-main-hed">Privacy Policy & Telemetry Governance</h1>
        <p class="privacy-subhed">
          Our immutable commitment to enterprise data sovereignty: zero tracking beacons, zero cloud exfiltration, local-first analytical execution, and zero PII requirements.
        </p>

        <!-- Vitals Badges Row -->
        <div class="vitals-badges-strip">
          <span class="pastel-chip chip-mint">Zero External Beacons</span>
          <span class="pastel-chip chip-sky">Zero Third-Party Cookies</span>
          <span class="pastel-chip chip-lavender">Localhost Ollama Loopback</span>
          <span class="pastel-chip chip-peach">100% Air-Gappable</span>
          <span class="pastel-chip chip-rose">GDPR Article 25 Compliant</span>
        </div>

        <!-- Filter & Search Bar -->
        <div class="privacy-filter-bar">
          <div class="filter-pills-row">
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'all' }"
              @click="setCategory('all')"
              @mouseenter="setCursor('ALL PRIVACY', 'default')"
              @mouseleave="resetCursor"
            >
              All Articles ({{ articles.length }})
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'architecture' }"
              @click="setCategory('architecture')"
              @mouseenter="setCursor('ARCHITECTURE', 'default')"
              @mouseleave="resetCursor"
            >
              Zero Exfiltration
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'telemetry' }"
              @click="setCategory('telemetry')"
              @mouseenter="setCursor('TELEMETRY', 'default')"
              @mouseleave="resetCursor"
            >
              Non-PII Telemetry
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'ai' }"
              @click="setCategory('ai')"
              @mouseenter="setCursor('AI PRIVACY', 'default')"
              @mouseleave="resetCursor"
            >
              Local AI Isolation
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'sovereignty' }"
              @click="setCategory('sovereignty')"
              @mouseenter="setCursor('SOVEREIGNTY', 'default')"
              @mouseleave="resetCursor"
            >
              Sovereignty & Rights
            </button>
          </div>

          <!-- Quick Search Filter -->
          <div class="search-input-pill">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Filter zero-tracking, PII, local AI..."
            />
            <button v-if="searchQuery" type="button" class="clear-btn" @click="searchQuery = ''">✕</button>
          </div>
        </div>
      </header>

      <!-- 2. Privacy Architecture Manifesto Callout -->
      <section class="manifesto-card">
        <div class="manifesto-header">
          <span class="manifesto-tag pastel-chip chip-mint">Core Privacy Architecture</span>
          <h2 class="manifesto-title">"Your Enterprise Data Never Leaves Your Device."</h2>
          <p class="manifesto-lead">
            Vedanam is explicitly engineered to reject the surveillance SaaS paradigm. In our architecture, the code travels to the data—the data never travels to a remote cloud vendor.
          </p>
        </div>

        <div class="sovereignty-flow-grid">
          <div class="flow-step-box">
            <div class="flow-num">01</div>
            <h3>Client Browser DOM</h3>
            <p>Nuxt 4 & Three.js render UI locally. Web Audio procedures synthesize frequencies without microphone access.</p>
            <span class="flow-badge pastel-chip chip-lavender">Zero Remote Beacons</span>
          </div>
          <div class="flow-step-box">
            <div class="flow-num">02</div>
            <h3>In-Process DuckDB</h3>
            <p>General Ledger accounting tables & OLAP aggregations live in local C++ memory or disk files (.duckdb).</p>
            <span class="flow-badge pastel-chip chip-sky">Local File Isolation</span>
          </div>
          <div class="flow-step-box">
            <div class="flow-num">03</div>
            <h3>In-Memory NetworkX</h3>
            <p>Typed enterprise dependency graph executes multi-hop blast radius closures in local RAM with zero network I/O.</p>
            <span class="flow-badge pastel-chip chip-mint">Local RAM Execution</span>
          </div>
          <div class="flow-step-box">
            <div class="flow-num">04</div>
            <h3>Localhost Ollama LLM</h3>
            <p>Generative natural language queries resolve strictly to http://localhost:11434 via the local loopback adapter.</p>
            <span class="flow-badge pastel-chip chip-peach">Loopback 127.0.0.1</span>
          </div>
        </div>
      </section>

      <!-- 3. Telemetry Ingestion Matrix Card -->
      <section class="matrix-card">
        <div class="matrix-header">
          <span class="section-tag">Data Classification & Hygiene</span>
          <h2 class="matrix-title">Telemetry Ingestion Comparison Matrix</h2>
          <p class="matrix-subtitle">
            An explicit line-by-line demarcation of what data Vedanam ingests versus what data is strictly prohibited and filtered.
          </p>
        </div>

        <div class="matrix-table-wrap">
          <table class="matrix-table">
            <thead>
              <tr>
                <th>Data Category</th>
                <th>Permissible Enterprise Telemetry (Ingested)</th>
                <th>Personal & Sensitive Data (Strictly Prohibited)</th>
                <th>Processing Safeguard</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Application Identity</strong></td>
                <td>System code (APP-042), architecture tier, lifecycle status, hosting type</td>
                <td>Employee owner personal cell numbers, home addresses</td>
                <td><span class="pastel-chip chip-mint">System Identifier Only</span></td>
              </tr>
              <tr>
                <td><strong>Financial Records</strong></td>
                <td>GL ledger account numbers, cost pool categories, vendor corporate names</td>
                <td>Personal expense accounts, executive salary details, banking PINs</td>
                <td><span class="pastel-chip chip-sky">Cost Pool Aggregation</span></td>
              </tr>
              <tr>
                <td><strong>Hardware & Telemetry</strong></td>
                <td>vCPU cores, RAM gigabytes, transaction volumes, API response p99 latency</td>
                <td>Individual user keystrokes, personal browsing histories, GPS data</td>
                <td><span class="pastel-chip chip-lavender">Non-PII System Workloads</span></td>
              </tr>
              <tr>
                <td><strong>AI Natural Language</strong></td>
                <td>Structured query intents, parameter tokens, application TCO lookups</td>
                <td>Confidential human chat transcripts, proprietary source code files</td>
                <td><span class="pastel-chip chip-peach">Localhost Ollama Loopback</span></td>
              </tr>
              <tr>
                <td><strong>Sensory & Audio</strong></td>
                <td>Synthesized mathematical sine waves (432Hz) procedurally generated on CPU</td>
                <td>Microphone input, room audio recordings, biometric voiceprints</td>
                <td><span class="pastel-chip chip-rose">Procedural Math Only</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 4. Articles Feed -->
      <main class="privacy-articles-container">
        <article
          v-for="art in filteredArticles"
          :key="art.id"
          :id="art.id"
          class="privacy-article-card"
        >
          <!-- Article Header -->
          <div class="article-top-bar">
            <div class="article-meta">
              <span class="article-num">{{ art.number }}</span>
              <span class="pastel-chip" :class="art.badgeClass">{{ art.badge }}</span>
            </div>
            <button
              type="button"
              class="anchor-copy-btn"
              @click="copyAnchor(art.id)"
              @mouseenter="setCursor('COPY LINK', 'default')"
              @mouseleave="resetCursor"
              title="Copy link to this article"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              <span>{{ copiedClause === art.id ? 'Copied Link!' : 'Permalink' }}</span>
            </button>
          </div>

          <h2 class="article-heading">{{ art.title }}</h2>
          <p class="article-summary">{{ art.summary }}</p>

          <!-- Clauses List -->
          <div class="clauses-list">
            <div
              v-for="(clause, idx) in art.clauses"
              :key="idx"
              class="clause-item"
              :class="{ 'is-warning': clause.isWarning, 'is-highlight': clause.isHighlight }"
            >
              <h3 class="clause-title">
                {{ clause.heading }}
                <span v-if="clause.isWarning" class="clause-tag warning-tag">PII Exclusion</span>
                <span v-if="clause.isHighlight" class="clause-tag highlight-tag">Sovereignty Standard</span>
              </h3>
              <p class="clause-text">{{ clause.text }}</p>
            </div>
          </div>

          <!-- Bottom Key Takeaway Strip -->
          <div class="article-takeaway-bar">
            <span class="takeaway-label">Key Privacy Takeaway</span>
            <p class="takeaway-text">{{ art.keyTakeaway }}</p>
          </div>
        </article>

        <!-- Empty Results Fallback -->
        <div v-if="filteredArticles.length === 0" class="empty-results-box">
          <p>No articles found matching "{{ searchQuery }}".</p>
          <button type="button" class="pill-btn-dark" @click="searchQuery = ''; activeCategory = 'all'">
            Reset Filter
          </button>
        </div>
      </main>

      <!-- 5. Data Sovereignty Purge Showcase Card -->
      <section class="purge-showcase-card">
        <div class="purge-card-content">
          <div class="purge-text-col">
            <span class="section-tag">Instant Sovereign Destruction</span>
            <h2 class="purge-hed">Total Data Deletion in a Single Command</h2>
            <p class="purge-desc">
              Unlike cloud SaaS vendors who retain your data across geo-redundant backups for 90 days following contract termination, Vedanam offers true cryptographic and physical deletion. Since all records live on your local filesystem, removing the data directories completely eradicates all traces immediately.
            </p>
            <div class="command-box">
              <span class="cmd-label">Local Purge Shell Command</span>
              <code>rm -rf database/tvi.duckdb data/generated/*.csv data/parquet/*.parquet</code>
            </div>
          </div>
          <div class="purge-action-col">
            <a
              href="mailto:privacy@vedanam.pt"
              class="pill-btn-dark"
              @mouseenter="setCursor('EMAIL DPO', 'highlight'); playInteractChime(1.4)"
              @mouseleave="resetCursor"
            >
              Contact Data Protection Officer ↗
            </a>
            <NuxtLink
              to="/terms"
              class="pill-btn-light"
              @mouseenter="setCursor('TERMS', 'default'); playInteractChime(1.2)"
              @mouseleave="resetCursor"
            >
              Review Terms of Service →
            </NuxtLink>
          </div>
        </div>
      </section>
    </div>

    <!-- Culminating Footer -->
    <FooterSection />
  </div>
</template>

<style scoped>
.privacy-page {
  padding-top: 8rem;
  background-color: var(--bg-canvas);
  min-height: 100vh;
}

.privacy-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 var(--container-padding) 5rem;
}

/* 1. Hero */
.privacy-hero {
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

.privacy-main-hed {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 4.4vw, 3.8rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.025em;
  color: #121316;
  margin-bottom: 1rem;
}

.privacy-subhed {
  font-size: 1.15rem;
  line-height: 1.65;
  color: #555966;
  max-width: 950px;
  margin-bottom: 2rem;
}

.vitals-badges-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2.2rem;
}

/* Filter Bar */
.privacy-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-pills-row {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-pill);
  padding: 0.35rem;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
  overflow-x: auto;
  max-width: 100%;
}

.filter-pill {
  padding: 0.55rem 1.25rem;
  border-radius: var(--radius-pill);
  font-size: 0.85rem;
  font-weight: 600;
  color: #555966;
  background: transparent;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-pill:hover {
  color: #121316;
}

.filter-pill.active {
  background: #121316;
  color: #ffffff;
}

.search-input-pill {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-pill);
  padding: 0.45rem 1rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  min-width: 280px;
}

.search-input-pill input {
  border: none;
  outline: none;
  font-size: 0.86rem;
  color: #121316;
  width: 100%;
  background: transparent;
}

.clear-btn {
  font-size: 0.85rem;
  color: #8c92a0;
}

/* 2. Manifesto Card */
.manifesto-card {
  background: #17181d;
  color: #ffffff;
  border-radius: var(--radius-card);
  padding: clamp(2rem, 4vw, 3.5rem);
  margin-bottom: 3.5rem;
  box-shadow: 0 20px 48px -10px rgba(0, 0, 0, 0.18);
  background-image: radial-gradient(circle at 100% 0%, rgba(167, 243, 208, 0.08) 0%, rgba(23, 24, 29, 0) 65%);
}

.manifesto-header {
  margin-bottom: 2.5rem;
}

.manifesto-title {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 3.2vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-top: 0.6rem;
  margin-bottom: 0.8rem;
}

.manifesto-lead {
  font-size: 1.05rem;
  line-height: 1.65;
  color: #b4b9c5;
  max-width: 850px;
}

.sovereignty-flow-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.flow-step-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.flow-num {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--pastel-mint);
}

.flow-step-box h3 {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
}

.flow-step-box p {
  font-size: 0.88rem;
  line-height: 1.55;
  color: #a0a4b0;
  flex: 1;
}

.flow-badge {
  align-self: flex-start;
  margin-top: 0.5rem;
}

/* 3. Matrix Card */
.matrix-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: var(--glass-card-shadow);
  padding: clamp(2rem, 4vw, 3.5rem);
  margin-bottom: 3.5rem;
}

.matrix-header {
  margin-bottom: 2rem;
}

.matrix-title {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 3vw, 2.3rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 0.5rem;
}

.matrix-subtitle {
  font-size: 1.05rem;
  color: #555966;
}

.matrix-table-wrap {
  overflow-x: auto;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
}

.matrix-table th,
.matrix-table td {
  padding: 1rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.matrix-table th {
  background: #f7f7fa;
  font-weight: 700;
  color: #121316;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.matrix-table tr:last-child td {
  border-bottom: none;
}

/* 4. Articles Feed */
.privacy-articles-container {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  margin-bottom: 4rem;
}

.privacy-article-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: var(--glass-card-shadow);
  padding: clamp(2rem, 4.5vw, 3.5rem);
  transition: box-shadow var(--transition-fast);
  will-change: transform, opacity;
}

.privacy-article-card:hover {
  box-shadow: var(--glass-card-hover-shadow);
}

.article-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.article-num {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 700;
  color: #8c92a0;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.anchor-copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: #717582;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(0, 0, 0, 0.06);
  background: #fafafc;
  transition: all 0.2s ease;
}

.anchor-copy-btn:hover {
  background: #f0f1f4;
  color: #121316;
}

.article-heading {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  font-weight: 700;
  color: #121316;
  letter-spacing: -0.02em;
  margin-bottom: 0.8rem;
}

.article-summary {
  font-size: 1.05rem;
  line-height: 1.65;
  color: #555966;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

/* Clauses */
.clauses-list {
  display: flex;
  flex-direction: column;
  gap: 1.6rem;
  margin-bottom: 2.2rem;
}

.clause-item {
  background: #fafafc;
  border-radius: 16px;
  padding: 1.5rem 1.8rem;
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease;
}

.clause-item:hover {
  transform: translateX(4px);
  background: #f7f7fa;
}

.clause-item.is-warning {
  border-left: 4px solid #f43f5e;
  background: #fff5f5;
}

.clause-item.is-highlight {
  border-left: 4px solid #059669;
  background: #f0fdf4;
}

.clause-title {
  font-family: var(--font-sans);
  font-size: 1.05rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.clause-tag {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-pill);
}

.warning-tag {
  background: #ffe4e6;
  color: #be123c;
}

.highlight-tag {
  background: #d1fae5;
  color: #065f46;
}

.clause-text {
  font-size: 0.95rem;
  line-height: 1.65;
  color: #383a42;
}

/* Takeaway Bar */
.article-takeaway-bar {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  background: #f4f5f8;
  border-radius: 14px;
  padding: 1rem 1.4rem;
}

.takeaway-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #717582;
  white-space: nowrap;
}

.takeaway-text {
  font-size: 0.88rem;
  font-weight: 600;
  color: #121316;
}

/* Empty State */
.empty-results-box {
  background: #ffffff;
  border-radius: var(--radius-card);
  padding: 4rem 2rem;
  text-align: center;
  color: #717582;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

/* 5. Purge Showcase Card */
.purge-showcase-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: var(--glass-card-shadow);
  padding: clamp(2.5rem, 5vw, 4rem);
  margin-bottom: 4rem;
}

.purge-card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
}

.purge-text-col {
  max-width: 720px;
}

.purge-hed {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 3.2vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 0.8rem;
}

.purge-desc {
  font-size: 1.05rem;
  line-height: 1.65;
  color: #555966;
  margin-bottom: 1.5rem;
}

.command-box {
  background: #17181d;
  color: #a7f3d0;
  border-radius: 14px;
  padding: 1rem 1.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.cmd-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #8c909e;
}

.command-box code {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  word-break: break-all;
}

.purge-action-col {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  min-width: 260px;
}

@media (max-width: 1024px) {
  .sovereignty-flow-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .purge-card-content {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .sovereignty-flow-grid {
    grid-template-columns: 1fr;
  }
  .privacy-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input-pill {
    min-width: 100%;
  }
  .article-takeaway-bar {
    flex-direction: column;
    gap: 0.3rem;
  }
}
</style>
