<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useTechSpecs, type TechSpecStep } from '~/composables/useTechSpecs'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import MathFormula from '~/components/MathFormula.vue'

const { steps } = useTechSpecs()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const canvasRef = ref<HTMLDivElement | null>(null)
const capitalVolume = ref<number>(120) // in Millions USD
const flowVelocity = ref<number>(1.0)
const isAuditingConservation = ref<boolean>(false)
const selectedTaxonomyIndex = ref<number>(2) // 0: Pools, 1: Towers, 2: Apps, 3: Caps, 4: Value
const copiedCode = ref<boolean>(false)

// 5 TBM Taxonomic Stages
const taxonomyStages = [
  { id: 0, name: 'GL Cost Pools', spend: '$120.4M', stepId: 2, desc: 'General ledger invoice inputs & expense classification.' },
  { id: 1, name: 'IT Towers', spend: '$120.4M', stepId: 4, desc: 'Hardware, storage, compute, cloud vCPUs, and labor.' },
  { id: 2, name: 'Enterprise Apps', spend: '$120.4M', stepId: 5, desc: '48 monitored applications with fully burdened TCO.' },
  { id: 3, name: 'Business Capabilities', spend: '$120.4M', stepId: 5, desc: 'Bipartite capability attribution with double-counting prevention.' },
  { id: 4, name: 'TVR Realized Value', spend: '$148.2M', stepId: 9, desc: 'Longitudinal benefit realization and KPI movements.' }
]

const activeStage = computed(() => taxonomyStages[selectedTaxonomyIndex.value])
const currentStep = computed<TechSpecStep>(() => {
  return steps.find(s => s.id === activeStage.value.stepId) || steps[0]
})

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let ribbonCurves: THREE.CatmullRomCurve3[] = []
let pulseBeads: { mesh: THREE.Mesh; curveIndex: number; t: number; speed: number }[] = []
let discMeshes: THREE.Mesh[] = []
let auditLaser: THREE.Mesh | null = null

const selectStage = (index: number) => {
  selectedTaxonomyIndex.value = index
  playInteractChime(1.1 + index * 0.12)

  // Move camera to frame stage
  if (camera) {
    const targetX = (index - 2) * 3.5
    gsap.to(camera.position, {
      x: targetX,
      duration: 1.0,
      ease: 'power3.out'
    })
  }
}

const runConservationAudit = () => {
  if (isAuditingConservation.value) return
  isAuditingConservation.value = true
  playInteractChime(0.9)

  if (auditLaser) {
    auditLaser.position.x = -8
    auditLaser.visible = true
    gsap.to(auditLaser.position, {
      x: 8,
      duration: 1.8,
      ease: 'power2.inOut',
      onComplete: () => {
        isAuditingConservation.value = false
        if (auditLaser) auditLaser.visible = false
        playInteractChime(1.8)
      }
    })
  }
}

