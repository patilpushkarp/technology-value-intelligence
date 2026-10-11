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

const canvasRef = ref<HTMLDivElement | null>(null)
const activeFloorIndex = ref<number>(0) // 0 to 5 (Phases 1 to 6)
const explodeFactor = ref<number>(0.35) // 0 (assembled) to 1 (expanded)
const sunAngle = ref<number>(45) // Directional light angle in degrees
const selectedStepId = ref<number>(1)
const copiedCode = ref<boolean>(false)

const currentStep = computed<TechSpecStep>(() => {
  return steps.find(s => s.id === selectedStepId.value) || steps[0]
})

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let pavilionGroup: THREE.Group
let dirLight: THREE.DirectionalLight
let floorPlates: { id: number; group: THREE.Group; mesh: THREE.Mesh; baseY: number; colorHex: number }[] = []
let stepNodes: { id: number; mesh: THREE.Mesh; parentFloor: number }[] = []

// Floor levels palette (Sophisticated Vedanam Pastels)
const floorPalette = [
  0xa7f3d0, // Phase 1: Mint (Data Foundation & Copulas)
  0x7dd3fc, // Phase 2: Sky (DuckDB Columnar OLAP)
  0xc4b5fd, // Phase 3: Lavender (Activity Cost Lattice)
  0xfed7aa, // Phase 4: Peach (TIME Rationalization)
  0xfecdd3, // Phase 5: Rose (Value Realization & Variance)
  0xddd6fe  // Phase 6: Soft Purple (AI Governance & SLM)
]

const selectFloor = (floorIdx: number) => {
  activeFloorIndex.value = floorIdx
  const phaseNum = floorIdx + 1
  const firstStep = steps.find(s => s.phaseNumber === phaseNum)
  if (firstStep) {
    selectedStepId.value = firstStep.id
  }
  playInteractChime(1.1 + floorIdx * 0.1)

  // Camera smooth elevate to floor height
  if (camera) {
    const targetY = (floorIdx - 2.5) * (1.2 + explodeFactor.value * 2.2) + 4.5
    gsap.to(camera.position, {
      y: targetY,
      duration: 1.2,
      ease: 'power3.out'
    })
  }
}

const updateExplosion = (val: number) => {
  explodeFactor.value = val
  const baseSpacing = 0.85
  const explodeSpacing = 2.4

  floorPlates.forEach(fp => {
    const targetY = (fp.id - 2.5) * (baseSpacing + val * explodeSpacing)
    gsap.to(fp.group.position, {
      y: targetY,
      duration: 0.6,
      ease: 'power2.out'
    })
  })
}

const updateSunAngle = (deg: number) => {
  sunAngle.value = deg
  if (dirLight) {
    const rad = (deg * Math.PI) / 180
    dirLight.position.x = Math.cos(rad) * 16
    dirLight.position.z = Math.sin(rad) * 16
  }
}

const copySnippet = async () => {
  if (process.client && navigator.clipboard) {
    await navigator.clipboard.writeText(currentStep.value.codeSnippet)
    copiedCode.value = true
    playInteractChime(1.5)
    setTimeout(() => { copiedCode.value = false }, 1800)
  }
}

