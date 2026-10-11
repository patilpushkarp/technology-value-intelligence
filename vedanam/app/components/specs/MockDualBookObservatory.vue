<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useExpeditionMilestones, type ExpeditionMilestone } from '~/composables/useExpeditionMilestones'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import MathFormula from '~/components/MathFormula.vue'
import ExpeditionNotebookModal from '~/components/specs/ExpeditionNotebookModal.vue'

const { milestones } = useExpeditionMilestones()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const currentMilestoneIndex = ref(0)
const activeMilestone = ref<ExpeditionMilestone>(milestones[0])
const isModalOpen = ref(false)
const modalInitialBook = ref<'business' | 'technical'>('business')

// Layout View Modes: 'dual' (both side-by-side), 'business-focus', 'technical-focus'
const viewMode = ref<'dual' | 'business' | 'technical'>('dual')
const copiedCode = ref(false)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number
let distantPeaksGroup: THREE.Group
let bookLeftMesh: THREE.Mesh
let bookRightMesh: THREE.Mesh
let pedestalMesh: THREE.Mesh

const openNotebookModal = (bookType: 'business' | 'technical') => {
  modalInitialBook.value = bookType
  isModalOpen.value = true
  playInteractChime(bookType === 'business' ? 1.2 : 1.5)
}

const selectMilestone = (index: number) => {
  if (index < 0 || index >= milestones.length) return
  currentMilestoneIndex.value = index
  activeMilestone.value = milestones[index]

  // Trigger 3D Book Page Flip Animation
  if (bookLeftMesh && bookRightMesh) {
    gsap.to(bookLeftMesh.rotation, {
      y: 0.4,
      duration: 0.35,
      yoyo: true,
      repeat: 1,
      ease: 'power2.inOut'
    })
    gsap.to(bookRightMesh.rotation, {
      y: -0.4,
      duration: 0.35,
      yoyo: true,
      repeat: 1,
      ease: 'power2.inOut'
    })
  }

  // Smooth camera subtle refocus
  if (camera) {
    gsap.to(camera.position, {
      y: 8 + (index * 0.4),
      duration: 1.2,
      ease: 'power2.out'
    })
  }

  playInteractChime(1.1 + index * 0.1)
}

const copySnippet = async () => {
  if (process.client && navigator.clipboard) {
    await navigator.clipboard.writeText(activeMilestone.value.technical.codeSnippet)
    copiedCode.value = true
    playInteractChime(1.5)
    setTimeout(() => { copiedCode.value = false }, 1800)
  }
}

