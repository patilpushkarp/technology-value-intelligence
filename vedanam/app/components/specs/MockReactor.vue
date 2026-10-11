<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useTechSpecs, type TechSpecStep } from '~/composables/useTechSpecs'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import MathFormula from '~/components/MathFormula.vue'

const { steps, phases, hardwareBenchmarks } = useTechSpecs()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const canvasHostRef = ref<HTMLDivElement | null>(null)
const selectedStepId = ref<number>(1)
const selectedPhaseNumber = ref<number>(0) // 0 = all phases
const coreFrequency = ref<number>(1.0)
const isIgniting = ref<boolean>(false)
const ignitionProgress = ref<number>(0)
const cameraMode = ref<'orbit' | 'step' | 'core'>('orbit')
const copiedCode = ref<boolean>(false)

const currentStep = computed<TechSpecStep>(() => {
  return steps.find(s => s.id === selectedStepId.value) || steps[0]
})

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let coreGroup: THREE.Group
let ringsGroup: THREE.Group
let nodesGroup: THREE.Group
let beamLine: THREE.Line | null = null
let particlesMesh: THREE.Points | null = null
const stepMeshes: { id: number; mesh: THREE.Mesh; halo: THREE.Mesh; ringIndex: number; angle: number; radius: number; speed: number }[] = []
const ringMeshes: THREE.Mesh[] = []

// Raycasting for 3D interaction
const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2(-999, -999)
let hoveredStepId: number | null = null

// Palette mapping
const phaseColors: Record<number, number> = {
  1: 0x10b981, // Mint
  2: 0x8b5cf6, // Lavender
  3: 0xf97316, // Peach
  4: 0x0284c7, // Sky
  5: 0xf43f5e, // Rose
  6: 0xa855f7  // Purple
}

const copySnippet = async () => {
  if (process.client && navigator.clipboard) {
    await navigator.clipboard.writeText(currentStep.value.codeSnippet)
    copiedCode.value = true
    playInteractChime(1.5)
    setTimeout(() => { copiedCode.value = false }, 1800)
  }
}

const selectStep = (id: number, playSound = true) => {
  selectedStepId.value = id
  if (playSound) playInteractChime(1.2 + (id % 6) * 0.08)

  const found = stepMeshes.find(s => s.id === id)
  if (found && camera) {
    // Smooth camera drift towards selected node in 3D
    const targetPos = new THREE.Vector3()
    found.mesh.getWorldPosition(targetPos)

    if (cameraMode.value === 'step') {
      gsap.to(camera.position, {
        x: targetPos.x * 1.3 + 1.2,
        y: targetPos.y * 1.3 + 0.8,
        z: targetPos.z * 1.3 + 3.0,
        duration: 1.2,
        ease: 'power3.out',
        onUpdate: () => {
          camera.lookAt(targetPos)
        }
      })
    }
  }
  updateEnergyBeam()
}

const setPhaseFilter = (phaseNum: number) => {
  selectedPhaseNumber.value = phaseNum
  playInteractChime(phaseNum === 0 ? 1.0 : 1.3)

  ringMeshes.forEach((ring, idx) => {
    const pNum = idx + 1
    const mat = ring.material as THREE.MeshBasicMaterial
    if (phaseNum === 0 || phaseNum === pNum) {
      gsap.to(mat, { opacity: 0.65, duration: 0.5 })
    } else {
      gsap.to(mat, { opacity: 0.1, duration: 0.5 })
    }
  })

  stepMeshes.forEach(sm => {
    const stepObj = steps.find(s => s.id === sm.id)
    const mat = sm.mesh.material as THREE.MeshStandardMaterial
    if (phaseNum === 0 || (stepObj && stepObj.phaseNumber === phaseNum)) {
      gsap.to(sm.mesh.scale, { x: 1, y: 1, z: 1, duration: 0.4 })
      gsap.to(mat, { opacity: 1.0, duration: 0.4 })
    } else {
      gsap.to(sm.mesh.scale, { x: 0.4, y: 0.4, z: 0.4, duration: 0.4 })
      gsap.to(mat, { opacity: 0.2, duration: 0.4 })
    }
  })
}

