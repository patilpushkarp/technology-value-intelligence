<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useExpeditionMilestones, type ExpeditionMilestone } from '~/composables/useExpeditionMilestones'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import ExpeditionNotebookModal from '~/components/specs/ExpeditionNotebookModal.vue'

const { milestones } = useExpeditionMilestones()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const currentMilestoneIndex = ref(0)
const activeMilestone = ref<ExpeditionMilestone>(milestones[0])
const isModalOpen = ref(false)
const modalInitialBook = ref<'business' | 'technical'>('business')

// Interactive Topographic Controls
const sliceElevation = ref(milestones[0].altitude)
const contourInterval = ref<'100m' | '500m'>('500m')
const cameraViewMode = ref<'angled' | 'top' | 'profile'>('angled')
const isAutoRotating = ref(false)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number
let reliefMeshGroup: THREE.Group
let contourLineGroup: THREE.Group
let beaconPins: THREE.Group[] = []
let slicePlaneMesh: THREE.Mesh

// 3D coordinates for the 6 milestone cairns on the physical contour table
const cairnPositions = [
  { x: -14, y: 1.2, z: 12, alt: 1400 },
  { x: -8, y: 2.8, z: 6, alt: 2900 },
  { x: -2, y: 4.6, z: 0, alt: 4400 },
  { x: 4, y: 6.4, z: -4, alt: 5900 },
  { x: 9, y: 8.2, z: -8, alt: 7300 },
  { x: 13, y: 10.5, z: -12, alt: 8848 }
]

const openNotebook = (bookType: 'business' | 'technical') => {
  modalInitialBook.value = bookType
  isModalOpen.value = true
  playInteractChime(bookType === 'business' ? 1.2 : 1.5)
}

const selectMilestone = (index: number) => {
  if (index < 0 || index >= milestones.length) return
  currentMilestoneIndex.value = index
  activeMilestone.value = milestones[index]
  
  // Smoothly move elevation slice plane
  gsap.to(sliceElevation, {
    value: activeMilestone.value.altitude,
    duration: 1.0,
    ease: 'power2.out',
    onUpdate: () => {
      updateSliceHeight()
    }
  })

  // Highlight active beacon pin
  beaconPins.forEach((pin, idx) => {
    const isAct = idx === index
    gsap.to(pin.scale, { x: isAct ? 1.4 : 1.0, y: isAct ? 1.4 : 1.0, z: isAct ? 1.4 : 1.0, duration: 0.4 })
  })

  playInteractChime(1.1 + index * 0.08)
}

const updateSliceHeight = () => {
  if (!slicePlaneMesh) return
  // Map 1400m - 8848m to y: 1.0 - 11.0
  const normalizedY = 1.0 + ((sliceElevation.value - 1400) / (8848 - 1400)) * 10.0
  slicePlaneMesh.position.y = normalizedY
}

const setCameraView = (mode: 'angled' | 'top' | 'profile') => {
  cameraViewMode.value = mode
  if (!camera) return

  if (mode === 'angled') {
    gsap.to(camera.position, { x: 26, y: 22, z: 28, duration: 1.4, ease: 'power2.inOut' })
  } else if (mode === 'top') {
    gsap.to(camera.position, { x: 0, y: 38, z: 0.1, duration: 1.4, ease: 'power2.inOut' })
  } else if (mode === 'profile') {
    gsap.to(camera.position, { x: 34, y: 8, z: 0, duration: 1.4, ease: 'power2.inOut' })
  }
  playInteractChime(1.3)
}

