<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useTechSpecs, type TechSpecStep } from '~/composables/useTechSpecs'
import { useTVIData } from '~/composables/useTVIData'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import MathFormula from '~/components/MathFormula.vue'

const { steps } = useTechSpecs()
const { applications, selectedApp, selectApp } = useTVIData()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const canvasRef = ref<HTMLDivElement | null>(null)
const layoutMode = ref<'constellation' | 'hierarchy' | 'time'>('constellation')
const isSimulatingBlast = ref<boolean>(false)
const blastCount = ref<number>(0)
const selectedNodeId = ref<string>('APP010') // Default to central Auth Hub

const activeStep = computed<TechSpecStep>(() => {
  return steps.find(s => s.id === 3) || steps[2] // Step 03: Graph Topology
})

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let graphGroup: THREE.Group
let edgeLinesGroup: THREE.Group
let nodeMeshes: {
  id: string
  mesh: THREE.Mesh
  halo: THREE.Mesh
  constellationPos: THREE.Vector3
  hierarchyPos: THREE.Vector3
  timePos: THREE.Vector3
  blastAffected: boolean
}[] = []

const setLayout = (mode: 'constellation' | 'hierarchy' | 'time') => {
  layoutMode.value = mode
  playInteractChime(mode === 'constellation' ? 1.1 : mode === 'hierarchy' ? 1.3 : 1.5)

  nodeMeshes.forEach(nm => {
    let targetPos = nm.constellationPos
    if (mode === 'hierarchy') targetPos = nm.hierarchyPos
    else if (mode === 'time') targetPos = nm.timePos

    gsap.to(nm.mesh.position, {
      x: targetPos.x,
      y: targetPos.y,
      z: targetPos.z,
      duration: 1.2,
      ease: 'power3.out'
    })
  })
}

const simulateBlastRadius = () => {
  if (isSimulatingBlast.value) return
  isSimulatingBlast.value = true
  blastCount.value = 0
  playInteractChime(0.8)

  // Stagger ripple across affected downstream nodes
  nodeMeshes.forEach((nm, idx) => {
    if (nm.blastAffected) {
      setTimeout(() => {
        blastCount.value++
        playInteractChime(1.1 + idx * 0.08)

        gsap.fromTo(
          nm.halo.scale,
          { x: 1, y: 1, z: 1 },
          { x: 2.5, y: 2.5, z: 2.5, duration: 0.8, ease: 'power2.out' }
        )
        const mat = nm.halo.material as THREE.MeshBasicMaterial
        mat.opacity = 0.9
        gsap.to(mat, { opacity: 0.2, duration: 0.8 })
      }, idx * 120)
    }
  })

  setTimeout(() => {
    isSimulatingBlast.value = false
    playInteractChime(1.7)
  }, 1600)
}

