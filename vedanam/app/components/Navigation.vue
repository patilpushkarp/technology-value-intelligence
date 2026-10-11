<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useTVIData } from '~/composables/useTVIData'
import { useCursor } from '~/composables/useCursor'

const { isAudioActive, toggleSound, playInteractChime } = useAudioSynth()
const { applications, selectedApp, selectApp } = useTVIData()
const { setCursor, resetCursor } = useCursor()

const isScrolled = ref(false)
const isAppDropdownOpen = ref(false)
const isSearchOpen = ref(false)
const isMobileMenuOpen = ref(false)
const searchQuery = ref('')

const onScroll = () => {
  if (process.client) {
    isScrolled.value = window.scrollY > 25
  }
}

const toggleAppDropdown = (state?: boolean) => {
  if (state !== undefined) {
    isAppDropdownOpen.value = state
  } else {
    isAppDropdownOpen.value = !isAppDropdownOpen.value
  }
}

const openSearch = () => {
  isSearchOpen.value = true
  playInteractChime(1.3)
}

const closeSearch = () => {
  isSearchOpen.value = false
}

const selectFromSearch = (app: any) => {
  selectApp(app.id)
  isSearchOpen.value = false
}

onMounted(() => {
  if (process.client) {
    window.addEventListener('scroll', onScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('scroll', onScroll)
  }
})
</script>

<template>
  <header class="ledup-header-fixed" :class="{ 'scrolled-header': isScrolled }">
    <div class="header-container">
      <!-- 1. Left: Bold Geometric Logo (LEDUP style) -->
      <NuxtLink
        to="/"
        class="header-brand-logo"
        @mouseenter="setCursor('VEDANAM', 'highlight'); playInteractChime(1.5)"
        @mouseleave="resetCursor"
      >
        <span class="logo-text">VEDANAM</span>
      </NuxtLink>

      <!-- 2. Center: Exact Floating Frosted Glass Capsule (ledup.pt Header_menu_container) -->
      <nav class="header-center-nav" aria-label="Main Navigation">
        <div class="frosted-glass-pill">
          <ul class="nav-links-row">
            <!-- Dropdown Item: Applications & Topology -->
            <li
              class="nav-item has-dropdown"
              @mouseenter="toggleAppDropdown(true)"
              @mouseleave="toggleAppDropdown(false)"
            >
              <button
                type="button"
                class="pill-nav-link dropdown-trigger"
                @mouseenter="setCursor('TOPOLOGY', 'default')"
                @mouseleave="resetCursor"
              >
                <span>Applications & Topology</span>
                <svg
                  class="chevron-icon"
                  :class="{ 'rotate-180': isAppDropdownOpen }"
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>

              <!-- Glassmorphism Dropdown Menu -->
              <transition name="dropdown-anim">
                <div v-if="isAppDropdownOpen" class="glass-dropdown-card">
                  <div class="dropdown-header">
                    <span class="dropdown-title">Monitored Applications</span>
                    <span class="dropdown-badge">{{ applications.length }} Nodes</span>
                  </div>
                  <div class="dropdown-list">
                    <button
                      v-for="app in applications.slice(0, 5)"
                      :key="app.id"
                      type="button"
                      class="dropdown-row-btn"
                      :class="{ 'is-selected': selectedApp.id === app.id }"
                      @click="selectApp(app.id); isAppDropdownOpen = false; playInteractChime(1.2)"
                    >
                      <div class="row-info">
                        <span class="row-name">{{ app.name }}</span>
                        <span class="row-tier">{{ app.tier }} · {{ app.capabilityCount }} Capabilities</span>
                      </div>
                      <span class="row-tco">${{ (app.tco / 1000000).toFixed(1) }}M</span>
                    </button>
                  </div>
                  <div class="dropdown-footer">
                    <NuxtLink to="/reference-application" class="dropdown-ref-pill" @click="isAppDropdownOpen = false">
                      <span>Explore Reference Application</span>
                      <span class="arrow">↗</span>
                    </NuxtLink>
                    <NuxtLink to="/#highlights" class="dropdown-more-link" @click="isAppDropdownOpen = false">
                      View Full Matrix →
                    </NuxtLink>
                  </div>
                </div>
              </transition>
            </li>

            <!-- Reference Application Link -->
            <li class="nav-item">
              <NuxtLink
                to="/reference-application"
                class="pill-nav-link nav-ref-link"
                @mouseenter="setCursor('REFERENCE APP', 'highlight'); playInteractChime(1.15)"
                @mouseleave="resetCursor"
              >
                <span>Reference App</span>
                <span class="nav-mini-badge">Archetype</span>
              </NuxtLink>
            </li>

            <!-- Technical Specs -->
            <li class="nav-item">
              <NuxtLink
                to="/technical-specs"
                class="pill-nav-link"
                @mouseenter="setCursor('TECH SPECS', 'highlight'); playInteractChime(1.1)"
                @mouseleave="resetCursor"
              >
                <span>Technical Specs</span>
              </NuxtLink>
            </li>

            <!-- About Us -->
            <li class="nav-item">
              <a
                href="/#about-us"
                class="pill-nav-link"
                @mouseenter="setCursor('ABOUT US', 'default'); playInteractChime(1.1)"
                @mouseleave="resetCursor"
              >
                About Us
              </a>
            </li>

            <!-- Documentation -->
            <li class="nav-item">
              <NuxtLink
                to="/docs"
                class="pill-nav-link"
                @mouseenter="setCursor('DOCUMENTATION', 'default'); playInteractChime(1.1)"
                @mouseleave="resetCursor"
              >
                Documentation
              </NuxtLink>
            </li>
          </ul>
        </div>
      </nav>

      <!-- 3. Right: Exact ledup.pt Control Cluster -->
      <div class="header-right-cluster">
        <!-- Pill Action Button: Runbook ↗ -->
        <NuxtLink
          to="/docs"
          class="header-action-pill"
          @mouseenter="setCursor('RUNBOOK', 'highlight'); playInteractChime(1.3)"
          @mouseleave="resetCursor"
        >
          <span>Runbook ↗</span>
        </NuxtLink>

        <!-- Circular Glass Search Button -->
        <button
          type="button"
          class="glass-icon-circle"
          @click="openSearch"
          @mouseenter="setCursor('SEARCH', 'default')"
          @mouseleave="resetCursor"
          title="Search Nodes & Technical Specs"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </button>

        <!-- Circular Glass Audio/Harmonic Button -->
        <button
          type="button"
          class="glass-icon-circle audio-toggle"
          :class="{ 'audio-active': isAudioActive }"
          @click="toggleSound"
          @mouseenter="setCursor(isAudioActive ? 'MUTE HARMONIC' : '432HZ SYNTH', 'default')"
          @mouseleave="resetCursor"
          title="Toggle 432Hz Harmonic Synthesizer"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 5L6 9H2v6h4l5 4V5z" />
            <path v-if="isAudioActive" d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
            <line v-else x1="23" y1="9" x2="17" y2="15" />
          </svg>
        </button>

        <!-- Mobile Menu Hamburger -->
        <button
          type="button"
          class="glass-icon-circle mobile-burger"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          aria-label="Open Navigation Menu"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Quick Glass Search Modal -->
    <transition name="fade">
      <div v-if="isSearchOpen" class="search-modal-backdrop" @click.self="closeSearch">
        <div class="search-modal-card">
          <div class="search-input-wrapper">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by application, TCO, capability, or blast radius..."
              autofocus
            />
            <button type="button" class="search-close-btn" @click="closeSearch">✕</button>
          </div>
          <div class="search-results-list">
            <div
              v-for="app in applications.filter(a => a.name.toLowerCase().includes(searchQuery.toLowerCase()) || a.category.toLowerCase().includes(searchQuery.toLowerCase()))"
              :key="`s-${app.id}`"
              class="search-result-item"
              @click="selectFromSearch(app)"
            >
              <div>
                <strong>{{ app.name }}</strong>
                <span class="search-result-cat">{{ app.category }} · {{ app.tier }}</span>
              </div>
              <span class="search-result-price">${{ (app.tco / 1000000).toFixed(2) }}M</span>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Mobile Drawer Overlay -->
    <transition name="drawer">
      <div v-if="isMobileMenuOpen" class="mobile-drawer-sheet">
        <div class="drawer-header">
          <span class="logo-text">VEDANAM</span>
          <button type="button" class="glass-icon-circle" @click="isMobileMenuOpen = false">✕</button>
        </div>
        <ul class="drawer-nav">
          <li><NuxtLink to="/reference-application" @click="isMobileMenuOpen = false">Reference Application</NuxtLink></li>
          <li><NuxtLink to="/technical-specs" @click="isMobileMenuOpen = false">Technical Specs</NuxtLink></li>
          <li><a href="/#projects" @click="isMobileMenuOpen = false">Projects & Hotspots</a></li>
          <li><a href="/#about-us" @click="isMobileMenuOpen = false">About Us</a></li>
          <li><NuxtLink to="/docs" @click="isMobileMenuOpen = false">Documentation</NuxtLink></li>
          <li><NuxtLink to="/terms" @click="isMobileMenuOpen = false">Terms of Service</NuxtLink></li>
          <li><NuxtLink to="/privacy" @click="isMobileMenuOpen = false">Privacy Policy</NuxtLink></li>
        </ul>
      </div>
    </transition>
  </header>
</template>

<style scoped>
.ledup-header-fixed {
  position: fixed;
  top: 1.5rem;
  left: 0;
  width: 100%;
  z-index: var(--z-nav);
  pointer-events: none;
  transition: transform 0.35s ease;
}

.header-container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 0 var(--container-padding);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 1. Left Logo */
.header-brand-logo {
  pointer-events: auto;
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo-text {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 1.25rem;
  letter-spacing: -0.02em;
  color: #121316;
  text-transform: uppercase;
}

/* 2. Center Frosted Pill (Exact ledup.pt capsule) */
.header-center-nav {
  pointer-events: auto;
}

.frosted-glass-pill {
  display: flex;
  align-items: center;
  background: var(--glass-nav-bg);
  backdrop-filter: blur(var(--glass-nav-blur)) saturate(160%);
  -webkit-backdrop-filter: blur(var(--glass-nav-blur)) saturate(160%);
  border: 1px solid var(--glass-nav-border);
  border-radius: var(--radius-pill);
  box-shadow: var(--glass-nav-shadow);
  padding: 0.38rem 0.6rem;
  transition: box-shadow 0.25s ease, background-color 0.25s ease;
}

.frosted-glass-pill:hover {
  box-shadow: 0 10px 36px -6px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.88);
}

.nav-links-row {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  position: relative;
}

.pill-nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.15rem;
  border-radius: var(--radius-pill);
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.125rem;
  color: #383a42;
  text-decoration: none;
  background: transparent;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.pill-nav-link:hover {
  color: #121316;
  background: rgba(0, 0, 0, 0.04);
}

.dropdown-trigger {
  cursor: pointer;
}

.chevron-icon {
  transition: transform 0.25s ease;
}

.rotate-180 {
  transform: rotate(180deg);
}

/* Glassmorphism Dropdown */
.glass-dropdown-card {
  position: absolute;
  top: calc(100% + 0.75rem);
  left: 0;
  width: 320px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 20px 48px -10px rgba(0, 0, 0, 0.14);
  padding: 1rem;
  z-index: 100;
}

.dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  margin-bottom: 0.5rem;
}

