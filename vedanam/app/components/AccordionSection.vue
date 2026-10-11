<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

interface PillarTab {
  id: string
  number: string
  title: string
  kpi: string
  kpiLabel: string
  desc: string
  pastelColor: string
  tagColor: string
  card1Title: string
  card2Title: string
}

const activeTabId = ref<string>('01')
const sectionRef = ref<HTMLElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const topSplitRef = ref<HTMLElement | null>(null)
const tabsStackRef = ref<HTMLElement | null>(null)

let gsapCtx: gsap.Context | null = null

const tabs: PillarTab[] = [
  {
    id: '01',
    number: '01.',
    title: 'INNOVATION',
    kpi: '100% Deterministic',
    kpiLabel: 'Semantic Graph + OLAP',
    desc: 'Fusing DuckDB dimensional tables with NetworkX relationship topology to eliminate budgeting assumptions and spreadsheet drift.',
    pastelColor: 'var(--pastel-lavender)',
    tagColor: 'chip-lavender',
    card1Title: 'Multi-Domain Graph Topology',
    card2Title: 'In-Memory Columnar OLAP Engine'
  },
  {
    id: '02',
    number: '02.',
    title: 'QUALITY',
    kpi: '4-Tier Integrity',
    kpiLabel: 'Automated Validation',
    desc: 'Continuous referential integrity verification, general ledger reconciliation audits, and automated MoM variance attribution.',
    pastelColor: 'var(--pastel-mint)',
    tagColor: 'chip-mint',
    card1Title: 'General Ledger Audit Reconciliation',
    card2Title: 'Month-over-Month Variance Tracing'
  },
  {
    id: '03',
    number: '03.',
    title: 'EFFICIENCY',
    kpi: '$2.3M Avoidable Spend',
    kpiLabel: 'MCDA Rationalization',
    desc: 'Immediate discovery of zombie applications, duplicative SaaS contracts, and idle compute clusters without operational disruption.',
    pastelColor: 'var(--pastel-sky)',
    tagColor: 'chip-sky',
    card1Title: 'TIME Rationalization Matrix',
    card2Title: 'Shared IT Overhead Optimization'
  },
  {
    id: '04',
    number: '04.',
    title: 'EXPERTISE',
    kpi: '12 Notebooks',
    kpiLabel: 'Full Curriculum',
    desc: 'Comprehensive research and engineering curriculum spanning 12 notebooks—from burdened unit economics to local zero-hallucination AI.',
    pastelColor: 'var(--pastel-peach)',
    tagColor: 'chip-peach',
    card1Title: 'Transitive Dependency Traversal',
    card2Title: 'Blast Radius Failure Decomposition'
  },
  {
    id: '05',
    number: '05.',
    title: 'SUSTAINABILITY',
    kpi: 'Carbon & FinOps',
    kpiLabel: 'GreenOps Efficiency',
    desc: 'Coupling carbon emissions and physical infrastructure power profiles directly to unit transactional cost and lifecycle stages.',
    pastelColor: 'var(--pastel-rose)',
    tagColor: 'chip-rose',
    card1Title: 'Datacenter Power & Carbon Profiling',
    card2Title: 'Application Lifecycle Sunsetting'
  }
]

const selectTab = (id: string) => {
  activeTabId.value = id
  playInteractChime(1.25)
}

