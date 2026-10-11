<script setup lang="ts">
import { ref } from 'vue'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'

const props = defineProps<{
  activeMock: 'ascent' | 'relief' | 'observatory'
}>()

const emit = defineEmits<{
  (e: 'update:activeMock', val: 'ascent' | 'relief' | 'observatory'): void
}>()

const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const isComparisonOpen = ref(false)

const setMock = (mode: 'ascent' | 'relief' | 'observatory') => {
  if (props.activeMock === mode) return
  emit('update:activeMock', mode)
  playInteractChime(mode === 'ascent' ? 1.1 : mode === 'relief' ? 1.3 : 1.5)
}

const toggleComparison = () => {
  isComparisonOpen.value = !isComparisonOpen.value
  playInteractChime(isComparisonOpen.value ? 1.4 : 1.0)
}
</script>

<template>
  <div class="specs-mock-switcher-root">
    <!-- Clean Floating White Alpine Studio Capsule -->
    <div class="mock-capsule-dock">
      <div class="capsule-branding">
        <span class="active-pulse-dot" />
        <span class="capsule-label">EXPEDITION MOCK:</span>
      </div>

      <!-- Mode 1: Summit Ridge Ascent -->
      <button
        type="button"
        class="dock-mode-btn"
        :class="{ active: activeMock === 'ascent' }"
        @click="setMock('ascent')"
        @mouseenter="setCursor('MOCK 01: SUMMIT RIDGE ASCENT', 'highlight')"
        @mouseleave="resetCursor"
      >
        <span class="mode-num">01</span>
        <span class="mode-name">Summit Ridge Ascent</span>
        <span class="mode-tag">Ridge Climber</span>
      </button>

      <!-- Mode 2: Topographic Relief Desk -->
      <button
        type="button"
        class="dock-mode-btn"
        :class="{ active: activeMock === 'relief' }"
        @click="setMock('relief')"
        @mouseenter="setCursor('MOCK 02: TOPOGRAPHIC RELIEF DESK', 'highlight')"
        @mouseleave="resetCursor"
      >
        <span class="mode-num">02</span>
        <span class="mode-name">Topographic Relief Desk</span>
        <span class="mode-tag">Cartography Desk</span>
      </button>

      <!-- Mode 3: Dual Codex Observatory -->
      <button
        type="button"
        class="dock-mode-btn"
        :class="{ active: activeMock === 'observatory' }"
        @click="setMock('observatory')"
        @mouseenter="setCursor('MOCK 03: DUAL CODEX OBSERVATORY', 'highlight')"
        @mouseleave="resetCursor"
      >
        <span class="mode-num">03</span>
        <span class="mode-name">Dual Codex Observatory</span>
        <span class="mode-tag">Dual Journals</span>
      </button>

      <!-- Compare Archetypes Button -->
      <button
        type="button"
        class="dock-compare-btn"
        :class="{ active: isComparisonOpen }"
        @click="toggleComparison"
        @mouseenter="setCursor('COMPARE EXPEDITION DESIGNS', 'default')"
        @mouseleave="resetCursor"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <span>Compare 3 Mocks</span>
      </button>
    </div>

    <!-- Comparative Modal Drawer -->
    <transition name="fade">
      <div v-if="isComparisonOpen" class="comparison-overlay" @click.self="isComparisonOpen = false">
        <div class="comparison-modal-card">
          <div class="modal-top">
            <div>
              <span class="modal-kicker">ICE-CAPPED EXPEDITION DESIGN SYSTEM</span>
              <h3 class="modal-title">3 Mountain Discovery Mocks with Dual Field Notebooks</h3>
              <p class="modal-desc">
                Every mock transforms the technical specifications into an ice-capped mountain climb. At every milestone along the route, the user accesses 2 clickable notebooks: 1 for Business Value & Strategy, and 1 for Mathematical Specification & Code.
              </p>
            </div>
            <button type="button" class="close-modal-btn" @click="isComparisonOpen = false">✕</button>
          </div>

          <div class="matrix-grid">
            <!-- Archetype 1 -->
            <div class="archetype-card" :class="{ current: activeMock === 'ascent' }">
              <div class="archetype-badge-row">
                <span class="pill-chip chip-sky">Mock 01</span>
                <span class="paradigm-label">First-Person Ridge Climber</span>
              </div>
              <h4>The Summit Ridge Ascent</h4>
              <p class="card-summary">
                Direct climb up the windswept snow ridge from Valley Basecamp (1,400m) to Apex Summit (8,848m). Dynamic camera ascents along the 3D mountain slope with live altimeter, barometric pressure, and milestone camps.
              </p>
              <ul class="feature-bullets">
                <li><strong>Mountain Metaphor:</strong> Physical ridge ascent with altimeter gauge & wind flurry</li>
                <li><strong>3D Centerpiece:</strong> Low-poly crystalline mountain peak & 3D books resting on snow</li>
                <li><strong>Dual Notebooks:</strong> 2 Tactile cards on active camp card opening full binder modal</li>
              </ul>
              <button type="button" class="switch-to-btn" @click="setMock('ascent'); isComparisonOpen = false">
                Launch Summit Ridge →
              </button>
            </div>

            <!-- Archetype 2 -->
            <div class="archetype-card" :class="{ current: activeMock === 'relief' }">
              <div class="archetype-badge-row">
                <span class="pill-chip chip-mint">Mock 02</span>
                <span class="paradigm-label">Cartography Studio Desk</span>
              </div>
              <h4>Topographic Relief Desk</h4>
              <p class="card-summary">
                Expedition surveyor tent with an interactive 3D physical contour model on an architectural desk. Users drag an elevation slice plane across the massif to illuminate contour isolines and milestone cairns.
              </p>
              <ul class="feature-bullets">
                <li><strong>Mountain Metaphor:</strong> Tactile physical 3D stepped contour model on surveyor drafting table</li>
                <li><strong>3D Centerpiece:</strong> 14-tier alabaster/ice relief tiers with glowing surveyor pins</li>
                <li><strong>Dual Notebooks:</strong> 2 Physical open journals laid flat on the leather desk blotter</li>
              </ul>
              <button type="button" class="switch-to-btn" @click="setMock('relief'); isComparisonOpen = false">
                Launch Relief Desk →
              </button>
            </div>

            <!-- Archetype 3 -->
            <div class="archetype-card" :class="{ current: activeMock === 'observatory' }">
              <div class="archetype-badge-row">
                <span class="pill-chip chip-lavender">Mock 03</span>
                <span class="paradigm-label">Dual Tome Summit Overlook</span>
              </div>
              <h4>Dual Codex Observatory</h4>
              <p class="card-summary">
                Panoramic glass summit overlook with sweeping snowy peaks in the background. Features two massive open 3D books resting side-by-side on a crystal lectern with animated 3D page-turn transitions.
              </p>
              <ul class="feature-bullets">
                <li><strong>Mountain Metaphor:</strong> Panoramic glass observatory perched over infinite snow peaks</li>
                <li><strong>3D Centerpiece:</strong> Two 3D leather/sapphire tomes turning pages on crystal pedestal</li>
                <li><strong>Dual Notebooks:</strong> Side-by-side living journal spreads with live KaTeX & code copy</li>
              </ul>
              <button type="button" class="switch-to-btn" @click="setMock('observatory'); isComparisonOpen = false">
                Launch Observatory →
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.specs-mock-switcher-root {
  position: fixed;
  top: 5.5rem;
  left: 0;
  width: 100%;
  z-index: 850;
  display: flex;
  justify-content: center;
  pointer-events: none;
}

