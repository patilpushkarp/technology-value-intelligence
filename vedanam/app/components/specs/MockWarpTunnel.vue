<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useTechSpecs, type TechSpecStep } from '~/composables/useTechSpecs'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import MathFormula from '~/components/MathFormula.vue'

const { steps, phases } = useTechSpecs()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const canvasHostRef = ref<HTMLDivElement | null>(null)
const splineProgress = ref<number>(0.04) // 0 to 1 along tunnel
const warpSpeed = ref<number>(1.0)
const isAutoCruising = ref<boolean>(false)
const selectedStepIndex = ref<number>(0)
const cockpitMode = ref<'pilot' | 'drone'>('pilot')

const currentStep = computed<TechSpecStep>(() => steps[selectedStepIndex.value] || steps[0])

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let tunnelCurve: THREE.CatmullRomCurve3
let gateObjects: { index: number; group: THREE.Group; progress: number }[] = []
let speedStreaks: THREE.Points | null = null
let ringMeshes: THREE.Mesh[] = []

// Target smooth progress with inertia
let targetProgress = 0.04
let velocity = 0

const hyperjumpToStep = (index: number) => {
  selectedStepIndex.value = index
  const targetP = (index + 0.5) / steps.length
  playInteractChime(1.4 + index * 0.05)

  // Cinematic warp camera swoop
  gsap.to(camera, {
    fov: 95,
    duration: 0.4,
    ease: 'power2.in',
    onUpdate: () => camera.updateProjectionMatrix(),
    onComplete: () => {
      gsap.to(camera, {
        fov: cockpitMode.value === 'pilot' ? 65 : 75,
        duration: 0.6,
        ease: 'power3.out',
        onUpdate: () => camera.updateProjectionMatrix()
      })
    }
  })

  gsap.to(splineProgress, {
    value: targetP,
    duration: 1.4,
    ease: 'power3.inOut',
    onUpdate: () => {
      targetProgress = splineProgress.value
    }
  })
}

const toggleAutoCruise = () => {
  isAutoCruising.value = !isAutoCruising.value
  playInteractChime(isAutoCruising.value ? 1.5 : 1.1)
}

const onWheel = (e: WheelEvent) => {
  e.preventDefault()
  const delta = e.deltaY * 0.00035
  targetProgress = Math.max(0.01, Math.min(0.99, targetProgress + delta))
}