onMounted(() => {
  if (!process.client || !sectionRef.value) return
  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    // 1. Giant Dark Container & Top Split (Manifesto + Dual Render Cards)
    if (topSplitRef.value && containerRef.value) {
      const topTl = gsap.timeline({
        scrollTrigger: {
          trigger: containerRef.value,
          start: 'top 82%',
          end: 'bottom 15%',
          toggleActions: 'play reverse play reverse'
        }
      })

      topTl
        .fromTo(containerRef.value, { opacity: 0, y: 55, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: 'power3.out' })
        .fromTo('.accordion-white-title', { opacity: 0, y: 35 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power4.out' }, '-=0.5')
        .fromTo('.accordion-white-desc', { opacity: 0, y: 25 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
        .fromTo('.accordion-right-cards .arch-render-card', { opacity: 0, x: 45, scale: 0.94 }, { opacity: 1, x: 0, scale: 1, duration: 0.8, stagger: 0.15, ease: 'power3.out' }, '-=0.6')
    }

    // 2. 5 Stacked Accordion Tabs (Cascade Story: 01 Innovation -> 02 Quality -> 03 Efficiency -> 04 Expertise -> 05 Sustainability)
    if (tabsStackRef.value) {
      const tabsTl = gsap.timeline({
        scrollTrigger: {
          trigger: tabsStackRef.value,
          start: 'top 80%',
          end: 'bottom 12%',
          toggleActions: 'play reverse play reverse'
        }
      })

      tabsTl.fromTo(
        '.accordion-tabs-stack .accordion-tab-bar',
        { opacity: 0, y: 45 },
        {
          opacity: 1,
          y: 0,
          duration: 0.75,
          stagger: 0.1,
          ease: 'power3.out'
        }
      )
    }
  }, sectionRef.value)
})

onUnmounted(() => {
  gsapCtx?.revert()
})
</script>

<template>
  <section ref="sectionRef" class="ledup-accordion-section" id="quality">
    <div class="container">
      <!-- Giant Dark Rounded Container (Exact ledup.pt design in English) -->
      <div ref="containerRef" class="giant-dark-container">
        <!-- TOP SECTION: Split Heading & Two Architectural Render Cards -->
        <div ref="topSplitRef" class="accordion-top-split">
          <!-- Left: Title & Description -->
          <div class="accordion-left-content">
            <h2 class="accordion-white-title">
              For those who demand more from technology value governance
            </h2>
            <p class="accordion-white-desc">
              VEDANAM transforms telemetry and ledger rows into breakthrough intelligence that makes a tangible difference. We anticipate strategic requirements and deliver visibility engineered to answer what you need today—and what you did not yet know you needed tomorrow. Performance, efficiency, and rigorous clarity built for those who demand more.
            </p>
          </div>

          <!-- Right: Two Side-by-Side Rounded Architectural Cards -->
          <div class="accordion-right-cards">
            <!-- Display Card 1 -->
            <div class="arch-render-card card-render-1">
              <div class="render-card-scrim" />
              <div class="render-card-content">
                <span class="render-card-badge">Topology</span>
                <h4 class="render-card-name">
                  {{ tabs.find(t => t.id === activeTabId)?.card1Title }}
                </h4>
              </div>
            </div>

            <!-- Display Card 2 -->
            <div class="arch-render-card card-render-2">
              <div class="render-card-scrim" />
              <div class="render-card-content">
                <span class="render-card-badge">Intelligence</span>
                <h4 class="render-card-name">
                  {{ tabs.find(t => t.id === activeTabId)?.card2Title }}
                </h4>
              </div>
            </div>
          </div>
        </div>

        <!-- BOTTOM SECTION: 5 Stacked Interactive Horizontal Tabs -->
        <div ref="tabsStackRef" class="accordion-tabs-stack">
          <div
            v-for="tab in tabs"
            :key="tab.id"
            class="accordion-tab-bar"
            :class="{ 'is-active-tab': activeTabId === tab.id }"
            @click="selectTab(tab.id)"
            @mouseenter="setCursor(tab.title, 'default')"
            @mouseleave="resetCursor"
          >
            <div class="tab-bar-main-row">
              <div class="tab-title-group">
                <span class="tab-num">{{ tab.number }}</span>
                <span class="tab-name">{{ tab.title }}</span>
              </div>
              <div class="tab-metric-preview" v-if="activeTabId === tab.id">
                <span class="tab-kpi-val">{{ tab.kpi }}</span>
                <span class="tab-kpi-lbl">{{ tab.kpiLabel }}</span>
              </div>
            </div>

            <!-- Expanded Description for Active Tab -->
            <div v-if="activeTabId === tab.id" class="tab-expanded-body">
              <p class="tab-desc-text">{{ tab.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ledup-accordion-section {
  padding: 4rem 0 6rem;
  background-color: var(--bg-canvas);
}

/* Giant Dark Rounded Container (Exact ledup.pt structure) */
.giant-dark-container {
  background-color: #1e1f26;
  background-image: radial-gradient(circle at 85% 15%, rgba(196, 181, 253, 0.08) 0%, rgba(30, 31, 38, 0) 60%);
  border-radius: var(--radius-container);
  padding: clamp(2.5rem, 5vw, 4.5rem);
  box-shadow: 0 24px 60px -15px rgba(0, 0, 0, 0.25);
  color: #ffffff;
  overflow: hidden;
}

/* Top Split */
.accordion-top-split {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 3.5rem;
  align-items: center;
  margin-bottom: 4rem;
}

.accordion-white-title {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.2vw, 2.25rem);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin-bottom: 1.2rem;
  max-width: 24ch;
}

.accordion-white-desc {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #b5b8c5;
  font-weight: 400;
  max-width: 65ch;
}

/* Right Render Cards */
.accordion-right-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.arch-render-card {
  height: 280px;
  border-radius: var(--radius-card);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1.5rem;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  transition: transform 0.4s var(--ease-expo);
}

.arch-render-card:hover {
  transform: translateY(-4px);
}

.card-render-1 {
  background-color: #2b2e38;
  background-image: 
    radial-gradient(ellipse at 50% 10%, rgba(196, 181, 253, 0.3) 0%, rgba(20, 21, 26, 0.9) 80%),
    linear-gradient(135deg, #373b49 0%, #1a1b22 100%);
}

.card-render-2 {
  background-color: #282a33;
  background-image: 
    radial-gradient(ellipse at 50% 10%, rgba(167, 243, 208, 0.3) 0%, rgba(20, 21, 26, 0.9) 80%),
    linear-gradient(135deg, #323642 0%, #181920 100%);
}

.render-card-scrim {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 30%, rgba(0, 0, 0, 0.85) 100%);
  pointer-events: none;
}

.render-card-content {
  position: relative;
  z-index: 2;
}

.render-card-badge {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--pastel-lavender);
  letter-spacing: 0.08em;
  display: block;
  margin-bottom: 0.35rem;
}

.render-card-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.35;
}

/* Bottom 5 Stacked Horizontal Tabs (Exact ledup.pt layout in English) */
.accordion-tabs-stack {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.accordion-tab-bar {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 18px;
  padding: 1.15rem 1.75rem;
  cursor: pointer;
  transition: background-color 0.25s ease, border-color 0.25s ease;
  will-change: transform, opacity;
}

.accordion-tab-bar:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.12);
}

.accordion-tab-bar.is-active-tab {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.22);
}

.tab-bar-main-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tab-title-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.tab-num {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 600;
  color: #8c909e;
}

.tab-name {
  font-family: var(--font-sans);
  font-size: 0.9375rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #ffffff;
}

.tab-metric-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tab-kpi-val {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--pastel-mint);
}

.tab-kpi-lbl {
  font-size: 0.75rem;
  color: #8c909e;
}

.tab-expanded-body {
  padding-top: 0.85rem;
  margin-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.tab-desc-text {
  font-size: 0.875rem;
  color: #b5b8c5;
  line-height: 1.6;
  max-width: 900px;
}

@media (max-width: 960px) {
  .accordion-top-split {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
}
</style>
