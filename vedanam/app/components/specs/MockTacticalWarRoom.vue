<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useTechSpecs, type TechSpecStep } from '~/composables/useTechSpecs'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import MathFormula from '~/components/MathFormula.vue'

const { steps, phases } = useTechSpecs()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const globeHostRef = ref<HTMLDivElement | null>(null)
const lockedTargetId = ref<number>(1)
const isSimulatingBlast = ref<boolean>(false)
const blastCascadeProgress = ref<number>(0)
const decryptingCode = ref<boolean>(false)

const currentTarget = computed<TechSpecStep>(() => {
  return steps.find(s => s.id === lockedTargetId.value) || steps[0]
})

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let globeGroup: THREE.Group
let targetNodes: { id: number; mesh: THREE.Mesh; pos: THREE.Vector3 }[] = []
let scanRingMesh: THREE.Mesh
let shockwaveRing: THREE.Mesh

const lockTarget = (id: number) => {
  lockedTargetId.value = id
  playInteractChime(1.4 + (id % 6) * 0.1)

  // Rotate globe to face selected node
  const found = targetNodes.find(t => t.id === id)
  if (found && globeGroup) {
    const targetRotY = -Math.atan2(found.pos.x, found.pos.z)
    gsap.to(globeGroup.rotation, {
      y: targetRotY,
      duration: 0.9,
      ease: 'power3.out'
    })
  }
}

const triggerBlastSimulation = () => {
  if (isSimulatingBlast.value) return
  isSimulatingBlast.value = true
  blastCascadeProgress.value = 0
  playInteractChime(0.8)

  if (shockwaveRing) {
    shockwaveRing.scale.set(0.1, 0.1, 0.1)
    gsap.to(shockwaveRing.scale, {
      x: 3.5,
      y: 3.5,
      z: 3.5,
      duration: 1.5,
      ease: 'power2.out',
      onComplete: () => {
        isSimulatingBlast.value = false
        playInteractChime(1.8)
      }
    })
  }

  // Stagger node flash
  targetNodes.forEach((tn, idx) => {
    setTimeout(() => {
      blastCascadeProgress.value = Math.round(((idx + 1) / targetNodes.length) * 100)
      playInteractChime(1.2 + idx * 0.05)
      gsap.fromTo(tn.mesh.scale, { x: 2, y: 2, z: 2 }, { x: 1, y: 1, z: 1, duration: 0.4 })
    }, idx * 100)
  })
}

onMounted(() => {
  if (!process.client || !globeHostRef.value) return

  const container = globeHostRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100)
  camera.position.set(0, 1.5, 9.5)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  const ambient = new THREE.AmbientLight(0xffffff, 1.0)
  scene.add(ambient)

  const dirLight = new THREE.DirectionalLight(0x38bdf8, 2.0)
  dirLight.position.set(5, 10, 5)
  scene.add(dirLight)

  globeGroup = new THREE.Group()
  scene.add(globeGroup)

  // 1. Tactical Wireframe Globe Sphere
  const globeGeom = new THREE.IcosahedronGeometry(3.0, 2)
  const globeMat = new THREE.MeshBasicMaterial({
    color: 0x0284c7,
    wireframe: true,
    transparent: true,
    opacity: 0.45
  })
  const globeMesh = new THREE.Mesh(globeGeom, globeMat)
  globeGroup.add(globeMesh)

  // Inner solid core sphere
  const innerGeom = new THREE.SphereGeometry(2.85, 32, 32)
  const innerMat = new THREE.MeshBasicMaterial({
    color: 0x081326,
    transparent: true,
    opacity: 0.8
  })
  const innerMesh = new THREE.Mesh(innerGeom, innerMat)
  globeGroup.add(innerMesh)

  // 2. 12 Tactical Beacons placed on the surface of the sphere
  steps.forEach((st, idx) => {
    const phi = Math.acos(-1 + (2 * idx) / steps.length)
    const theta = Math.sqrt(steps.length * Math.PI) * phi
    const r = 3.05

    const x = r * Math.sin(phi) * Math.cos(theta)
    const y = r * Math.cos(phi)
    const z = r * Math.sin(phi) * Math.sin(theta)

    const beaconGeom = new THREE.SphereGeometry(0.18, 16, 16)
    const beaconMat = new THREE.MeshBasicMaterial({
      color: idx % 2 === 0 ? 0x10b981 : 0x38bdf8
    })
    const beaconMesh = new THREE.Mesh(beaconGeom, beaconMat)
    beaconMesh.position.set(x, y, z)
    globeGroup.add(beaconMesh)

    targetNodes.push({ id: st.id, mesh: beaconMesh, pos: new THREE.Vector3(x, y, z) })
  })

  // 3. Shockwave Ring
  const shockGeom = new THREE.RingGeometry(2.8, 3.0, 64)
  const shockMat = new THREE.MeshBasicMaterial({
    color: 0xef4444,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.75
  })
  shockwaveRing = new THREE.Mesh(shockGeom, shockMat)
  shockwaveRing.rotation.x = Math.PI / 2
  scene.add(shockwaveRing)

  // Animation Loop
  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const t = clock.getElapsedTime()

    if (globeGroup) {
      globeGroup.rotation.y += 0.003
    }

    renderer.render(scene, camera)
  }

  animate()

  const handleResize = () => {
    if (!container || !renderer || !camera) return
    const w = container.clientWidth
    const h = container.clientHeight
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId)
  renderer?.dispose()
  resetCursor()
})
</script>