const initThreeScene = () => {
  if (!canvasRef.value) return

  const width = canvasRef.value.clientWidth
  const height = canvasRef.value.clientHeight

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf6f9fc) // Radiant white alpine sky

  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(0, 8, 22)
  camera.lookAt(0, 4, 0)

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: false,
    powerPreference: 'high-performance'
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true

  // Atmospheric Light
  const skyLight = new THREE.AmbientLight(0xe2e8f0, 1.4)
  scene.add(skyLight)

  const directSun = new THREE.DirectionalLight(0xffffff, 1.8)
  directSun.position.set(20, 35, 20)
  directSun.castShadow = true
  scene.add(directSun)

  // 1. Distant 3D Alpine Peaks Visible through Observatory Glass
  distantPeaksGroup = new THREE.Group()
  const peakCount = 18

  for (let i = 0; i < peakCount; i++) {
    const angle = (i / peakCount) * Math.PI * 1.6 - Math.PI * 0.8
    const distance = 45 + Math.random() * 25
    const peakHeight = 12 + Math.random() * 16

    const peakGeo = new THREE.ConeGeometry(8 + Math.random() * 6, peakHeight, 4)
    const peakMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.7,
      flatShading: true
    })
    const peak = new THREE.Mesh(peakGeo, peakMat)
    peak.position.set(Math.sin(angle) * distance, peakHeight / 2 - 4, -Math.cos(angle) * distance)
    peak.rotation.y = Math.random() * Math.PI
    distantPeaksGroup.add(peak)
  }
  scene.add(distantPeaksGroup)

  // 2. Crystal Ice Lectern / Pedestal
  const pedGeo = new THREE.BoxGeometry(16, 2, 8)
  const pedMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.2,
    metalness: 0.1,
    transparent: true,
    opacity: 0.85
  })
  pedestalMesh = new THREE.Mesh(pedGeo, pedMat)
  pedestalMesh.position.set(0, 1, 0)
  pedestalMesh.receiveShadow = true
  scene.add(pedestalMesh)

  // 3. Left 3D Book: Business Field Guide (Leather Amber)
  const bookGeo = new THREE.BoxGeometry(4.5, 0.4, 3.2)
  const bookLeftMat = new THREE.MeshStandardMaterial({ color: 0xb45309, roughness: 0.4, metalness: 0.2 })
  bookLeftMesh = new THREE.Mesh(bookGeo, bookLeftMat)
  bookLeftMesh.position.set(-3.2, 2.3, 0.5)
  bookLeftMesh.rotation.set(-0.25, 0.15, -0.05)
  bookLeftMesh.castShadow = true
  scene.add(bookLeftMesh)

  // 4. Right 3D Book: Technical Field Manual (Glacial Blue)
  const bookRightMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.3, metalness: 0.3 })
  bookRightMesh = new THREE.Mesh(bookGeo, bookRightMat)
  bookRightMesh.position.set(3.2, 2.3, 0.5)
  bookRightMesh.rotation.set(-0.25, -0.15, 0.05)
  bookRightMesh.castShadow = true
  scene.add(bookRightMesh)

  // 5. Snow Crystals Drifting
  const flakesGeo = new THREE.BufferGeometry()
  const flakePos = new Float32Array(300 * 3)
  for (let i = 0; i < 300 * 3; i += 3) {
    flakePos[i] = (Math.random() - 0.5) * 50
    flakePos[i + 1] = Math.random() * 25
    flakePos[i + 2] = (Math.random() - 0.5) * 30
  }
  flakesGeo.setAttribute('position', new THREE.BufferAttribute(flakePos, 3))
  const flakesMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.3, transparent: true, opacity: 0.8 })
  const flakes = new THREE.Points(flakesGeo, flakesMat)
  scene.add(flakes)

  // Animation Loop
  const clock = new THREE.Clock()
  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const elapsed = clock.getElapsedTime()

    // Gentle rotation of background distant mountain vista
    if (distantPeaksGroup) {
      distantPeaksGroup.rotation.y = Math.sin(elapsed * 0.05) * 0.04
    }

    // Gentle hovering animation for books
    if (bookLeftMesh && bookRightMesh) {
      bookLeftMesh.position.y = 2.3 + Math.sin(elapsed * 1.2) * 0.04
      bookRightMesh.position.y = 2.3 + Math.cos(elapsed * 1.2) * 0.04
    }

    camera.lookAt(0, 3.5, 0)
    renderer.render(scene, camera)
  }
  animate()
}

const handleResize = () => {
  if (!canvasRef.value || !renderer || !camera) return
  const w = canvasRef.value.clientWidth
  const h = canvasRef.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

onMounted(() => {
  initThreeScene()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId)
  window.removeEventListener('resize', handleResize)
  if (renderer) renderer.dispose()
})
</script>

