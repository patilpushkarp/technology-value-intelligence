<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'

useHead({
  title: 'Terms of Service & Governance — VEDANAM',
  meta: [
    {
      name: 'description',
      content: 'Operational governance, analytical guardrails, avoidable cost doctrines, and terms of service for the Vedanam Technology Value Intelligence platform.'
    }
  ]
})

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

type CategoryKey = 'all' | 'scope' | 'guardrails' | 'determinism' | 'legal'

const activeCategory = ref<CategoryKey>('all')
const searchQuery = ref('')
const termsPageRef = ref<HTMLElement | null>(null)
const copiedClause = ref<string | null>(null)
let gsapCtx: gsap.Context | null = null

interface ArticleItem {
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
    isWarning?: boolean
    isHighlight?: boolean
  }[]
  keyTakeaway: string
}

const articles: ArticleItem[] = [
  {
    id: 'article-01',
    number: 'Article 01',
    title: 'Architectural Nature, Definitions & Operational Scope',
    category: 'scope',
    badge: 'Scope & Architecture',
    badgeClass: 'chip-lavender',
    summary: 'Establishes the legal and operational definition of Vedanam as an architectural sensory digital twin and presentation layer operating over the Technology Value Intelligence (TVI) engine.',
    clauses: [
      {
        heading: '1.1 System Demarcation & Components',
        text: 'The Vedanam platform ("Vedanam") comprises the sensory digital twin interface, 3D WebGL topological luminaire, interactive decision workspaces, and Web Audio harmonic feedback systems. The underlying analytics are powered by the Technology Value Intelligence ("TVI") engine, which unites an in-process columnar OLAP engine (DuckDB) as Analytical Truth with an in-memory typed semantic property graph (NetworkX) as Relationship Intelligence.'
      },
      {
        heading: '1.2 Local-First Execution Contract',
        text: 'Vedanam is architected from inception as a 100% local-first, on-premises executable system configured for standard corporate workstations (16 GB RAM baseline). The software operates without mandatory cloud telemetry, external licensing servers, or continuous internet dependencies. Enterprises retain total physical and virtual custody of the computational stack.'
      },
      {
        heading: '1.3 Authorized Use Cases',
        text: 'Access to and utilization of Vedanam is strictly authorized for Technology Business Management (TBM), IT Financial Management (ITFM), Technology Value Realization (TVR), multi-criteria portfolio rationalization (MCDA/TOPSIS), and transitive blast-radius dependency modeling within deploying enterprise organizations.'
      }
    ],
    keyTakeaway: 'Vedanam is a sovereign, local-first analytical instrument; all processing occurs locally without cloud lock-in.'
  },
  {
    id: 'article-02',
    number: 'Article 02',
    title: 'Analytical Guardrails: The Avoidable Cost Doctrine',
    category: 'guardrails',
    badge: 'Analytical Guardrails',
    badgeClass: 'chip-peach',
    summary: 'Defines the mandatory analytical standard distinguishing modeled avoidable cost scenarios from guaranteed cash savings in financial reporting.',
    clauses: [
      {
        heading: '2.1 Avoidable Cost vs. Guaranteed Cash Savings',
        text: 'All portfolio rationalization recommendations, Gartner TIME classifications (Tolerate, Invest, Migrate, Eliminate), multi-criteria decision analysis (MCDA) rankings, and application decommissioning projections computed by Vedanam represent POTENTIAL AVOIDABLE COST SCENARIOS, NOT GUARANTEED CASH LIQUIDITY.',
        isWarning: true
      },
      {
        heading: '2.2 Contractual & Overhead Realities',
        text: 'The enterprise user acknowledges that gross annual contract spend cannot be mechanically translated into instantaneous cash recovery. Avoidable cost realization is strictly subject to: (a) non-cancelable multi-year vendor contract lock-ins and minimum spend commitments; (b) contractual early-termination penalties; (c) absorption of retained shared cloud infrastructure, cluster licensing, and virtualization overhead; and (d) human capital retraining and data migration latency.'
      },
      {
        heading: '2.3 Mandatory Executive Reporting Disclosures',
        text: 'Any internal board presentations, executive memos, or financial disclosures derived from Vedanam rationalization modules MUST explicitly label modeled figures as "Potential Avoidable Cost (Gross / Net of Contractual Overhead)" rather than "Guaranteed Bank Savings".'
      }
    ],
    keyTakeaway: 'Never present rationalization numbers as guaranteed cash; contractual lock-ins and platform overhead must be audited.'
  },
  {
    id: 'article-03',
    number: 'Article 03',
    title: 'Technology Value Realization (TVR) & Associative Causality',
    category: 'guardrails',
    badge: 'Value Realization',
    badgeClass: 'chip-mint',
    summary: 'Codifies the statistical boundary of project benefit realization, KPI linkages, and Stage-Gate governance models.',
    clauses: [
      {
        heading: '3.1 Statistical Association vs. Direct Mono-Causality',
        text: 'Project benefit realization calculations, Difference-in-Differences econometrics, benefit realization waterfalls, and Stage-Gate KPI linkage graphs document STATISTICAL AND TEMPORAL ASSOCIATIONS between technology initiatives and business performance metrics. They do not constitute proof of mono-causal attribution.'
      },
      {
        heading: '3.2 Confounding Enterprise Variables',
        text: 'In complex enterprise environments, shifts in business outcomes (such as customer churn, checkout conversion, or operational latency) are co-determined by marketing campaigns, macroeconomics, pricing restructuring, and competitor movements. The enterprise agrees not to claim sole attribution of broad commercial outcomes to discrete IT projects without controlled econometric validation.'
      },
      {
        heading: '3.3 Proportional Capability Attribution',
        text: 'Capability cost allocations computed via the TVI engine use strict proportional attribution (dividing application burden across mapped capabilities such that sum of proportions equals 1.000). Users are prohibited from double-counting shared services across business units.'
      }
    ],
    keyTakeaway: 'Technology investments are modeled as associated with KPI shifts, preventing ungrounded single-factor causal claims.'
  },
  {
    id: 'article-04',
    number: 'Article 04',
    title: 'Algorithmic Truth, Zero Reconciliation & Determinism',
    category: 'determinism',
    badge: 'Deterministic Truth',
    badgeClass: 'chip-sky',
    summary: 'Establishes the mathematical integrity standards, mass-balance conservation rules, and reproducible seed determinism.',
    clauses: [
      {
        heading: '4.1 Zero-Reconciliation Mass Balance Mandate',
        text: 'Vedanam enforces an uncompromising mass-balance conservation principle: the sum of General Ledger cost pool rows must equal the sum of IT tower allocations, which must equal fully-burdened application TCO, which must equal business capability attributions. The financial drift must remain exactly zero (Delta = $0.00). Any intentional alteration of the audit log table (financial_audit_log.parquet) invalidates compliance certificates.',
        isHighlight: true
      },
      {
        heading: '4.2 Seed 42 Reproducibility Protocol',
        text: 'All synthetic enterprise generation, non-Gaussian heavy-tailed distributions (Log-Normal telemetry, Weibull outage aging, Beta allocation ratios), and Sklar\'s copula correlation matrices are pinned to Seed 42 (config.yaml). This guarantees 100% deterministic, bit-for-bit reproducible results across operating environments.'
      },
      {
        heading: '4.3 Topological Integrity & DAG Verification',
        text: 'Dependency structures are continuously validated as Directed Acyclic Graphs (DAGs) using Tarjan Strongly Connected Components (SCC) and Kahn topological sorting to detect and flag cyclical dependencies before blast-radius cascades are calculated.'
      }
    ],
    keyTakeaway: 'Ledger mass balance is conserved to Delta = $0.00; calculations are deterministically verifiable and reproducible.'
  },
  {
    id: 'article-05',
    number: 'Article 05',
    title: 'Dual-Mode AI Governance & Zero Hallucination Standards',
    category: 'determinism',
    badge: 'AI Governance',
    badgeClass: 'chip-rose',
    summary: 'Governs the dual-mode natural language intelligence architecture, preventing arbitrary code execution and requiring human-in-the-loop sign-off.',
    clauses: [
      {
        heading: '5.1 Deterministic Rules Mode (Default Operational Standard)',
        text: 'By default, all natural language graph queries and decision summaries operate under deterministic rule-based algorithms with zero LLM hallucination risk. Queries map to pre-compiled, parameter-sanitized NetworkX graph traversals and DuckDB SQL queries.'
      },
      {
        heading: '5.2 Optional Local Ollama LLM Mode',
        text: 'When the user activates local Ollama integration (e.g. llama3.1:8b), prompts are dispatched strictly to local loopback (http://localhost:11434). Responses generated via probabilistic models are advisory only and must be treated as auxiliary analysis rather than audited truth.'
      },
      {
        heading: '5.3 Zero-Code Execution & Injection Defense',
        text: 'Vedanam strictly prohibits executing arbitrary unverified code or untrusted SQL from natural language inputs. All inputs are sanitized against prompt injection patterns and restricted to read-only query templates.'
      },
      {
        heading: '5.4 Human-in-the-Loop Decommissioning Sign-Off',
        text: 'No recommendation provided by Vedanam or TVI may automatically trigger automated server termination, vendor contract cancellation, or database dropping without explicit multi-party human executive authorization.'
      }
    ],
    keyTakeaway: 'AI models operate under strict parameterization; critical decommissioning mandates human executive authorization.'
  },
  {
    id: 'article-06',
    number: 'Article 06',
    title: 'Intellectual Property, Ontologies & Reference Archetypes',
    category: 'scope',
    badge: 'Intellectual Property',
    badgeClass: 'chip-lavender',
    summary: 'Defines rights, copyrights, and permitted usage of the TVI Enterprise Ontology, mathematical models, and sensory design system.',
    clauses: [
      {
        heading: '6.1 Proprietary Architectural Design System',
        text: 'The Vedanam visual identity, glassmorphic layout tokens, 3D constellation WebGL shaders, 432Hz harmonic audio synthesizer, and interactive hotspot room mechanics are proprietary works. Users may not clone, rebrand, or redistribute the sensory design system as a standalone commercial SaaS without written authorization.'
      },
      {
        heading: '6.2 Enterprise Ontology & Open Analytical Frameworks',
        text: 'The TVI Enterprise Ontology (ontology.yaml), mathematical formulas (TOPSIS MCDA, Lorenz concentration curves, betweenness centrality, difference-in-differences), and the 12-notebook educational curriculum are made available for internal enterprise evaluation and technological governance.'
      },
      {
        heading: '6.3 Canonical Archetypes',
        text: 'The reference application archetypes (ATHENA Core Retail Banking, ONYX Global Consumer Payments, ORBIS Enterprise Analytics Lakehouse) are fictitious synthetic representations provided for architectural benchmarking.'
      }
    ],
    keyTakeaway: 'The sensory design system and ontology are protected; enterprises have full freedom to adapt models internally.'
  },
  {
    id: 'article-07',
    number: 'Article 07',
    title: 'Enterprise Custody & Local Security Responsibilities',
    category: 'legal',
    badge: 'Security Custody',
    badgeClass: 'chip-peach',
    summary: 'Outlines the deploying enterprise\'s duties regarding data protection, encryption-at-rest, and database file access control.',
    clauses: [
      {
        heading: '7.1 Custody of Local Database & Artifacts',
        text: 'Because Vedanam operates entirely in-process, the deploying enterprise maintains exclusive custody and responsibility for the security, encryption, and access controls of local database files (database/tvi.duckdb), Parquet tables (data/parquet/), and configuration secrets (config.yaml).'
      },
      {
        heading: '7.2 Backup & Disaster Recovery',
        text: 'Vedanam does not maintain cloud backups or remote replicas of your enterprise data. Enterprises are solely responsible for executing periodic backups of local analytical directories to secure enterprise storage repositories.'
      },
      {
        heading: '7.3 Air-Gapped Environment Compliance',
        text: 'Vedanam is verified for deployment in fully air-gapped, zero-egress military-grade and financial-grade internal intranets. The user is responsible for ensuring internal network firewall policies conform to enterprise standards.'
      }
    ],
    keyTakeaway: 'You own and control your local storage; ensure regular backups and workstation access security.'
  },
  {
    id: 'article-08',
    number: 'Article 08',
    title: 'Limitation of Liability, Disclaimers & Governing Law',
    category: 'legal',
    badge: 'Legal & Compliance',
    badgeClass: 'chip-rose',
    summary: 'Standard enterprise limitation of liability, exclusion of consequential damages, and dispute resolution.',
    clauses: [
      {
        heading: '8.1 "As Is" Decision Support Disclaimer',
        text: 'VEDANAM AND THE TVI ENGINE ARE PROVIDED "AS IS" AND "AS AVAILABLE", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. VEDANAM IS A DECISION-SUPPORT INSTRUMENT AND DOES NOT CONSTITUTE CERTIFIED AUDIT, LEGAL, TAX, OR FINANCIAL FIDUCIARY ADVICE.',
        isWarning: true
      },
      {
        heading: '8.2 Exclusion of Consequential Damages',
        text: 'In no event shall the authors, maintainers, or contributors of Vedanam be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services, loss of use, data, or profits, business interruption, or vendor contract breach damages) arising from portfolio rationalization decisions or dependency failure simulations.'
      },
      {
        heading: '8.3 Severability & Entire Agreement',
        text: 'If any provision of these Terms is held to be invalid or unenforceable, such provision shall be severed and the remaining provisions shall continue in full force. These Terms constitute the entire operational agreement between the user and the Vedanam project.'
      }
    ],
    keyTakeaway: 'The platform is a decision-support instrument; users retain final fiduciary and architectural accountability.'
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
    const url = `${window.location.origin}/terms#${id}`
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
    '.terms-article-card',
    { opacity: 0, y: 30, scale: 0.98 },
    { opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: 0.08, ease: 'power3.out' }
  )
}

