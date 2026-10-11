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

// Altimeter & Environmental HUD State
const currentAltitude = ref(milestones[0].altitude)
const barometricHpa = ref(865)
const temperatureC = ref(-2)
const oxygenPercent = ref(84)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number
let snowParticles: THREE.Points
let mountainMesh: THREE.Mesh
let trailLine: THREE.Line
let campMarkers: THREE.Group[] = []
let booksGroup: THREE.Group

// Waypoint 3D positions corresponding to the 6 milestones along the mountain slope
const milestoneWaypoints = [
  { x: -18, y: -2, z: 22, lookAt: { x: -16, y: -1, z: 18 }, alt: 1400, hpa: 865, temp: -2, o2: 84 },
  { x: -10, y: 5, z: 12, lookAt: { x: -8, y: 6, z: 8 }, alt: 2900, hpa: 720, temp: -8, o2: 73 },
  { x: -2, y: 12, z: 4, lookAt: { x: 0, y: 13, z: 0 }, alt: 4400, hpa: 590, temp: -15, o2: 60 },
  { x: 5, y: 18, z: -4, lookAt: { x: 7, y: 19, z: -8 }, alt: 5900, hpa: 480, temp: -22, o2: 48 },
  { x: 11, y: 24, z: -12, lookAt: { x: 13, y: 25, z: -16 }, alt: 7300, hpa: 390, temp: -29, o2: 38 },
  { x: 16, y: 31, z: -20, lookAt: { x: 18, y: 32, z: -22 }, alt: 8848, hpa: 310, temp: -36, o2: 31 }
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
  
  const wp = milestoneWaypoints[index]
  
  // Animate HUD Telemetry
  gsap.to(currentAltitude, { value: wp.alt, duration: 1.2, ease: 'power2.out', roundProps: 'value' })
  gsap.to(barometricHpa, { value: wp.hpa, duration: 1.2, ease: 'power2.out', roundProps: 'value' })
  gsap.to(temperatureC, { value: wp.temp, duration: 1.2, ease: 'power2.out', roundProps: 'value' })
  gsap.to(oxygenPercent, { value: wp.o2, duration: 1.2, ease: 'power2.out', roundProps: 'value' })

  // Animate Camera to new waypoint
  if (camera) {
    const camOffset = { x: wp.x + 6, y: wp.y + 4, z: wp.z + 10 }
    gsap.to(camera.position, {
      x: camOffset.x,
      y: camOffset.y,
      z: camOffset.z,
      duration: 1.6,
      ease: 'power3.inOut'
    })
    
    // Position 3D Field Books near active waypoint
    if (booksGroup) {
      gsap.to(booksGroup.position, {
        x: wp.x,
        y: wp.y + 0.5,
        z: wp.z,
        duration: 1.4,
        ease: 'power2.out'
      })
    }
  }

  playInteractChime(1.1 + index * 0.1)
}

const nextMilestone = () => {
  if (currentMilestoneIndex.value < milestones.length - 1) {
    selectMilestone(currentMilestoneIndex.value + 1)
  }
}

const prevMilestone = () => {
  if (currentMilestoneIndex.value > 0) {
    selectMilestone(currentMilestoneIndex.value - 1)
  }
}

