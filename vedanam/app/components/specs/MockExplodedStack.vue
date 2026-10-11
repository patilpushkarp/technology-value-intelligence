<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { useTechSpecs, type SystemArchitectureSpec } from '~/composables/useTechSpecs'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'
import MathFormula from '~/components/MathFormula.vue'

const { systemArchitecture, steps, hardwareBenchmarks } = useTechSpecs()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

const canvasHostRef = ref<HTMLDivElement | null>(null)
const selectedTierIndex = ref<number>(0)
const explodeValue = ref<number>(0.65) // 0 to 1
const isXRayMode = ref<boolean>(false)
const isAutoRotating = ref<boolean>(true)
const isRunningDiag = ref<boolean>(false)
const diagStatus = ref<string>('All Systems Nominal')

// Tiers data with specialized 3D annotations
const tiersData = [
  {
    id: 0,
    name: 'Vectorized Silicon Substrate',
    engine: 'DuckDB Columnar OLAP + Parquet',
    role: 'Vectorized relational aggregation, zero-drift general ledger summation, columnar Parquet cache.',
    sla: '< 4.2 ms query avg',
    memory: '< 4.0 GB buffer pool',
    guarantee: '0.00% Mass-Balance Drift',
    colorHex: 0x38bdf8,
    formulaName: 'General Ledger Mass-Balance Conservation',
    formulaLatex: '\\sum_{k \\in \\text{Cost Pools}} C_k \\equiv \\sum_{t \\in \\text{IT Towers}} C_t \\equiv \\sum_{a \\in \\text{Apps}} C_a = C_{\\text{Total}} \\quad (\\Delta = 0.00\\%)',
    formulaDesc: 'Machine-exact integer-cents ledger summation confirming zero balance loss across all taxonomic transformations.',
    codeSnippet: `con = duckdb.connect("database/tvi.duckdb")
# Vectorized OLAP sum with Snappy Parquet zero-copy
df = con.execute("""
    SELECT app_id, SUM(amount_usd) as tco 
    FROM cost_records 
    GROUP BY app_id
""").df()`
  },
  {
    id: 1,
    name: 'Neural Synapse Property Graph',
    engine: 'NetworkX Semantic MultiDiGraph',
    role: 'Typed enterprise ontology, transitive blast-radius traversals, Brandes centrality, DAG validation.',
    sla: '< 8.5 ms BFS traversal',
    memory: '< 250 MB RAM',
    guarantee: 'Strict Multi-Hop Ontology Enforcement',
    colorHex: 0xa855f7,
    formulaName: 'Brandes Transitive Betweenness Centrality',
    formulaLatex: 'C_B(v) = \\sum_{s \\neq v \\neq t} \\frac{\\sigma_{st}(v)}{\\sigma_{st}} \\quad \\text{with} \\quad \\text{BlastRadius}(v) = |\\text{Descendants}(v)|',
    formulaDesc: 'Quantifies enterprise dependency leverage and cascading structural failure potential across all connected services.',
    codeSnippet: `G = build_enterprise_knowledge_graph(config)
centrality = nx.betweenness_centrality(G, weight='criticality')
blast_radius = {n: len(nx.descendants(G, n)) for n in G.nodes()}`
  },
  {
    id: 2,
    name: 'Activity-Based Cost Lattice',
    engine: '5-Layer Activity-Based Costing (ABC)',
    role: 'Disaggregates fully burdened infrastructure spend across compute, storage, vendor license, and labor.',
    sla: '< 1.8 ms allocation',
    memory: '< 85 MB RAM',
    guarantee: 'Bipartite Double-Counting Prevention Proof',
    colorHex: 0xf97316,
    formulaName: 'Proportional Capability Attribution',
    formulaLatex: 'C(c) = \\sum_{a \\in \\text{Apps}} C(a) \\times \\frac{w_{a,c}}{\\sum_{c\'} w_{a,c\'}} \\quad \\text{such that} \\quad \\sum_c C(c) \\equiv \\sum_a C(a)',
    formulaDesc: 'Normalized capability mapping guaranteeing exact financial conservation with mathematical proof against double-allocation.',
    codeSnippet: `def allocate_capability_costs(apps_df, rel_df):
    rel_weights = rel_df.groupby('app_id')['weight'].transform('sum')
    rel_df['norm_weight'] = rel_df['weight'] / rel_weights
    return rel_df.merge(apps_df).assign(alloc_cost=lambda d: d.tco * d.norm_weight)`
  },
  {
    id: 3,
    name: 'MCDA Rationalization Prism',
    engine: 'TOPSIS Vector Normalization + TIME',
    role: 'Multi-criteria decision analysis rank ordering candidates for Decommission, Retain, or Re-platform.',
    sla: '< 3.4 ms scoring',
    memory: '< 45 MB RAM',
    guarantee: 'Pareto-Optimal Euclidean Normalization',
    colorHex: 0x10b981,
    formulaName: 'TOPSIS Euclidean Closeness Index',
    formulaLatex: 'S_i^* = \\sqrt{\\sum_{j=1}^m (v_{ij} - v_j^*)^2}, \\quad C_i^* = \\frac{S_i^-}{S_i^* + S_i^-} \\in [0, 1]',
    formulaDesc: 'Projects applications onto multi-dimensional cost, risk, and utility criteria relative to ideal geometric solutions.',
    codeSnippet: `weights = [0.35, 0.25, 0.20, 0.20] # Cost, Risk, Health, Utilization
norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
closeness = compute_topsis_closeness(norm_matrix, weights, criteria_types)`
  },
  {
    id: 4,
    name: 'Autonomous Governance Sentinel',
    engine: 'Dual-Mode SLM + AST Query Firewall',
    role: 'Zero-hallucination deterministic rules parser paired with local Ollama SLM and 4-tier automated integrity validation.',
    sla: '< 1.8 ms regex / < 120 ms SLM',
    memory: '< 50 MB (Rules) / 5.2 GB (SLM)',
    guarantee: '100% Offline AST Query Sanitization',
    formulaName: 'Deterministic Intent AST Verification',
    formulaLatex: '\\mathcal{Q}_{\\text{safe}} = \\{q \\in \\mathcal{L} \\mid \\text{AST}(q) \\cap \\text{MutableOps} = \\emptyset \\land \\text{Param}(q) \\subseteq \\mathcal{E}\\}',
    formulaDesc: 'Guarantees execution safety by restricting natural language questions to read-only validated parameterized queries.',
    codeSnippet: `def execute_safe_analyst_query(user_nl: str) -> QueryResult:
    intent, params = parse_intent_ast(user_nl)
    if intent not in ALLOWLISTED_INTENTS:
        raise SecurityException("Unsanitized query structure")
    return run_parameterized_query(intent, params)`
  }
]

