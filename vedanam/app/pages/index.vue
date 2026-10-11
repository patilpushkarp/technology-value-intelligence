<script setup lang="ts">
import { onMounted, nextTick } from 'vue'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import HeroSection from '~/components/HeroSection.vue'
import BentoGridSection from '~/components/BentoGridSection.vue'
import HotspotShowcase from '~/components/HotspotShowcase.vue'
import AccordionSection from '~/components/AccordionSection.vue'
import FooterSection from '~/components/FooterSection.vue'

onMounted(() => {
  if (process.client) {
    nextTick(() => {
      setTimeout(() => {
        ScrollTrigger.refresh()
      }, 200)
    })
  }
})
</script>

<template>
  <main class="vedanam-main-layout">
    <!-- 1. Hero Section (3D Linear Ceiling Luminaire & Bottom-Left Typography) -->
    <HeroSection />

    <!-- 2. Highlights (7-Card Architectural Bento Grid) -->
    <BentoGridSection />

    <!-- 3. Projects & Hotspots (Interactive Room Slider with Radar Pins & About Us) -->
    <HotspotShowcase />

    <!-- 4. Strategic Pillars (Giant Dark Container with 5 Interactive Pillars) -->
    <AccordionSection />

    <!-- 5. Footer (Giant Rounded Top Container & 4-Column Directory) -->
    <FooterSection />
  </main>
</template>

<style scoped>
.vedanam-main-layout {
  position: relative;
  width: 100%;
  overflow-x: hidden;
  background-color: var(--bg-canvas);
}
</style>