const initThreeScene = () => {
  if (!canvasRef.value) return

  const width = canvasRef.value.clientWidth
  const height = canvasRef.value.clientHeight

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf8fafc) // Crisp white alpine daylight
  scene.fog = new THREE.FogExp2(0xf8fafc, 0.015)

  camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000)
  const initialWp = milestoneWaypoints[0]
  camera.position.set(initialWp.x + 6, initialWp.y + 4, initialWp.z + 10)
  camera.lookAt(initialWp.lookAt.x, initialWp.lookAt.y, initialWp.lookAt.z)

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

  // Alpine Daylight Lighting
  const ambientLight = new THREE.AmbientLight(0xe0f2fe, 1.2) // Soft icy sky light
  scene.add(ambientLight)

  const sunLight = new THREE.DirectionalLight(0xffffff, 1.8) // Bright sun on snow
  sunLight.position.set(40, 60, 30)
  sunLight.castShadow = true
  sunLight.shadow.mapSize.width = 1024
  sunLight.shadow.mapSize.height = 1024
  scene.add(sunLight)

  const blueBacklight = new THREE.DirectionalLight(0x93c5fd, 0.6) // Glacial bounce
  blueBacklight.position.set(-40, 20, -30)
  scene.add(blueBacklight)

  // 1. Procedural 3D Ice-Capped Mountain Range
  const mountainGeo = new THREE.PlaneGeometry(100, 100, 64, 64)
  mountainGeo.rotateX(-Math.PI / 2)

  const pos = mountainGeo.attributes.position
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i)
    const z = pos.getZ(i)
    
    // Mountain ridge mathematics: diagonal ridge with sharp summit at (20, -25)
    const distToPeak = Math.hypot(x - 18, z - (-22))
    const peakElevation = Math.max(0, 36 - distToPeak * 0.65)
    
    // Secondary alpine ridges
    const ridge1 = Math.sin(x * 0.08) * Math.cos(z * 0.08) * 6
    const ridge2 = Math.sin(x * 0.15 + z * 0.1) * 3
    const noise = Math.sin(x * 0.3) * Math.cos(z * 0.3) * 1.2

    let y = peakElevation + ridge1 + ridge2 + noise - 4
    if (distToPeak < 8) y += (8 - distToPeak) * 0.8 // Sharp apex pinnacle
    
    pos.setY(i, y)
  }
  mountainGeo.computeVertexNormals()

  // Mountain Material (Glacial Rock + Glistening White Snow Caps)
  const mountainMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.6,
    metalness: 0.1,
    flatShading: true
  })
  mountainMesh = new THREE.Mesh(mountainGeo, mountainMat)
  mountainMesh.receiveShadow = true
  scene.add(mountainMesh)

  // 2. Expedition Climbing Trail Ribbon
  const curvePoints = milestoneWaypoints.map(wp => new THREE.Vector3(wp.x, wp.y + 0.3, wp.z))
  const trailCurve = new THREE.CatmullRomCurve3(curvePoints)
  const trailGeo = new THREE.TubeGeometry(trailCurve, 64, 0.12, 8, false)
  const trailMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.75 })
  trailLine = new THREE.Mesh(trailGeo, trailMat)
  scene.add(trailLine)

  // 3. Milestone Waypoint Flags & Cairns
  milestoneWaypoints.forEach((wp, idx) => {
    const markerGroup = new THREE.Group()
    markerGroup.position.set(wp.x, wp.y, wp.z)

    // Flagpole
    const poleGeo = new THREE.CylinderGeometry(0.05, 0.05, 2.2, 8)
    const poleMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.8 })
    const pole = new THREE.Mesh(poleGeo, poleMat)
    pole.position.y = 1.1
    markerGroup.add(pole)

    // Vibrant Orange/Cyan Milestone Flag
    const flagGeo = new THREE.BoxGeometry(0.7, 0.45, 0.03)
    const flagMat = new THREE.MeshStandardMaterial({
      color: idx === 5 ? 0xe11d48 : idx % 2 === 0 ? 0x0284c7 : 0xd97706,
      roughness: 0.3
    })
    const flag = new THREE.Mesh(flagGeo, flagMat)
    flag.position.set(0.35, 1.9, 0)
    markerGroup.add(flag)

    // Glowing base cairn ring
    const ringGeo = new THREE.RingGeometry(0.4, 0.8, 16)
    ringGeo.rotateX(-Math.PI / 2)
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6
    })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.position.y = 0.05
    markerGroup.add(ring)

    campMarkers.push(markerGroup)
    scene.add(markerGroup)
  })

  // 4. Interactive 3D Field Books Resting on Mountain Snow Ledge
  booksGroup = new THREE.Group()
  const wp0 = milestoneWaypoints[0]
  booksGroup.position.set(wp0.x, wp0.y + 0.5, wp0.z)

  // Business Field Guide (Leather Amber Book)
  const bizBookGeo = new THREE.BoxGeometry(1.2, 0.2, 0.9)
  const bizBookMat = new THREE.MeshStandardMaterial({ color: 0xb45309, roughness: 0.4, metalness: 0.2 })
  const bizBookMesh = new THREE.Mesh(bizBookGeo, bizBookMat)
  bizBookMesh.position.set(-0.8, 0.1, 0)
  bizBookMesh.rotation.y = 0.25
  bizBookMesh.castShadow = true
  booksGroup.add(bizBookMesh)

  // Technical Field Manual (Glacial Blue Book)
  const techBookGeo = new THREE.BoxGeometry(1.2, 0.2, 0.9)
  const techBookMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.3, metalness: 0.3 })
  const techBookMesh = new THREE.Mesh(techBookGeo, techBookMat)
  techBookMesh.position.set(0.8, 0.1, 0)
  techBookMesh.rotation.y = -0.2
  techBookMesh.castShadow = true
  booksGroup.add(techBookMesh)

  scene.add(booksGroup)

  // 5. Alpine Drifting Snow Flurry Particle System
  const particleCount = 1200
  const snowGeo = new THREE.BufferGeometry()
  const snowPositions = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount * 3; i += 3) {
    snowPositions[i] = (Math.random() - 0.5) * 80
    snowPositions[i + 1] = Math.random() * 45
    snowPositions[i + 2] = (Math.random() - 0.5) * 80
  }
  snowGeo.setAttribute('position', new THREE.BufferAttribute(snowPositions, 3))

  const snowMat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.25,
    transparent: true,
    opacity: 0.75
  })
  snowParticles = new THREE.Points(snowGeo, snowMat)
  scene.add(snowParticles)

  // Animation Loop
  const clock = new THREE.Clock()
  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const elapsed = clock.getElapsedTime()

    // Snow Flurry Motion
    const positions = snowParticles.geometry.attributes.position.array as Float32Array
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i + 1] -= 0.08 // falling
      positions[i] += Math.sin(elapsed * 0.5 + positions[i + 1]) * 0.02 // drift
      if (positions[i + 1] < -5) {
        positions[i + 1] = 42
      }
    }
    snowParticles.geometry.attributes.position.needsUpdate = true

    // Gentle hover animation on 3D field books
    if (booksGroup) {
      booksGroup.children[0].rotation.y = 0.25 + Math.sin(elapsed * 1.5) * 0.05
      booksGroup.children[1].rotation.y = -0.2 + Math.cos(elapsed * 1.5) * 0.05
    }

    // Gentle camera breathing
    const targetWp = milestoneWaypoints[currentMilestoneIndex.value]
    camera.lookAt(
      targetWp.lookAt.x + Math.sin(elapsed * 0.4) * 0.3,
      targetWp.lookAt.y + Math.cos(elapsed * 0.4) * 0.2,
      targetWp.lookAt.z
    )

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
  <div class="mock-mountain-ascent-root">
    <!-- Three.js Canvas: 3D Mountain Ridge Ascent -->
    <canvas ref="canvasRef" class="webgl-canvas" />

    <!-- Pure White Alpine HUD Overlay -->
    <div class="ascent-interface-overlay">
      <!-- 1. Top Mountain Header & Telemetry Bar -->
      <header class="ascent-top-header">
        <div class="expedition-badge">
          <span class="compass-icon">🧭</span>
          <div>
            <span class="sub-label">TVI SUMMIT EXPEDITION · ARCHEPOINT 01</span>
            <h1 class="header-title">The Summit Ridge Ascent</h1>
          </div>
        </div>

        <!-- Telemetry Gauges -->
        <div class="telemetry-gauges-cluster">
          <div class="gauge-pill">
            <span class="gauge-label">ALTITUDE</span>
            <span class="gauge-value font-mono">{{ Math.round(currentAltitude) }}m</span>
          </div>
          <div class="gauge-pill">
            <span class="gauge-label">BAROMETER</span>
            <span class="gauge-value font-mono">{{ Math.round(barometricHpa) }} hPa</span>
          </div>
          <div class="gauge-pill">
            <span class="gauge-label">TEMP</span>
            <span class="gauge-value font-mono">{{ Math.round(temperatureC) }}°C</span>
          </div>
          <div class="gauge-pill highlight-pill">
            <span class="gauge-label">EFFECTIVE O₂</span>
            <span class="gauge-value font-mono">{{ Math.round(oxygenPercent) }}%</span>
          </div>
        </div>
      </header>

      <!-- 2. Left Altimeter Elevation Track -->
      <aside class="left-altimeter-track">
        <div class="altimeter-rail-header">
          <span class="rail-title">ASCENT ELEVATION</span>
          <span class="rail-sub">8,848M SUMMIT</span>
        </div>

        <div class="milestones-vertical-rail">
          <div
            v-for="(m, idx) in milestones"
            :key="m.id"
            class="rail-waypoint-item"
            :class="{ active: currentMilestoneIndex === idx, past: currentMilestoneIndex > idx }"
            @click="selectMilestone(idx)"
            @mouseenter="setCursor(`CAMP 0${m.number}: ${m.name.toUpperCase()}`, 'pointer')"
            @mouseleave="resetCursor"
          >
            <div class="waypoint-pin">
              <span class="pin-dot" />
              <span class="pin-pulse" v-if="currentMilestoneIndex === idx" />
            </div>
            <div class="waypoint-info">
              <span class="waypoint-alt font-mono">{{ m.altitude }}m</span>
              <span class="waypoint-name">{{ m.name }}</span>
            </div>
          </div>
        </div>

        <!-- Ascent Progress Meter -->
        <div class="elevation-progress-bar">
          <div
            class="progress-fill"
            :style="{ height: `${((currentMilestoneIndex + 1) / milestones.length) * 100}%` }"
          />
        </div>
      </aside>

      <!-- 3. Active Milestone Camp Card with TWO Clickable Notebooks -->
      <section class="milestone-spotlight-card">
        <div class="spotlight-header">
          <div class="camp-pill">
            <span class="camp-num">CAMP 0{{ activeMilestone.number }}</span>
            <span class="camp-alt font-mono">{{ activeMilestone.altitude }}m</span>
          </div>
          <span class="terrain-tag">{{ activeMilestone.location }}</span>
        </div>

        <h2 class="spotlight-title">{{ activeMilestone.name }}</h2>
        <p class="spotlight-desc">{{ activeMilestone.subTitle }}</p>

        <!-- THE 2 MANDATORY CLICKABLE FIELD NOTEBOOKS -->
        <div class="dual-notebooks-launchpad">
          <div class="notebook-launch-hed">
            <span>FIELD RECORDS AVAILABLE AT THIS MILESTONE:</span>
          </div>

          <div class="notebooks-cards-grid">
            <!-- Notebook 1: Business Field Guide -->
            <button
              type="button"
              class="notebook-clickable-card business-card"
              @click="openNotebook('business')"
              @mouseenter="setCursor('OPEN BUSINESS FIELD GUIDE', 'action')"
              @mouseleave="resetCursor"
            >
              <div class="book-cover-accent business-accent" />
              <div class="book-card-body">
                <div class="book-card-top">
                  <span class="book-icon-badge">📖</span>
                  <span class="book-status">CLICK TO INSPECT</span>
                </div>
                <h3 class="book-card-title">Business Field Guide</h3>
                <p class="book-card-sub">Executive ROI, TBM Strategy & KPI Trajectories</p>
                <div class="book-meta-footer">
                  <span class="meta-tag">CFO Takeaway</span>
                  <span class="meta-tag">Zero Drift</span>
                  <span class="open-arrow">↗</span>
                </div>
              </div>
            </button>

            <!-- Notebook 2: Technical Field Manual -->
            <button
              type="button"
              class="notebook-clickable-card technical-card"
              @click="openNotebook('technical')"
              @mouseenter="setCursor('OPEN TECHNICAL FIELD MANUAL', 'action')"
              @mouseleave="resetCursor"
            >
              <div class="book-cover-accent technical-accent" />
              <div class="book-card-body">
                <div class="book-card-top">
                  <span class="book-icon-badge">📐</span>
                  <span class="book-status">CLICK TO INSPECT</span>
                </div>
                <h3 class="book-card-title">Technical Field Manual</h3>
                <p class="book-card-sub">Mathematical Proofs, SLA Budgets & Source Code</p>
                <div class="book-meta-footer">
                  <span class="meta-tag">KaTeX Proof</span>
                  <span class="meta-tag">Python Module</span>
                  <span class="open-arrow">↗</span>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Navigation Controls between Camps -->
        <div class="milestone-nav-buttons">
          <button
            type="button"
            class="camp-nav-btn"
            :disabled="currentMilestoneIndex === 0"
            @click="prevMilestone"
          >
            ← Previous Camp
          </button>
          <span class="step-indicator">
            Milestone {{ currentMilestoneIndex + 1 }} of {{ milestones.length }}
          </span>
          <button
            type="button"
            class="camp-nav-btn primary"
            :disabled="currentMilestoneIndex === milestones.length - 1"
            @click="nextMilestone"
          >
            Ascend Next Camp →
          </button>
        </div>
      </section>

      <!-- 4. Bottom Horizontal Camp Navigation Bar -->
      <nav class="bottom-camps-dock">
        <button
          v-for="(m, idx) in milestones"
          :key="m.id"
          type="button"
          class="camp-dock-btn"
          :class="{ active: currentMilestoneIndex === idx }"
          @click="selectMilestone(idx)"
        >
          <span class="dock-num">0{{ m.number }}</span>
          <div class="dock-text">
            <span class="dock-name">{{ m.name }}</span>
            <span class="dock-alt font-mono">{{ m.altitude }}m</span>
          </div>
        </button>
      </nav>
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
.mock-mountain-ascent-root {
  position: relative;
  width: 100%;
  height: 100vh;
  background-color: #f8fafc;
  overflow: hidden;
  user-select: none;
}