onMounted(() => {
  if (!process.client || !canvasRef.value) return

  const container = canvasRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  // Studio Scene on Pure White / Light Canvas
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xfafafc)

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100)
  camera.position.set(13, 8.5, 13)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.05
  container.appendChild(renderer.domElement)

  // Architectural Studio Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.4)
  scene.add(ambientLight)

  dirLight = new THREE.DirectionalLight(0xffffff, 2.0)
  dirLight.position.set(12, 18, 12)
  dirLight.castShadow = true
  dirLight.shadow.mapSize.width = 2048
  dirLight.shadow.mapSize.height = 2048
  dirLight.shadow.camera.near = 0.5
  dirLight.shadow.camera.far = 40
  dirLight.shadow.camera.left = -12
  dirLight.shadow.camera.right = 12
  dirLight.shadow.camera.top = 12
  dirLight.shadow.camera.bottom = -12
  dirLight.shadow.bias = -0.0005
  scene.add(dirLight)

  // Soft sky bounce light
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0xe2e8f0, 0.8)
  scene.add(hemiLight)

  // Clean Studio Ground Pedestal
  const pedestalGeom = new THREE.CylinderGeometry(9.5, 10, 0.35, 64)
  const pedestalMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.3,
    metalness: 0.05
  })
  const pedestal = new THREE.Mesh(pedestalGeom, pedestalMat)
  pedestal.position.y = -6.2
  pedestal.receiveShadow = true
  scene.add(pedestal)

  // Pavilion Structure Group
  pavilionGroup = new THREE.Group()
  scene.add(pavilionGroup)

  // Build the 6 Architectural Frosted Glass Floors
  const floorWidth = 7.5
  const floorDepth = 5.5
  const floorThickness = 0.2

  phases.forEach((p, idx) => {
    const fGroup = new THREE.Group()
    const colorHex = floorPalette[idx] || 0xa7f3d0

    // Frosted architectural glass plate
    const plateGeom = new THREE.BoxGeometry(floorWidth, floorThickness, floorDepth)
    const plateMat = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      emissive: colorHex,
      emissiveIntensity: 0.18,
      roughness: 0.15,
      metalness: 0.05,
      transmission: 0.82,
      thickness: 1.2,
      transparent: true,
      opacity: 0.95
    })
    const plateMesh = new THREE.Mesh(plateGeom, plateMat)
    plateMesh.castShadow = true
    plateMesh.receiveShadow = true
    fGroup.add(plateMesh)

    // Architectural Edge Perimeter Trim (Optical Dark Grey)
    const trimGeom = new THREE.BoxGeometry(floorWidth + 0.08, 0.04, floorDepth + 0.08)
    const trimMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.4
    })
    const trimMesh = new THREE.Mesh(trimGeom, trimMat)
    plateMesh.add(trimMesh)

    // Architectural Columns & Structural Elements on this floor
    const colCount = 4
    const colPositions = [
      { x: -floorWidth / 2 + 0.5, z: -floorDepth / 2 + 0.5 },
      { x: floorWidth / 2 - 0.5, z: -floorDepth / 2 + 0.5 },
      { x: -floorWidth / 2 + 0.5, z: floorDepth / 2 - 0.5 },
      { x: floorWidth / 2 - 0.5, z: floorDepth / 2 - 0.5 }
    ]

    colPositions.forEach(cPos => {
      const colGeom = new THREE.CylinderGeometry(0.12, 0.12, 1.2, 16)
      const colMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.2
      })
      const colMesh = new THREE.Mesh(colGeom, colMat)
      colMesh.position.set(cPos.x, -0.6, cPos.z)
      colMesh.castShadow = true
      colMesh.receiveShadow = true
      fGroup.add(colMesh)
    })

    // Step Pods situated as sleek architectural pavilions on the floor
    const stepsInThisPhase = steps.filter(s => s.phaseNumber === p.number)
    stepsInThisPhase.forEach((st, sIdx) => {
      const podW = 1.4
      const podD = 1.2
      const podH = 0.45
      const podGeom = new THREE.BoxGeometry(podW, podH, podD)
      const podMat = new THREE.MeshStandardMaterial({
        color: colorHex,
        roughness: 0.2,
        metalness: 0.1
      })
      const podMesh = new THREE.Mesh(podGeom, podMat)
      const offsetX = (sIdx - (stepsInThisPhase.length - 1) / 2) * 2.2
      podMesh.position.set(offsetX, floorThickness / 2 + podH / 2, 0)
      podMesh.castShadow = true
      podMesh.receiveShadow = true
      podMesh.userData = { stepId: st.id, floorIdx: idx }
      fGroup.add(podMesh)
      stepNodes.push({ id: st.id, mesh: podMesh, parentFloor: idx })
    })

    pavilionGroup.add(fGroup)
    floorPlates.push({
      id: idx,
      group: fGroup,
      mesh: plateMesh,
      baseY: 0,
      colorHex
    })
  })

  updateExplosion(explodeFactor.value)

  // Animation Loop
  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const t = clock.getElapsedTime()

    // Gentle architectural turntable slow rotation
    if (pavilionGroup) {
      pavilionGroup.rotation.y = t * 0.05
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
  <div class="architectural-city-view">
    <!-- 3D Three.js Studio Canvas -->
    <div ref="canvasRef" class="canvas-viewport" />

    <!-- Overlaid Architectural Studio UI -->
    <div class="studio-ui-layer">
      <!-- 1. Top Architectural Masthead -->
      <header class="studio-masthead">
        <div class="masthead-brand">
          <span class="studio-tag">ARCHITECTURAL DIGITAL TWIN // MOCK 01</span>
          <h2 class="studio-title">The Enterprise Value Pavilion</h2>
          <p class="studio-sub">
            The 6-phase Technology Value pipeline rendered as an architectural studio model. Explore each structural level from Silicon OLAP foundations to Executive Realization.
          </p>
        </div>

        <div class="studio-vitals-strip">
          <div class="s-vital">
            <span class="v-label">Host Footprint</span>
            <strong class="v-val">16 GB Laptop</strong>
          </div>
          <div class="s-vital">
            <span class="v-label">Accounting Drift</span>
            <strong class="v-val text-mint">0.00% Zero-Loss</strong>
          </div>
          <div class="s-vital">
            <span class="v-label">Analytical SLA</span>
            <strong class="v-val text-sky">&lt; 4.2 ms</strong>
          </div>
        </div>
      </header>

      <!-- 2. Left Side Architectural Controls -->
      <aside class="studio-left-dock">
        <!-- Floor Level Elevator -->
        <div class="studio-card">
          <span class="dock-hed">Architectural Levels</span>
          <div class="elevator-buttons">
            <button
              v-for="(p, idx) in phases"
              :key="p.number"
              type="button"
              class="floor-btn"
              :class="{ active: activeFloorIndex === idx }"
              @click="selectFloor(idx)"
              @mouseenter="setCursor(`LEVEL 0${p.number}`, 'highlight')"
              @mouseleave="resetCursor"
            >
              <div class="f-num">0{{ p.number }}</div>
              <div class="f-info">
                <strong class="f-title">{{ p.name }}</strong>
                <span class="f-desc">{{ p.shortName }}</span>
              </div>
            </button>
          </div>
        </div>

        <!-- 3D Spacing & Sunlight Controls -->
        <div class="studio-card">
          <div class="slider-row">
            <span class="dock-hed">Floor Separation</span>
            <strong class="s-val">{{ Math.round(explodeFactor * 100) }}%</strong>
          </div>
          <input
            v-model.number="explodeFactor"
            type="range"
            min="0"
            max="1"
            step="0.01"
            class="clean-slider"
            @input="updateExplosion(explodeFactor)"
          />

          <div class="slider-row mt-3">
            <span class="dock-hed">Sunlight Angle</span>
            <strong class="s-val">{{ sunAngle }}°</strong>
          </div>
          <input
            v-model.number="sunAngle"
            type="range"
            min="0"
            max="360"
            step="5"
            class="clean-slider"
            @input="updateSunAngle(sunAngle)"
          />
        </div>
      </aside>

      <!-- 3. Right Side Architectural Specification Sheet -->
      <aside class="studio-right-plaque">
        <div class="plaque-header">
          <div class="badge-cluster">
            <span class="step-chip">{{ currentStep.code }}</span>
            <span class="pastel-badge" :class="`badge-${currentStep.badgeColor}`">{{ currentStep.category }}</span>
          </div>
          <span class="sla-text">{{ currentStep.latencySla }} SLA</span>
        </div>

        <h3 class="plaque-title">{{ currentStep.title }}</h3>
        <p class="plaque-summary">{{ currentStep.summary }}</p>

        <!-- Execution Steps Checklist -->
        <div class="plaque-section">
          <span class="section-micro">Execution Mechanics</span>
          <ul class="mechanics-list">
            <li v-for="(item, i) in currentStep.executionDetails" :key="i" class="mech-item">
              <span class="mech-bullet">{{ i + 1 }}</span>
              <span class="mech-desc">{{ item }}</span>
            </li>
          </ul>
        </div>

        <!-- KaTeX Math Formulation Block -->
        <div class="plaque-section">
          <MathFormula
            :latex="currentStep.formulaLatex"
            :formula-html="currentStep.formulaHtml"
            :name="currentStep.formulaName"
          />
          <p class="formula-caption">{{ currentStep.formulaExplanation }}</p>
        </div>

        <!-- Code & Lineage Box -->
        <div class="code-plaque-box">
          <div class="code-box-top">
            <span class="mono-lineage">{{ currentStep.pythonModule }}</span>
            <button type="button" class="copy-btn" @click="copySnippet">
              {{ copiedCode ? 'Copied ✓' : 'Copy Code' }}
            </button>
          </div>
          <pre class="plaque-code"><code>{{ currentStep.codeSnippet }}</code></pre>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.architectural-city-view {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #fafafc;
  color: #121316;
  overflow: hidden;
}

.canvas-viewport {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* Studio UI Overlay */
.studio-ui-layer {
  position: relative;
  z-index: 10;
  pointer-events: none;
  min-height: 100vh;
  padding: 6.5rem 3rem 2.5rem;
}

.studio-ui-layer * {
  pointer-events: auto;
}

/* 1. Masthead */
.studio-masthead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  max-width: 1100px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 24px;
  padding: 1.25rem 2rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
}

.studio-tag {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #0284c7;
  text-transform: uppercase;
}

.studio-title {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 800;
  color: #121316;
  margin: 0.2rem 0 0.4rem;
}

.studio-sub {
  font-size: 0.92rem;
  color: #555968;
  max-width: 650px;
  line-height: 1.5;
  margin: 0;
}

.studio-vitals-strip {
  display: flex;
  align-items: center;
  gap: 1.4rem;
}

.s-vital {
  display: flex;
  flex-direction: column;
}

.v-label {
  font-size: 0.68rem;
  color: #8c909e;
  text-transform: uppercase;
  font-weight: 600;
}

.v-val {
  font-size: 0.92rem;
  font-weight: 700;
  color: #121316;
}

.text-mint { color: #059669; }
.text-sky { color: #0284c7; }

/* 2. Left Controls */
.studio-left-dock {
  position: absolute;
  top: 15rem;
  left: 3rem;
  width: 290px;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.studio-card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  padding: 1.2rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
}

.dock-hed {
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8c909e;
  display: block;
  margin-bottom: 0.6rem;
}

.elevator-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.floor-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.55rem 0.75rem;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.floor-btn:hover {
  background: rgba(0, 0, 0, 0.03);
}

.floor-btn.active {
  background: #121316;
  color: #ffffff;
}

.f-num {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 800;
  color: #0284c7;
}

.floor-btn.active .f-num {
  color: #a7f3d0;
}

.f-info {
  display: flex;
  flex-direction: column;
}

.f-title {
  font-size: 0.8rem;
  font-weight: 700;
}

.f-desc {
  font-size: 0.68rem;
  color: #7b808e;
}

.floor-btn.active .f-desc {
  color: #9ba1b2;
}

.slider-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.s-val {
  font-size: 0.82rem;
  color: #0284c7;
}

.mt-3 {
  margin-top: 0.8rem;
}

.clean-slider {
  width: 100%;
  accent-color: #121316;
  cursor: pointer;
}

/* 3. Right Specification Plaque */
.studio-right-plaque {
  position: absolute;
  top: 15rem;
  right: 3rem;
  width: 480px;
  max-height: calc(100vh - 19rem);
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(28px);
  border: 1px solid rgba(0, 0, 0, 0.09);
  border-radius: 24px;
  padding: 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.06);
}

.plaque-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.badge-cluster {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.step-chip {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  font-weight: 800;
  background: #121316;
  color: #ffffff;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.pastel-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.badge-mint { background: #d1fae5; color: #065f46; }
.badge-sky { background: #e0f2fe; color: #0369a1; }
.badge-lavender { background: #ede9fe; color: #5b21b6; }
.badge-peach { background: #ffedd5; color: #c2410c; }
.badge-rose { background: #ffe4e6; color: #be123c; }

.sla-text {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #059669;
  font-weight: 700;
}

.plaque-title {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  color: #121316;
  margin: 0;
  line-height: 1.25;
}

.plaque-summary {
  font-size: 0.88rem;
  line-height: 1.5;
  color: #4b4f5d;
}

.plaque-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-micro {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8c909e;
}

.mechanics-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.mech-item {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.82rem;
  line-height: 1.45;
  color: #33363f;
}

.mech-bullet {
  font-size: 0.68rem;
  font-weight: 800;
  color: #0284c7;
  background: #e0f2fe;
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
  color: #6b7280;
  line-height: 1.4;
  margin-top: 0.35rem;
}

.code-plaque-box {
  background: #f1f3f7;
  border: 1px solid #e2e5eb;
  border-radius: 14px;
  overflow: hidden;
}

.code-box-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0.85rem;
  background: #e5e8f0;
  border-bottom: 1px solid #dcdfe6;
}

.mono-lineage {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #4b4f5d;
}

.copy-btn {
  font-size: 0.7rem;
  font-weight: 700;
  color: #0284c7;
  background: transparent;
  border: none;
  cursor: pointer;
}

.plaque-code {
  margin: 0;
  padding: 0.85rem;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: #121316;
  line-height: 1.45;
  max-height: 140px;
  overflow-y: auto;
}

@media (max-width: 1100px) {
  .studio-left-dock {
    display: none;
  }
  .studio-right-plaque {
    width: 380px;
  }
}
</style>
