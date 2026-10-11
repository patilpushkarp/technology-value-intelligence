<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useTVIData } from '~/composables/useTVIData'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()
const { enterpriseStats } = useTVIData()

const activeCard = ref<string | null>(null)
const sectionRef = ref<HTMLElement | null>(null)
const headerRef = ref<HTMLElement | null>(null)
const rowTopRef = ref<HTMLElement | null>(null)
const rowBottomRef = ref<HTMLElement | null>(null)

let gsapCtx: gsap.Context | null = null

onMounted(() => {
  if (!process.client || !sectionRef.value) return
  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    // 1. Header Reveal as user reaches Highlights
    if (headerRef.value) {
      const headerTl = gsap.timeline({
        scrollTrigger: {
          trigger: headerRef.value,
          start: 'top 85%',
          end: 'bottom 15%',
          toggleActions: 'play reverse play reverse'
        }
      })
      headerTl
        .fromTo('.bento-header-center .section-tag', { opacity: 0, y: 22 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' })
        .fromTo('.bento-header-center .bento-title', { opacity: 0, y: 35 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power4.out' }, '-=0.4')
        .fromTo('.bento-header-center .bento-desc', { opacity: 0, y: 25 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
    }

    // 2. Row 1 Story (Foundation Archetypes: Reference App, Athena Core, 102 Nodes, Governance)
    if (rowTopRef.value) {
      const rowTopTl = gsap.timeline({
        scrollTrigger: {
          trigger: rowTopRef.value,
          start: 'top 82%',
          end: 'bottom 12%',
          toggleActions: 'play reverse play reverse'
        }
      })
      rowTopTl.fromTo(
        '.bento-row-top .bento-card',
        { opacity: 0, y: 55, scale: 0.94 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.85,
          stagger: 0.12,
          ease: 'power3.out'
        }
      )
      .fromTo(
        '.luminaire-athena',
        { scale: 0.8, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.6, ease: 'back.out(1.5)' },
        '-=0.5'
      )
      .fromTo(
        '.stat-huge-number',
        { scale: 0.8, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(1.6)' },
        '-=0.5'
      )
    }

    // 3. Row 2 Story (Engines of Intelligence: ONYX Columnar, CATALOG 2026, ORBIS Graph)
    if (rowBottomRef.value) {
      const rowBottomTl = gsap.timeline({
        scrollTrigger: {
          trigger: rowBottomRef.value,
          start: 'top 82%',
          end: 'bottom 12%',
          toggleActions: 'play reverse play reverse'
        }
      })
      rowBottomTl.fromTo(
        '.bento-row-bottom .bento-card',
        { opacity: 0, y: 55, scale: 0.94 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.85,
          stagger: 0.14,
          ease: 'power3.out'
        }
      )
      .fromTo(
        '.luminaire-onyx rect',
        { scaleY: 0, transformOrigin: 'bottom center', opacity: 0 },
        { scaleY: 1, opacity: 1, duration: 0.5, stagger: 0.08, ease: 'power2.out' },
        '-=0.4'
      )
      .fromTo(
        '.luminaire-orbis circle',
        { scale: 0, transformOrigin: 'center', opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.6, stagger: 0.06, ease: 'back.out(1.7)' },
        '-=0.4'
      )
    }
  }, sectionRef.value)
})

onUnmounted(() => {
  gsapCtx?.revert()
})
</script>

<template>
  <section ref="sectionRef" class="ledup-bento-section" id="highlights">
    <div class="container">
      <!-- Centered Section Header (Exact ledup.pt layout in English) -->
      <div ref="headerRef" class="bento-header-center">
        <span class="section-tag">Highlights</span>
        <h2 class="bento-title">The right intelligence at the right moment.</h2>
        <p class="bento-desc">
          Instant access to technical sheets, unit economics, and rationalization catalogs. Transparent data structures driving confident, audit-ready executive decisions.
        </p>
      </div>

      <!-- 7-Card Bento Grid Layout (Exact ledup.pt structure) -->
      <div class="bento-grid-wrapper">
        <!-- ROW 1 -->
        <div ref="rowTopRef" class="bento-row bento-row-top">
          <!-- Card 1: Architectural Image Card with Bottom Text & Arrow -->
          <div
            class="bento-card card-photo-left"
            @mouseenter="setCursor('SPECS', 'highlight'); playInteractChime(1.15)"
            @mouseleave="resetCursor"
          >
            <div class="card-photo-bg img-modern-office" />
            <div class="card-photo-scrim" />
            <div class="card-photo-footer">
              <div class="footer-text">
                <span class="pastel-chip chip-mint bento-mini-chip">Feature Benchmark</span>
                <h3 class="card-hed-light">Reference Application</h3>
                <p class="card-sub-light">Inspect our canonical archetype architectures with 3D local subgraphs and what-if simulation.</p>
              </div>
              <NuxtLink to="/reference-application" class="circular-arrow-btn" aria-label="Open Reference Application">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M7 17L17 7H7M17 7V17" />
                </svg>
              </NuxtLink>
            </div>
          </div>

          <!-- Card 2: Pure White Product Card (ATHENA Engine) -->
          <div
            class="bento-card card-white-product"
            @mouseenter="setCursor('ATHENA', 'default'); playInteractChime(1.2)"
            @mouseleave="resetCursor"
          >
            <div class="product-render-box">
              <div class="product-luminaire-3d luminaire-athena">
                <!-- Isometric Multi-Tier Analytics Core Vector -->
                <svg width="130" height="95" viewBox="0 0 140 100" fill="none">
                  <!-- Bottom Tier -->
                  <path d="M70 65 L115 45 L70 25 L25 45 Z" fill="#242630" />
                  <path d="M25 45 L70 65 L70 78 L25 58 Z" fill="#181920" />
                  <path d="M115 45 L70 65 L70 78 L115 58 Z" fill="#1f212a" />
                  <!-- Middle Analytical Tier (Pastel Mint Accent) -->
                  <path d="M70 48 L105 32 L70 16 L35 32 Z" fill="#a7f3d0" fill-opacity="0.85" />
                  <path d="M35 32 L70 48 L70 56 L35 40 Z" fill="#6ee7b7" />
                  <path d="M105 32 L70 48 L70 56 L105 40 Z" fill="#34d399" />
                  <!-- Top In-Memory Core (Pastel Lavender Accent) -->
                  <path d="M70 30 L95 18 L70 6 L45 18 Z" fill="#c4b5fd" />
                  <circle cx="70" cy="18" r="4" fill="#ffffff" />
                </svg>
              </div>
            </div>
            <div class="product-title-row">
              <span class="product-name">ATHENA Analytics Node</span>
            </div>
          </div>

          <!-- Card 3: Soft Pastel Stat Card (102 Nodes in Production) -->
          <div
            class="bento-card card-stat-pastel"
            @mouseenter="setCursor('102 NODES', 'highlight'); playInteractChime(1.3)"
            @mouseleave="resetCursor"
          >
            <div class="stat-content">
              <span class="stat-huge-number">102</span>
              <span class="stat-label-text">Production enterprise nodes</span>
            </div>
          </div>

          <!-- Card 4: Dark Architectural Card (Governance Workspace) -->
          <div
            class="bento-card card-photo-right"
            @mouseenter="setCursor('GOVERNANCE', 'highlight'); playInteractChime(1.15)"
            @mouseleave="resetCursor"
          >
            <div class="card-photo-bg img-boardroom" />
            <div class="card-photo-scrim" />
            <div class="card-photo-footer">
              <div class="footer-text">
                <h3 class="card-hed-light">Governance Portal</h3>
                <p class="card-sub-light">Access your executive decision workspace with end-to-end analytical auditability.</p>
              </div>
              <NuxtLink to="/docs#governance" class="circular-arrow-btn" aria-label="Open Governance Workspace">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M7 17L17 7H7M17 7V17" />
                </svg>
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- ROW 2 -->
        <div ref="rowBottomRef" class="bento-row bento-row-bottom">
          <!-- Card 5: Pure White Card (ONYX Vector Engine / DuckDB) -->
          <div
            class="bento-card card-white-product"
            @mouseenter="setCursor('ONYX ENGINE', 'default'); playInteractChime(1.2)"
            @mouseleave="resetCursor"
          >
            <div class="product-render-box">
              <div class="product-luminaire-3d luminaire-onyx">
                <!-- Columnar Vectorized Execution Matrix Vector -->
                <svg width="130" height="90" viewBox="0 0 140 100" fill="none">
                  <!-- Outer Enclosure -->
                  <rect x="20" y="16" width="100" height="68" rx="8" fill="#f8f9fa" stroke="#22242c" stroke-width="3" />
                  <!-- Columnar Slices -->
                  <rect x="30" y="26" width="16" height="48" rx="4" fill="#1e2028" />
                  <rect x="52" y="26" width="16" height="48" rx="4" fill="#a7f3d0" />
                  <rect x="74" y="26" width="16" height="48" rx="4" fill="#c4b5fd" />
                  <rect x="96" y="26" width="14" height="48" rx="4" fill="#fed7aa" />
                  <!-- Vector Execution Indicator Beam -->
                  <line x1="26" y1="50" x2="114" y2="50" stroke="#ffffff" stroke-width="2.5" stroke-dasharray="4 3" />
                </svg>
              </div>
            </div>
            <div class="product-title-row">
              <span class="product-name">ONYX Vector Engine (DuckDB OLAP)</span>
            </div>
          </div>

          <!-- Card 6: Wide Gradient Banner Card (Catalog 2026) -->
          <div
            class="bento-card card-wide-banner"
            @mouseenter="setCursor('CATALOG 2026', 'highlight'); playInteractChime(1.25)"
            @mouseleave="resetCursor"
          >
            <div class="banner-center-text">
              <span class="banner-eyebrow">VEDANAM</span>
              <h3 class="banner-huge-title">CATALOG 2026</h3>
            </div>
            <div class="banner-footer-row">
              <div>
                <span class="banner-label-hed">Catalog 2026</span>
                <p class="banner-label-sub">Explore our comprehensive rationalization matrix and value roadmap.</p>
              </div>
              <NuxtLink to="/docs#catalog" class="circular-arrow-btn" aria-label="Open Catalog">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M7 17L17 7H7M17 7V17" />
                </svg>
              </NuxtLink>
            </div>
          </div>

          <!-- Card 7: Pure White Card (ORBIS Knowledge Graph / NetworkX with Pill Tags) -->
          <div
            class="bento-card card-white-product card-orbis"
            @mouseenter="setCursor('ORBIS GRAPH', 'default'); playInteractChime(1.2)"
            @mouseleave="resetCursor"
          >
            <div class="product-render-box">
              <div class="product-luminaire-3d luminaire-orbis">
                <!-- Semantic Topology Constellation Vector -->
                <svg width="120" height="100" viewBox="0 0 130 110" fill="none">
                  <!-- Interconnecting Links -->
                  <line x1="65" y1="55" x2="35" y2="28" stroke="#d1d5db" stroke-width="2" />
                  <line x1="65" y1="55" x2="98" y2="34" stroke="#d1d5db" stroke-width="2" />
                  <line x1="65" y1="55" x2="88" y2="85" stroke="#d1d5db" stroke-width="2" />
                  <line x1="65" y1="55" x2="38" y2="80" stroke="#d1d5db" stroke-width="2" />
                  <!-- Satellite Nodes -->
                  <circle cx="35" cy="28" r="10" fill="#a7f3d0" stroke="#1f212a" stroke-width="2.5" />
                  <circle cx="98" cy="34" r="9" fill="#c4b5fd" stroke="#1f212a" stroke-width="2.5" />
                  <circle cx="88" cy="85" r="11" fill="#7dd3fc" stroke="#1f212a" stroke-width="2.5" />
                  <circle cx="38" cy="80" r="8" fill="#fed7aa" stroke="#1f212a" stroke-width="2.5" />
                  <!-- Central Knowledge Hub -->
                  <circle cx="65" cy="55" r="16" fill="#1e2028" stroke="#ffffff" stroke-width="3" />
                  <circle cx="65" cy="55" r="6" fill="#a7f3d0" />
                </svg>
              </div>
            </div>
            <div class="orbis-content-footer">
              <span class="product-name">ORBIS Topology Engine (NetworkX)</span>
              <div class="orbis-tags-row">
                <span class="pastel-chip chip-mint">Optimized TCO</span>
                <span class="pastel-chip chip-lavender">Zero Hallucination</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ledup-bento-section {
  padding: 6rem 0 5rem;
  background-color: var(--bg-canvas);
  position: relative;
}

/* Header */
.bento-header-center {
  text-align: center;
  max-width: 960px;
  margin: 0 auto 4rem;
}

.bento-title {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.2vw, 2.25rem);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 1rem;
  max-width: 24ch;
  margin-left: auto;
  margin-right: auto;
}

.bento-desc {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #555966;
  font-weight: 400;
  max-width: 65ch;
  margin: 0 auto;
}

/* Bento Grid */
.bento-grid-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.bento-row {
  display: grid;
  gap: 1.5rem;
}

.bento-row-top {
  grid-template-columns: 2.2fr 1.6fr 1.3fr 2fr;
}

.bento-row-bottom {
  grid-template-columns: 1.6fr 3.5fr 1.9fr;
}

/* Base Bento Card */
.bento-card {
  border-radius: var(--radius-card);
  overflow: hidden;
  position: relative;
  transition: box-shadow 0.35s var(--ease-expo);
  will-change: transform, opacity;
}

.bento-card:hover {
  box-shadow: var(--glass-card-hover-shadow);
}

/* Photo Cards (Card 1 & Card 4) */
.card-photo-left,
.card-photo-right {
  min-height: 340px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 2rem;
  box-shadow: var(--glass-card-shadow);
}

.card-photo-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transition: transform 0.7s var(--ease-expo);
}

.bento-card:hover .card-photo-bg {
  transform: scale(1.05);
}

.img-modern-office {
  background-color: #2b2e38;
  background-image: radial-gradient(circle at 70% 30%, #3e4454 0%, #17181f 100%);
}

.img-boardroom {
  background-color: #1c1d24;
  background-image: radial-gradient(circle at 40% 40%, #353846 0%, #111216 100%);
}

.card-photo-scrim {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.05) 0%, rgba(0, 0, 0, 0.78) 100%);
  pointer-events: none;
}

.card-photo-footer {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.card-hed-light {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.25;
  margin-bottom: 0.35rem;
}

.card-sub-light {
  font-size: 0.875rem;
  color: #d1d4de;
  line-height: 1.5;
  max-width: 380px;
}

/* White Product Cards (Card 2, Card 5, Card 7) */
.card-white-product {
  background-color: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: var(--glass-card-shadow);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 2.2rem 1.5rem 1.8rem;
  min-height: 340px;
}

.product-render-box {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.product-luminaire-3d {
  transition: transform 0.4s var(--ease-expo);
}

.bento-card:hover .product-luminaire-3d {
  transform: translateY(-6px) scale(1.05);
}

.product-title-row {
  width: 100%;
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #f1f2f5;
}

.product-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #121316;
  letter-spacing: -0.01em;
}

/* Pastel Stat Card (Card 3: 102 Nodes) */
.card-stat-pastel {
  background: linear-gradient(145deg, #fce7d2 0%, #fed7aa 60%, #fdba74 100%);
  box-shadow: var(--glass-card-shadow);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem 1.5rem;
  min-height: 340px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-huge-number {
  font-family: var(--font-display);
  font-size: clamp(3.2rem, 5.5vw, 4.5rem);
  font-weight: 500;
  line-height: 1.05;
  color: #7c2d12;
  letter-spacing: -0.03em;
  margin-bottom: 0.5rem;
}

.stat-label-text {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #9a3412;
  max-width: 140px;
  line-height: 1.35;
}

/* Wide Banner Card (Card 6: Catalog 2026) */
.card-wide-banner {
  background: linear-gradient(135deg, #2c2826 0%, #1f1d1c 50%, #171615 100%);
  box-shadow: var(--glass-card-shadow);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 2.5rem;
  min-height: 340px;
}

.banner-center-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: auto 0;
  text-align: center;
}

.banner-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  color: #fed7aa;
  text-transform: uppercase;
  margin-bottom: 0.6rem;
}

.banner-huge-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 3.5vw, 2.75rem);
  font-weight: 500;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.banner-footer-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 1.25rem;
}

.banner-label-hed {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #ffffff;
  display: block;
  margin-bottom: 0.25rem;
}

.banner-label-sub {
  font-size: 0.8125rem;
  color: #c2c4cb;
}

/* Orbis Card (Card 7) */
.card-orbis {
  padding: 2rem 1.5rem 1.5rem;
}

.orbis-content-footer {
  width: 100%;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f2f5;
}

.orbis-tags-row {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  justify-content: center;
}

@media (max-width: 1100px) {
  .bento-row-top {
    grid-template-columns: 1fr 1fr;
  }
  .bento-row-bottom {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .bento-row-top {
    grid-template-columns: 1fr;
  }
}
</style>