onMounted(() => {
  if (!process.client || !termsPageRef.value) return
  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    const heroTl = gsap.timeline({ delay: 0.1 })
    heroTl
      .fromTo('.back-pill-link', { opacity: 0, x: -25 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power3.out' })
      .fromTo('.terms-hero .section-tag', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }, '-=0.4')
      .fromTo('.terms-main-hed', { opacity: 0, y: 35, filter: 'blur(5px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.9, ease: 'power4.out' }, '-=0.3')
      .fromTo('.terms-subhed', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
      .fromTo('.vitals-badges-strip', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, '-=0.4')
      .fromTo('.terms-filter-bar', { opacity: 0, y: 20, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'back.out(1.4)' }, '-=0.3')

    animateCards()
  }, termsPageRef.value)
})

onUnmounted(() => {
  gsapCtx?.revert()
})
</script>

<template>
  <div ref="termsPageRef" class="terms-page">
    <div class="container terms-container">
      <!-- 1. Hero & Breadcrumbs -->
      <header class="terms-hero">
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

        <span class="section-tag">Enterprise Governance & Legal Terms</span>
        <h1 class="terms-main-hed">Terms of Service & Operational Governance</h1>
        <p class="terms-subhed">
          Operational rules, analytical boundaries, avoidable cost doctrines, and mass-balance mandates governing the deployment and utilization of the Vedanam Sensory Digital Twin and Technology Value Intelligence (TVI) engine.
        </p>

        <!-- Vitals Badges Row -->
        <div class="vitals-badges-strip">
          <span class="pastel-chip chip-lavender">Version 1.4 · Enterprise</span>
          <span class="pastel-chip chip-sky">Effective October 2026</span>
          <span class="pastel-chip chip-mint">Mass-Balance Guardrail (Δ = $0.00)</span>
          <span class="pastel-chip chip-peach">Avoidable Cost Protocol</span>
          <span class="pastel-chip chip-rose">Seed 42 Determinism</span>
        </div>

        <!-- Filter & Search Bar -->
        <div class="terms-filter-bar">
          <div class="filter-pills-row">
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'all' }"
              @click="setCategory('all')"
              @mouseenter="setCursor('ALL TERMS', 'default')"
              @mouseleave="resetCursor"
            >
              All Articles ({{ articles.length }})
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'scope' }"
              @click="setCategory('scope')"
              @mouseenter="setCursor('SCOPE', 'default')"
              @mouseleave="resetCursor"
            >
              Scope & IP
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'guardrails' }"
              @click="setCategory('guardrails')"
              @mouseenter="setCursor('GUARDRAILS', 'default')"
              @mouseleave="resetCursor"
            >
              Analytical Guardrails
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'determinism' }"
              @click="setCategory('determinism')"
              @mouseenter="setCursor('DETERMINISM', 'default')"
              @mouseleave="resetCursor"
            >
              Deterministic Truth
            </button>
            <button
              type="button"
              class="filter-pill"
              :class="{ active: activeCategory === 'legal' }"
              @click="setCategory('legal')"
              @mouseenter="setCursor('LEGAL', 'default')"
              @mouseleave="resetCursor"
            >
              Liability & Custody
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
              placeholder="Filter clauses, avoidability, mass-balance..."
            />
            <button v-if="searchQuery" type="button" class="clear-btn" @click="searchQuery = ''">✕</button>
          </div>
        </div>
      </header>

      <!-- 2. Architectural Guardrail Manifesto Callout -->
      <section class="manifesto-card">
        <div class="manifesto-header">
          <span class="manifesto-tag pastel-chip chip-lavender">Foundational Governance Principle</span>
          <h2 class="manifesto-title">The Three Pillars of Vedanam Analytical Truth</h2>
        </div>
        <div class="manifesto-grid">
          <div class="manifesto-box">
            <div class="box-badge pastel-chip chip-peach">Guardrail 01</div>
            <h3>Avoidable Cost ≠ Guaranteed Cash</h3>
            <p>
              Portfolio rationalization identifies <em>avoidable cost scenarios</em>. Gross IT contract sums cannot be instantaneously pocketed as cash due to multi-year vendor lock-ins, contract termination fees, and shared cluster overhead.
            </p>
          </div>
          <div class="manifesto-box">
            <div class="box-badge pastel-chip chip-mint">Guardrail 02</div>
            <h3>Association ≠ Mono-Causality</h3>
            <p>
              Value realization links projects to KPI shifts through <em>statistical association</em>. In complex corporate landscapes, no single software transformation can unilaterally claim 100% causal credit for commercial outcomes.
            </p>
          </div>
          <div class="manifesto-box">
            <div class="box-badge pastel-chip chip-sky">Guardrail 03</div>
            <h3>Zero Reconciliation Variance (Δ = $0.00)</h3>
            <p>
              DuckDB OLAP guarantees exact mathematical mass balance. Every allocated dollar across towers, apps, and capabilities ties out precisely to General Ledger records with zero spreadsheet reconciliation drift.
            </p>
          </div>
        </div>
      </section>

      <!-- 3. Articles Feed -->
      <main class="terms-articles-container">
        <article
          v-for="art in filteredArticles"
          :key="art.id"
          :id="art.id"
          class="terms-article-card"
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
                <span v-if="clause.isWarning" class="clause-tag warning-tag">Mandatory Guardrail</span>
                <span v-if="clause.isHighlight" class="clause-tag highlight-tag">Mathematical Standard</span>
              </h3>
              <p class="clause-text">{{ clause.text }}</p>
            </div>
          </div>

          <!-- Bottom Key Takeaway Strip -->
          <div class="article-takeaway-bar">
            <span class="takeaway-label">Key Governance Takeaway</span>
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

      <!-- 4. Contact & Governance Support Card -->
      <section class="governance-contact-card">
        <div class="contact-card-content">
          <div class="contact-text-col">
            <span class="section-tag">Enterprise Inquiries & Compliance</span>
            <h2 class="contact-hed">Need customized institutional governance terms?</h2>
            <p class="contact-desc">
              For enterprise legal audits, sovereign air-gapped deployment certifications, custom ontology integrations, or compliance with internal internal audit committees, contact our technology governance team.
            </p>
          </div>
          <div class="contact-action-col">
            <a
              href="mailto:governance@vedanam.pt"
              class="pill-btn-dark"
              @mouseenter="setCursor('EMAIL US', 'highlight'); playInteractChime(1.4)"
              @mouseleave="resetCursor"
            >
              Contact Governance Council ↗
            </a>
            <NuxtLink
              to="/privacy"
              class="pill-btn-light"
              @mouseenter="setCursor('PRIVACY', 'default'); playInteractChime(1.2)"
              @mouseleave="resetCursor"
            >
              Review Privacy Policy →
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
.terms-page {
  padding-top: 8rem;
  background-color: var(--bg-canvas);
  min-height: 100vh;
}