const initThreeScene = () => {
  if (!canvasRef.value) return

  const width = canvasRef.value.clientWidth
  const height = canvasRef.value.clientHeight

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xfcfcfd) // Pristine architectural drafting daylight

  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(26, 22, 28)
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
  renderer.shadowMap.type = THREE.PCFSoftShadowMap

  // Studio Lighting
  const ambientLight = new THREE.AmbientLight(0xf1f5f9, 1.4)
  scene.add(ambientLight)

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.6)
  keyLight.position.set(30, 40, 20)
  keyLight.castShadow = true
  keyLight.shadow.mapSize.width = 1024
  keyLight.shadow.mapSize.height = 1024
  scene.add(keyLight)

  const softFillLight = new THREE.DirectionalLight(0xe0f2fe, 0.7)
  softFillLight.position.set(-25, 20, -15)
  scene.add(softFillLight)

  // 1. Architect's Desk Table Pedestal
  const tableGeo = new THREE.CylinderGeometry(20, 20, 1.5, 48)
  const tableMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.8, metalness: 0.05 })
  const tableMesh = new THREE.Mesh(tableGeo, tableMat)
  tableMesh.position.y = -0.75
  tableMesh.receiveShadow = true
  scene.add(tableMesh)

  // Table edge brass rim
  const rimGeo = new THREE.TorusGeometry(20, 0.15, 16, 64)
  rimGeo.rotateX(Math.PI / 2)
  const rimMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, metalness: 0.7, roughness: 0.3 })
  const rimMesh = new THREE.Mesh(rimGeo, rimMat)
  rimMesh.position.y = 0.02
  scene.add(rimMesh)

  // 2. Stepped 3D Topographic Contour Relief Massif
  reliefMeshGroup = new THREE.Group()
  const numTiers = 14

  for (let t = 0; t < numTiers; t++) {
    const tierHeight = 0.8
    const tierRadius = 18 - t * 1.15
    const tierGeo = new THREE.CylinderGeometry(tierRadius * 0.96, tierRadius, tierHeight, 36)
    
    // Alabaster snow white to glacial translucent tone
    const tierMat = new THREE.MeshStandardMaterial({
      color: t > 10 ? 0xffffff : t > 5 ? 0xf8fafc : 0xf1f5f9,
      roughness: 0.5,
      metalness: 0.1
    })
    const tierMesh = new THREE.Mesh(tierGeo, tierMat)
    tierMesh.position.set(t * 0.85, (t + 0.5) * tierHeight, -t * 0.8)
    tierMesh.castShadow = true
    tierMesh.receiveShadow = true
    reliefMeshGroup.add(tierMesh)
  }
  scene.add(reliefMeshGroup)

  // 3. Topographic Isolines (Contour Rings)
  contourLineGroup = new THREE.Group()
  for (let t = 0; t < numTiers; t++) {
    const tierRadius = 18 - t * 1.15
    const ringGeo = new THREE.RingGeometry(tierRadius * 0.99, tierRadius * 1.01, 48)
    ringGeo.rotateX(-Math.PI / 2)
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, side: THREE.DoubleSide, opacity: 0.45, transparent: true })
    const ringMesh = new THREE.Mesh(ringGeo, ringMat)
    ringMesh.position.set(t * 0.85, (t + 1) * 0.8 + 0.02, -t * 0.8)
    contourLineGroup.add(ringMesh)
  }
  scene.add(contourLineGroup)

  // 4. Milestone Surveyor Beacon Cairns / Pins
  cairnPositions.forEach((cp, idx) => {
    const pinGroup = new THREE.Group()
    pinGroup.position.set(cp.x, cp.y, cp.z)

    // Stainless Surveyor Pin Needle
    const needleGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.4, 8)
    const needleMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.9, roughness: 0.2 })
    const needle = new THREE.Mesh(needleGeo, needleMat)
    needle.position.y = 1.2
    pinGroup.add(needle)

    // Beacon Head Sphere
    const headGeo = new THREE.SphereGeometry(0.42, 16, 16)
    const headMat = new THREE.MeshStandardMaterial({
      color: idx === 5 ? 0xe11d48 : idx % 2 === 0 ? 0x0284c7 : 0xd97706,
      emissive: idx === 5 ? 0xbe123c : idx % 2 === 0 ? 0x0369a1 : 0xb45309,
      emissiveIntensity: 0.3
    })
    const head = new THREE.Mesh(headGeo, headMat)
    head.position.y = 2.4
    pinGroup.add(head)

    beaconPins.push(pinGroup)
    scene.add(pinGroup)
  })

  // 5. Interactive Translucent Elevation Slice Plane
  const sliceGeo = new THREE.PlaneGeometry(36, 36)
  sliceGeo.rotateX(-Math.PI / 2)
  const sliceMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    transparent: true,
    opacity: 0.18,
    side: THREE.DoubleSide
  })
  slicePlaneMesh = new THREE.Mesh(sliceGeo, sliceMat)
  slicePlaneMesh.position.y = 1.2
  scene.add(slicePlaneMesh)

  // Animation Loop
  const clock = new THREE.Clock()
  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const elapsed = clock.getElapsedTime()

    if (isAutoRotating.value && reliefMeshGroup) {
      reliefMeshGroup.rotation.y = elapsed * 0.15
      contourLineGroup.rotation.y = elapsed * 0.15
    }

    // Gentle pulse on the active beacon pin head
    const activePin = beaconPins[currentMilestoneIndex.value]
    if (activePin) {
      const head = activePin.children[1] as THREE.Mesh
      head.position.y = 2.4 + Math.sin(elapsed * 4) * 0.12
    }

    camera.lookAt(0, 4, 0)
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
  <div class="mock-topo-relief-root">
    <!-- Split Layout: 3D Relief Table (Left 55%) + Surveyor Drafting Desk (Right 45%) -->
    <div class="topo-split-container">
      <!-- LEFT 55%: 3D Topographic Relief Table -->
      <div class="topo-viewport-pane">
        <canvas ref="canvasRef" class="topo-webgl-canvas" />

        <!-- Topo Studio Floating Controls Overlay -->
        <div class="topo-controls-overlay">
          <div class="studio-badge-pill">
            <span class="compass-marker">📐</span>
            <div class="badge-text">
              <span class="studio-sub">TVI CARTOGRAPHY STUDIO · ARCHEPOINT 02</span>
              <h1 class="studio-title">Topographic Relief Desk</h1>
            </div>
          </div>

          <!-- Camera View Angle Toggle -->
          <div class="view-angle-segmented">
            <button
              type="button"
              class="angle-seg-btn"
              :class="{ active: cameraViewMode === 'angled' }"
              @click="setCameraView('angled')"
            >
              3D Ortho
            </button>
            <button
              type="button"
              class="angle-seg-btn"
              :class="{ active: cameraViewMode === 'top' }"
              @click="setCameraView('top')"
            >
              Plan View
            </button>
            <button
              type="button"
              class="angle-seg-btn"
              :class="{ active: cameraViewMode === 'profile' }"
              @click="setCameraView('profile')"
            >
              Elevation Cut
            </button>
          </div>
        </div>

        <!-- Bottom Elevation Slicer Slider Bar -->
        <div class="topo-slice-dock">
          <div class="slice-header">
            <span class="slice-lbl">CONTOUR SLICER ELEVATION:</span>
            <span class="slice-val font-mono">{{ Math.round(sliceElevation) }}M</span>
          </div>
          <input
            type="range"
            min="1400"
            max="8848"
            step="50"
            v-model.number="sliceElevation"
            class="slice-slider"
            @input="updateSliceHeight"
          />
          <div class="slice-waypoints-ticks">
            <span
              v-for="(m, idx) in milestones"
              :key="m.id"
              class="tick-btn"
              :class="{ active: currentMilestoneIndex === idx }"
              @click="selectMilestone(idx)"
            >
              {{ m.altitude }}m
            </span>
          </div>
        </div>
      </div>

      <!-- RIGHT 45%: Expedition Surveyor's Field Drafting Desk -->
      <div class="surveyor-desk-pane">
        <!-- Milestone Elevation Header Bar -->
        <div class="milestone-tabs-strip">
          <button
            v-for="(m, idx) in milestones"
            :key="m.id"
            type="button"
            class="milestone-strip-tab"
            :class="{ active: currentMilestoneIndex === idx }"
            @click="selectMilestone(idx)"
            @mouseenter="setCursor(`INSPECT SURVEY 0${m.number}`, 'pointer')"
            @mouseleave="resetCursor"
          >
            <span class="tab-stage">STG 0{{ m.number }}</span>
            <span class="tab-alt font-mono">{{ m.altitude }}m</span>
          </button>
        </div>

        <!-- Surveyor Record Dossier Header -->
        <div class="dossier-meta-card">
          <div class="dossier-top">
            <span class="survey-badge">OFFICIAL SURVEY RECORD #0{{ activeMilestone.number }}</span>
            <span class="coord-tag font-mono">LAT 27°59′N · LONG 86°55′E</span>
          </div>
          <h2 class="dossier-heading">{{ activeMilestone.name }}</h2>
          <p class="dossier-summary">{{ activeMilestone.business.executiveSummary }}</p>
        </div>

        <!-- THE 2 DUAL NOTEBOOKS LAID OPEN ON THE SURVEY DESK BLOTTER -->
        <div class="desk-blotter-area">
          <div class="blotter-instruction">
            <span>FIELD LOGS RESTING ON DRAFTING DESK (CLICK TO OPEN):</span>
          </div>

          <div class="dual-notebooks-blotter-grid">
            <!-- 1. Left Open Notebook: Business Survey Dossier -->
            <div
              class="open-desk-notebook business-book"
              @click="openNotebook('business')"
              @mouseenter="setCursor('OPEN BUSINESS FIELD GUIDE', 'action')"
              @mouseleave="resetCursor"
            >
              <div class="notebook-spine business-spine">
                <span class="spine-text">BUSINESS GUIDE</span>
              </div>
              <div class="open-pages-surface">
                <div class="page-corner-tag">FIELD GUIDE · 0{{ activeMilestone.number }}</div>
                <h3 class="notebook-hed">Executive ROI & Strategy</h3>
                <p class="notebook-snippet">{{ activeMilestone.business.businessImpact }}</p>

                <!-- CFO Insight Ribbon -->
                <div class="cfo-blotter-note">
                  <span class="cfo-mini-hed">CFO TAKEAWAY:</span>
                  <p class="cfo-mini-quote">“{{ activeMilestone.business.cfoTakeaway }}”</p>
                </div>

                <div class="open-book-cta">
                  <span>Inspect Full Guide</span>
                  <span class="cta-arrow">→</span>
                </div>
              </div>
            </div>

            <!-- 2. Right Open Notebook: Technical Survey Blueprint -->
            <div
              class="open-desk-notebook technical-book"
              @click="openNotebook('technical')"
              @mouseenter="setCursor('OPEN TECHNICAL FIELD MANUAL', 'action')"
              @mouseleave="resetCursor"
            >
              <div class="notebook-spine technical-spine">
                <span class="spine-text">TECH MANUAL</span>
              </div>
              <div class="open-pages-surface">
                <div class="page-corner-tag tech">TECH MANUAL · 0{{ activeMilestone.number }}</div>
                <h3 class="notebook-hed">Mathematical Specification</h3>
                <p class="notebook-snippet">{{ activeMilestone.technical.formulaExplanation }}</p>

                <!-- Formula Preview Pill -->
                <div class="formula-blotter-note">
                  <span class="cfo-mini-hed tech">FIRST-PRINCIPLES MATH:</span>
                  <span class="formula-mini-name">{{ activeMilestone.technical.formulaName }}</span>
                  <span class="sla-mini-badge">SLA: {{ activeMilestone.technical.latencySla }}</span>
                </div>

                <div class="open-book-cta tech">
                  <span>Inspect Code & Proofs</span>
                  <span class="cta-arrow">→</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Desk Footer: Surveyor Verification Stamp -->
        <div class="desk-footer-stamp">
          <div class="carto-seal">
            <span class="seal-ring">CARTOGRAPHIC AUDIT PASS</span>
          </div>
          <div class="seal-meta">
            <strong>Datum: WGS84 Alpine Orthometric</strong>
            <span>Dual-Notebook Reconciled · Machine Epsilon Certified</span>
          </div>
        </div>
      </div>
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
.mock-topo-relief-root {
  position: relative;
  width: 100%;
  height: 100vh;
  background-color: #fcfcfd;
  overflow: hidden;
  user-select: none;
}