const currentTier = computed(() => tiersData[selectedTierIndex.value])

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let stackGroup: THREE.Group
const layerGroups: { id: number; group: THREE.Group; basePlate: THREE.Mesh; chips: THREE.Mesh[] }[] = []
let verticalBuses: THREE.Mesh[] = []
let busPackets: { mesh: THREE.Mesh; minY: number; maxY: number; speed: number; dir: number }[] = []

// Mouse interaction
const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2(-999, -999)

const selectTier = (index: number) => {
  selectedTierIndex.value = index
  playInteractChime(1.1 + index * 0.1)

  // Camera glide to look closer at target tier
  if (camera && stackGroup) {
    const targetY = (index - 2) * (explodeValue.value * 3.5)
    gsap.to(camera.position, {
      y: targetY + 6,
      duration: 1.2,
      ease: 'power3.out'
    })
  }
}

const updateExplosion = (val: number) => {
  explodeValue.value = val
  const baseSpacing = 0.65
  const explodeSpacing = 3.6

  layerGroups.forEach(lg => {
    const layerIdx = lg.id
    const targetY = (layerIdx - 2) * (baseSpacing + val * explodeSpacing)
    gsap.to(lg.group.position, {
      y: targetY,
      duration: 0.6,
      ease: 'power2.out'
    })
  })

  // Update vertical bus lines height
  verticalBuses.forEach(vb => {
    const totalHeight = 4 * (baseSpacing + val * explodeSpacing) + 1.2
    vb.scale.y = totalHeight
    vb.position.y = 0
  })

  // Update packet travel bounds
  busPackets.forEach(bp => {
    bp.minY = -2 * (baseSpacing + val * explodeSpacing)
    bp.maxY = 2 * (baseSpacing + val * explodeSpacing)
  })
}