const triggerIgnition = () => {
  if (isIgniting.value) return
  isIgniting.value = true
  ignitionProgress.value = 0
  playInteractChime(0.9)

  const tl = gsap.timeline({
    onComplete: () => {
      isIgniting.value = false
      playInteractChime(1.8)
    }
  })

  steps.forEach((st, idx) => {
    tl.to({}, {
      duration: 0.35,
      onStart: () => {
        selectStep(st.id, true)
        ignitionProgress.value = Math.round(((idx + 1) / steps.length) * 100)
      }
    })
  })
}

const updateEnergyBeam = () => {
  if (!scene || !coreGroup) return
  const found = stepMeshes.find(s => s.id === selectedStepId.value)
  if (!found) return

  const start = new THREE.Vector3(0, 0, 0)
  const end = new THREE.Vector3()
  found.mesh.getWorldPosition(end)

  if (beamLine) {
    const positions = (beamLine.geometry as THREE.BufferGeometry).attributes.position
    positions.setXYZ(0, start.x, start.y, start.z)
    positions.setXYZ(1, end.x, end.y, end.z)
    positions.needsUpdate = true
  }
}

const onMouseMove = (event: MouseEvent) => {
  if (!canvasHostRef.value) return
  const rect = canvasHostRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
}

const onCanvasClick = () => {
  if (hoveredStepId !== null) {
    selectStep(hoveredStepId)
  }
}