.mock-capsule-dock {
  pointer-events: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.4rem 0.65rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(28px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.06);
  transition: all 0.25s ease;
}

.mock-capsule-dock:hover {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 16px 44px rgba(0, 0, 0, 0.08);
}

.capsule-branding {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.65rem 0 0.4rem;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
}

.active-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #0284c7;
  box-shadow: 0 0 10px #0284c7;
}

.capsule-label {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #6b7280;
}

.dock-mode-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.95rem;
  border-radius: var(--radius-pill);
  background: transparent;
  border: 1px solid transparent;
  color: #4b4f5d;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dock-mode-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  color: #111827;
}

.dock-mode-btn.active {
  background: #0f172a;
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.2);
}

.mode-num {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 800;
  opacity: 0.7;
}

.mode-name {
  font-size: 0.8rem;
  font-weight: 700;
}

.mode-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.12rem 0.45rem;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.06);
  color: #64748b;
}

.dock-mode-btn.active .mode-tag {
  background: rgba(255, 255, 255, 0.2);
  color: #f8fafc;
}

.dock-compare-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-pill);
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 0.25rem;
}

.dock-compare-btn:hover,
.dock-compare-btn.active {
  background: #e2e8f0;
  color: #0f172a;
}

/* Comparison Modal Drawer */
.comparison-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  pointer-events: auto;
}

.comparison-modal-card {
  width: 100%;
  max-width: 1100px;
  background: #ffffff;
  border-radius: 28px;
  box-shadow: 0 32px 72px rgba(0, 0, 0, 0.16);
  padding: 2.2rem;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.modal-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.8rem;
  padding-bottom: 1.2rem;
  border-bottom: 1px solid #f1f5f9;
}

.modal-kicker {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #0284c7;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 1.55rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.3rem 0 0.4rem;
}

.modal-desc {
  font-size: 0.9rem;
  color: #64748b;
  max-width: 780px;
  line-height: 1.5;
  margin: 0;
}

.close-modal-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #475569;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-modal-btn:hover {
  background: #0f172a;
  color: #ffffff;
}

.matrix-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.4rem;
}

.archetype-card {
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 20px;
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
}

.archetype-card:hover {
  border-color: #cbd5e1;
  transform: translateY(-2px);
}

.archetype-card.current {
  border-color: #0284c7;
  background: #f0f9ff;
  box-shadow: 0 8px 24px rgba(2, 132, 199, 0.12);
}

.archetype-badge-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.pill-chip {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
}

.chip-sky { background: #e0f2fe; color: #0369a1; }
.chip-mint { background: #dcfce7; color: #15803d; }
.chip-lavender { background: #f3e8ff; color: #7e22ce; }

.paradigm-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748b;
}

.archetype-card h4 {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.card-summary {
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.feature-bullets {
  list-style: none;
  padding: 0;
  margin: 0 0 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  font-size: 0.78rem;
  color: #334155;
}

.feature-bullets li {
  line-height: 1.4;
}

.feature-bullets strong {
  color: #0f172a;
}

.switch-to-btn {
  margin-top: auto;
  padding: 0.65rem 1rem;
  border-radius: var(--radius-pill);
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #0f172a;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.switch-to-btn:hover {
  background: #0f172a;
  color: #ffffff;
  border-color: #0f172a;
}

@media (max-width: 900px) {
  .matrix-grid {
    grid-template-columns: 1fr;
  }
}
</style>