<template>
  <div class="tactical-war-room-root">
    <!-- Top Military Tactical Ops Ribbon -->
    <header class="tactical-ops-ribbon">
      <div class="ribbon-left">
        <span class="classification-tag">UNCLASSIFIED // TVR DEFENSE LEVEL 4</span>
        <h2 class="mission-name">Technology Value Command Hub</h2>
      </div>

      <div class="tactical-telemetry-cluster">
        <div class="tac-item">
          <span class="tac-k">BLAST RADIUS INDEX</span>
          <strong class="tac-v text-red">APP010 (10 Inbound)</strong>
        </div>
        <div class="tac-item">
          <span class="tac-k">SATELLITE TOPOLOGY</span>
          <strong class="tac-v text-sky">102 Nodes · 196 Edges</strong>
        </div>
        <div class="tac-item">
          <span class="tac-k">LEDGER CONSERVATION</span>
          <strong class="tac-v text-green">0.00% Zero-Loss</strong>
        </div>
      </div>

      <button
        type="button"
        class="tactical-blast-btn"
        :class="{ active: isSimulatingBlast }"
        @click="triggerBlastSimulation"
      >
        <span class="radar-ping" />
        <span>{{ isSimulatingBlast ? `CASCADE TEST ${blastCascadeProgress}%` : 'TRIGGER BLAST RADIUS' }}</span>
      </button>
    </header>

    <!-- Main Command Layout (3 Columns) -->
    <div class="tactical-grid-layout">
      <!-- Left Column: Target Lock-On Carousel -->
      <aside class="tactical-sidebar-left">
        <div class="scope-panel-header">
          <span class="p-title">TARGET SATELLITE NODES</span>
          <span class="p-sub">RADAR LOCK</span>
        </div>

        <div class="target-nodes-list">
          <button
            v-for="st in steps"
            :key="st.id"
            type="button"
            class="target-lock-btn"
            :class="{ locked: lockedTargetId === st.id }"
            @click="lockTarget(st.id)"
            @mouseenter="setCursor(`LOCK ${st.code}`, 'highlight')"
            @mouseleave="resetCursor"
          >
            <div class="target-crosshair">
              <span class="ch-line" />
            </div>
            <div class="target-meta">
              <div class="meta-row">
                <span class="t-code">{{ st.code }}</span>
                <span class="t-sla">{{ st.latencySla }}</span>
              </div>
              <strong class="t-name">{{ st.shortTitle }}</strong>
            </div>
          </button>
        </div>
      </aside>

      <!-- Center: 3D Tactical Holo-Sphere & Decryptor Terminal -->
      <main class="tactical-center-column">
        <!-- 3D Globe Card -->
        <div class="globe-tactical-casing">
          <div class="globe-hud-overlay">
            <span class="hud-marker marker-tl">+</span>
            <span class="hud-marker marker-tr">+</span>
            <span class="hud-marker marker-bl">+</span>
            <span class="hud-marker marker-br">+</span>
            <span class="hud-center-crosshair">⌖</span>
          </div>

          <div ref="globeHostRef" class="globe-three-canvas" />

          <!-- Target Card Floating Over Globe -->
          <div class="tactical-target-hud">
            <span class="hud-target-kicker">LOCKED TARGET: {{ currentTarget.code }}</span>
            <h3 class="hud-target-name">{{ currentTarget.title }}</h3>
            <p class="hud-target-summary">{{ currentTarget.summary }}</p>
          </div>
        </div>

        <!-- Formula Decryptor Terminal -->
        <div class="formula-decryptor-card">
          <div class="terminal-bar">
            <span class="term-kicker">MATHEMATICAL DECRYPTOR: {{ currentTarget.formulaName }}</span>
            <span class="decrypt-status">STATUS: DECRYPTED ✓</span>
          </div>
          <div class="decryptor-math-body">
            <MathFormula
              :latex="currentTarget.formulaLatex"
              :formula-html="currentTarget.formulaHtml"
            />
            <p class="decryptor-expl">{{ currentTarget.formulaExplanation }}</p>
          </div>
        </div>
      </main>

      <!-- Right Column: Integrity Scorecard & Mission Specs -->
      <aside class="tactical-sidebar-right">
        <div class="scope-panel-header">
          <span class="p-title">MISSION INTEGRITY AUDIT</span>
          <span class="p-sub">MACHINE EPSILON EXACT</span>
        </div>

        <!-- Radial Integrity Gauges -->
        <div class="gauges-container">
          <div class="radial-gauge-item">
            <div class="circle-gauge">
              <span class="gauge-val">0.00%</span>
            </div>
            <span class="gauge-lbl">GL Ledger Loss</span>
          </div>
          <div class="radial-gauge-item">
            <div class="circle-gauge text-sky">
              <span class="gauge-val">83/83</span>
            </div>
            <span class="gauge-lbl">Pytest Suites</span>
          </div>
          <div class="radial-gauge-item">
            <div class="circle-gauge text-mint">
              <span class="gauge-val">100%</span>
            </div>
            <span class="gauge-lbl">Offline Airgap</span>
          </div>
        </div>

        <!-- Target Parameters Specs -->
        <div class="target-parameters-box">
          <span class="box-title">DEPLOYED PARAMETERS</span>
          <div class="params-column">
            <div v-for="param in currentTarget.keyParameters" :key="param.name" class="param-row">
              <span class="pk mono">{{ param.name }}</span>
              <strong class="pv text-sky">{{ param.value }}</strong>
            </div>
          </div>
        </div>

        <!-- Python Kernel Lineage -->
        <div class="kernel-lineage-box">
          <span class="box-title">CODE CONTRACT: {{ currentTarget.pythonModule }}</span>
          <pre class="kernel-pre"><code>{{ currentTarget.codeSnippet }}</code></pre>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.tactical-war-room-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #05080f;
  color: #c9d1d9;
  padding: 6.5rem 1.8rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 1. Top Ribbon */