<template>
  <div class="mock-observatory-root">
    <!-- Background 3D Alpine Glass Overlook Canvas -->
    <canvas ref="canvasRef" class="observatory-canvas" />

    <!-- Living Dual-Book Spread Interface -->
    <div class="observatory-ui-container">
      <!-- 1. Top Observatory Horizon Nav Bar -->
      <header class="observatory-header">
        <div class="observatory-brand">
          <span class="crest-icon">🏔️</span>
          <div>
            <span class="brand-sub font-mono">SUMMIT OBSERVATORY · ARCHEPOINT 03</span>
            <h1 class="brand-title">Dual Field Codex Overlook</h1>
          </div>
        </div>

        <!-- 6 Milestone Peak Steps on Horizon -->
        <nav class="horizon-milestone-peaks">
          <button
            v-for="(m, idx) in milestones"
            :key="m.id"
            type="button"
            class="peak-step-btn"
            :class="{ active: currentMilestoneIndex === idx }"
            @click="selectMilestone(idx)"
            @mouseenter="setCursor(`MILESTONE 0${m.number}: ${m.name.toUpperCase()}`, 'pointer')"
            @mouseleave="resetCursor"
          >
            <span class="peak-icon">▲</span>
            <span class="peak-label">0{{ m.number }}</span>
            <span class="peak-alt font-mono">{{ m.altitude }}m</span>
          </button>
        </nav>

        <!-- View Mode Segmented Controls -->
        <div class="view-mode-toggle">
          <button
            type="button"
            class="view-btn"
            :class="{ active: viewMode === 'dual' }"
            @click="viewMode = 'dual'"
          >
            Dual Spread
          </button>
          <button
            type="button"
            class="view-btn"
            :class="{ active: viewMode === 'business' }"
            @click="viewMode = 'business'"
          >
            Business
          </button>
          <button
            type="button"
            class="view-btn"
            :class="{ active: viewMode === 'technical' }"
            @click="viewMode = 'technical'"
          >
            Technical
          </button>
        </div>
      </header>

      <!-- 2. Dual Open Books Main Spread (Side-by-Side Living Journals) -->
      <main class="dual-books-stage" :class="`mode-${viewMode}`">
        <!-- LEFT BOOK SPREAD: Business Field Guide -->
        <section
          v-if="viewMode === 'dual' || viewMode === 'business'"
          class="journal-book-spread business-journal"
        >
          <!-- Leather Journal Header Tab -->
          <div class="journal-spine-header business-spine">
            <div class="spine-identity">
              <span class="book-emblem">📖</span>
              <div>
                <span class="spine-badge">EXPEDITION RECORD #0{{ activeMilestone.number }}</span>
                <h2 class="book-spread-title">Business Field Guide</h2>
              </div>
            </div>
            <button
              type="button"
              class="expand-journal-btn"
              @click="openNotebookModal('business')"
            >
              Expand Binder ↗
            </button>
          </div>

          <!-- Journal Body Content -->
          <div class="journal-scroll-content">
            <div class="spread-chapter-badge">
              <span>ALTITUDE {{ activeMilestone.altitude }}M · {{ activeMilestone.location }}</span>
            </div>

            <h3 class="chapter-hed">{{ activeMilestone.business.title }}</h3>
            <p class="chapter-lead">{{ activeMilestone.business.executiveSummary }}</p>

            <div class="journal-section-block">
              <span class="sec-label">Enterprise Strategic Impact</span>
              <p class="sec-body">{{ activeMilestone.business.businessImpact }}</p>
            </div>

            <div class="journal-section-block">
              <span class="sec-label">Cost Avoidance & Economic Rationale</span>
              <p class="sec-body">{{ activeMilestone.business.costImplications }}</p>
            </div>

            <!-- CFO Takeaway Card -->
            <div class="cfo-journal-quote-box">
              <span class="cfo-stamp">CFO / CIO Core Takeaway</span>
              <p class="cfo-quote-text">“{{ activeMilestone.business.cfoTakeaway }}”</p>
            </div>

            <!-- Target KPI Cards -->
            <div class="kpi-mini-grid">
              <div v-for="kpi in activeMilestone.business.kpis" :key="kpi.label" class="kpi-mini-card">
                <span class="kpi-mini-label">{{ kpi.label }}</span>
                <strong class="kpi-mini-val font-mono">{{ kpi.value }}</strong>
              </div>
            </div>
          </div>
        </section>

        <!-- RIGHT BOOK SPREAD: Technical Field Manual -->
        <section
          v-if="viewMode === 'dual' || viewMode === 'technical'"
          class="journal-book-spread technical-journal"
        >
          <!-- Glacial Journal Header Tab -->
          <div class="journal-spine-header technical-spine">
            <div class="spine-identity">
              <span class="book-emblem">📐</span>
              <div>
                <span class="spine-badge">SPECIFICATION CONTRACT #0{{ activeMilestone.number }}</span>
                <h2 class="book-spread-title">Technical Field Manual</h2>
              </div>
            </div>
            <button
              type="button"
              class="expand-journal-btn tech"
              @click="openNotebookModal('technical')"
            >
              Expand Binder ↗
            </button>
          </div>

          <!-- Journal Body Content -->
          <div class="journal-scroll-content">
            <div class="tech-metrics-strip">
              <span class="tech-metric-pill">Latency: <strong>{{ activeMilestone.technical.latencySla }}</strong></span>
              <span class="tech-metric-pill">Memory: <strong>{{ activeMilestone.technical.memoryBudget }}</strong></span>
              <span class="tech-metric-pill">Determinism: <strong>Seed 42</strong></span>
            </div>

            <h3 class="chapter-hed">{{ activeMilestone.technical.title }}</h3>

            <!-- KaTeX Math Formulation -->
            <div class="math-proof-box">
              <span class="sec-label">First-Principles Formulation</span>
              <MathFormula
                :latex="activeMilestone.technical.formulaLatex"
                :formula-html="activeMilestone.technical.formulaHtml"
                :name="activeMilestone.technical.formulaName"
              />
              <p class="formula-caption-text">{{ activeMilestone.technical.formulaExplanation }}</p>
            </div>

            <!-- Contracts -->
            <div class="contracts-box">
              <div class="contract-row">
                <span class="c-tag">Input Contract:</span>
                <span class="c-val font-mono">{{ activeMilestone.technical.inputContract }}</span>
              </div>
              <div class="contract-row">
                <span class="c-tag">Output Artifact:</span>
                <span class="c-val font-mono">{{ activeMilestone.technical.outputContract }}</span>
              </div>
            </div>

            <!-- Code Module Snippet -->
            <div class="code-module-wrapper">
              <div class="code-top">
                <span class="code-title font-mono">{{ activeMilestone.technical.moduleLineage }}</span>
                <button type="button" class="copy-btn" @click="copySnippet">
                  {{ copiedCode ? 'Copied ✓' : 'Copy' }}
                </button>
              </div>
              <pre class="code-body font-mono"><code>{{ activeMilestone.technical.codeSnippet }}</code></pre>
            </div>
          </div>
        </section>
      </main>

      <!-- 3. Bottom Milestone Pagination Footbar -->
      <footer class="observatory-footer">
        <button
          type="button"
          class="stage-nav-btn"
          :disabled="currentMilestoneIndex === 0"
          @click="selectMilestone(currentMilestoneIndex - 1)"
        >
          ◀ Previous Altitude Stage
        </button>

        <div class="current-altitude-indicator">
          <span class="alt-big font-mono">{{ activeMilestone.altitude }}M</span>
          <span class="alt-sub">{{ activeMilestone.name }} · {{ activeMilestone.location }}</span>
        </div>

        <button
          type="button"
          class="stage-nav-btn next"
          :disabled="currentMilestoneIndex === milestones.length - 1"
          @click="selectMilestone(currentMilestoneIndex + 1)"
        >
          Next Altitude Stage ▶
        </button>
      </footer>
    </div>

    <!-- Expedition Dual Notebook Modal Reader -->
    <ExpeditionNotebookModal
      v-if="isModalOpen"
      :milestone="activeMilestone"
      :initial-book="modalInitialBook"
      @close="isModalOpen = false"
    />
  </div>