.webgl-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}

/* Pure White Alpine HUD Overlay */
.ascent-interface-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.5rem 2rem 1.8rem;
}

.ascent-interface-overlay > * {
  pointer-events: auto;
}

/* 1. Top Mountain Header & Telemetry Bar */
.ascent-top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  padding: 0.9rem 1.6rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
}

.expedition-badge {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.compass-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 2px 6px rgba(2, 132, 199, 0.2));
}

.sub-label {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #0284c7;
  display: block;
}

.header-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.telemetry-gauges-cluster {
  display: flex;
  gap: 0.75rem;
}

.gauge-pill {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 0.4rem 0.85rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.gauge-label {
  font-size: 0.62rem;
  font-weight: 800;
  color: #64748b;
  letter-spacing: 0.05em;
}

.gauge-value {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
}

.highlight-pill {
  background: #e0f2fe;
  border-color: #bae6fd;
}
.highlight-pill .gauge-value {
  color: #0369a1;
}

/* 2. Left Altimeter Elevation Track */
.left-altimeter-track {
  position: absolute;
  top: 6.5rem;
  left: 2rem;
  width: 220px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  padding: 1.2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
}

.altimeter-rail-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid #e2e8f0;
}

.rail-title {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #0f172a;
}

.rail-sub {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  color: #0284c7;
}

