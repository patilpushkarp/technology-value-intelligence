<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

const footerRef = ref<HTMLElement | null>(null)
let gsapCtx: gsap.Context | null = null

onMounted(() => {
  if (!process.client || !footerRef.value) return
  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    const footerTl = gsap.timeline({
      scrollTrigger: {
        trigger: footerRef.value,
        start: 'top 88%',
        end: 'bottom 5%',
        toggleActions: 'play reverse play reverse'
      }
    })

    footerTl
      .fromTo('.footer-rounded-card', { opacity: 0, y: 70, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.95, ease: 'power3.out' })
      .fromTo('.footer-headline', { opacity: 0, y: 35 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power4.out' }, '-=0.6')
      .fromTo('.footer-col', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.1, ease: 'power3.out' }, '-=0.5')
      .fromTo('.footer-bottom-strip', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, '-=0.3')
  }, footerRef.value)
})

onUnmounted(() => {
  gsapCtx?.revert()
})
</script>

<template>
  <footer ref="footerRef" class="ledup-footer-wrapper">
    <!-- Massive Dark Rounded Container (Exact ledup.pt layout in English) -->
    <div class="footer-rounded-card">
      <div class="container footer-content-container">
        <!-- Huge Top Title -->
        <div class="footer-hero-hed">
          <h2 class="footer-headline">The confidence that illuminates your technology initiatives.</h2>
        </div>

        <!-- 4-Column Structured Directory -->
        <div class="footer-columns-grid">
          <!-- Col 1: Resources -->
          <div class="footer-col">
            <h4 class="col-title">Resources</h4>
            <ul class="col-links">
              <li>
                <a href="#highlights" @mouseenter="setCursor('WHAT IS NEW', 'default')">What's New</a>
              </li>
              <li>
                <a href="#highlights" @mouseenter="setCursor('BROCHURES', 'default')">Brochures</a>
              </li>
              <li>
                <NuxtLink to="/reference-application" @mouseenter="setCursor('REFERENCE APP', 'highlight')">Reference Application</NuxtLink>
              </li>
              <li>
                <a href="#highlights" @mouseenter="setCursor('CATALOG', 'default')">Catalog 2026</a>
              </li>
              <li>
                <NuxtLink to="/technical-specs" @mouseenter="setCursor('TECHNICAL SPECS', 'default')">Technical Specs</NuxtLink>
              </li>
            </ul>
          </div>

          <!-- Col 2: Information -->
          <div class="footer-col">
            <h4 class="col-title">Information</h4>
            <ul class="col-links">
              <li>
                <a href="#highlights" @mouseenter="setCursor('DECISION WORKSPACE', 'default')">Decision Workspace</a>
              </li>
              <li>
                <a href="#about-us" @mouseenter="setCursor('ABOUT US', 'default')">About Us</a>
              </li>
              <li>
                <NuxtLink to="/docs" @mouseenter="setCursor('METHODOLOGY', 'default')">TVR Methodology</NuxtLink>
              </li>
              <li>
                <NuxtLink to="/terms" @mouseenter="setCursor('TERMS', 'default')">Terms & Governance</NuxtLink>
              </li>
              <li>
                <NuxtLink to="/privacy" @mouseenter="setCursor('PRIVACY', 'default')">Privacy Policy</NuxtLink>
              </li>
            </ul>
          </div>

          <!-- Col 3: Categories -->
          <div class="footer-col">
            <h4 class="col-title">Categories</h4>
            <ul class="col-links">
              <li>
                <a href="#highlights" @mouseenter="setCursor('CORE APPS', 'default')">Core Applications</a>
              </li>
              <li>
                <a href="#highlights" @mouseenter="setCursor('GRAPH TOPOLOGY', 'default')">Graph Topology</a>
              </li>
              <li>
                <a href="#highlights" @mouseenter="setCursor('DUCKDB ENGINE', 'default')">DuckDB OLAP Engine</a>
              </li>
              <li>
                <a href="#projects" @mouseenter="setCursor('HOTSPOTS', 'default')">Projects & Hotspots</a>
              </li>
              <li>
                <a href="#quality" @mouseenter="setCursor('MCDA', 'default')">MCDA Rationalization</a>
              </li>
              <li>
                <NuxtLink to="/docs" @mouseenter="setCursor('SMART CONTROL', 'default')">Smart Control</NuxtLink>
              </li>
            </ul>
          </div>

          <!-- Col 4: Contact & Social -->
          <div class="footer-col col-contact">
            <div class="contact-entry">
              <a href="mailto:info@vedanam.pt" class="contact-email" @mouseenter="setCursor('EMAIL', 'highlight')">
                info@vedanam.pt
              </a>
            </div>
            <div class="contact-entry">
              <a href="https://github.com/patilpushkarp/technology-value-intelligence" target="_blank" rel="noopener noreferrer" class="contact-social" @mouseenter="setCursor('GITHUB', 'default')">
                GitHub Repository
              </a>
            </div>
            <div class="contact-entry">
              <NuxtLink to="/docs" class="contact-social" @mouseenter="setCursor('DOCUMENTATION', 'default')">
                Project Documentation
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Bottom Copyright Strip -->
        <div class="footer-bottom-strip">
          <p class="copyright-text">
            VEDANAM © 2026. All rights reserved.
          </p>
          <div class="legal-links">
            <NuxtLink to="/terms" @mouseenter="setCursor('TERMS', 'default')">Terms & Conditions</NuxtLink>
            <span class="legal-sep">·</span>
            <NuxtLink to="/privacy" @mouseenter="setCursor('PRIVACY', 'default')">Privacy Policy</NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.ledup-footer-wrapper {
  background-color: var(--bg-canvas);
  position: relative;
  width: 100%;
}