const copyCode = async () => {
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

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xffffff)

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100)
  camera.position.set(0, 4.5, 14.5)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.05
  container.appendChild(renderer.domElement)

  // Studio Lighting
  const ambient = new THREE.AmbientLight(0xffffff, 1.3)
  scene.add(ambient)

  const dirLight = new THREE.DirectionalLight(0xffffff, 1.8)
  dirLight.position.set(8, 14, 10)
  dirLight.castShadow = true
  scene.add(dirLight)

  const bounceLight = new THREE.DirectionalLight(0x7dd3fc, 0.6)
  bounceLight.position.set(-10, -5, 5)
  scene.add(bounceLight)

  // Stage Discs & Kinetic Ribbon Conduits
  const stageSpacing = 3.6
  const stageY = [0, 0.4, -0.2, 0.5, 0.1]
  const pastelColors = [0x7dd3fc, 0xa7f3d0, 0xc4b5fd, 0xfed7aa, 0xa7f3d0]

  taxonomyStages.forEach((st, idx) => {
    const x = (idx - 2) * stageSpacing
    const y = stageY[idx]

    // Frosted glass disc
    const discGeom = new THREE.CylinderGeometry(1.2, 1.2, 0.22, 32)
    const discMat = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      emissive: pastelColors[idx],
      emissiveIntensity: 0.25,
      roughness: 0.15,
      metalness: 0.05,
      transmission: 0.85,
      transparent: true,
      opacity: 0.95
    })
    const discMesh = new THREE.Mesh(discGeom, discMat)
    discMesh.position.set(x, y, 0)
    discMesh.rotation.x = Math.PI / 6
    discMesh.castShadow = true
    discMesh.receiveShadow = true
    scene.add(discMesh)
    discMeshes.push(discMesh)

    // Sleek architectural border ring
    const ringGeom = new THREE.RingGeometry(1.22, 1.26, 32)
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x121316, side: THREE.DoubleSide })
    const ringMesh = new THREE.Mesh(ringGeom, ringMat)
    ringMesh.rotation.x = -Math.PI / 2
    ringMesh.position.y = 0.12
    discMesh.add(ringMesh)
  })

  // Build Kinetic 3D Spline Ribbons between stages
  for (let s = 0; s < taxonomyStages.length - 1; s++) {
    const startX = (s - 2) * stageSpacing
    const endX = (s - 1) * stageSpacing
    const startY = stageY[s]
    const endY = stageY[s + 1]

    for (let r = 0; r < 3; r++) {
      const midY = (startY + endY) / 2 + (r - 1) * 0.6
      const midZ = (r - 1) * 0.8

      const curve = new THREE.CatmullRomCurve3([
        new THREE.Vector3(startX, startY, 0),
        new THREE.Vector3((startX + endX) / 2, midY, midZ),
        new THREE.Vector3(endX, endY, 0)
      ])
      ribbonCurves.push(curve)

      // Ribbon tube mesh
      const tubeGeom = new THREE.TubeGeometry(curve, 32, 0.05, 8, false)
      const tubeMat = new THREE.MeshStandardMaterial({
        color: pastelColors[s],
        roughness: 0.3,
        transparent: true,
        opacity: 0.65
      })
      const tubeMesh = new THREE.Mesh(tubeGeom, tubeMat)
      scene.add(tubeMesh)

      // Add animated pulse beads
      for (let p = 0; p < 2; p++) {
        const beadGeom = new THREE.SphereGeometry(0.12, 16, 16)
        const beadMat = new THREE.MeshBasicMaterial({ color: 0x059669 })
        const beadMesh = new THREE.Mesh(beadGeom, beadMat)
        scene.add(beadMesh)
        pulseBeads.push({
          mesh: beadMesh,
          curveIndex: ribbonCurves.length - 1,
          t: p * 0.5,
          speed: 0.006 + Math.random() * 0.004
        })
      }
    }
  }

  // Conservation Audit Laser Plane
  const laserGeom = new THREE.PlaneGeometry(0.1, 8)
  const laserMat = new THREE.MeshBasicMaterial({
    color: 0x10b981,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.75
  })
  auditLaser = new THREE.Mesh(laserGeom, laserMat)
  auditLaser.position.set(-8, 0, 0)
  auditLaser.visible = false
  scene.add(auditLaser)

  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const delta = clock.getDelta()
    const speedFactor = flowVelocity.value

    // Animate travelling pulse beads along 3D ribbons
    pulseBeads.forEach(pb => {
      pb.t += pb.speed * speedFactor
      if (pb.t > 1) pb.t = 0
      const curve = ribbonCurves[pb.curveIndex]
      if (curve) {
        const pt = curve.getPointAt(pb.t)
        pb.mesh.position.copy(pt)
      }
    })

    // Gentle floating disc oscillation
    discMeshes.forEach((dm, i) => {
      dm.rotation.z += 0.005
    })

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
  <div class="flow-ribbon-view">
    <!-- 3D Three.js Studio Canvas -->
    <div ref="canvasRef" class="canvas-viewport" />

    <!-- Overlaid Studio UI Layer -->
    <div class="flow-ui-layer">
      <!-- 1. Top Masthead -->
      <header class="flow-masthead">
        <div class="masthead-left">
          <span class="flow-tag">FINANCIAL TOPOLOGY // MOCK 02</span>
          <h2 class="flow-title">Kinetic Capital & Cost Attribution Flow</h2>
          <p class="flow-desc">
            Tracing $1 of General Ledger spend through IT Towers and Applications into Business Capabilities and Value Realization. Zero double-counting guaranteed.
          </p>
        </div>

        <div class="audit-btn-wrap">
          <button
            type="button"
            class="audit-laser-btn"
            :class="{ active: isAuditingConservation }"
            @click="runConservationAudit"
          >
            <span class="laser-dot" />
            <span>{{ isAuditingConservation ? 'Auditing Mass Balance...' : 'Audit 0.00% Conservation' }}</span>
          </button>
        </div>
      </header>

      <!-- 2. Bottom Taxonomy Timeline Navigator -->
      <div class="taxonomy-stage-dock">
        <div class="dock-title-strip">
          <span class="d-label">5-LAYER ACTIVITY-BASED COSTING PIPELINE</span>
          <span class="d-status">MACHINE-PRECISION CONSERVATION CONFIRMED</span>
        </div>

        <div class="stages-pills-row">
          <button
            v-for="(stage, idx) in taxonomyStages"
            :key="stage.id"
            type="button"
            class="stage-pill-btn"
            :class="{ active: selectedTaxonomyIndex === idx }"
            @click="selectStage(idx)"
            @mouseenter="setCursor(stage.name, 'highlight')"
            @mouseleave="resetCursor"
          >
            <span class="s-step">STAGE 0{{ idx + 1 }}</span>
            <strong class="s-name">{{ stage.name }}</strong>
            <span class="s-spend">{{ stage.spend }}</span>
          </button>
        </div>
      </div>

      <!-- 3. Left Simulation Sandbox Controls -->
      <aside class="flow-left-controls">
        <div class="ctrl-card">
          <div class="ctrl-row">
            <span class="ctrl-lbl">Capital Volume Injector</span>
            <strong class="ctrl-val">${{ capitalVolume }}M</strong>
          </div>
          <input
            v-model.number="capitalVolume"
            type="range"
            min="40"
            max="250"
            step="5"
            class="clean-slider"
          />
          <span class="ctrl-sub">Dynamically resizes transactional pulse conduits</span>
        </div>

        <div class="ctrl-card">
          <div class="ctrl-row">
            <span class="ctrl-lbl">Flow Velocity</span>
            <strong class="ctrl-val">{{ flowVelocity.toFixed(1) }}x</strong>
          </div>
          <input
            v-model.number="flowVelocity"
            type="range"
            min="0.2"
            max="3.0"
            step="0.1"
            class="clean-slider"
          />
          <span class="ctrl-sub">Controls kinematic bead travel speed</span>
        </div>
      </aside>

      <!-- 4. Right Forensic Attribution Plaque -->
      <aside class="flow-right-plaque">
        <div class="plaque-top">
          <span class="badge-black">STAGE 0{{ selectedTaxonomyIndex + 1 }}</span>
          <span class="active-spend-badge">{{ activeStage.spend }} Ledger</span>
        </div>

        <h3 class="stage-hed">{{ activeStage.name }}</h3>
        <p class="stage-sub">{{ activeStage.desc }}</p>

        <!-- Mathematical Proof of Conservation -->
        <div class="flow-proof-box">
          <span class="proof-title">Proportional Capability Attribution</span>
          <MathFormula
            :latex="currentStep.formulaLatex"
            :formula-html="currentStep.formulaHtml"
          />
          <p class="proof-expl">{{ currentStep.formulaExplanation }}</p>
        </div>

        <!-- Lineage & Code -->
        <div class="flow-code-card">
          <div class="code-head">
            <span class="c-mod">{{ currentStep.pythonModule }}</span>
            <button type="button" class="copy-pill" @click="copyCode">
              {{ copiedCode ? 'Copied ✓' : 'Copy' }}
            </button>
          </div>
          <pre class="flow-pre"><code>{{ currentStep.codeSnippet }}</code></pre>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.flow-ribbon-view {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
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

.flow-ui-layer {
  position: relative;
  z-index: 10;
  pointer-events: none;
  min-height: 100vh;
  padding: 6.5rem 3rem 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.flow-ui-layer * {
  pointer-events: auto;
}

/* 1. Masthead */
.flow-masthead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  max-width: 1100px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 24px;
  padding: 1.25rem 2rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
}

.flow-tag {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #059669;
  text-transform: uppercase;
}

.flow-title {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 800;
  color: #121316;
  margin: 0.2rem 0 0.4rem;
}

.flow-desc {
  font-size: 0.92rem;
  color: #555968;
  max-width: 650px;
  line-height: 1.5;
  margin: 0;
}

.audit-laser-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.3rem;
  border-radius: var(--radius-pill);
  background: #121316;
  color: #ffffff;
  font-size: 0.84rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.audit-laser-btn:hover {
  background: #252834;
  transform: translateY(-1px);
}

.audit-laser-btn.active {
  background: #059669;
}

.laser-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
}