</template>

<style scoped>
.mock-observatory-root {
  position: relative;
  width: 100%;
  height: 100vh;
  background-color: #f6f9fc;
  overflow: hidden;
  user-select: none;
}

.observatory-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}

.observatory-ui-container {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.2rem 1.8rem;
  pointer-events: none;
}

.observatory-ui-container > * {
  pointer-events: auto;
}

/* 1. Header */
.observatory-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  padding: 0.8rem 1.5rem;
  border-radius: 20px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.observatory-brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.crest-icon {
  font-size: 1.6rem;
}

.brand-sub {
  font-size: 0.65rem;
  font-weight: 800;
  color: #0284c7;
  letter-spacing: 0.08em;
  display: block;
}

.brand-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.horizon-milestone-peaks {
  display: flex;
  gap: 0.4rem;
}

.peak-step-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.35rem 0.65rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.peak-step-btn:hover {
  background: #f1f5f9;
}

.peak-step-btn.active {
  background: #0284c7;
  border-color: #0284c7;
}

.peak-icon {
  font-size: 0.65rem;
  color: #94a3b8;
}

.peak-label {
  font-size: 0.68rem;
  font-weight: 800;
  color: #334155;
}

.peak-alt {
  font-size: 0.6rem;
  font-weight: 700;
  color: #64748b;
}

.peak-step-btn.active .peak-icon,
.peak-step-btn.active .peak-label,
.peak-step-btn.active .peak-alt {
  color: #ffffff;
}

.view-mode-toggle {
  display: flex;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: var(--radius-pill);
}