.milestones-vertical-rail {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  position: relative;
  z-index: 2;
}

.rail-waypoint-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.35rem 0.5rem;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.rail-waypoint-item:hover {
  background: #f1f5f9;
}

.rail-waypoint-item.active {
  background: #e0f2fe;
}

.waypoint-pin {
  position: relative;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pin-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  transition: all 0.2s ease;
}

.rail-waypoint-item.past .pin-dot {
  background: #0284c7;
}

.rail-waypoint-item.active .pin-dot {
  background: #0284c7;
  transform: scale(1.3);
}

.pin-pulse {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 2px solid #0284c7;
  animation: pulse-ring 1.8s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.8); opacity: 0; }
}

.waypoint-info {
  display: flex;
  flex-direction: column;
}

.waypoint-alt {
  font-size: 0.68rem;
  font-weight: 800;
  color: #0284c7;
}

.waypoint-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
}

.rail-waypoint-item.active .waypoint-name {
  color: #0f172a;
  font-weight: 800;
}

/* 3. Active Milestone Camp Card with TWO Clickable Notebooks */
.milestone-spotlight-card {
  position: absolute;
  top: 6.5rem;
  right: 2rem;
  width: 480px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 24px;
  padding: 1.6rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.06);
}

.spotlight-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.6rem;
}