/* 2. Bottom Taxonomy Dock */
.taxonomy-stage-dock {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  padding: 1rem 1.5rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.05);
  margin-top: auto;
}

.dock-title-strip {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.6rem;
}

.d-label {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #8c909e;
}

.d-status {
  font-size: 0.7rem;
  font-weight: 700;
  color: #059669;
}

.stages-pills-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.6rem;
}

.stage-pill-btn {
  display: flex;
  flex-direction: column;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  background: #f8f9fc;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
}

.stage-pill-btn:hover {
  background: #f0f2f6;
}

.stage-pill-btn.active {
  background: #121316;
  color: #ffffff;
}

.s-step {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  color: #0284c7;
}

.stage-pill-btn.active .s-step {
  color: #a7f3d0;
}

.s-name {
  font-size: 0.82rem;
  font-weight: 700;
}

.s-spend {
  font-size: 0.72rem;
  color: #6b7280;
}

.stage-pill-btn.active .s-spend {
  color: #cbd5e1;
}

/* 3. Left Controls */
.flow-left-controls {
  position: absolute;
  top: 15rem;
  left: 3rem;
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ctrl-card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 18px;
  padding: 1.1rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
}

.ctrl-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.ctrl-lbl {
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #8c909e;
}

.ctrl-val {
  font-size: 0.84rem;
  color: #059669;
}