.tactical-ops-ribbon {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #090e1a;
  border: 1px solid #1c2638;
  border-radius: 14px;
  padding: 0.85rem 1.5rem;
}

.classification-tag {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 800;
  color: #38bdf8;
  letter-spacing: 0.08em;
}

.mission-name {
  font-family: var(--font-mono);
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
}

.tactical-telemetry-cluster {
  display: flex;
  align-items: center;
  gap: 1.8rem;
}

.tac-item {
  display: flex;
  flex-direction: column;
}

.tac-k {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: #64748b;
}

.tac-v {
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.text-red { color: #f87171; }
.text-sky { color: #38bdf8; }
.text-green { color: #4ade80; }

.tactical-blast-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  background: #1e293b;
  border: 1px solid #ef4444;
  color: #f87171;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tactical-blast-btn:hover {
  background: #ef4444;
  color: #ffffff;
}

.tactical-blast-btn.active {
  background: #ef4444;
  color: #ffffff;
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.6);
}

.radar-ping {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
}

/* 2. Grid Layout */
.tactical-grid-layout {
  display: grid;
  grid-template-columns: 280px 1fr 340px;
  gap: 1rem;
  height: calc(100vh - 12rem);
}

.tactical-sidebar-left,
.tactical-sidebar-right {
  background: #090e1a;
  border: 1px solid #1c2638;
  border-radius: 14px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  overflow-y: auto;
}

.scope-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #1c2638;
  padding-bottom: 0.5rem;
}

.p-title {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 800;
  color: #94a3b8;
}

.p-sub {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: #38bdf8;
}

.target-nodes-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.target-lock-btn {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  background: #0d1527;
  border: 1px solid #1e293b;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
}

.target-lock-btn:hover {
  background: #172036;
}

.target-lock-btn.locked {
  background: rgba(56, 189, 248, 0.15);
  border-color: #38bdf8;
}

.target-crosshair {
  width: 14px;
  height: 14px;
  border: 1px solid #64748b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.target-lock-btn.locked .target-crosshair {
  border-color: #38bdf8;
  background: #38bdf8;
}

.target-meta {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.meta-row {
  display: flex;
  justify-content: space-between;
}

.t-code {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  color: #38bdf8;
}

.t-sla {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: #4ade80;
}

.t-name {
  font-size: 0.76rem;
  color: #e2e8f0;
}

/* Center Column */
.tactical-center-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.globe-tactical-casing {
  position: relative;
  flex: 1.3;
  background: #070b14;
  border: 1px solid #1c2638;
  border-radius: 14px;
  overflow: hidden;
}

.globe-three-canvas {
  width: 100%;
  height: 100%;
}

.globe-hud-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hud-marker {
  position: absolute;
  font-family: var(--font-mono);
  font-size: 1rem;
  color: #38bdf8;
  opacity: 0.6;
}
.marker-tl { top: 10px; left: 10px; }
.marker-tr { top: 10px; right: 10px; }
.marker-bl { bottom: 10px; left: 10px; }
.marker-br { bottom: 10px; right: 10px; }

.hud-center-crosshair {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.8rem;
  color: #38bdf8;
  opacity: 0.35;
}

.tactical-target-hud {
  position: absolute;
  bottom: 1.2rem;
  left: 1.5rem;
  right: 1.5rem;
  background: rgba(9, 14, 26, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid #1c2638;
  border-radius: 10px;
  padding: 0.85rem 1.2rem;
}

.hud-target-kicker {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 800;
  color: #38bdf8;
}

.hud-target-name {
  font-family: var(--font-mono);
  font-size: 1.05rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.2rem 0;
}

.hud-target-summary {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

.formula-decryptor-card {
  flex: 0.9;
  background: #090e1a;
  border: 1px solid #1c2638;
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.terminal-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background: #0d1527;
  border-bottom: 1px solid #1c2638;
}

.term-kicker {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 800;
  color: #38bdf8;
}

.decrypt-status {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: #4ade80;
}

.decryptor-math-body {
  padding: 1rem 1.4rem;
  overflow-y: auto;
}

.decryptor-expl {
  font-size: 0.78rem;
  color: #94a3b8;
  margin-top: 0.5rem;
}

/* Right Column */
.gauges-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.radial-gauge-item {
  background: #0d1527;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 0.65rem 0.4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.circle-gauge {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 800;
  color: #4ade80;
}

.gauge-lbl {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: #64748b;
  text-align: center;
}

.target-parameters-box,
.kernel-lineage-box {
  background: #0d1527;
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.box-title {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 800;
  color: #94a3b8;
}

.params-column {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.param-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
}

.mono { font-family: var(--font-mono); }

.kernel-pre {
  margin: 0;
  padding: 0.65rem;
  background: #05080f;
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #93c5fd;
  max-height: 140px;
  overflow-y: auto;
}

@media (max-width: 1100px) {
  .tactical-grid-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
}
</style>