watch(explodeValue, (newVal) => {
  updateExplosion(newVal)
})

const toggleXRay = () => {
  isXRayMode.value = !isXRayMode.value
  playInteractChime(isXRayMode.value ? 1.6 : 1.2)

  layerGroups.forEach(lg => {
    const baseMat = lg.basePlate.material as THREE.MeshStandardMaterial
    baseMat.wireframe = isXRayMode.value
    if (isXRayMode.value) {
      baseMat.emissiveIntensity = 0.9
    } else {
      baseMat.emissiveIntensity = 0.25
    }

    lg.chips.forEach(c => {
      const chipMat = c.material as THREE.MeshStandardMaterial
      chipMat.wireframe = isXRayMode.value
    })
  })
}

const runHardwareDiagnostics = () => {
  if (isRunningDiag.value) return
  isRunningDiag.value = true
  diagStatus.value = 'Executing 4-Tier Diagnostics...'
  playInteractChime(0.95)

  const stepsList = [
    'Verifying DuckDB Snappy Parquet Tables...',
    'Checking NetworkX MultiDiGraph DAG Acyclicity...',
    'Validating 0.00% Zero-Reconciliation Balance...',
    'Auditing AST Query Sanitization Guardrails...',
    'All 4 Tiers Verified: 83/83 Tests Passing (0.00% Drift)'
  ]

  let stepIdx = 0
  const interval = setInterval(() => {
    stepIdx++
    if (stepIdx < stepsList.length) {
      diagStatus.value = stepsList[stepIdx]
      playInteractChime(1.1 + stepIdx * 0.12)
    } else {
      clearInterval(interval)
      isRunningDiag.value = false
      playInteractChime(1.8)
    }
  }, 450)
}