.clean-slider {
  width: 100%;
  accent-color: #121316;
  cursor: pointer;
}

.ctrl-sub {
  display: block;
  font-size: 0.68rem;
  color: #7b808e;
  margin-top: 0.4rem;
}

/* 4. Right Plaque */
.flow-right-plaque {
  position: absolute;
  top: 15rem;
  right: 3rem;
  width: 460px;
  max-height: calc(100vh - 22rem);
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(28px);
  border: 1px solid rgba(0, 0, 0, 0.09);
  border-radius: 24px;
  padding: 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.06);
}

.plaque-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.badge-black {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 800;
  background: #121316;
  color: #ffffff;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.active-spend-badge {
  font-size: 0.74rem;
  font-weight: 700;
  color: #059669;
}

.stage-hed {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  margin: 0;
}

.stage-sub {
  font-size: 0.86rem;
  color: #4b4f5d;
  line-height: 1.5;
  margin: 0;
}

.proof-title {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #8c909e;
  display: block;
  margin-bottom: 0.4rem;
}

.proof-expl {
  font-size: 0.76rem;
  color: #6b7280;
  line-height: 1.4;
  margin-top: 0.35rem;
}

.flow-code-card {
  background: #f1f3f7;
  border: 1px solid #e2e5eb;
  border-radius: 12px;
  overflow: hidden;
}

.code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.75rem;
  background: #e5e8f0;
}

.c-mod {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: #4b4f5d;
}

.copy-pill {
  font-size: 0.68rem;
  font-weight: 700;
  color: #059669;
  background: transparent;
  border: none;
  cursor: pointer;
}

.flow-pre {
  margin: 0;
  padding: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: #121316;
  max-height: 120px;
  overflow-y: auto;
}

@media (max-width: 1100px) {
  .flow-left-controls {
    display: none;
  }
  .flow-right-plaque {
    width: 380px;
  }
}
</style>