onMounted(() => {
  if (!process.client || !canvasHostRef.value) return

  const container = canvasHostRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  // Scene & Camera
  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x0c0d12, 0.04)

  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100)
  camera.position.set(0, 4.5, 14.5)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  container.appendChild(renderer.domElement)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.9)
  scene.add(ambientLight)

  const dirLight1 = new THREE.DirectionalLight(0x10b981, 1.8)
  dirLight1.position.set(10, 15, 10)
  scene.add(dirLight1)

  const dirLight2 = new THREE.DirectionalLight(0x8b5cf6, 1.6)
  dirLight2.position.set(-10, -10, -5)
  scene.add(dirLight2)

  const pointCoreLight = new THREE.PointLight(0x38bdf8, 3.5, 15)
  pointCoreLight.position.set(0, 0, 0)
  scene.add(pointCoreLight)

  // Core Group (DuckDB OLAP Analytical Singularity)
  coreGroup = new THREE.Group()
  scene.add(coreGroup)

  // Outer wireframe dodecahedron
  const outerCoreGeom = new THREE.IcosahedronGeometry(1.6, 2)
  const outerCoreMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    wireframe: true,
    emissive: 0x0284c7,
    emissiveIntensity: 0.8,
    roughness: 0.2,
    metalness: 0.9
  })
  const outerCoreMesh = new THREE.Mesh(outerCoreGeom, outerCoreMat)
  coreGroup.add(outerCoreMesh)

  // Inner solid glowing core
  const innerCoreGeom = new THREE.DodecahedronGeometry(0.85)
  const innerCoreMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x10b981,
    emissiveIntensity: 1.2,
    roughness: 0.1,
    metalness: 0.5
  })
  const innerCoreMesh = new THREE.Mesh(innerCoreGeom, innerCoreMat)
  coreGroup.add(innerCoreMesh)

  // Rings Group (6 TVI Phases)
  ringsGroup = new THREE.Group()
  scene.add(ringsGroup)

  nodesGroup = new THREE.Group()
  scene.add(nodesGroup)

  const ringRadii = [3.2, 4.4, 5.6, 6.8, 8.0, 9.2]
  const ringTilts = [0.15, -0.22, 0.35, -0.12, 0.28, -0.3]

  ringRadii.forEach((radius, idx) => {
    const pNumber = idx + 1
    const colorHex = phaseColors[pNumber] || 0x10b981

    const ringGeom = new THREE.TorusGeometry(radius, 0.025, 16, 120)
    const ringMat = new THREE.MeshBasicMaterial({
      color: colorHex,
      transparent: true,
      opacity: 0.65
    })
    const ringMesh = new THREE.Mesh(ringGeom, ringMat)
    ringMesh.rotation.x = Math.PI / 2 + ringTilts[idx]
    ringMesh.rotation.y = ringTilts[idx] * 0.8
    ringsGroup.add(ringMesh)
    ringMeshes.push(ringMesh)
  })

  // 12 Step Nodes positioned on the 6 rings
  steps.forEach((st, idx) => {
    const ringIdx = (st.phaseNumber - 1) % ringRadii.length
    const radius = ringRadii[ringIdx]
    const pColor = phaseColors[st.phaseNumber] || 0x10b981

    // Spread steps along their ring
    const stepsInThisPhase = steps.filter(s => s.phaseNumber === st.phaseNumber)
    const subIdx = stepsInThisPhase.findIndex(s => s.id === st.id)
    const angleOffset = (subIdx / Math.max(stepsInThisPhase.length, 1)) * Math.PI + (idx * 0.5)

    const sphereGeom = new THREE.SphereGeometry(0.32, 24, 24)
    const sphereMat = new THREE.MeshStandardMaterial({
      color: pColor,
      emissive: pColor,
      emissiveIntensity: 0.9,
      roughness: 0.2,
      metalness: 0.7,
      transparent: true
    })
    const nodeMesh = new THREE.Mesh(sphereGeom, sphereMat)
    nodeMesh.userData = { stepId: st.id }

    // Pulsing halo ring around node
    const haloGeom = new THREE.TorusGeometry(0.55, 0.02, 16, 32)
    const haloMat = new THREE.MeshBasicMaterial({
      color: pColor,
      transparent: true,
      opacity: 0.5
    })
    const haloMesh = new THREE.Mesh(haloGeom, haloMat)
    nodeMesh.add(haloMesh)

    nodesGroup.add(nodeMesh)
    stepMeshes.push({
      id: st.id,
      mesh: nodeMesh,
      halo: haloMesh,
      ringIndex: ringIdx,
      radius,
      angle: angleOffset,
      speed: 0.003 + (idx % 3) * 0.0015
    })
  })

  // Energy Beam from Core to Active Step
  const beamGeom = new THREE.BufferGeometry()
  const beamPositions = new Float32Array([0, 0, 0, 0, 0, 0])
  beamGeom.setAttribute('position', new THREE.BufferAttribute(beamPositions, 3))
  const beamMat = new THREE.LineBasicMaterial({
    color: 0x38bdf8,
    linewidth: 3,
    transparent: true,
    opacity: 0.85
  })
  beamLine = new THREE.Line(beamGeom, beamMat)
  scene.add(beamLine)

  // Ambient Stardust Nebula Field
  const particleCount = 550
  const particlePositions = new Float32Array(particleCount * 3)
  for (let i = 0; i < particleCount * 3; i += 3) {
    particlePositions[i] = (Math.random() - 0.5) * 35
    particlePositions[i + 1] = (Math.random() - 0.5) * 30
    particlePositions[i + 2] = (Math.random() - 0.5) * 35
  }
  const particlesGeom = new THREE.BufferGeometry()
  particlesGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3))
  const particlesMat = new THREE.PointsMaterial({
    color: 0xc4b5fd,
    size: 0.06,
    transparent: true,
    opacity: 0.45
  })
  particlesMesh = new THREE.Points(particlesGeom, particlesMat)
  scene.add(particlesMesh)

  // Animation Loop
  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const elapsedTime = clock.getElapsedTime()
    const speedMultiplier = coreFrequency.value

    // Rotate core
    if (coreGroup) {
      coreGroup.rotation.y = elapsedTime * 0.4 * speedMultiplier
      coreGroup.rotation.x = Math.sin(elapsedTime * 0.25) * 0.2
      const pulseScale = 1 + Math.sin(elapsedTime * 2.5 * speedMultiplier) * 0.06
      coreGroup.scale.set(pulseScale, pulseScale, pulseScale)
    }

    // Slowly rotate ambient particles
    if (particlesMesh) {
      particlesMesh.rotation.y = elapsedTime * 0.02
    }

    // Update Step Nodes along their orbital rings
    stepMeshes.forEach(sm => {
      sm.angle += sm.speed * speedMultiplier
      const tilt = ringTilts[sm.ringIndex] || 0
      const x = Math.cos(sm.angle) * sm.radius
      const z = Math.sin(sm.angle) * sm.radius
      const y = Math.sin(sm.angle + tilt) * (sm.radius * 0.35)

      sm.mesh.position.set(x, y, z)
      sm.halo.rotation.z += 0.02

      if (sm.id === selectedStepId.value) {
        sm.halo.scale.set(1.4, 1.4, 1.4)
        const haloMat = sm.halo.material as THREE.MeshBasicMaterial
        haloMat.opacity = 0.95
      } else {
        sm.halo.scale.set(1.0, 1.0, 1.0)
        const haloMat = sm.halo.material as THREE.MeshBasicMaterial
        haloMat.opacity = 0.35
      }
    })

    // Update dynamic beam
    updateEnergyBeam()

    // Raycast detection
    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObjects(nodesGroup.children, true)
    if (intersects.length > 0) {
      let hitMesh: THREE.Object3D | null = intersects[0].object
      while (hitMesh && !hitMesh.userData.stepId && hitMesh.parent) {
        hitMesh = hitMesh.parent
      }
      if (hitMesh && hitMesh.userData.stepId) {
        hoveredStepId = hitMesh.userData.stepId
        setCursor(`INSPECT ${currentStep.value.code}`, 'highlight')
      }
    } else {
      hoveredStepId = null
      resetCursor()
    }

    // Camera orbit if orbit mode
    if (cameraMode.value === 'orbit') {
      const radius = 15.5
      camera.position.x = Math.sin(elapsedTime * 0.08) * radius
      camera.position.z = Math.cos(elapsedTime * 0.08) * radius
      camera.lookAt(0, 0, 0)
    }

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
  <div class="mock-reactor-root">
    <!-- 3D Canvas Viewport -->
    <div
      ref="canvasHostRef"
      class="canvas-viewport"
      @mousemove="onMouseMove"
      @click="onCanvasClick"
    />

    <!-- Overlaid Interactive Cyber-HUD Controls -->
    <div class="hud-layer">
      <!-- 1. Top Horizon Telemetry Strip -->
      <div class="hud-top-bar">
        <div class="hud-branding">
          <div class="reactor-pulse-dot" :class="{ 'is-ignited': isIgniting }" />
          <div>
            <span class="hud-kicker">MOCK 01 // QUANTUM ARCHITECTURAL ENGINE</span>
            <h2 class="hud-title">The Spatial Quantum Reactor</h2>
          </div>
        </div>

        <!-- Telemetry Stream Pills -->
        <div class="hud-vitals">
          <div class="vital-tag">
            <span class="v-label">Analytical Core</span>
            <strong class="v-value text-sky">DuckDB OLAP</strong>
          </div>
          <div class="vital-tag">
            <span class="v-label">GL Drift Loss</span>
            <strong class="v-value text-mint">0.0000%</strong>
          </div>
          <div class="vital-tag">
            <span class="v-label">Graph Dimension</span>
            <strong class="v-value text-lavender">102N · 196E</strong>
          </div>
          <div class="vital-tag">
            <span class="v-label">Test Suites</span>
            <strong class="v-value text-mint">83/83 PASS</strong>
          </div>
        </div>

        <!-- Simulation Ignition Trigger -->
        <div class="hud-actions">
          <button
            type="button"
            class="ignite-trigger-btn"
            :class="{ active: isIgniting }"
            @click="triggerIgnition"
            @mouseenter="setCursor('IGNITE PIPELINE', 'highlight')"
            @mouseleave="resetCursor"
          >
            <span class="sparkle-icon">⚡</span>
            <span>{{ isIgniting ? `Synthesizing ${ignitionProgress}%` : 'Ignite Full Pipeline' }}</span>
          </button>
        </div>
      </div>

      <!-- 2. Left Side Phase Matrix Selector -->
      <div class="hud-left-panel">
        <div class="panel-header">
          <span class="panel-label">Phase Matrix</span>
          <span class="panel-badge">{{ selectedPhaseNumber === 0 ? 'All 6 Phases' : `Phase 0${selectedPhaseNumber}` }}</span>
        </div>

        <div class="phase-buttons-stack">
          <button
            type="button"
            class="phase-pill-btn"
            :class="{ 'is-selected': selectedPhaseNumber === 0 }"
            @click="setPhaseFilter(0)"
          >
            <span class="pill-dot dot-all" />
            <span class="pill-name">00 All Phases</span>
          </button>

          <button
            v-for="p in phases"
            :key="p.number"
            type="button"
            class="phase-pill-btn"
            :class="{ 'is-selected': selectedPhaseNumber === p.number }"
            @click="setPhaseFilter(p.number)"
            @mouseenter="setCursor(p.name, 'default')"
            @mouseleave="resetCursor"
          >
            <span class="pill-dot" :class="`dot-${p.badgeColor}`" />
            <span class="pill-name">0{{ p.number }} {{ p.shortName }}</span>
          </button>
        </div>

        <!-- Core Frequency Interactive Dial -->
        <div class="frequency-slider-card">
          <div class="dial-header">
            <span class="dial-label">Reactor Core Frequency</span>
            <strong class="dial-val">{{ coreFrequency.toFixed(1) }}x</strong>
          </div>
          <input
            v-model.number="coreFrequency"
            type="range"
            min="0.2"
            max="3.0"
            step="0.1"
            class="cyber-range-input"
          />
          <div class="dial-sub">Modulates particle turbulence & orbital velocity</div>
        </div>

        <!-- Camera Perspective Selector -->
        <div class="camera-mode-tabs">
          <button
            type="button"
            class="cam-btn"
            :class="{ active: cameraMode === 'orbit' }"
            @click="cameraMode = 'orbit'; playInteractChime(1.1)"
          >
            Orbit
          </button>
          <button
            type="button"
            class="cam-btn"
            :class="{ active: cameraMode === 'step' }"
            @click="cameraMode = 'step'; playInteractChime(1.2)"
          >
            Target Step
          </button>
          <button
            type="button"
            class="cam-btn"
            :class="{ active: cameraMode === 'core' }"
            @click="cameraMode = 'core'; playInteractChime(1.3)"
          >
            Core
          </button>
        </div>
      </div>

      <!-- 3. Right Floating Spatial Cyber-HUD: Active Step Forensic Deep Dive -->
      <aside class="hud-inspector-card">
        <div class="inspector-top-row">
          <div class="step-chip-group">
            <span class="step-code-badge">{{ currentStep.code }}</span>
            <span class="step-category-badge" :class="`badge-${currentStep.badgeColor}`">{{ currentStep.category }}</span>
            <span class="sla-chip">{{ currentStep.latencySla }}</span>
          </div>
          <NuxtLink :to="currentStep.subpageUrl" class="deep-doc-link">
            Guide ↗
          </NuxtLink>
        </div>

        <h3 class="inspector-step-title">{{ currentStep.title }}</h3>
        <p class="inspector-summary">{{ currentStep.summary }}</p>

        <!-- Step Execution Mechanics List -->
        <div class="inspector-mechanics-section">
          <span class="section-micro-hed">Execution Mechanics</span>
          <ul class="mechanics-list">
            <li v-for="(detail, i) in currentStep.executionDetails" :key="i" class="mechanic-row">
              <span class="num-dot">{{ i + 1 }}</span>
              <span class="text-content">{{ detail }}</span>
            </li>
          </ul>
        </div>

        <!-- Integrated KaTeX / Semantic Math Formula -->
        <div class="inspector-formula-section">
          <MathFormula
            :latex="currentStep.formulaLatex"
            :formula-html="currentStep.formulaHtml"
            :name="currentStep.formulaName"
          />
          <p class="formula-caption">{{ currentStep.formulaExplanation }}</p>
        </div>

        <!-- Engineering Contracts -->
        <div class="contracts-grid">
          <div class="contract-card">
            <span class="c-key">Memory Budget</span>
            <span class="c-val text-mint">{{ currentStep.memoryBudget }}</span>
          </div>
          <div class="contract-card">
            <span class="c-key">Module Lineage</span>
            <span class="c-val mono">{{ currentStep.pythonModule }}</span>
          </div>
        </div>

        <!-- Code Terminal Box with Copy Button -->
        <div class="hud-terminal-box">
          <div class="terminal-bar">
            <div class="term-dots">
              <span class="t-red" /><span class="t-yellow" /><span class="t-green" />
            </div>
            <span class="term-label">Deterministic Kernel Lineage</span>
            <button type="button" class="copy-term-btn" @click="copySnippet">
              {{ copiedCode ? 'Copied ✓' : 'Copy Code' }}
            </button>
          </div>
          <pre class="terminal-pre"><code>{{ currentStep.codeSnippet }}</code></pre>
        </div>
      </aside>

      <!-- 4. Bottom 12-Step Orbital Timeline Navigator -->
      <div class="hud-bottom-rail">
        <div class="rail-title-row">
          <span class="rail-label">12-Step Continuous Execution Timeline</span>
          <span class="rail-hint">Click any orbital node to lock 3D focus</span>
        </div>
        <div class="steps-rail-scroll">
          <button
            v-for="st in steps"
            :key="st.id"
            type="button"
            class="rail-step-pill"
            :class="{ 'is-active': selectedStepId === st.id }"
            @click="selectStep(st.id)"
            @mouseenter="setCursor(st.code, 'highlight')"
            @mouseleave="resetCursor"
          >
            <span class="st-num">{{ st.id < 10 ? '0' + st.id : st.id }}</span>
            <span class="st-title">{{ st.shortTitle }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mock-reactor-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #0b0c10;
  color: #e2e8f0;
  overflow: hidden;
}