/* Giant Dark Rounded Top Container */
.footer-rounded-card {
  background-color: #14151a;
  background-image: radial-gradient(circle at 50% 0%, rgba(196, 181, 253, 0.06) 0%, rgba(20, 21, 26, 0) 70%);
  border-radius: var(--radius-container) var(--radius-container) 0 0;
  padding: clamp(3.5rem, 6vw, 5.5rem) 0 2.5rem;
  color: #ffffff;
  will-change: transform, opacity;
}

.footer-content-container {
  display: flex;
  flex-direction: column;
}

/* Huge Headline */
.footer-hero-hed {
  margin-bottom: 4rem;
}

.footer-headline {
  font-family: var(--font-display);
  font-size: clamp(2.25rem, 4.5vw, 4.25rem);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #ffffff;
  max-width: 22ch;
}

/* 4 Columns Grid */
.footer-columns-grid {
  display: grid;
  grid-template-columns: 1.2fr 1.2fr 1.5fr 1.2fr;
  gap: 3rem;
  padding-bottom: 4rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.col-title {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #ffffff;
  margin-bottom: 1.25rem;
}

.col-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin: 0;
  padding: 0;
}

.col-links a {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #9da0ab;
  transition: color 0.2s ease;
}

.col-links a:hover {
  color: #ffffff;
}

.col-contact {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.contact-email {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #ffffff;
  transition: color 0.2s ease;
}

.contact-email:hover {
  color: var(--pastel-lavender);
}

.contact-social {
  font-size: 0.875rem;
  color: #9da0ab;
  transition: color 0.2s ease;
}

.contact-social:hover {
  color: #ffffff;
}

/* Bottom Strip */
.footer-bottom-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 2rem;
  font-size: 0.8125rem;
  color: #717582;
}

.copyright-text {
  margin: 0;
}

.legal-links {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.legal-links a {
  color: #717582;
  transition: color 0.2s ease;
}

.legal-links a:hover {
  color: #ffffff;
}

.legal-sep {
  color: #4b4e58;
}

@media (max-width: 900px) {
  .footer-columns-grid {
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
}

@media (max-width: 550px) {
  .footer-columns-grid {
    grid-template-columns: 1fr;
  }
  .footer-bottom-strip {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>