.terms-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 var(--container-padding) 5rem;
}

/* 1. Hero */
.terms-hero {
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

.terms-main-hed {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 4.4vw, 3.8rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.025em;
  color: #121316;
  margin-bottom: 1rem;
}

.terms-subhed {
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
.terms-filter-bar {
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
  background-image: radial-gradient(circle at 100% 0%, rgba(196, 181, 253, 0.08) 0%, rgba(23, 24, 29, 0) 65%);
}

.manifesto-header {
  margin-bottom: 2rem;
}

.manifesto-title {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 3.2vw, 2.4rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-top: 0.6rem;
}

.manifesto-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.8rem;
}

.manifesto-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 1.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.manifesto-box h3 {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: #ffffff;
}

.manifesto-box p {
  font-size: 0.92rem;
  line-height: 1.6;
  color: #b4b9c5;
}

/* 3. Articles Feed */
.terms-articles-container {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  margin-bottom: 4rem;
}

.terms-article-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: var(--glass-card-shadow);
  padding: clamp(2rem, 4.5vw, 3.5rem);
  transition: box-shadow var(--transition-fast);
  will-change: transform, opacity;
}

.terms-article-card:hover {
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
  border-left: 4px solid #0284c7;
  background: #f0f9ff;
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
  background: #e0f2fe;
  color: #0369a1;
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

/* 4. Contact Card */
.governance-contact-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: var(--glass-card-shadow);
  padding: clamp(2.5rem, 5vw, 4rem);
  margin-bottom: 4rem;
}

.contact-card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
}

.contact-text-col {
  max-width: 720px;
}

.contact-hed {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 3.2vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 0.8rem;
}

.contact-desc {
  font-size: 1.05rem;
  line-height: 1.65;
  color: #555966;
}

.contact-action-col {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  min-width: 260px;
}

@media (max-width: 1024px) {
  .manifesto-grid {
    grid-template-columns: 1fr;
  }
  .contact-card-content {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .terms-filter-bar {
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
