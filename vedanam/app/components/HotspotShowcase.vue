<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

interface Hotspot {
  id: string
  x: number // percentage
  y: number // percentage
  name: string
  spec: string
  tco: string
  deps: number
  tier: string
  status: 'Optimized' | 'Critical' | 'Under Review'
}

interface ProjectCard {
  id: string
  title: string
  space: string
  bgClass: string
  hotspots: Hotspot[]
}

const activeHotspot = ref<Hotspot | null>(null)
const activeProjectIndex = ref(0)
const sectionRef = ref<HTMLElement | null>(null)
const topSplitRef = ref<HTMLElement | null>(null)
const aboutCardRef = ref<HTMLElement | null>(null)

let gsapCtx: gsap.Context | null = null

const projects: ProjectCard[] = [
  {
    id: 'proj-1',
    title: 'Executive Decision Center & Infrastructure Topology',
    space: 'Governance & Value Realization Suite',
    bgClass: 'space-boardroom',
    hotspots: [
      {
        id: 'h1',
        x: 72,
        y: 42,
        name: 'Core ERP Platform [SAP/HANA]',
        spec: 'In-Memory OLAP · vCPU: 128 · RAM: 512GB · SLA: 99.99%',
        tco: '$4.2M / yr',
        deps: 14,
        tier: 'Tier 1 Critical',
        status: 'Critical'
      },
      {
        id: 'h2',
        x: 84,
        y: 48,
        name: 'Customer Digital Gateway',
        spec: 'Cloud-Native Kubernetes · Istio Mesh · 18k req/s',
        tco: '$890k / yr',
        deps: 6,
        tier: 'Tier 2 Operational',
        status: 'Optimized'
      },
      {
        id: 'h3',
        x: 52,
        y: 66,
        name: 'DuckDB OLAP Analytical Truth Core',
        spec: 'Vectorized In-Process OLAP · Parquet Storage',
        tco: '$1.1M / yr',
        deps: 9,
        tier: 'Tier 1 Analytical',
        status: 'Optimized'
      },
      {
        id: 'h4',
        x: 62,
        y: 38,
        name: 'Legacy Billing Engine (Sunsetting)',
        spec: 'Monolithic Architecture · Oracle 19c · Avoidable Spend',
        tco: '$2.4M / yr',
        deps: 4,
        tier: 'Tier 3 Sunsetting',
        status: 'Under Review'
      }
    ]
  },
  {
    id: 'proj-2',
    title: 'Cloud & Hybrid Infrastructure Constellation',
    space: 'Multi-Cloud & Microservices Grid',
    bgClass: 'space-retail',
    hotspots: [
      {
        id: 'h5',
        x: 48,
        y: 32,
        name: 'Global API Gateway & Service Mesh',
        spec: 'Envoy Proxy · Mutual TLS · Multi-Region Routing',
        tco: '$1.3M / yr',
        deps: 12,
        tier: 'Tier 1 Critical',
        status: 'Optimized'
      },
      {
        id: 'h6',
        x: 64,
        y: 45,
        name: 'Analytical Parquet Data Lake',
        spec: 'Columnar Storage · Distributed Caching · Sub-Second Query',
        tco: '$1.9M / yr',
        deps: 8,
        tier: 'Tier 2 Analytical',
        status: 'Optimized'
      },
      {
        id: 'h7',
        x: 76,
        y: 36,
        name: 'Identity & Governance IAM Core',
        spec: 'Zero-Trust Federation · SAML/OIDC · Audit Trail',
        tco: '$620k / yr',
        deps: 18,
        tier: 'Tier 2 Security',
        status: 'Optimized'
      }
    ]
  }
]

const openHotspot = (hotspot: Hotspot) => {
  activeHotspot.value = hotspot
  playInteractChime(1.4)
}

const closeHotspot = () => {
  activeHotspot.value = null
}