onMounted(() => {
  if (!process.client || !canvasHostRef.value) return

  const container = canvasHostRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  // Scene setup
  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x0f1117, 0.035)

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100)
  camera.position.set(13, 10, 13)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.3
  container.appendChild(renderer.domElement)

  // Lighting (Architectural studio CAD style)
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.2)
  scene.add(ambientLight)

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.8)
  keyLight.position.set(15, 20, 15)
  scene.add(keyLight)

  const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.5)
  rimLight.position.set(-15, 5, -15)
  scene.add(rimLight)

  // Holographic Coordinate Floor Grid
  const gridHelper = new THREE.GridHelper(24, 24, 0x38bdf8, 0x1e2230)
  gridHelper.position.y = -8
  scene.add(gridHelper)

  stackGroup = new THREE.Group()
  scene.add(stackGroup)

  // Construct 5 Substrate Layers
  const layerWidth = 8.5
  const layerDepth = 6.0
  const layerThickness = 0.22

  tiersData.forEach((tier, idx) => {
    const lGroup = new THREE.Group()
    lGroup.position.y = (idx - 2) * (0.65 + explodeValue.value * 3.6)
    lGroup.userData = { tierIndex: idx }

    // Glass Substrate Base Plate
    const plateGeom = new THREE.BoxGeometry(layerWidth, layerThickness, layerDepth)
    const plateMat = new THREE.MeshStandardMaterial({
      color: 0x181a24,
      emissive: tier.colorHex,
      emissiveIntensity: 0.25,
      roughness: 0.2,
      metalness: 0.85,
      transparent: true,
      opacity: 0.92
    })
    const basePlate = new THREE.Mesh(plateGeom, plateMat)
    basePlate.userData = { tierIndex: idx }
    lGroup.add(basePlate)

    // Gold / Neon Edge Trim
    const edgeGeom = new THREE.BoxGeometry(layerWidth + 0.1, 0.05, layerDepth + 0.1)
    const edgeMat = new THREE.MeshBasicMaterial({ color: tier.colorHex })
    const edgeMesh = new THREE.Mesh(edgeGeom, edgeMat)
    basePlate.add(edgeMesh)

    // Microchip Dies & Silicon Components on the Plate
    const chipMeshes: THREE.Mesh[] = []
    const chipCount = 6 + (idx % 3) * 2

    for (let c = 0; c < chipCount; c++) {
      const chipW = 0.8 + (c % 3) * 0.3
      const chipD = 0.8 + (c % 2) * 0.4
      const chipH = 0.15 + (c % 2) * 0.15
      const chipGeom = new THREE.BoxGeometry(chipW, chipH, chipD)
      const chipMat = new THREE.MeshStandardMaterial({
        color: 0x242838,
        emissive: tier.colorHex,
        emissiveIntensity: c === 0 ? 0.8 : 0.2,
        roughness: 0.3,
        metalness: 0.9
      })
      const chipMesh = new THREE.Mesh(chipGeom, chipMat)

      // Distribute on plate
      const posX = ((c % 4) - 1.5) * 1.8
      const posZ = (Math.floor(c / 4) - 0.5) * 2.2
      chipMesh.position.set(posX, layerThickness / 2 + chipH / 2, posZ)
      chipMesh.userData = { tierIndex: idx }
      lGroup.add(chipMesh)
      chipMeshes.push(chipMesh)
    }

    // Floating 3D Holographic Marker Dot
    const markerGeom = new THREE.SphereGeometry(0.2, 16, 16)
    const markerMat = new THREE.MeshBasicMaterial({ color: tier.colorHex })
    const markerMesh = new THREE.Mesh(markerGeom, markerMat)
    markerMesh.position.set(layerWidth / 2 + 0.6, 0, -layerDepth / 2)
    lGroup.add(markerMesh)

    stackGroup.add(lGroup)
    layerGroups.push({
      id: idx,
      group: lGroup,
      basePlate,
      chips: chipMeshes
    })
  })

  // Vertical Laser Data Buses (conduits connecting all tiers)
  const busCoordinates = [
    { x: -layerWidth / 2 + 0.4, z: -layerDepth / 2 + 0.4 },
    { x: layerWidth / 2 - 0.4, z: -layerDepth / 2 + 0.4 },
    { x: -layerWidth / 2 + 0.4, z: layerDepth / 2 - 0.4 },
    { x: layerWidth / 2 - 0.4, z: layerDepth / 2 - 0.4 }
  ]

  busCoordinates.forEach(coord => {
    const cylGeom = new THREE.CylinderGeometry(0.04, 0.04, 1, 16)
    const cylMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.6
    })
    const busMesh = new THREE.Mesh(cylGeom, cylMat)
    busMesh.position.set(coord.x, 0, coord.z)
    stackGroup.add(busMesh)
    verticalBuses.push(busMesh)

    // Animated energy packet along each bus
    const packetGeom = new THREE.SphereGeometry(0.12, 12, 12)
    const packetMat = new THREE.MeshBasicMaterial({ color: 0xffffff })
    const packetMesh = new THREE.Mesh(packetGeom, packetMat)
    packetMesh.position.set(coord.x, 0, coord.z)
    stackGroup.add(packetMesh)
    busPackets.push({
      mesh: packetMesh,
      minY: -5,
      maxY: 5,
      speed: 0.04 + Math.random() * 0.03,
      dir: 1
    })
  })

  updateExplosion(explodeValue.value)

  // Animation Loop
  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const elapsedTime = clock.getElapsedTime()

    // Auto slow rotation if enabled
    if (isAutoRotating.value && stackGroup) {
      stackGroup.rotation.y = elapsedTime * 0.12
    }

    // Animate bus energy packets
    busPackets.forEach(bp => {
      bp.mesh.position.y += bp.speed * bp.dir
      if (bp.mesh.position.y > bp.maxY) {
        bp.mesh.position.y = bp.maxY
        bp.dir = -1
      } else if (bp.mesh.position.y < bp.minY) {
        bp.mesh.position.y = bp.minY
        bp.dir = 1
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
  <div class="mock-exploded-root">
    <!-- 3D Canvas Host -->
    <div ref="canvasHostRef" class="canvas-viewport" />

    <!-- Overlaid Industrial CAD HUD Interface -->
    <div class="cad-hud-layer">
      <!-- 1. Header Toolbar -->
      <div class="cad-header-bar">
        <div class="cad-title-cluster">
          <span class="cad-kicker">MOCK 02 // ISOMETRIC ARCHITECTURAL CAD TWIN</span>
          <h2 class="cad-main-title">Exploded 3D Architectural Motherboard</h2>
        </div>

        <div class="cad-meta-badges">
          <div class="cad-badge">
            <span class="dot dot-sky" />
            <span>Architecture: <strong>5 Decoupled Tiers</strong></span>
          </div>
          <div class="cad-badge">
            <span class="dot dot-mint" />
            <span>Memory Budget: <strong>&lt; 4.0 GB RAM</strong></span>
          </div>
          <div class="cad-badge">
            <span class="dot dot-lavender" />
            <span>Query SLA: <strong>&lt; 4.2 ms</strong></span>
          </div>
        </div>

        <!-- Right CAD Toolbar Controls -->
        <div class="cad-action-cluster">
          <button
            type="button"
            class="cad-pill-toggle"
            :class="{ active: isXRayMode }"
            @click="toggleXRay"
          >
            <span class="icon-toggle">⚡</span>
            <span>{{ isXRayMode ? 'Standard Shading' : 'X-Ray Heatmap' }}</span>
          </button>

          <button
            type="button"
            class="cad-pill-toggle"
            :class="{ active: isAutoRotating }"
            @click="isAutoRotating = !isAutoRotating"
          >
            <span>{{ isAutoRotating ? 'Pause Orbit' : 'Resume Orbit' }}</span>
          </button>
        </div>
      </div>

      <!-- 2. Left CAD Stack Disassembler Panel -->
      <aside class="cad-left-controls">
        <div class="cad-panel-box">
          <div class="panel-hed-row">
            <span class="p-hed">Exploded View Spacing</span>
            <strong class="p-val">{{ Math.round(explodeValue * 100) }}%</strong>
          </div>
          <input
            v-model.number="explodeValue"
            type="range"
            min="0"
            max="1"
            step="0.01"
            class="cad-range-slider"
          />
          <div class="slider-presets">
            <button type="button" class="preset-btn" @click="explodeValue = 0">Assembly (0%)</button>
            <button type="button" class="preset-btn" @click="explodeValue = 0.5">Balanced (50%)</button>
            <button type="button" class="preset-btn" @click="explodeValue = 1.0">Expanded (100%)</button>
          </div>
        </div>

        <!-- Tier Selection Stack -->
        <div class="cad-panel-box">
          <span class="p-hed">Substrate Tiers</span>
          <div class="tier-nav-buttons">
            <button
              v-for="(t, idx) in tiersData"
              :key="t.id"
              type="button"
              class="tier-selector-btn"
              :class="{ active: selectedTierIndex === idx }"
              @click="selectTier(idx)"
              @mouseenter="setCursor(t.engine, 'highlight')"
              @mouseleave="resetCursor"
            >
              <div class="btn-top-info">
                <span class="tier-num">Tier 0{{ idx + 1 }}</span>
                <span class="tier-sla">{{ t.sla }}</span>
              </div>
              <strong class="tier-title">{{ t.name }}</strong>
              <span class="tier-engine-desc">{{ t.engine }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- 3. Right Forensic Architectural Spec Sheet -->
      <aside class="cad-inspector-drawer">
        <div class="drawer-header">
          <div class="drawer-tag-group">
            <span class="tier-pill-chip">TIER 0{{ selectedTierIndex + 1 }}</span>
            <span class="guarantee-pill">{{ currentTier.guarantee }}</span>
          </div>
          <span class="sla-chip-mono">{{ currentTier.sla }}</span>
        </div>

        <h3 class="active-tier-name">{{ currentTier.name }}</h3>
        <p class="active-tier-role">{{ currentTier.role }}</p>

        <!-- Hardware & Memory Specifications -->
        <div class="cad-specs-matrix">
          <div class="matrix-cell">
            <span class="m-k">Engine Specification</span>
            <strong class="m-v mono">{{ currentTier.engine }}</strong>
          </div>
          <div class="matrix-cell">
            <span class="m-k">Memory Footprint</span>
            <strong class="m-v text-mint">{{ currentTier.memory }}</strong>
          </div>
          <div class="matrix-cell">
            <span class="m-k">Latency SLA</span>
            <strong class="m-v text-sky">{{ currentTier.sla }}</strong>
          </div>
          <div class="matrix-cell">
            <span class="m-k">Accounting Drift</span>
            <strong class="m-v text-lavender">0.00% Zero-Loss</strong>
          </div>
        </div>

        <!-- Formatted Mathematical Formulation -->
        <div class="cad-math-container">
          <MathFormula
            :latex="currentTier.formulaLatex"
            :name="currentTier.formulaName"
          />
          <p class="math-expl-text">{{ currentTier.formulaDesc }}</p>
        </div>

        <!-- Python Kernel Lineage -->
        <div class="cad-code-card">
          <div class="code-card-header">
            <span class="code-tag">Python Architecture Lineage</span>
            <span class="mono-badge">src/tvi/</span>
          </div>
          <pre class="cad-pre"><code>{{ currentTier.codeSnippet }}</code></pre>
        </div>
      </aside>

      <!-- 4. Bottom System Health Diagnostic Console -->
      <div class="cad-bottom-console">
        <div class="console-left">
          <div class="status-indicator-dot" :class="{ 'is-diagnosing': isRunningDiag }" />
          <div>
            <span class="console-label">4-Tier Hardware & Mathematical Diagnostics</span>
            <strong class="console-status-text">{{ diagStatus }}</strong>
          </div>
        </div>

        <button
          type="button"
          class="run-diag-btn"
          :class="{ active: isRunningDiag }"
          @click="runHardwareDiagnostics"
        >
          <span>{{ isRunningDiag ? 'Executing Audit...' : 'Run Diagnostics Test' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mock-exploded-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #0d0f14;
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

/* ---------------- CAD HUD Layer ---------------- */
.cad-hud-layer {
  position: relative;
  z-index: 10;
  pointer-events: none;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 6.5rem 2.5rem 2rem;
}

.cad-hud-layer * {
  pointer-events: auto;
}

/* 1. Header Toolbar */
.cad-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: rgba(18, 21, 30, 0.85);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 1rem 1.6rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

.cad-kicker {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #38bdf8;
  text-transform: uppercase;
}

.cad-main-title {
  font-family: var(--font-display);
  font-size: 1.22rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
}

.cad-meta-badges {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.cad-badge {
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
.dot-sky { background: #38bdf8; }
.dot-mint { background: #10b981; }
.dot-lavender { background: #8b5cf6; }

.cad-action-cluster {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cad-pill-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.95rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #c9cedc;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cad-pill-toggle:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.cad-pill-toggle.active {
  background: #38bdf8;
  color: #0b0c10;
  border-color: #38bdf8;
  font-weight: 700;
}

/* 2. Left CAD Controls */
.cad-left-controls {
  position: absolute;
  top: 13rem;
  left: 2.5rem;
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cad-panel-box {
  background: rgba(18, 21, 30, 0.88);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 1.15rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
}

.panel-hed-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.p-hed {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #8c92a4;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.5rem;
}

.p-val {
  font-size: 0.84rem;
  color: #38bdf8;
}

.cad-range-slider {
  width: 100%;
  accent-color: #38bdf8;
  cursor: pointer;
}

.slider-presets {
  display: flex;
  justify-content: space-between;
  margin-top: 0.6rem;
}

.preset-btn {
  font-size: 0.68rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #a0a6b7;
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  cursor: pointer;
}

.preset-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.tier-nav-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.tier-selector-btn {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
}

.tier-selector-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.tier-selector-btn.active {
  background: rgba(56, 189, 248, 0.15);
  border-color: rgba(56, 189, 248, 0.4);
}

.btn-top-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tier-num {
  font-size: 0.68rem;
  font-weight: 700;
  color: #38bdf8;
  text-transform: uppercase;
}

.tier-sla {
  font-size: 0.68rem;
  font-family: var(--font-mono);
  color: #a7f3d0;
}

.tier-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #ffffff;
}

.tier-engine-desc {
  font-size: 0.7rem;
  color: #7b8192;
}

/* 3. Right Inspector Drawer */
.cad-inspector-drawer {
  position: absolute;
  top: 13rem;
  right: 2.5rem;
  width: 480px;
  max-height: calc(100vh - 22rem);
  overflow-y: auto;
  background: rgba(18, 21, 30, 0.88);
  backdrop-filter: blur(28px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.drawer-tag-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tier-pill-chip {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 800;
  background: #38bdf8;
  color: #0b0c10;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.guarantee-pill {
  font-size: 0.72rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.15);
  color: #a7f3d0;
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.sla-chip-mono {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #93c5fd;
}

.active-tier-name {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  color: #ffffff;
}

.active-tier-role {
  font-size: 0.86rem;
  color: #9ba1b2;
  line-height: 1.5;
}

.cad-specs-matrix {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.matrix-cell {
  background: rgba(0, 0, 0, 0.28);
  border-radius: 10px;
  padding: 0.55rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.m-k {
  font-size: 0.66rem;
  text-transform: uppercase;
  color: #7b8192;
}

.m-v {
  font-size: 0.8rem;
}

.mono { font-family: var(--font-mono); }
.text-mint { color: #a7f3d0; }
.text-sky { color: #7dd3fc; }
.text-lavender { color: #c4b5fd; }

.math-expl-text {
  font-size: 0.76rem;
  color: #8c92a4;
  line-height: 1.45;
  margin-top: 0.35rem;
}

.cad-code-card {
  background: #090a0f;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

.code-card-header {
  display: flex;
  justify-content: space-between;
  padding: 0.4rem 0.75rem;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.code-tag {
  font-size: 0.68rem;
  font-weight: 600;
  color: #8c92a4;
}

.mono-badge {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: #38bdf8;
}

.cad-pre {
  margin: 0;
  padding: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: #93c5fd;
  line-height: 1.45;
  max-height: 130px;
  overflow-y: auto;
}

/* 4. Bottom Diagnostic Console */
.cad-bottom-console {
  margin-top: auto;
  background: rgba(18, 21, 30, 0.88);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 0.95rem 1.6rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

.console-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.status-indicator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 12px #10b981;
}

.status-indicator-dot.is-diagnosing {
  background: #f59e0b;
  box-shadow: 0 0 18px #f59e0b;
  animation: pulse-rapid 0.4s infinite alternate;
}

.console-label {
  display: block;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8c92a4;
}

.console-status-text {
  font-size: 0.88rem;
  color: #ffffff;
}

.run-diag-btn {
  padding: 0.55rem 1.3rem;
  border-radius: var(--radius-pill);
  background: linear-gradient(135deg, #0284c7, #8b5cf6);
  color: #ffffff;
  font-size: 0.82rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.run-diag-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 22px rgba(2, 132, 199, 0.4);
}

.run-diag-btn.active {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
}

@media (max-width: 1200px) {
  .cad-left-controls {
    display: none;
  }
  .cad-inspector-drawer {
    width: 380px;
  }
}

@media (max-width: 900px) {
  .cad-header-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  .cad-inspector-drawer {
    position: static;
    width: 100%;
    margin-top: 1rem;
    max-height: none;
  }
}
</style>