onMounted(() => {
  if (!process.client || !canvasHostRef.value) return

  const container = canvasHostRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  // Scene setup
  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x06080d, 0.018)

  camera = new THREE.PerspectiveCamera(65, width / height, 0.1, 300)
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.4
  container.appendChild(renderer.domElement)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.0)
  scene.add(ambientLight)

  // 1. Build 3D Tunnel Spline Track
  const splinePoints: THREE.Vector3[] = []
  const numControlPoints = 20
  for (let i = 0; i < numControlPoints; i++) {
    const angle = (i / numControlPoints) * Math.PI * 4
    const x = Math.sin(angle) * 18
    const y = Math.cos(angle * 0.7) * 8
    const z = -i * 18
    splinePoints.push(new THREE.Vector3(x, y, z))
  }
  tunnelCurve = new THREE.CatmullRomCurve3(splinePoints)

  // 2. Neon Octagonal Tunnel Rings along the Spline
  const numRings = 75
  for (let i = 0; i < numRings; i++) {
    const t = i / numRings
    const pt = tunnelCurve.getPointAt(t)
    const tangent = tunnelCurve.getTangentAt(t)

    const ringGeom = new THREE.RingGeometry(4.5, 4.65, 8)
    const ringMat = new THREE.MeshBasicMaterial({
      color: i % 4 === 0 ? 0x38bdf8 : 0x8b5cf6,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.4
    })
    const ringMesh = new THREE.Mesh(ringGeom, ringMat)
    ringMesh.position.copy(pt)
    ringMesh.lookAt(pt.clone().add(tangent))
    scene.add(ringMesh)
    ringMeshes.push(ringMesh)
  }

  // 3. Position the 12 Cyber-Monolith Gates along the Spline
  steps.forEach((st, idx) => {
    const t = (idx + 0.5) / steps.length
    const pt = tunnelCurve.getPointAt(t)
    const tangent = tunnelCurve.getTangentAt(t)

    const gateGroup = new THREE.Group()
    gateGroup.position.copy(pt)
    gateGroup.lookAt(pt.clone().add(tangent))

    // Main glowing octagonal gate frame
    const gateFrameGeom = new THREE.TorusGeometry(5.2, 0.12, 8, 8)
    const gateFrameMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: idx % 2 === 0 ? 0x10b981 : 0x8b5cf6,
      emissiveIntensity: 1.2,
      roughness: 0.2,
      metalness: 0.8
    })
    const gateFrameMesh = new THREE.Mesh(gateFrameGeom, gateFrameMat)
    gateGroup.add(gateFrameMesh)

    // Secondary inner rotating ring
    const innerRingGeom = new THREE.TorusGeometry(4.0, 0.05, 16, 32)
    const innerRingMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.7
    })
    const innerRingMesh = new THREE.Mesh(innerRingGeom, innerRingMat)
    gateGroup.add(innerRingMesh)

    // Side Cyber Pylons
    const pylonGeom = new THREE.BoxGeometry(0.4, 6.5, 0.4)
    const pylonMat = new THREE.MeshStandardMaterial({
      color: 0x1b1f2e,
      emissive: 0x38bdf8,
      emissiveIntensity: 0.5
    })
    const leftPylon = new THREE.Mesh(pylonGeom, pylonMat)
    leftPylon.position.set(-5.6, 0, 0)
    gateGroup.add(leftPylon)

    const rightPylon = new THREE.Mesh(pylonGeom, pylonMat)
    rightPylon.position.set(5.6, 0, 0)
    gateGroup.add(rightPylon)

    scene.add(gateGroup)
    gateObjects.push({
      index: idx,
      group: gateGroup,
      progress: t
    })
  })

  // 4. Relativistic Speed Streaks Particles
  const streakCount = 600
  const streakPositions = new Float32Array(streakCount * 3)
  for (let i = 0; i < streakCount * 3; i += 3) {
    streakPositions[i] = (Math.random() - 0.5) * 40
    streakPositions[i + 1] = (Math.random() - 0.5) * 40
    streakPositions[i + 2] = -Math.random() * 320
  }
  const streaksGeom = new THREE.BufferGeometry()
  streaksGeom.setAttribute('position', new THREE.BufferAttribute(streakPositions, 3))
  const streaksMat = new THREE.PointsMaterial({
    color: 0x7dd3fc,
    size: 0.08,
    transparent: true,
    opacity: 0.65
  })
  speedStreaks = new THREE.Points(streaksGeom, streaksMat)
  scene.add(speedStreaks)

  // Attach wheel listener to canvas container
  container.addEventListener('wheel', onWheel, { passive: false })

  // Animation Loop
  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const delta = clock.getDelta()

    // Auto cruise progression
    if (isAutoCruising.value) {
      targetProgress += delta * 0.02 * warpSpeed.value
      if (targetProgress > 0.98) targetProgress = 0.02
    }

    // Smooth inertia interpolation
    splineProgress.value += (targetProgress - splineProgress.value) * 0.08

    // Calculate active step based on progress
    const computedStepIdx = Math.min(
      steps.length - 1,
      Math.max(0, Math.floor(splineProgress.value * steps.length))
    )
    if (computedStepIdx !== selectedStepIndex.value) {
      selectedStepIndex.value = computedStepIdx
      playInteractChime(1.1 + (computedStepIdx % 4) * 0.1)
    }

    // Camera track flight along spline
    const currentPoint = tunnelCurve.getPointAt(splineProgress.value)
    const lookAheadT = Math.min(0.999, splineProgress.value + 0.025)
    const lookAheadPoint = tunnelCurve.getPointAt(lookAheadT)
    const tangent = tunnelCurve.getTangentAt(splineProgress.value)

    if (cockpitMode.value === 'pilot') {
      camera.position.copy(currentPoint)
      camera.lookAt(lookAheadPoint)
    } else {
      // Third-person drone chase mode
      const offset = new THREE.Vector3(0, 2.2, 5.0)
      offset.applyAxisAngle(new THREE.Vector3(0, 1, 0), tangent.x)
      camera.position.copy(currentPoint).add(offset)
      camera.lookAt(lookAheadPoint)
    }

    // Rotate gate inner rings
    gateObjects.forEach(go => {
      if (go.group.children[1]) {
        go.group.children[1].rotation.z += 0.015
      }
    })

    renderer.render(scene, camera)
  }

  animate()

  // Handle Resize
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
  <div class="mock-warp-root">
    <!-- 3D Canvas Host -->
    <div ref="canvasHostRef" class="canvas-viewport" />

    <!-- Overlaid Hyperspace Flight HUD Interface -->
    <div class="warp-hud-layer">
      <!-- 1. Top Flight Control Horizon -->
      <div class="warp-top-bar">
        <div class="flight-title-cluster">
          <span class="flight-kicker">MOCK 03 // SCROLLYTELLING HYPERSPACE RUNWAY</span>
          <h2 class="flight-main-title">The Hyperspace Warp Runway</h2>
        </div>

        <div class="flight-status-pills">
          <div class="flight-badge">
            <span class="dot dot-mint" />
            <span>Velocity: <strong>{{ (warpSpeed * 100).toFixed(0) }} km/s</strong></span>
          </div>
          <div class="flight-badge">
            <span class="dot dot-sky" />
            <span>Docked Gate: <strong>{{ currentStep.code }}</strong></span>
          </div>
          <div class="flight-badge">
            <span class="dot dot-lavender" />
            <span>Latency SLA: <strong>{{ currentStep.latencySla }}</strong></span>
          </div>
        </div>

        <!-- Cockpit Controls -->
        <div class="cockpit-btn-cluster">
          <button
            type="button"
            class="flight-action-pill"
            :class="{ active: isAutoCruising }"
            @click="toggleAutoCruise"
          >
            <span>{{ isAutoCruising ? 'Pause Cruise' : 'Auto-Cruise Flight' }}</span>
          </button>

          <button
            type="button"
            class="flight-action-pill"
            :class="{ active: cockpitMode === 'drone' }"
            @click="cockpitMode = cockpitMode === 'pilot' ? 'drone' : 'pilot'"
          >
            <span>{{ cockpitMode === 'pilot' ? 'Cockpit View' : 'Orbital Drone' }}</span>
          </button>
        </div>
      </div>

      <!-- 2. Left Warp Drive Throttle -->
      <aside class="warp-left-throttle">
        <div class="throttle-card">
          <div class="throttle-hed">
            <span class="t-label">Warp Drive Throttle</span>
            <strong class="t-val">{{ warpSpeed.toFixed(1) }}x</strong>
          </div>
          <input
            v-model.number="warpSpeed"
            type="range"
            min="0.5"
            max="3.0"
            step="0.1"
            class="warp-throttle-slider"
          />
          <span class="t-sub">Controls cruise velocity and particle warp flare</span>
        </div>

        <!-- Hyperjump Waypoint Nav -->
        <div class="waypoints-card">
          <span class="wp-title">Gate Coordinates</span>
          <div class="waypoints-list">
            <button
              v-for="(st, idx) in steps"
              :key="st.id"
              type="button"
              class="wp-btn"
              :class="{ active: selectedStepIndex === idx }"
              @click="hyperjumpToStep(idx)"
              @mouseenter="setCursor(`WARP TO ${st.code}`, 'highlight')"
              @mouseleave="resetCursor"
            >
              <span class="wp-num">0{{ idx + 1 }}</span>
              <span class="wp-code">{{ st.code }}</span>
              <span class="wp-sla">{{ st.latencySla }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- 3. Right Floating Holographic Gate HUD -->
      <aside class="flight-hud-modal">
        <div class="hud-modal-top">
          <div class="gate-marker-chips">
            <span class="gate-tag">GATE 0{{ selectedStepIndex + 1 }}</span>
            <span class="step-chip-code">{{ currentStep.code }}</span>
            <span class="cat-chip" :class="`chip-${currentStep.badgeColor}`">{{ currentStep.category }}</span>
          </div>
          <NuxtLink :to="currentStep.subpageUrl" class="spec-manual-btn">
            Detailed Guide ↗
          </NuxtLink>
        </div>

        <h3 class="docked-step-title">{{ currentStep.title }}</h3>
        <p class="docked-summary">{{ currentStep.summary }}</p>

        <!-- Mechanics Checklist -->
        <div class="flight-mechanics-box">
          <span class="box-micro-hed">Pipeline Execution Sequence</span>
          <ul class="mechanics-ul">
            <li v-for="(item, i) in currentStep.executionDetails" :key="i" class="mech-li">
              <span class="step-index-dot">{{ i + 1 }}</span>
              <span class="step-body">{{ item }}</span>
            </li>
          </ul>
        </div>

        <!-- Mathematical Proof -->
        <div class="flight-formula-box">
          <MathFormula
            :latex="currentStep.formulaLatex"
            :formula-html="currentStep.formulaHtml"
            :name="currentStep.formulaName"
          />
          <p class="formula-notes">{{ currentStep.formulaExplanation }}</p>
        </div>

        <!-- Flight Specs Matrix -->
        <div class="flight-telemetry-row">
          <div class="telemetry-box">
            <span class="tel-k">Execution SLA</span>
            <span class="tel-v text-sky">{{ currentStep.latencySla }}</span>
          </div>
          <div class="telemetry-box">
            <span class="tel-k">Memory Budget</span>
            <span class="tel-v text-mint">{{ currentStep.memoryBudget }}</span>
          </div>
          <div class="telemetry-box">
            <span class="tel-k">Accounting Drift</span>
            <span class="tel-v text-lavender">0.00% Zero-Loss</span>
          </div>
        </div>

        <!-- Code Terminal -->
        <div class="cockpit-terminal-card">
          <div class="term-header-strip">
            <span class="term-kernel-tag">Python Kernel Execution</span>
            <span class="term-module-path">{{ currentStep.pythonModule }}</span>
          </div>
          <pre class="cockpit-pre"><code>{{ currentStep.codeSnippet }}</code></pre>
        </div>
      </aside>

      <!-- 4. Bottom Kinetic Spline Progress Bar -->
      <div class="warp-bottom-progress">
        <div class="progress-meta-row">
          <span class="meta-hed">Continuous Spline Trajectory Progress</span>
          <span class="meta-val">{{ (splineProgress * 100).toFixed(1) }}% · Scroll Wheel to Accelerate</span>
        </div>
        <div class="spline-track-bar">
          <div class="track-fill" :style="{ width: `${splineProgress * 100}%` }" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mock-warp-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #06080d;
  color: #e2e8f0;
  overflow: hidden;
}