.view-btn {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.35rem 0.75rem;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn.active {
  background: #0f172a;
  color: #ffffff;
}

/* 2. Main Dual Books Stage */
.dual-books-stage {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  flex: 1;
  margin: 1rem 0;
  overflow: hidden;
}

.dual-books-stage.mode-business {
  grid-template-columns: 1fr;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.dual-books-stage.mode-technical {
  grid-template-columns: 1fr;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.journal-book-spread {
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 24px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.journal-spine-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.4rem;
  border-bottom: 1px solid #e2e8f0;
}

.business-spine {
  background: #fffbeb;
  border-top: 4px solid #b45309;
}

.technical-spine {
  background: #f0f9ff;
  border-top: 4px solid #0284c7;
}

.spine-identity {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.book-emblem {
  font-size: 1.3rem;
}

.spine-badge {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #64748b;
  display: block;
}

.book-spread-title {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.expand-journal-btn {
  font-size: 0.72rem;
  font-weight: 800;
  color: #b45309;
  background: #ffffff;
  border: 1px solid #fde68a;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: all 0.2s ease;
}

.expand-journal-btn:hover {
  background: #b45309;
  color: #ffffff;
}

.expand-journal-btn.tech {
  color: #0284c7;
  border-color: #bae6fd;
}
.expand-journal-btn.tech:hover {
  background: #0284c7;
  color: #ffffff;
}

.journal-scroll-content {
  padding: 1.4rem;
  overflow-y: auto;
  flex: 1;
}

.spread-chapter-badge {
  font-family: var(--font-mono);
  font-size: 0.66rem;
  font-weight: 800;
  color: #0284c7;
  margin-bottom: 0.3rem;
}

.chapter-hed {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.3rem;
}

.chapter-lead {
  font-size: 0.85rem;
  color: #475569;
  line-height: 1.45;
  margin-bottom: 1.1rem;
}

.journal-section-block {
  margin-bottom: 0.9rem;
}

.sec-label {
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #64748b;
  display: block;
  margin-bottom: 0.25rem;
}

.sec-body {
  font-size: 0.8rem;
  color: #334155;
  line-height: 1.45;
  margin: 0;
}

.cfo-journal-quote-box {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  padding: 0.8rem 1rem;
  border-radius: 12px;
  margin: 1rem 0;
}

.cfo-stamp {
  font-size: 0.64rem;
  font-weight: 800;
  color: #b45309;
  display: block;
}

.cfo-quote-text {
  font-size: 0.78rem;
  font-style: italic;
  color: #78350f;
  margin: 0.2rem 0 0;
  line-height: 1.4;
}

.kpi-mini-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
}

.kpi-mini-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.5rem 0.7rem;
  display: flex;
  flex-direction: column;
}

.kpi-mini-label {
  font-size: 0.64rem;
  color: #64748b;
  font-weight: 600;
}

.kpi-mini-val {
  font-size: 0.82rem;
  font-weight: 800;
  color: #0f172a;
}

.tech-metrics-strip {
  display: flex;
  gap: 0.6rem;
  margin-bottom: 0.8rem;
}

.tech-metric-pill {
  font-size: 0.68rem;
  background: #f1f5f9;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  color: #334155;
}

.math-proof-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 0.9rem;
  margin-bottom: 1rem;
}

.formula-caption-text {
  font-size: 0.74rem;
  color: #64748b;
  margin-top: 0.4rem;
  line-height: 1.4;
}

.contracts-box {
  background: #f8fafc;
  border-radius: 12px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.contract-row {
  font-size: 0.72rem;
  display: flex;
  flex-direction: column;
}

.c-tag {
  font-weight: 700;
  color: #64748b;
}

.c-val {
  color: #0f172a;
}

.code-module-wrapper {
  background: #020617;
  border-radius: 14px;
  overflow: hidden;
}

.code-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.8rem;
  background: #0f172a;
}

.code-title {
  font-size: 0.68rem;
  color: #94a3b8;
}

.copy-btn {
  font-size: 0.66rem;
  color: #38bdf8;
  background: transparent;
  border: none;
  cursor: pointer;
  font-weight: 700;
}

.code-body {
  margin: 0;
  padding: 0.8rem;
  font-size: 0.72rem;
  color: #93c5fd;
  line-height: 1.45;
  max-height: 180px;
  overflow-y: auto;
}

/* 3. Footer */
.observatory-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  padding: 0.7rem 1.4rem;
  border-radius: 20px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.stage-nav-btn {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.45rem 0.9rem;
  border-radius: var(--radius-pill);
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stage-nav-btn:hover:not(:disabled) {
  background: #0f172a;
  color: #ffffff;
}

.stage-nav-btn.next {
  background: #0284c7;
  color: #ffffff;
  border-color: #0284c7;
}

.stage-nav-btn.next:hover:not(:disabled) {
  background: #0369a1;
}

.stage-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.current-altitude-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.alt-big {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0284c7;
}

.alt-sub {
  font-size: 0.72rem;
  color: #475569;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .dual-books-stage {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
}
</style>