.camp-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #0f172a;
  color: #ffffff;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
}

.terrain-tag {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748b;
}

.spotlight-title {
  font-family: var(--font-display);
  font-size: 1.45rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.3rem;
}

.spotlight-desc {
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.45;
  margin-bottom: 1.3rem;
}

/* DUAL NOTEBOOKS LAUNCHPAD */
.dual-notebooks-launchpad {
  margin-bottom: 1.2rem;
}

.notebook-launch-hed {
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #64748b;
  margin-bottom: 0.6rem;
}

.notebooks-cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.notebook-clickable-card {
  position: relative;
  text-align: left;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 0;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
}

.notebook-clickable-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
}

.book-cover-accent {
  height: 6px;
  width: 100%;
}
.business-accent { background: linear-gradient(90deg, #d97706, #b45309); }
.technical-accent { background: linear-gradient(90deg, #0284c7, #0369a1); }

.book-card-body {
  padding: 0.9rem;
}

.book-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.book-icon-badge {
  font-size: 1.1rem;
}

.book-status {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 800;
  color: #94a3b8;
  letter-spacing: 0.05em;
}

.book-card-title {
  font-size: 0.88rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.25rem;
}

.book-card-sub {
  font-size: 0.72rem;
  color: #64748b;
  line-height: 1.35;
  margin: 0 0 0.75rem;
  min-height: 38px;
}

.book-meta-footer {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.meta-tag {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
  background: #f1f5f9;
  color: #475569;
}

.open-arrow {
  margin-left: auto;
  font-size: 0.85rem;
  font-weight: 800;
  color: #0f172a;
}

.notebook-clickable-card:hover .open-arrow {
  transform: translate(2px, -2px);
  color: #0284c7;
}

/* Nav Controls */
.milestone-nav-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.camp-nav-btn {
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

.camp-nav-btn:hover:not(:disabled) {
  background: #0f172a;
  color: #ffffff;
}

.camp-nav-btn.primary {
  background: #0284c7;
  color: #ffffff;
  border-color: #0284c7;
}
.camp-nav-btn.primary:hover:not(:disabled) {
  background: #0369a1;
}

.camp-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.step-indicator {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 600;
}

/* 4. Bottom Horizontal Camp Navigation Bar */
.bottom-camps-dock {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  padding: 0.6rem 0.9rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
  width: fit-content;
  margin: 0 auto;
}

.camp-dock-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.85rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.camp-dock-btn:hover {
  background: #f1f5f9;
}

.camp-dock-btn.active {
  background: #ffffff;
  border-color: #0284c7;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.15);
}

.dock-num {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 800;
  color: #94a3b8;
}

.camp-dock-btn.active .dock-num {
  color: #0284c7;
}

.dock-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.dock-name {
  font-size: 0.78rem;
  font-weight: 700;
  color: #334155;
}

.camp-dock-btn.active .dock-name {
  color: #0f172a;
}

.dock-alt {
  font-size: 0.66rem;
  font-weight: 600;
  color: #64748b;
}

@media (max-width: 1024px) {
  .left-altimeter-track {
    display: none;
  }
  .milestone-spotlight-card {
    position: relative;
    top: auto;
    right: auto;
    width: 100%;
    margin-top: 1rem;
  }
}
</style>