.canvas-viewport {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* ---------------- Flight HUD Layer ---------------- */
.warp-hud-layer {
  position: relative;
  z-index: 10;
  pointer-events: none;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 6.5rem 2.5rem 2rem;
}

.warp-hud-layer * {
  pointer-events: auto;
}

/* 1. Top Bar */
.warp-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: rgba(14, 17, 26, 0.85);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 1rem 1.6rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

.flight-kicker {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #38bdf8;
  text-transform: uppercase;
}

.flight-main-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
}

.flight-status-pills {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.flight-badge {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.78rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.dot-mint { background: #10b981; }
.dot-sky { background: #38bdf8; }
.dot-lavender { background: #8b5cf6; }

.cockpit-btn-cluster {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.flight-action-pill {
  padding: 0.45rem 1rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #c9cedc;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.flight-action-pill:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.flight-action-pill.active {
  background: linear-gradient(135deg, #0284c7, #10b981);
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 0 16px rgba(2, 132, 199, 0.4);
}

/* 2. Left Throttle */
.warp-left-throttle {
  position: absolute;
  top: 13rem;
  left: 2.5rem;
  width: 270px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.throttle-card,
.waypoints-card {
  background: rgba(14, 17, 26, 0.88);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 1.15rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
}

.throttle-hed {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.t-label, .wp-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #8c92a4;
  letter-spacing: 0.05em;
}

.t-val {
  color: #38bdf8;
  font-size: 0.84rem;
}

.warp-throttle-slider {
  width: 100%;
  accent-color: #38bdf8;
  cursor: pointer;
}

.t-sub {
  display: block;
  font-size: 0.66rem;
  color: #656b7c;
  margin-top: 0.4rem;
}

.waypoints-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-top: 0.6rem;
  max-height: 250px;
  overflow-y: auto;
}

.wp-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0.65rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: #a8b0c2;
  cursor: pointer;
  transition: all 0.18s ease;
}

.wp-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.wp-btn.active {
  background: rgba(56, 189, 248, 0.2);
  border-color: #38bdf8;
  color: #ffffff;
}

.wp-num {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: #38bdf8;
}

.wp-code {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  font-weight: 700;
}

.wp-sla {
  font-size: 0.66rem;
  color: #10b981;
}

/* 3. Right Docked HUD */
.flight-hud-modal {
  position: absolute;
  top: 13rem;
  right: 2.5rem;
  width: 480px;
  max-height: calc(100vh - 22rem);
  overflow-y: auto;
  background: rgba(14, 17, 26, 0.88);
  backdrop-filter: blur(28px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}

.hud-modal-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.gate-marker-chips {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.gate-tag {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 800;
  background: #38bdf8;
  color: #06080d;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.step-chip-code {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.cat-chip {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.chip-mint { background: rgba(16, 185, 129, 0.2); color: #a7f3d0; }
.chip-lavender { background: rgba(139, 92, 246, 0.2); color: #c4b5fd; }
.chip-sky { background: rgba(2, 132, 199, 0.2); color: #7dd3fc; }
.chip-peach { background: rgba(249, 115, 22, 0.2); color: #fed7aa; }
.chip-rose { background: rgba(244, 63, 94, 0.2); color: #fecdd3; }

.spec-manual-btn {
  font-size: 0.76rem;
  font-weight: 700;
  color: #38bdf8;
  text-decoration: none;
}

.docked-step-title {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.25;
}

.docked-summary {
  font-size: 0.86rem;
  color: #9ba1b2;
  line-height: 1.5;
}

.flight-mechanics-box {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.box-micro-hed {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6d7385;
}

.mechanics-ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.mech-li {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  font-size: 0.8rem;
  color: #d1d5db;
  line-height: 1.45;
}

.step-index-dot {
  font-size: 0.68rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.15);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

.formula-notes {
  font-size: 0.76rem;
  color: #8c92a4;
  line-height: 1.4;
  margin-top: 0.35rem;
}

.flight-telemetry-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.telemetry-box {
  background: rgba(0, 0, 0, 0.28);
  border-radius: 10px;
  padding: 0.55rem 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.tel-k {
  font-size: 0.64rem;
  text-transform: uppercase;
  color: #7b8192;
}

.tel-v {
  font-size: 0.78rem;
  font-weight: 700;
}

.text-sky { color: #7dd3fc; }
.text-mint { color: #a7f3d0; }
.text-lavender { color: #c4b5fd; }

.cockpit-terminal-card {
  background: #090a0f;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.term-header-strip {
  display: flex;
  justify-content: space-between;
  padding: 0.4rem 0.75rem;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.term-kernel-tag {
  font-size: 0.68rem;
  font-weight: 600;
  color: #8c92a4;
}

.term-module-path {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: #38bdf8;
}

.cockpit-pre {
  margin: 0;
  padding: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: #93c5fd;
  line-height: 1.45;
  max-height: 130px;
  overflow-y: auto;
}

/* 4. Bottom Progress Bar */
.warp-bottom-progress {
  margin-top: auto;
  background: rgba(14, 17, 26, 0.85);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 0.9rem 1.6rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

.progress-meta-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.meta-hed {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #8c92a4;
  letter-spacing: 0.05em;
}

.meta-val {
  font-size: 0.74rem;
  font-weight: 600;
  color: #38bdf8;
}

.spline-track-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  overflow: hidden;
}

.track-fill {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8, #10b981);
  border-radius: 999px;
  box-shadow: 0 0 12px #38bdf8;
}

@media (max-width: 1200px) {
  .warp-left-throttle {
    display: none;
  }
  .flight-hud-modal {
    width: 380px;
  }
}

@media (max-width: 900px) {
  .warp-top-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  .flight-hud-modal {
    position: static;
    width: 100%;
    margin-top: 1rem;
    max-height: none;
  }
}
</style>