onMounted(() => {
  if (!process.client || !sectionRef.value) return
  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    // 1. Projects Top Split Story (Narrative -> Rotating Stamp -> Room Carousel -> Sonar Pins)
    if (topSplitRef.value) {
      const topTl = gsap.timeline({
        scrollTrigger: {
          trigger: topSplitRef.value,
          start: 'top 82%',
          end: 'bottom 15%',
          toggleActions: 'play reverse play reverse'
        }
      })

      topTl
        .fromTo('.projects-left-meta .section-tag', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' })
        .fromTo('.projects-left-meta .projects-title', { opacity: 0, y: 35 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power4.out' }, '-=0.4')
        .fromTo('.projects-left-meta .projects-desc', { opacity: 0, y: 25 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
        .fromTo('.rotating-stamp-wrapper', { opacity: 0, scale: 0.6, rotation: -60 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.9, ease: 'back.out(1.6)' }, '-=0.5')
        .fromTo('.projects-cards-carousel', { opacity: 0, x: 50, scale: 0.96 }, { opacity: 1, x: 0, scale: 1, duration: 0.9, ease: 'power3.out' }, '-=0.7')
        .fromTo('.hotspot-pin-wrapper', { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.5, stagger: 0.1, ease: 'back.out(2.2)' }, '-=0.3')
    }

    // 2. "About Us" / Commitment to Excellence Card Story
    if (aboutCardRef.value) {
      const aboutTl = gsap.timeline({
        scrollTrigger: {
          trigger: aboutCardRef.value,
          start: 'top 85%',
          end: 'bottom 15%',
          toggleActions: 'play reverse play reverse'
        }
      })

      aboutTl
        .fromTo(aboutCardRef.value, { opacity: 0, y: 50, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: 'power3.out' })
        .fromTo(
          aboutCardRef.value.querySelectorAll('.section-tag, .about-title, .about-desc, .pill-btn-light'),
          { opacity: 0, y: 25 },
          { opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: 'power3.out' },
          '-=0.6'
        )
    }
  }, sectionRef.value)
})

onUnmounted(() => {
  gsapCtx?.revert()
})
</script>

<template>
  <section ref="sectionRef" class="ledup-projects-section" id="projects">
    <div class="container">
      <!-- Top Split Header & Interactive Slider (Exact ledup.pt layout in English) -->
      <div ref="topSplitRef" class="projects-top-split">
        <!-- Left: Tag, Title, Subtitle, and Rotating Stamp Badge -->
        <div class="projects-left-meta">
          <span class="section-tag">Projects</span>
          <h2 class="projects-title">Ideas that illuminate the path forward.</h2>
          <p class="projects-desc">
            Explore bespoke architectural solutions, engineered to respond with precision to the unique requirements and characteristics of every enterprise domain.
          </p>

          <!-- Rotating Circular Drag Badge (ledup.pt exact feature) -->
          <div
            class="rotating-stamp-wrapper"
            @mouseenter="setCursor('DRAG SLIDE', 'highlight'); playInteractChime(1.2)"
            @mouseleave="resetCursor"
            @click="activeProjectIndex = (activeProjectIndex + 1) % projects.length"
          >
            <svg class="stamp-svg" viewBox="0 0 160 160" width="140" height="140">
              <defs>
                <path
                  id="circlePath"
                  d="M 80, 80 m -58, 0 a 58,58 0 1,1 116,0 a 58,58 0 1,1 -116,0"
                />
              </defs>
              <text class="stamp-text">
                <textPath href="#circlePath" startOffset="0%">
                  • DRAG TO EXPLORE MORE VALUE INITIATIVES
                </textPath>
              </text>
            </svg>
            <div class="stamp-center-arrow">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Right: Project Cards with Interactive Hotspots Pins -->
        <div class="projects-cards-carousel">
          <div
            v-for="(proj, idx) in projects"
            :key="proj.id"
            class="project-room-card"
            :class="[proj.bgClass, { 'is-active-slide': idx === activeProjectIndex }]"
          >
            <!-- Hotspot Pins -->
            <div
              v-for="hs in proj.hotspots"
              :key="hs.id"
              class="hotspot-pin-wrapper"
              :style="{ left: `${hs.x}%`, top: `${hs.y}%` }"
              @mouseenter="openHotspot(hs)"
              @click.stop="openHotspot(hs)"
            >
              <!-- Outer Radar Pulse Ring -->
              <span class="hotspot-pulse-ring" />
              <!-- Inner White Dot with Dark Ring -->
              <span class="hotspot-white-dot" />

              <!-- Floating Tooltip Card -->
              <transition name="pop">
                <div v-if="activeHotspot?.id === hs.id" class="hotspot-tooltip-card" @click.stop>
                  <div class="tooltip-top-row">
                    <span class="tooltip-tier">{{ hs.tier }}</span>
                    <button type="button" class="tooltip-close" @click="closeHotspot">✕</button>
                  </div>
                  <h4 class="tooltip-name">{{ hs.name }}</h4>
                  <p class="tooltip-spec">{{ hs.spec }}</p>
                  <div class="tooltip-metrics-row">
                    <div class="metric-col">
                      <span class="m-val">{{ hs.tco }}</span>
                      <span class="m-lbl">Burdened TCO</span>
                    </div>
                    <div class="metric-col">
                      <span class="m-val">{{ hs.deps }}</span>
                      <span class="m-lbl">Dependencies</span>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom: "About Us" / "Commitment to Excellence" (Exact ledup.pt layout in English) -->
      <div ref="aboutCardRef" class="about-commitment-card" id="about-us">
        <span class="section-tag">About Us</span>
        <h3 class="about-title">Commitment to Excellence</h3>
        <p class="about-desc">
          Pioneering proactive governance for modern enterprises: uniting the columnar analytical speed of DuckDB, the relationship intelligence of NetworkX, and auditable TBM realization aligned to executive decision-makers.
        </p>
        <NuxtLink
          to="/docs"
          class="pill-btn-light"
          @mouseenter="setCursor('LEARN MORE', 'highlight'); playInteractChime(1.15)"
          @mouseleave="resetCursor"
        >
          <span>Learn More ↗</span>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ledup-projects-section {
  padding: 6rem 0;
  background-color: var(--bg-canvas);
  position: relative;
  overflow: hidden;
}

/* Split Header & Slider */
.projects-top-split {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 3.5rem;
  align-items: center;
  margin-bottom: 7rem;
}

.projects-left-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.projects-title {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.2vw, 2.25rem);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 1rem;
  max-width: 22ch;
}

.projects-desc {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #555966;
  font-weight: 400;
  margin-bottom: 2.5rem;
  max-width: 58ch;
}

/* Rotating Stamp Badge (ledup.pt exact feature) */
.rotating-stamp-wrapper {
  position: relative;
  width: 140px;
  height: 140px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stamp-svg {
  animation: rotateBadge 16s linear infinite;
  transform-origin: center;
}

@keyframes rotateBadge {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.stamp-text {
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.16em;
  fill: #8c909e;
  text-transform: uppercase;
}

.stamp-center-arrow {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #121316;
  transition: transform 0.25s ease;
}

.rotating-stamp-wrapper:hover .stamp-center-arrow {
  transform: translateX(5px);
}

/* Projects Cards Carousel with Hotspots */
.projects-cards-carousel {
  position: relative;
  width: 100%;
  height: clamp(480px, 40vw, 650px);
  border-radius: var(--radius-card);
  overflow: hidden;
  box-shadow: 0 20px 48px -12px rgba(0, 0, 0, 0.12);
}

.project-room-card {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-card);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.6s var(--ease-expo);
  background-size: cover;
  background-position: center;
}

.project-room-card.is-active-slide {
  opacity: 1;
  pointer-events: auto;
}

.space-boardroom {
  background-color: #121318;
  background-image: 
    linear-gradient(180deg, rgba(18, 19, 24, 0.2) 0%, rgba(18, 19, 24, 0.75) 100%),
    url('/images/hotspot_room_01.jpg');
  background-size: cover;
  background-position: center;
}

.space-retail {
  background-color: #14151a;
  background-image: 
    radial-gradient(circle at 65% 35%, rgba(196, 181, 253, 0.22) 0%, rgba(18, 19, 24, 0.95) 75%),
    linear-gradient(135deg, #1f212a 0%, #0e0f12 100%);
  background-size: cover;
  background-position: center;
}

/* Interactive Hotspot Pins */
.hotspot-pin-wrapper {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 20;
}

.hotspot-pulse-ring {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.7);
  animation: hotspotRadar 2.2s cubic-bezier(0.25, 0.1, 0.25, 1) infinite;
  pointer-events: none;
}

@keyframes hotspotRadar {
  0% {
    transform: scale(0.6);
    opacity: 1;
  }
  100% {
    transform: scale(1.8);
    opacity: 0;
  }
}

.hotspot-white-dot {
  display: block;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background-color: #ffffff;
  border: 3px solid #16171d;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  transition: transform 0.25s ease;
}

.hotspot-pin-wrapper:hover .hotspot-white-dot {
  transform: scale(1.25);
}

/* Hotspot Glass Tooltip Card */
.hotspot-tooltip-card {
  position: absolute;
  bottom: calc(100% + 14px);
  left: 50%;
  transform: translateX(-50%);
  width: 280px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 18px;
  padding: 1rem 1.15rem;
  box-shadow: 0 16px 40px -8px rgba(0, 0, 0, 0.18);
  color: #121316;
  z-index: 50;
  pointer-events: auto;
}

.tooltip-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.tooltip-tier {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #7b808e;
}

.tooltip-close {
  font-size: 0.85rem;
  color: #959aa8;
}

.tooltip-name {
  font-size: 0.92rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.25rem;
}

.tooltip-spec {
  font-size: 0.76rem;
  color: #555966;
  margin-bottom: 0.75rem;
}

.tooltip-metrics-row {
  display: flex;
  gap: 1.25rem;
  padding-top: 0.65rem;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.metric-col {
  display: flex;
  flex-direction: column;
}

.m-val {
  font-size: 0.86rem;
  font-weight: 700;
  color: #121316;
}

.m-lbl {
  font-size: 0.68rem;
  color: #8c909e;
}

/* About / Commitment to Excellence */
.about-commitment-card {
  text-align: center;
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.about-title {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.2vw, 2.25rem);
  font-weight: 500;
  color: #121316;
  letter-spacing: -0.02em;
  margin-bottom: 1rem;
  max-width: 24ch;
}

.about-desc {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #555966;
  font-weight: 400;
  margin-bottom: 2rem;
  max-width: 65ch;
}

@media (max-width: 900px) {
  .projects-top-split {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
}
</style>