.canvas-viewport {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  cursor: grab;
}

.canvas-viewport:active {
  cursor: grabbing;
}

/* ---------------- HUD Overlay ---------------- */
.hud-layer {
  position: relative;
  z-index: 10;
  pointer-events: none;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 6.5rem 2.5rem 2rem;
}

.hud-layer * {
  pointer-events: auto;
}

/* 1. Top Bar */
.hud-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: rgba(18, 20, 29, 0.82);
  backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 1rem 1.6rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

.hud-branding {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.reactor-pulse-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 14px #10b981;
  animation: pulse-glow 2s infinite ease-in-out;
}

.reactor-pulse-dot.is-ignited {
  background: #38bdf8;
  box-shadow: 0 0 22px #38bdf8;
  animation: pulse-rapid 0.4s infinite alternate;
}

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.4); opacity: 1; }
}

@keyframes pulse-rapid {
  0% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1.8); opacity: 0.7; }
}

.hud-kicker {
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #38bdf8;
  text-transform: uppercase;
}

.hud-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.02em;
}

.hud-vitals {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.vital-tag {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.v-label {
  font-size: 0.68rem;
  color: #8c92a4;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.v-value {
  font-size: 0.92rem;
  font-weight: 700;
}

.text-mint { color: #a7f3d0; }
.text-lavender { color: #c4b5fd; }
.text-sky { color: #7dd3fc; }

.ignite-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.4rem;
  border-radius: var(--radius-pill);
  background: linear-gradient(135deg, #10b981, #0284c7);
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.35);
  transition: all 0.25s ease;
}

.ignite-trigger-btn:hover {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 8px 28px rgba(16, 185, 129, 0.5);
}

.ignite-trigger-btn.active {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  box-shadow: 0 0 25px rgba(245, 158, 11, 0.6);
}

/* 2. Left Side Panel */
.hud-left-panel {
  position: absolute;
  top: 13rem;
  left: 2.5rem;
  width: 260px;
  background: rgba(18, 20, 29, 0.85);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.45);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.5rem;
}

.panel-label {
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8c92a4;
}

.panel-badge {
  font-size: 0.7rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.08);
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  color: #38bdf8;
}

.phase-buttons-stack {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.phase-pill-btn {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  color: #c5cbd8;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
}

.phase-pill-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.phase-pill-btn.is-selected {
  background: rgba(56, 189, 248, 0.15);
  border-color: rgba(56, 189, 248, 0.4);
  color: #ffffff;
}

.pill-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.dot-all { background: #ffffff; }
.dot-mint { background: #10b981; }
.dot-lavender { background: #8b5cf6; }
.dot-peach { background: #f97316; }
.dot-sky { background: #0284c7; }
.dot-rose { background: #f43f5e; }

.frequency-slider-card {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  padding: 0.75rem;
}

.dial-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #8c92a4;
  margin-bottom: 0.4rem;
}

.dial-val {
  color: #38bdf8;
}

.cyber-range-input {
  width: 100%;
  accent-color: #38bdf8;
  cursor: pointer;
}

.dial-sub {
  font-size: 0.66rem;
  color: #656b7c;
  margin-top: 0.35rem;
}

.camera-mode-tabs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.3rem;
  background: rgba(0, 0, 0, 0.25);
  padding: 0.25rem;
  border-radius: 10px;
}

.cam-btn {
  padding: 0.35rem 0;
  font-size: 0.72rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #8c92a4;
  cursor: pointer;
  transition: all 0.15s ease;
}

.cam-btn.active {
  background: #38bdf8;
  color: #0b0c10;
  font-weight: 700;
}

/* 3. Right Floating Inspector Card */
.hud-inspector-card {
  position: absolute;
  top: 13rem;
  right: 2.5rem;
  width: 460px;
  max-height: calc(100vh - 22rem);
  overflow-y: auto;
  background: rgba(18, 20, 29, 0.88);
  backdrop-filter: blur(28px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}

.inspector-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.step-chip-group {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.step-code-badge {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 800;
  background: #ffffff;
  color: #0b0c10;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.step-category-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.badge-mint { background: rgba(16, 185, 129, 0.2); color: #a7f3d0; border: 1px solid rgba(16, 185, 129, 0.4); }
.badge-lavender { background: rgba(139, 92, 246, 0.2); color: #c4b5fd; border: 1px solid rgba(139, 92, 246, 0.4); }
.badge-sky { background: rgba(2, 132, 199, 0.2); color: #7dd3fc; border: 1px solid rgba(2, 132, 199, 0.4); }
.badge-peach { background: rgba(249, 115, 22, 0.2); color: #fed7aa; border: 1px solid rgba(249, 115, 22, 0.4); }
.badge-rose { background: rgba(244, 63, 94, 0.2); color: #fecdd3; border: 1px solid rgba(244, 63, 94, 0.4); }

.sla-chip {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.deep-doc-link {
  font-size: 0.76rem;
  font-weight: 700;
  color: #38bdf8;
  text-decoration: none;
  transition: transform 0.2s ease;
}

.deep-doc-link:hover {
  transform: translateX(2px);
}

.inspector-step-title {
  font-family: var(--font-display);
  font-size: 1.28rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.25;
}

.inspector-summary {
  font-size: 0.86rem;
  line-height: 1.5;
  color: #9ba1b2;
}

.inspector-mechanics-section {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.section-micro-hed {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #6d7385;
}

.mechanics-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.mechanic-row {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  font-size: 0.8rem;
  line-height: 1.45;
  color: #d1d5db;
}

.num-dot {
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

.formula-caption {
  font-size: 0.76rem;
  color: #8c92a4;
  line-height: 1.4;
  margin-top: 0.4rem;
}

.contracts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.contract-card {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 10px;
  padding: 0.55rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.c-key {
  font-size: 0.66rem;
  color: #7b8192;
  text-transform: uppercase;
}

.c-val {
  font-size: 0.78rem;
  font-weight: 600;
}

.hud-terminal-box {
  background: #08090d;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.terminal-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.75rem;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.term-dots {
  display: flex;
  gap: 0.25rem;
}

.term-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.t-red { background: #ef4444; }
.t-yellow { background: #eab308; }
.t-green { background: #22c55e; }

.term-label {
  font-size: 0.68rem;
  color: #6b7280;
  font-family: var(--font-mono);
}

.copy-term-btn {
  font-size: 0.68rem;
  font-weight: 600;
  color: #38bdf8;
  background: transparent;
  border: none;
  cursor: pointer;
}

.terminal-pre {
  margin: 0;
  padding: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: #93c5fd;
  line-height: 1.45;
  max-height: 140px;
  overflow-y: auto;
}

/* 4. Bottom Rail */
.hud-bottom-rail {
  margin-top: auto;
  background: rgba(18, 20, 29, 0.85);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 0.85rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

.rail-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rail-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #8c92a4;
}

.rail-hint {
  font-size: 0.68rem;
  color: #38bdf8;
}

.steps-rail-scroll {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  overflow-x: auto;
  padding-bottom: 0.2rem;
}

.rail-step-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #a0a6b7;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.rail-step-pill:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.rail-step-pill.is-active {
  background: #38bdf8;
  color: #0b0c10;
  font-weight: 700;
  border-color: #38bdf8;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
}

.st-num {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  opacity: 0.8;
}

/* Responsiveness */
@media (max-width: 1200px) {
  .hud-left-panel {
    display: none;
  }
  .hud-inspector-card {
    width: 380px;
    right: 1.5rem;
  }
}

@media (max-width: 900px) {
  .hud-top-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  .hud-vitals {
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  .hud-inspector-card {
    position: static;
    width: 100%;
    margin-top: 1rem;
    max-height: none;
  }
}
</style>