onMounted(() => {
  if (!process.client || !canvasRef.value) return

  const container = canvasRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf8f9fb)

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100)
  camera.position.set(0, 5, 15)
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
  const ambient = new THREE.AmbientLight(0xffffff, 1.4)
  scene.add(ambient)

  const dirLight = new THREE.DirectionalLight(0xffffff, 1.8)
  dirLight.position.set(10, 16, 12)
  dirLight.castShadow = true
  scene.add(dirLight)

  graphGroup = new THREE.Group()
  scene.add(graphGroup)

  edgeLinesGroup = new THREE.Group()
  graphGroup.add(edgeLinesGroup)

  // Architectural Pedestal Plinth
  const plinthGeom = new THREE.CylinderGeometry(8.5, 9, 0.3, 64)
  const plinthMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.25
  })
  const plinth = new THREE.Mesh(plinthGeom, plinthMat)
  plinth.position.y = -5.5
  plinth.receiveShadow = true
  scene.add(plinth)

  // Populate 3D Knowledge Graph Nodes based on enterprise apps
  const appList = applications.slice(0, 24)
  const pastelColors = [0x7dd3fc, 0xa7f3d0, 0xc4b5fd, 0xfed7aa, 0xfecdd3]

  appList.forEach((app, idx) => {
    // 1. Constellation spherical positions
    const phi = Math.acos(-1 + (2 * idx) / appList.length)
    const theta = Math.sqrt(appList.length * Math.PI) * phi
    const r = 4.2
    const cPos = new THREE.Vector3(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.cos(phi),
      r * Math.sin(phi) * Math.sin(theta)
    )

    // 2. Hierarchical layered tree positions
    const tierOffset = app.tier.includes('Mission') ? 2.5 : app.tier.includes('Business') ? 0 : -2.5
    const hPos = new THREE.Vector3(
      ((idx % 6) - 2.5) * 1.6,
      tierOffset,
      (Math.floor(idx / 6) - 1.5) * 1.5
    )

    // 3. 2x2 TIME Matrix quadrant positions
    const qX = (idx % 2 === 0 ? 1 : -1) * (1.8 + (idx % 3) * 0.8)
    const qY = (idx % 4 < 2 ? 1 : -1) * (1.8 + (idx % 2) * 0.8)
    const tPos = new THREE.Vector3(qX, qY, 0)

    // Frosted glass node sphere
    const isHub = app.id === 'APP010'
    const nodeGeom = new THREE.SphereGeometry(isHub ? 0.45 : 0.28, 24, 24)
    const nodeMat = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      emissive: isHub ? 0xf87171 : pastelColors[idx % pastelColors.length],
      emissiveIntensity: 0.35,
      roughness: 0.15,
      transmission: 0.82,
      transparent: true,
      opacity: 0.95
    })
    const nodeMesh = new THREE.Mesh(nodeGeom, nodeMat)
    nodeMesh.position.copy(cPos)
    nodeMesh.castShadow = true
    graphGroup.add(nodeMesh)

    // Halo pulse ring
    const haloGeom = new THREE.RingGeometry(0.35, 0.4, 32)
    const haloMat = new THREE.MeshBasicMaterial({
      color: isHub ? 0xef4444 : 0x0284c7,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.25
    })
    const haloMesh = new THREE.Mesh(haloGeom, haloMat)
    haloMesh.rotation.x = Math.PI / 2
    nodeMesh.add(haloMesh)

    nodeMeshes.push({
      id: app.id,
      mesh: nodeMesh,
      halo: haloMesh,
      constellationPos: cPos,
      hierarchyPos: hPos,
      timePos: tPos,
      blastAffected: isHub || idx < 10
    })
  })

  // Subtle connection lines
  for (let i = 0; i < nodeMeshes.length; i++) {
    for (let j = i + 1; j < Math.min(i + 3, nodeMeshes.length); j++) {
      const lineGeom = new THREE.BufferGeometry().setFromPoints([
        nodeMeshes[i].constellationPos,
        nodeMeshes[j].constellationPos
      ])
      const lineMat = new THREE.LineBasicMaterial({
        color: 0x94a3b8,
        transparent: true,
        opacity: 0.35
      })
      const lineMesh = new THREE.Line(lineGeom, lineMat)
      edgeLinesGroup.add(lineMesh)
    }
  }

  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const t = clock.getElapsedTime()

    // Gentle graph pedestal drift
    if (graphGroup) {
      graphGroup.rotation.y = t * 0.04
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
  <div class="kg-gallery-view">
    <!-- 3D Studio Canvas -->
    <div ref="canvasRef" class="canvas-viewport" />

    <!-- Overlaid Studio UI Layer -->
    <div class="gallery-ui-layer">
      <!-- 1. Top Masthead -->
      <header class="gallery-masthead">
        <div class="masthead-left">
          <span class="gallery-tag">SEMANTIC GRAPH INTELLIGENCE // MOCK 03</span>
          <h2 class="gallery-title">Living Knowledge Graph & Blast Radius Gallery</h2>
          <p class="gallery-desc">
            102 enterprise nodes and 196 typed relationships. Experience topological betweenness centrality, transitive blast radius reachability, and 3D TIME matrix rationalization.
          </p>
        </div>

        <div class="blast-action-wrap">
          <button
            type="button"
            class="simulate-blast-btn"
            :class="{ active: isSimulatingBlast }"
            @click="simulateBlastRadius"
          >
            <span class="pulse-spark" />
            <span>{{ isSimulatingBlast ? `Rippling Outage: ${blastCount} Nodes` : 'Simulate APP010 Outage' }}</span>
          </button>
        </div>
      </header>

      <!-- 2. Left 3D Layout Morphing Dock -->
      <aside class="gallery-left-dock">
        <div class="layout-toggle-card">
          <span class="dock-label">3D Topological Layout</span>
          <div class="layout-options-stack">
            <button
              type="button"
              class="layout-pill-btn"
              :class="{ active: layoutMode === 'constellation' }"
              @click="setLayout('constellation')"
              @mouseenter="setCursor('3D CONSTELLATION', 'highlight')"
              @mouseleave="resetCursor"
            >
              <span class="l-name">3D Constellation</span>
              <span class="l-desc">Natural force-directed cluster</span>
            </button>

            <button
              type="button"
              class="layout-pill-btn"
              :class="{ active: layoutMode === 'hierarchy' }"
              @click="setLayout('hierarchy')"
              @mouseenter="setCursor('HIERARCHICAL TIERS', 'highlight')"
              @mouseleave="resetCursor"
            >
              <span class="l-name">Hierarchical Tiers</span>
              <span class="l-desc">Mission -> Core -> Edge</span>
            </button>

            <button
              type="button"
              class="layout-pill-btn"
              :class="{ active: layoutMode === 'time' }"
              @click="setLayout('time')"
              @mouseenter="setCursor('2X2 TIME MATRIX', 'highlight')"
              @mouseleave="resetCursor"
            >
              <span class="l-name">2x2 TIME Rationalization</span>
              <span class="l-desc">Spatial Gartner quadrants</span>
            </button>
          </div>
        </div>

        <!-- Node Vitals Plaque -->
        <div class="node-vitals-card">
          <span class="dock-label">Selected Anchor Node</span>
          <strong class="node-hed">APP010 Central Auth Hub</strong>
          <div class="vitals-matrix">
            <div class="v-cell">
              <span class="v-k">Blast Radius</span>
              <strong class="v-v text-red">10 Inbound Apps</strong>
            </div>
            <div class="v-cell">
              <span class="v-k">Centrality</span>
              <strong class="v-v text-sky">0.248 Brandes</strong>
            </div>
          </div>
        </div>
      </aside>

      <!-- 3. Right Forensic Graph Engineering Plaque -->
      <aside class="gallery-right-plaque">
        <div class="plaque-top">
          <span class="badge-black">TOPOLOGY STEP 03 & 08</span>
          <span class="centrality-chip">&lt; 8.5 ms BFS Traversal</span>
        </div>

        <h3 class="plaque-hed">Brandes Centrality & Transitive Reachability</h3>
        <p class="plaque-sub">
          Computing directional betweenness centrality and transitive closure reachability to detect single points of failure before production incidents.
        </p>

        <!-- Brandes Centrality Mathematical Formulation -->
        <div class="graph-formula-box">
          <span class="box-title">Betweenness Centrality & Blast Radius</span>
          <MathFormula
            :latex="activeStep.formulaLatex"
            :formula-html="activeStep.formulaHtml"
          />
          <p class="box-caption">{{ activeStep.formulaExplanation }}</p>
        </div>

        <!-- Python NetworkX Lineage -->
        <div class="graph-code-card">
          <div class="code-head">
            <span class="mod-path">src/tvi/dependency.py</span>
            <span class="tag-nx">NetworkX MultiDiGraph</span>
          </div>
          <pre class="graph-pre"><code>{{ activeStep.codeSnippet }}</code></pre>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.kg-gallery-view {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #f8f9fb;
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

.gallery-ui-layer {
  position: relative;
  z-index: 10;
  pointer-events: none;
  min-height: 100vh;
  padding: 6.5rem 3rem 2.5rem;
}

.gallery-ui-layer * {
  pointer-events: auto;
}

/* 1. Masthead */
.gallery-masthead {
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

.gallery-tag {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #7c3aed;
  text-transform: uppercase;
}

.gallery-title {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 800;
  color: #121316;
  margin: 0.2rem 0 0.4rem;
}

.gallery-desc {
  font-size: 0.92rem;
  color: #555968;
  max-width: 650px;
  line-height: 1.5;
  margin: 0;
}

.simulate-blast-btn {
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

.simulate-blast-btn:hover {
  background: #be123c;
  transform: translateY(-1px);
}

.simulate-blast-btn.active {
  background: #e11d48;
}

.pulse-spark {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f43f5e;
}

/* 2. Left Dock */
.gallery-left-dock {
  position: absolute;
  top: 15rem;
  left: 3rem;
  width: 290px;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.layout-toggle-card,
.node-vitals-card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  padding: 1.2rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
}

.dock-label {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #8c909e;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.6rem;
}

.layout-options-stack {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.layout-pill-btn {
  display: flex;
  flex-direction: column;
  padding: 0.55rem 0.75rem;
  border-radius: 12px;
  background: #f8f9fc;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.layout-pill-btn:hover {
  background: #f0f2f6;
}

.layout-pill-btn.active {
  background: #121316;
  color: #ffffff;
}

.l-name {
  font-size: 0.8rem;
  font-weight: 700;
}

.l-desc {
  font-size: 0.68rem;
  color: #7b808e;
}

.layout-pill-btn.active .l-desc {
  color: #9ba1b2;
}

.node-hed {
  font-size: 0.92rem;
  font-weight: 800;
  margin-bottom: 0.6rem;
  display: block;
}

.vitals-matrix {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.v-cell {
  background: #f8f9fc;
  border-radius: 10px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
}

.v-k {
  font-size: 0.64rem;
  color: #8c909e;
}

.v-v {
  font-size: 0.82rem;
}

.text-red { color: #e11d48; }
.text-sky { color: #0284c7; }

/* 3. Right Plaque */
.gallery-right-plaque {
  position: absolute;
  top: 15rem;
  right: 3rem;
  width: 460px;
  max-height: calc(100vh - 19rem);
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

.centrality-chip {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #7c3aed;
  font-weight: 700;
}

.plaque-hed {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  margin: 0;
  line-height: 1.25;
}

.plaque-sub {
  font-size: 0.86rem;
  color: #4b4f5d;
  line-height: 1.5;
  margin: 0;
}

.graph-formula-box {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.box-title {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #8c909e;
}

.box-caption {
  font-size: 0.76rem;
  color: #6b7280;
  line-height: 1.4;
  margin-top: 0.35rem;
}

.graph-code-card {
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

.mod-path {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: #4b4f5d;
}

.tag-nx {
  font-size: 0.68rem;
  font-weight: 700;
  color: #7c3aed;
}

.graph-pre {
  margin: 0;
  padding: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: #121316;
  max-height: 130px;
  overflow-y: auto;
}

@media (max-width: 1100px) {
  .gallery-left-dock {
    display: none;
  }
  .gallery-right-plaque {
    width: 380px;
  }
}
</style>