.dropdown-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8c909e;
}

.dropdown-badge {
  font-size: 0.7rem;
  font-weight: 600;
  background: var(--pastel-lavender-soft);
  color: #5b21b6;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.dropdown-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.dropdown-row-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.55rem 0.75rem;
  border-radius: 12px;
  text-align: left;
  transition: all 0.18s ease;
}

.dropdown-row-btn:hover,
.dropdown-row-btn.is-selected {
  background: rgba(0, 0, 0, 0.04);
}

.row-info {
  display: flex;
  flex-direction: column;
}

.row-name {
  font-size: 0.84rem;
  font-weight: 600;
  color: #121316;
}

.row-tier {
  font-size: 0.72rem;
  color: #7b808e;
}

.row-tco {
  font-size: 0.82rem;
  font-weight: 700;
  color: #121316;
}

.dropdown-footer {
  padding-top: 0.6rem;
  margin-top: 0.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.dropdown-ref-pill {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.85rem;
  border-radius: var(--radius-pill);
  background: #1d1e24;
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.dropdown-ref-pill:hover {
  background: #2c2f38;
  transform: translateY(-1px);
}

.dropdown-more-link {
  font-size: 0.76rem;
  font-weight: 600;
  color: #555966;
  text-align: right;
  padding: 0.2rem 0;
  transition: color var(--transition-fast);
}

.dropdown-more-link:hover {
  color: #121316;
}

.nav-ref-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.nav-mini-badge {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.45rem;
  border-radius: var(--radius-pill);
  background: var(--pastel-mint-soft);
  color: #065f46;
  border: 1px solid rgba(167, 243, 208, 0.5);
}

/* 3. Right Cluster */
.header-right-cluster {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.header-action-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 1.35rem;
  border-radius: var(--radius-pill);
  background: #121316;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.125rem;
  text-decoration: none;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(18, 19, 22, 0.15);
}

.header-action-pill:hover {
  background: #25272e;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(18, 19, 22, 0.25);
}

.glass-icon-circle {
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-circle-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--glass-circle-border);
  box-shadow: var(--glass-circle-shadow);
  color: #121316;
  cursor: pointer;
  transition: all 0.2s ease;
}

.glass-icon-circle:hover {
  background: #ffffff;
  transform: scale(1.06);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.glass-icon-circle.audio-active {
  color: #5b21b6;
  border-color: var(--pastel-lavender);
  background: var(--pastel-lavender-soft);
}

.mobile-burger {
  display: none;
}

/* Search Modal */
.search-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(18, 19, 22, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 6rem;
  z-index: var(--z-modal);
  pointer-events: auto;
}

.search-modal-card {
  width: 100%;
  max-width: 580px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.16);
  padding: 1.25rem;
  overflow: hidden;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid #ebecee;
  padding-bottom: 0.85rem;
}

.search-input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1rem;
  color: #121316;
  background: transparent;
}

.search-close-btn {
  font-size: 1rem;
  color: #8c909e;
}

.search-results-list {
  max-height: 320px;
  overflow-y: auto;
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.search-result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.search-result-item:hover {
  background: #f4f5f8;
}

.search-result-cat {
  display: block;
  font-size: 0.75rem;
  color: #7b808e;
}

.search-result-price {
  font-weight: 700;
  font-size: 0.88rem;
}

/* Mobile Drawer */
.mobile-drawer-sheet {
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(24px);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  pointer-events: auto;
  z-index: var(--z-modal);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
}

.drawer-nav {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  font-size: 1.4rem;
  font-weight: 700;
}

@media (max-width: 900px) {
  .header-center-nav {
    display: none;
  }
  .mobile-burger {
    display: flex;
  }
}
</style>