.topo-split-container {
  display: flex;
  width: 100%;
  height: 100%;
}

/* LEFT 55%: 3D Topographic Relief Table */
.topo-viewport-pane {
  position: relative;
  width: 55%;
  height: 100%;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
}

.topo-webgl-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.topo-controls-overlay {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  right: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  pointer-events: none;
}

.topo-controls-overlay > * {
  pointer-events: auto;
}

.studio-badge-pill {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  padding: 0.75rem 1.4rem;
  border-radius: 20px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.compass-marker {
  font-size: 1.6rem;
}

.studio-sub {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 800;
  color: #0284c7;
  letter-spacing: 0.08em;
  display: block;
}

.studio-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.view-angle-segmented {
  display: flex;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  padding: 0.3rem;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.angle-seg-btn {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.4rem 0.85rem;
  border: none;
  background: transparent;
  color: #475569;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: all 0.2s ease;
}

.angle-seg-btn.active {
  background: #0f172a;
  color: #ffffff;
}

/* Bottom Elevation Slicer Dock */
.topo-slice-dock {
  position: absolute;
  bottom: 1.5rem;
  left: 1.5rem;
  right: 1.5rem;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  padding: 1rem 1.5rem;
  border-radius: 20px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}

.slice-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.slice-lbl {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #64748b;
}

.slice-val {
  font-size: 0.85rem;
  font-weight: 800;
  color: #0284c7;
}

.slice-slider {
  width: 100%;
  accent-color: #0284c7;
  cursor: pointer;
}

.slice-waypoints-ticks {
  display: flex;
  justify-content: space-between;
  margin-top: 0.4rem;
}

.tick-btn {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.tick-btn:hover {
  color: #0284c7;
}

.tick-btn.active {
  color: #0284c7;
  font-weight: 800;
  background: #e0f2fe;
}

/* RIGHT 45%: Expedition Surveyor's Field Drafting Desk */
.surveyor-desk-pane {
  width: 45%;
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 2rem;
  overflow-y: auto;
}

.milestone-tabs-strip {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #e2e8f0;
}

.milestone-strip-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.45rem 0.65rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
}

.milestone-strip-tab:hover {
  background: #f1f5f9;
}

.milestone-strip-tab.active {
  background: #0284c7;
  border-color: #0284c7;
}

.tab-stage {
  font-size: 0.62rem;
  font-weight: 800;
  color: #64748b;
}

.tab-alt {
  font-size: 0.72rem;
  font-weight: 800;
  color: #0f172a;
}

.milestone-strip-tab.active .tab-stage,
.milestone-strip-tab.active .tab-alt {
  color: #ffffff;
}

.dossier-meta-card {
  margin-bottom: 1.4rem;
}

.dossier-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.survey-badge {
  font-size: 0.68rem;
  font-weight: 800;
  color: #b45309;
  letter-spacing: 0.05em;
}

.coord-tag {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: 600;
}

.dossier-heading {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.4rem;
}

.dossier-summary {
  font-size: 0.88rem;
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

/* DUAL NOTEBOOKS ON DESK BLOTTER */
.desk-blotter-area {
  margin-bottom: 1.5rem;
  flex: 1;
}

.blotter-instruction {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #64748b;
  margin-bottom: 0.8rem;
}

.dual-notebooks-blotter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.1rem;
}

.open-desk-notebook {
  position: relative;
  display: flex;
  background: #fdfefe;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  overflow: hidden;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.open-desk-notebook:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.08);
}

.notebook-spine {
  width: 24px;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.8rem 0;
}

.business-spine {
  background: #b45309;
}

.technical-spine {
  background: #0284c7;
}

.spine-text {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 0.1em;
}

.open-pages-surface {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.page-corner-tag {
  font-size: 0.6rem;
  font-weight: 800;
  color: #b45309;
  margin-bottom: 0.3rem;
}

.page-corner-tag.tech {
  color: #0284c7;
}

.notebook-hed {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.35rem;
}

.notebook-snippet {
  font-size: 0.78rem;
  color: #475569;
  line-height: 1.4;
  margin-bottom: 0.8rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cfo-blotter-note {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  padding: 0.5rem 0.7rem;
  border-radius: 8px;
  margin-bottom: 0.8rem;
}

.formula-blotter-note {
  background: #f0f9ff;
  border-left: 3px solid #0284c7;
  padding: 0.5rem 0.7rem;
  border-radius: 8px;
  margin-bottom: 0.8rem;
}

.cfo-mini-hed {
  font-size: 0.6rem;
  font-weight: 800;
  color: #b45309;
  display: block;
}

.cfo-mini-hed.tech {
  color: #0284c7;
}

.cfo-mini-quote {
  font-size: 0.72rem;
  font-style: italic;
  color: #78350f;
  margin: 0.2rem 0 0;
  line-height: 1.35;
}

.formula-mini-name {
  font-size: 0.72rem;
  font-weight: 700;
  color: #0369a1;
  display: block;
  margin: 0.2rem 0;
}

.sla-mini-badge {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: #64748b;
  background: rgba(255, 255, 255, 0.8);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

.open-book-cta {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  font-weight: 800;
  color: #b45309;
  padding-top: 0.6rem;
  border-top: 1px dashed #e2e8f0;
}

.open-book-cta.tech {
  color: #0284c7;
}

.cta-arrow {
  font-size: 0.9rem;
  transition: transform 0.2s ease;
}

.open-desk-notebook:hover .cta-arrow {
  transform: translateX(3px);
}

/* Desk Footer Stamp */
.desk-footer-stamp {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.2rem;
  background: #f8fafc;
  border-radius: 14px;
  border: 1px dashed #cbd5e1;
}

.carto-seal {
  font-family: var(--font-mono);
  font-size: 0.66rem;
  font-weight: 800;
  color: #059669;
  border: 1.5px solid #059669;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  white-space: nowrap;
}

.seal-meta {
  display: flex;
  flex-direction: column;
  font-size: 0.72rem;
  color: #64748b;
}

.seal-meta strong {
  color: #334155;
}

@media (max-width: 1024px) {
  .topo-split-container {
    flex-direction: column;
  }
  .topo-viewport-pane {
    width: 100%;
    height: 50vh;
  }
  .surveyor-desk-pane {
    width: 100%;
    height: 50vh;
  }
}
</style>
