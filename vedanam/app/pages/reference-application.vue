<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useTVIData } from '~/composables/useTVIData'
import { useTVIScenarios, type EnterpriseScenario } from '~/composables/useTVIScenarios'
import { useAudioSynth } from '~/composables/useAudioSynth'
import { useCursor } from '~/composables/useCursor'

const pageRef = ref<HTMLElement | null>(null)
let gsapCtx: gsap.Context | null = null

const { referenceApplications, activeReferenceAppId, activeReferenceApp, setReferenceApp } = useTVIData()
const { scenarios } = useTVIScenarios()
const { playInteractChime } = useAudioSynth()
const { setCursor, resetCursor } = useCursor()

// Interactive What-If Simulation State
const simVolume = ref(1.0)
const simRightsizing = ref(0)
const simLicenseEscalation = ref(0)

// Active Applied Scenario on Simulator
const currentlyAppliedScenario = ref<EnterpriseScenario | null>(null)

// Reset what-if simulation to defaults when active app changes
watch(activeReferenceAppId, () => {
  const defaults = activeReferenceApp.value.whatIfDefaults
  simVolume.value = defaults.volumeMultiplier
  simRightsizing.value = defaults.rightsizingPercent
  simLicenseEscalation.value = defaults.licenseEscalation
  rebuildGraph()
  playInteractChime(1.3)
  if (process.client) {
    gsap.fromTo(
      ['.overview-glass-card', '.metrics-grid .metric-card'],
      { opacity: 0.5, y: 12 },
      { opacity: 1, y: 0, duration: 0.45, stagger: 0.04, ease: 'power3.out' }
    )
  }
})

// Dynamic Recalculated What-If Metrics
const simulatedMetrics = computed(() => {
  const app = activeReferenceApp.value
  const baseInfra = app.costBreakdown.infrastructure
  const baseSoftware = app.costBreakdown.software
  const basePersonnel = app.costBreakdown.personnel
  const baseOverhead = app.costBreakdown.overhead

  // Infrastructure adjusts with volume elasticity and rightsizing savings
  const simInfra = Math.round(
    baseInfra * (1 - simRightsizing.value / 100) * (1 + (simVolume.value - 1) * 0.42)
  )

  // Software license escalates or reduces with contractual negotiation
  const simSoft = Math.round(baseSoftware * (1 + simLicenseEscalation.value / 100))

  const simPers = basePersonnel
  const simOver = baseOverhead

  const totalSimTco = simInfra + simSoft + simPers + simOver
  const baseTco = app.tco
  const diffDollars = totalSimTco - baseTco
  const annualSavings = Math.max(0, -diffDollars)

  const simulatedEvents = Math.round(app.monthlyEvents * simVolume.value)
  const simulatedCostPerUser = (totalSimTco / app.activeUsers).toFixed(2)
  const simulatedCostPer1k = ((totalSimTco / (simulatedEvents * 12)) * 1000).toFixed(4)

  return {
    simInfra,
    simSoft,
    simPers,
    simOver,
    totalSimTco,
    diffDollars,
    annualSavings,
    simulatedEvents,
    simulatedCostPerUser,
    simulatedCostPer1k
  }
})

// ----------------------------------------------------------------------------
// Scenario Intelligence Matrix State & Filtering
// ----------------------------------------------------------------------------
const selectedScenarioTier = ref<'all' | 'basic' | 'intermediate' | 'advanced'>('all')
const scenarioSearchQuery = ref<string>('')
const activeInspectedScenario = ref<EnterpriseScenario | null>(null)

const filteredScenarios = computed(() => {
  return scenarios.filter(s => {
    const matchesTier = selectedScenarioTier.value === 'all' || s.tier === selectedScenarioTier.value
    const query = scenarioSearchQuery.value.toLowerCase().trim()
    const matchesQuery =
      !query ||
      s.name.toLowerCase().includes(query) ||
      s.code.toLowerCase().includes(query) ||
      s.letter.toLowerCase() === query ||
      s.targetEntity.toLowerCase().includes(query) ||
      s.category.toLowerCase().includes(query) ||
      s.description.toLowerCase().includes(query)

    return matchesTier && matchesQuery
  })
})

const openScenarioModal = (scn: EnterpriseScenario) => {
  activeInspectedScenario.value = scn
  playInteractChime(1.2)
}

const closeScenarioModal = () => {
  activeInspectedScenario.value = null
}

const applyScenarioToSimulator = (scn: EnterpriseScenario) => {
  currentlyAppliedScenario.value = scn
  setReferenceApp(scn.suggestedAppId)
  simVolume.value = scn.simulationPreset.volumeMultiplier
  simRightsizing.value = scn.simulationPreset.rightsizingPercent
  simLicenseEscalation.value = scn.simulationPreset.licenseEscalation
  activeInspectedScenario.value = null
  playInteractChime(1.45)

  if (process.client) {
    const el = document.getElementById('whatif-simulator')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
}

const resetAppliedScenario = () => {
  currentlyAppliedScenario.value = null
  const defaults = activeReferenceApp.value.whatIfDefaults
  simVolume.value = defaults.volumeMultiplier
  simRightsizing.value = defaults.rightsizingPercent
  simLicenseEscalation.value = defaults.licenseEscalation
  playInteractChime(1.1)
}

// ----------------------------------------------------------------------------
// Three.js 3D Local Subgraph Visualizer
// ----------------------------------------------------------------------------
const canvasContainerRef = ref<HTMLDivElement | null>(null)
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let graphGroup: THREE.Group
let pulseGroup: THREE.Group
let pulses: { mesh: THREE.Mesh; path: THREE.CatmullRomCurve3; progress: number; speed: number }[] = []

const rebuildGraph = () => {
  if (!graphGroup || !pulseGroup) return

  // Clear existing objects
  while (graphGroup.children.length > 0) {
    const obj = graphGroup.children[0]
    graphGroup.remove(obj)
  }
  while (pulseGroup.children.length > 0) {
    const obj = pulseGroup.children[0]
    pulseGroup.remove(obj)
  }
  pulses = []

  const app = activeReferenceApp.value
  const nodes = app.topologyNodes

  // Place core application node at origin
  const corePos = new THREE.Vector3(0, 0, 0)

  // Core mesh
  const coreMat = new THREE.MeshStandardMaterial({
    color: 0x121318,
    emissive: 0x222530,
    roughness: 0.2,
    metalness: 0.8
  })
  const coreGeo = new THREE.SphereGeometry(0.38, 32, 32)
  const coreMesh = new THREE.Mesh(coreGeo, coreMat)
  coreMesh.position.copy(corePos)
  graphGroup.add(coreMesh)

  // Pulsing halo around core
  const haloMat = new THREE.MeshBasicMaterial({
    color: 0xa7f3d0,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.4
  })
  const haloGeo = new THREE.RingGeometry(0.5, 0.58, 32)
  const haloMesh = new THREE.Mesh(haloGeo, haloMat)
  haloMesh.rotation.x = Math.PI / 3
  graphGroup.add(haloMesh)

  // Position satellite nodes radially in 3D
  const count = nodes.length - 1
  let index = 0

  nodes.forEach(n => {
    if (n.type === 'core') return

    let radius = 2.4
    let theta = (index / count) * Math.PI * 2
    let y = Math.sin(index * 1.8) * 0.9

    if (n.type === 'capability') {
      radius = 2.2
      y = 1.1 + index * 0.2
    } else if (n.type === 'infra') {
      radius = 2.5
      y = -1.0 - index * 0.2
    } else if (n.type === 'consumer') {
      radius = 2.8
      y = 0.2
    }

    const pos = new THREE.Vector3(
      Math.cos(theta) * radius,
      y,
      Math.sin(theta) * radius
    )
    index++

    // Satellite Mesh
    const mat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: new THREE.Color(n.color),
      emissiveIntensity: 0.65,
      roughness: 0.15,
      metalness: 0.1
    })
    const nodeSize = n.type === 'capability' ? 0.22 : 0.18
    const geo = new THREE.SphereGeometry(nodeSize, 20, 20)
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.copy(pos)
    graphGroup.add(mesh)

    // Bezier Spline Edge connecting to Core
    const mid = new THREE.Vector3().addVectors(corePos, pos).multiplyScalar(0.5)
    mid.y += (Math.random() - 0.5) * 0.3
    const curve = new THREE.CatmullRomCurve3([corePos, mid, pos])
    const curvePoints = curve.getPoints(24)
    const edgeGeo = new THREE.BufferGeometry().setFromPoints(curvePoints)
    const edgeMat = new THREE.LineBasicMaterial({
      color: 0xd1d5db,
      transparent: true,
      opacity: 0.45
    })
    const edgeLine = new THREE.Line(edgeGeo, edgeMat)
    graphGroup.add(edgeLine)

    // Telemetry pulse
    const pGeo = new THREE.SphereGeometry(0.05, 12, 12)
    const pMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(n.color) })
    const pMesh = new THREE.Mesh(pGeo, pMat)
    pulseGroup.add(pMesh)
    pulses.push({
      mesh: pMesh,
      path: curve,
      progress: Math.random(),
      speed: 0.004 + Math.random() * 0.004
    })
  })
}

// Mouse Drag Orbit
let isDragging = false
let prevMouseX = 0
let prevMouseY = 0

const onMouseDown = (e: MouseEvent) => {
  isDragging = true
  prevMouseX = e.clientX
  prevMouseY = e.clientY
}

const onMouseMove = (e: MouseEvent) => {
  if (!isDragging || !graphGroup) return
  const deltaX = e.clientX - prevMouseX
  const deltaY = e.clientY - prevMouseY
  graphGroup.rotation.y += deltaX * 0.008
  graphGroup.rotation.x += deltaY * 0.008
  prevMouseX = e.clientX
  prevMouseY = e.clientY
}

const onMouseUp = () => {
  isDragging = false
}

const resetCamera = () => {
  if (camera && graphGroup) {
    gsap.to(graphGroup.rotation, { x: 0.2, y: -0.4, duration: 0.8, ease: 'power2.out' })
    gsap.to(camera.position, { x: 0, y: 0.5, z: 6.2, duration: 0.8, ease: 'power2.out' })
  }
}

onMounted(() => {
  if (!process.client || !canvasContainerRef.value) return

  const container = canvasContainerRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100)
  camera.position.set(0, 0.5, 6.2)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  const ambientLight = new THREE.AmbientLight(0xffffff, 1.4)
  scene.add(ambientLight)

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8)
  dirLight.position.set(5, 8, 6)
  scene.add(dirLight)

  graphGroup = new THREE.Group()
  pulseGroup = new THREE.Group()
  graphGroup.rotation.x = 0.2
  graphGroup.rotation.y = -0.4
  scene.add(graphGroup)
  scene.add(pulseGroup)

  rebuildGraph()

  const handleResize = () => {
    if (!canvasContainerRef.value) return
    const w = canvasContainerRef.value.clientWidth
    const h = canvasContainerRef.value.clientHeight
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
  }
  window.addEventListener('resize', handleResize)

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)

    if (!isDragging && graphGroup) {
      graphGroup.rotation.y += 0.0015
    }

    pulses.forEach(p => {
      p.progress += p.speed
      if (p.progress > 1) p.progress = 0
      const pos = p.path.getPointAt(p.progress)
      p.mesh.position.copy(pos)
    })

    renderer.render(scene, camera)
  }
  animate()

  gsap.registerPlugin(ScrollTrigger)

  gsapCtx = gsap.context(() => {
    // 1. Hero Header Arrival Entry
    const heroTl = gsap.timeline({ delay: 0.1 })
    heroTl
      .fromTo('.ref-hero-header .eyebrow-row', { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power3.out' })
      .fromTo('.ref-title', { opacity: 0, y: 35, filter: 'blur(5px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.9, ease: 'power4.out' }, '-=0.4')
      .fromTo('.ref-subtitle', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
      .fromTo('.archetype-tab-btn', { opacity: 0, y: 30, scale: 0.95 }, { opacity: 1, y: 0, scale: 1, duration: 0.75, stagger: 0.1, ease: 'back.out(1.4)' }, '-=0.4')

    // 2. Active Application Overview (Glass card)
    gsap.fromTo(
      '.overview-glass-card',
      { opacity: 0, y: 45, scale: 0.98 },
      {
        scrollTrigger: {
          trigger: '.ref-app-overview',
          start: 'top 85%',
          end: 'bottom 15%',
          toggleActions: 'play reverse play reverse'
        },
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.85,
        ease: 'power3.out'
      }
    )

    // 3. Key Unit Economic Metrics Cards (4-card cascade)
    gsap.fromTo(
      '.metrics-grid .metric-card',
      { opacity: 0, y: 45, scale: 0.94 },
      {
        scrollTrigger: {
          trigger: '.ref-metrics-grid-section',
          start: 'top 82%',
          end: 'bottom 12%',
          toggleActions: 'play reverse play reverse'
        },
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.8,
        stagger: 0.1,
        ease: 'power3.out'
      }
    )

    // 4. Interactive 3D Subgraph & Cost Stack Split
    const splitTl = gsap.timeline({
      scrollTrigger: {
        trigger: '.ref-subgraph-split-section',
        start: 'top 80%',
        end: 'bottom 12%',
        toggleActions: 'play reverse play reverse'
      }
    })
    splitTl
      .fromTo('.subgraph-3d-card', { opacity: 0, x: -45, scale: 0.97 }, { opacity: 1, x: 0, scale: 1, duration: 0.85, ease: 'power3.out' })
      .fromTo('.cost-stack-card', { opacity: 0, x: 45, scale: 0.97 }, { opacity: 1, x: 0, scale: 1, duration: 0.85, ease: 'power3.out' }, '-=0.7')
      .fromTo('.cost-segmented-bar > div', { scaleX: 0, transformOrigin: 'left' }, { scaleX: 1, duration: 0.6, stagger: 0.08, ease: 'power2.out' }, '-=0.4')
      .fromTo('.breakdown-item', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: 'power2.out' }, '-=0.4')

    // 5. Capability Attribution & Governance Scorecard
    const capGovTl = gsap.timeline({
      scrollTrigger: {
        trigger: '.ref-capability-governance-section',
        start: 'top 80%',
        end: 'bottom 12%',
        toggleActions: 'play reverse play reverse'
      }
    })
    capGovTl
      .fromTo('.capability-attribution-card', { opacity: 0, y: 45, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'power3.out' })
      .fromTo('.governance-audit-card', { opacity: 0, y: 45, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'power3.out' }, '-=0.65')
      .fromTo('.cap-bar-row', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: 'power2.out' }, '-=0.4')
      .fromTo('.audit-cell', { opacity: 0, scale: 0.92 }, { opacity: 1, scale: 1, duration: 0.5, stagger: 0.06, ease: 'back.out(1.5)' }, '-=0.4')

    // 6. Interactive What-If Scenario Simulator
    const simTl = gsap.timeline({
      scrollTrigger: {
        trigger: '.ref-simulator-section',
        start: 'top 80%',
        end: 'bottom 12%',
        toggleActions: 'play reverse play reverse'
      }
    })
    simTl
      .fromTo('.simulator-main-card', { opacity: 0, y: 50, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.85, ease: 'power3.out' })
      .fromTo('.sim-controls-col', { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
      .fromTo('.sim-results-col', { opacity: 0, x: 30, scale: 0.97 }, { opacity: 1, x: 0, scale: 1, duration: 0.7, ease: 'power3.out' }, '-=0.6')

    // 7. Enterprise Scenario Intelligence Matrix (Scenarios A through Y)
    const scnTl = gsap.timeline({
      scrollTrigger: {
        trigger: '.ref-scenarios-section',
        start: 'top 82%',
        end: 'bottom 10%',
        toggleActions: 'play reverse play reverse'
      }
    })
    scnTl
      .fromTo('.scenarios-matrix-header', { opacity: 0, y: 35 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' })
      .fromTo('.scenarios-grid .scenario-card', { opacity: 0, y: 40, scale: 0.95 }, { opacity: 1, y: 0, scale: 1, duration: 0.65, stagger: 0.035, ease: 'power3.out' }, '-=0.4')
  }, pageRef.value ?? undefined)
})

onUnmounted(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId)
  if (renderer && renderer.domElement) {
    renderer.domElement.remove()
    renderer.dispose()
  }
  gsapCtx?.revert()
})

// Export Specification Action
const exportSpecification = () => {
  playInteractChime(1.4)
  const app = activeReferenceApp.value
  const exportPayload = {
    canonical_id: app.id,
    enterprise_code: app.code,
    name: app.name,
    tier: app.tier,
    burdened_tco: app.tco,
    avoidable_cost: app.avoidableCost,
    unit_economics: {
      cost_per_active_user: app.unitCostPerUser,
      cost_per_1k_transactions: app.unitCostPer1kEvents,
      monthly_events: app.monthlyEvents,
      active_users: app.activeUsers
    },
    cost_breakdown: app.costBreakdown,
    capabilities: app.capabilityAttribution,
    governance: app.governanceAudit,
    exported_at: new Date().toISOString(),
    engine: 'Technology Value Intelligence (DuckDB + NetworkX)'
  }

  const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${app.code}_reference_architecture_spec.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div ref="pageRef" class="ref-app-page">
    <Navigation />

    <main class="ref-main-container">
      <!-- 1. Page Header & Archetype Context -->
      <section class="ref-hero-header">
        <div class="container">
          <div class="eyebrow-row">
            <span class="section-tag">Feature · Reference Application</span>
            <span class="pastel-chip chip-mint">Canonical Archetype Benchmark</span>
            <a href="#scenarios-matrix" class="pastel-chip chip-lavender">25 Scenarios Ready ↓</a>
          </div>
          <h1 class="ref-title">Reference Application Architecture</h1>
          <p class="ref-subtitle">
            An end-to-end exemplar of Technology Value Realization. Inspect how burdened cost modeling, multi-hop relationship topology, unit economics, and governance guardrails fuse into auditable executive decision intelligence.
          </p>

          <!-- 3 Archetype Selector Tabs -->
          <div class="archetype-tabs-container">
            <button
              v-for="app in referenceApplications"
              :key="app.id"
              type="button"
              class="archetype-tab-btn"
              :class="{ 'is-active': activeReferenceAppId === app.id }"
              @click="setReferenceApp(app.id)"
              @mouseenter="setCursor(app.archetypeTag, 'default')"
              @mouseleave="resetCursor"
            >
              <div class="tab-btn-header">
                <span class="tab-code">{{ app.code }}</span>
                <span class="tab-tag" :class="app.archetypeTag === 'Mission Critical' ? 'tag-mint' : app.archetypeTag === 'Cloud Native' ? 'tag-lavender' : 'tag-rose'">
                  {{ app.archetypeTag }}
                </span>
              </div>
              <span class="tab-name">{{ app.name }}</span>
              <div class="tab-footer">
                <span class="tab-tco">${{ (app.tco / 1000000).toFixed(2) }}M TCO</span>
                <span class="tab-quadrant">{{ app.timeQuadrant }}</span>
              </div>
            </button>
          </div>
        </div>
      </section>

      <!-- 2. Active Application Overview & Action Row -->
      <section class="ref-app-overview">
        <div class="container">
          <div class="overview-glass-card">
            <div class="overview-left">
              <div class="code-and-tier">
                <span class="app-code-pill">{{ activeReferenceApp.code }}</span>
                <span class="app-tier-text">{{ activeReferenceApp.tier }}</span>
                <span class="app-health-badge">Health {{ activeReferenceApp.healthScore }}/100</span>
              </div>
              <h2 class="active-app-heading">{{ activeReferenceApp.name }}</h2>
              <p class="active-app-desc">{{ activeReferenceApp.description }}</p>
            </div>
            <div class="overview-actions">
              <button
                type="button"
                class="pill-btn-dark"
                @click="exportSpecification"
                @mouseenter="setCursor('EXPORT SPEC', 'highlight')"
                @mouseleave="resetCursor"
              >
                <span>Export TVR Spec (JSON) ↗</span>
              </button>
              <a
                href="#scenarios-matrix"
                class="pill-btn-light"
                @mouseenter="setCursor('SCENARIOS', 'default')"
                @mouseleave="resetCursor"
              >
                <span>Check 25 Scenarios ↓</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      <!-- 3. Key Unit Economic Metrics Cards -->
      <section class="ref-metrics-grid-section">
        <div class="container">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="metric-label">Burdened Annual TCO</span>
              <div class="metric-number-row">
                <span class="metric-value">${{ (activeReferenceApp.tco / 1000000).toFixed(2) }}M</span>
                <span class="metric-unit">/ year</span>
              </div>
              <span class="metric-caption">Direct Compute + Licenses + Labor + Overhead</span>
            </div>

            <div class="metric-card">
              <span class="metric-label">Unit Cost per User</span>
              <div class="metric-number-row">
                <span class="metric-value">${{ activeReferenceApp.unitCostPerUser.toLocaleString() }}</span>
                <span class="metric-unit">/ user / yr</span>
              </div>
              <span class="metric-caption">{{ activeReferenceApp.activeUsers.toLocaleString() }} active enterprise users</span>
            </div>

            <div class="metric-card">
              <span class="metric-label">Unit Cost per 1k Txn</span>
              <div class="metric-number-row">
                <span class="metric-value">${{ activeReferenceApp.unitCostPer1kEvents }}</span>
                <span class="metric-unit">/ 1,000</span>
              </div>
              <span class="metric-caption">{{ (activeReferenceApp.monthlyEvents / 1000000).toFixed(1) }}M monthly transactions</span>
            </div>

            <div class="metric-card">
              <span class="metric-label">Transitive Blast Radius</span>
              <div class="metric-number-row">
                <span class="metric-value">${{ (activeReferenceApp.blastRadiusDollars / 1000000).toFixed(2) }}M</span>
                <span class="metric-unit">max impact</span>
              </div>
              <span class="metric-caption">{{ activeReferenceApp.dependenciesCount }} transitive multi-hop dependencies</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 4. Interactive 3D Subgraph & Cost Stack Split -->
      <section class="ref-subgraph-split-section">
        <div class="container">
          <div class="subgraph-split-grid">
            <!-- Left: Interactive 3D Local Subgraph (Three.js WebGL) -->
            <div class="subgraph-3d-card">
              <div class="card-header-row">
                <div>
                  <span class="sub-card-tag">Relationship Intelligence · NetworkX</span>
                  <h3 class="sub-card-title">Local 3D Knowledge Graph Subgraph</h3>
                </div>
                <div class="graph-controls-group">
                  <button type="button" class="graph-ctrl-btn" @click="resetCamera" title="Reset Viewpoint">
                    Reset ⟲
                  </button>
                </div>
              </div>

              <!-- WebGL Canvas Container -->
              <div
                ref="canvasContainerRef"
                class="subgraph-canvas-viewport"
                @mousedown="onMouseDown"
                @mousemove="onMouseMove"
                @mouseup="onMouseUp"
                @mouseleave="onMouseUp"
              >
                <div class="graph-legend-overlay">
                  <span class="legend-item"><span class="legend-dot dot-core" /> Core App</span>
                  <span class="legend-item"><span class="legend-dot dot-cap" /> Capability</span>
                  <span class="legend-item"><span class="legend-dot dot-infra" /> Infrastructure</span>
                  <span class="legend-item"><span class="legend-dot dot-consumer" /> Upstream API</span>
                </div>
                <div class="drag-hint-pill">Drag to Orbit · Click to Inspect</div>
              </div>

              <div class="subgraph-card-footer">
                <div class="node-chips-row">
                  <span
                    v-for="node in activeReferenceApp.topologyNodes"
                    :key="node.id"
                    class="pastel-chip"
                    :style="{ borderColor: node.color }"
                  >
                    {{ node.label }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Right: Burdened Cost Breakdown Stack -->
            <div class="cost-stack-card">
              <div class="card-header-row">
                <div>
                  <span class="sub-card-tag">Analytical Truth · DuckDB OLAP</span>
                  <h3 class="sub-card-title">Fully Burdened Cost Allocation</h3>
                </div>
              </div>

              <!-- Segmented Visual Bar -->
              <div class="cost-segmented-bar">
                <div
                  class="seg-infra"
                  :style="{ width: `${(activeReferenceApp.costBreakdown.infrastructure / activeReferenceApp.tco) * 100}%` }"
                  title="Infrastructure"
                />
                <div
                  class="seg-soft"
                  :style="{ width: `${(activeReferenceApp.costBreakdown.software / activeReferenceApp.tco) * 100}%` }"
                  title="Software"
                />
                <div
                  class="seg-pers"
                  :style="{ width: `${(activeReferenceApp.costBreakdown.personnel / activeReferenceApp.tco) * 100}%` }"
                  title="Personnel"
                />
                <div
                  class="seg-over"
                  :style="{ width: `${(activeReferenceApp.costBreakdown.overhead / activeReferenceApp.tco) * 100}%` }"
                  title="Overhead"
                />
              </div>

              <!-- Detailed Breakdown Rows -->
              <div class="cost-breakdown-list">
                <div class="breakdown-item">
                  <div class="b-row-top">
                    <span class="b-label"><span class="b-color-sq sq-infra" /> Cloud & Infrastructure</span>
                    <span class="b-val">${{ activeReferenceApp.costBreakdown.infrastructure.toLocaleString() }}</span>
                  </div>
                  <p class="b-detail-text">{{ activeReferenceApp.infrastructureDetail }}</p>
                </div>

                <div class="breakdown-item">
                  <div class="b-row-top">
                    <span class="b-label"><span class="b-color-sq sq-soft" /> Software & SaaS Licensing</span>
                    <span class="b-val">${{ activeReferenceApp.costBreakdown.software.toLocaleString() }}</span>
                  </div>
                  <p class="b-detail-text">{{ activeReferenceApp.softwareDetail }}</p>
                </div>

                <div class="breakdown-item">
                  <div class="b-row-top">
                    <span class="b-label"><span class="b-color-sq sq-pers" /> Engineering & DevOps Labor</span>
                    <span class="b-val">${{ activeReferenceApp.costBreakdown.personnel.toLocaleString() }}</span>
                  </div>
                  <p class="b-detail-text">{{ activeReferenceApp.personnelDetail }}</p>
                </div>

                <div class="breakdown-item">
                  <div class="b-row-top">
                    <span class="b-label"><span class="b-color-sq sq-over" /> Shared IT Overhead</span>
                    <span class="b-val">${{ activeReferenceApp.costBreakdown.overhead.toLocaleString() }}</span>
                  </div>
                  <p class="b-detail-text">{{ activeReferenceApp.overheadDetail }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 5. Business Capability Attribution & Governance Matrix -->
      <section class="ref-capability-governance-section">
        <div class="container">
          <div class="subgraph-split-grid">
            <!-- Left: Business Capability Attribution -->
            <div class="capability-attribution-card">
              <span class="sub-card-tag">Value Realization · Strategic Mapping</span>
              <h3 class="sub-card-title">Proportional Capability Attribution</h3>
              <p class="card-desc-text">
                How this application's fully burdened TCO is apportioned across enterprise business capabilities based on transactional consumption telemetry.
              </p>

              <div class="capability-bars-stack">
                <div
                  v-for="cap in activeReferenceApp.capabilityAttribution"
                  :key="cap.name"
                  class="cap-bar-row"
                >
                  <div class="cap-header">
                    <span class="cap-name">{{ cap.name }}</span>
                    <span class="cap-amount">${{ cap.burdenedCost.toLocaleString() }} ({{ cap.percentage }}%)</span>
                  </div>
                  <div class="cap-progress-track">
                    <div
                      class="cap-progress-fill"
                      :style="{ width: `${cap.percentage}%` }"
                      :class="cap.tag"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Governance & Audit Trail -->
            <div class="governance-audit-card">
              <span class="sub-card-tag">Operational Guardrails · Auditability</span>
              <h3 class="sub-card-title">Enterprise Governance Scorecard</h3>
              <p class="card-desc-text">
                Continuous referential integrity checks and SLA tolerances verified against DuckDB general ledger records.
              </p>

              <div class="audit-matrix-grid">
                <div class="audit-cell">
                  <span class="audit-lbl">GL Reconciliation</span>
                  <span class="audit-val val-green">{{ activeReferenceApp.governanceAudit.reconciliationStatus }}</span>
                </div>

                <div class="audit-cell">
                  <span class="audit-lbl">SOX / SOC2 Compliance</span>
                  <span class="audit-val">{{ activeReferenceApp.governanceAudit.soxCompliance }}</span>
                </div>

                <div class="audit-cell">
                  <span class="audit-lbl">Disaster Recovery RPO</span>
                  <span class="audit-val">{{ activeReferenceApp.governanceAudit.drRecoveryRpo }}</span>
                </div>

                <div class="audit-cell">
                  <span class="audit-lbl">Disaster Recovery RTO</span>
                  <span class="audit-val">{{ activeReferenceApp.governanceAudit.drRecoveryRto }}</span>
                </div>

                <div class="audit-cell full-width-cell">
                  <span class="audit-lbl">Zero-Trust Workload Identity</span>
                  <span class="audit-val">{{ activeReferenceApp.governanceAudit.zeroTrustStatus }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 6. Interactive What-If Scenario Simulator -->
      <section id="whatif-simulator" class="ref-simulator-section">
        <div class="container">
          <div class="simulator-main-card">
            <!-- Injected Scenario Alert Banner -->
            <div v-if="currentlyAppliedScenario" class="applied-scenario-banner">
              <div class="banner-left">
                <span class="active-pulse-dot" />
                <div class="banner-texts">
                  <div class="banner-top-line">
                    <span class="active-badge">Simulating Scenario {{ currentlyAppliedScenario.letter }} ({{ currentlyAppliedScenario.id }})</span>
                    <strong class="active-scn-name">{{ currentlyAppliedScenario.name }}</strong>
                  </div>
                  <span class="active-scn-note">{{ currentlyAppliedScenario.simulationPreset.simNote }}</span>
                </div>
              </div>
              <button type="button" class="clear-scn-btn" @click="resetAppliedScenario">
                Reset Scenario ✕
              </button>
            </div>

            <div class="sim-header-split">
              <div>
                <span class="section-tag">Executive Sandbox</span>
                <h3 class="sim-title">Interactive What-If Scenario Simulator</h3>
                <p class="sim-desc">
                  Simulate transaction volume surges, FinOps rightsizing initiatives, or contractual license escalations in real time to assess projected unit economics.
                </p>
              </div>
              <div class="sim-savings-pill" v-if="simulatedMetrics.annualSavings > 0">
                <span class="savings-label">Projected Net Avoidable Savings</span>
                <span class="savings-amount">+${{ simulatedMetrics.annualSavings.toLocaleString() }} / yr</span>
              </div>
            </div>

            <div class="sim-body-grid">
              <!-- Sliders Column -->
              <div class="sim-controls-col">
                <!-- Slider 1: Volume Multiplier -->
                <div class="sim-slider-group">
                  <div class="slider-header-row">
                    <label class="slider-label">Transaction Volume Multiplier</label>
                    <span class="slider-value-badge">{{ simVolume.toFixed(2) }}x ({{ (simulatedMetrics.simulatedEvents / 1000000).toFixed(1) }}M txn/mo)</span>
                  </div>
                  <input
                    v-model.number="simVolume"
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.05"
                    class="custom-slider"
                  />
                  <div class="slider-ticks">
                    <span>0.5x (-50%)</span>
                    <span>1.0x (Baseline)</span>
                    <span>2.0x (+100%)</span>
                  </div>
                </div>

                <!-- Slider 2: Cloud Rightsizing Factor -->
                <div class="sim-slider-group">
                  <div class="slider-header-row">
                    <label class="slider-label">Cloud Rightsizing Factor</label>
                    <span class="slider-value-badge">{{ simRightsizing }}% compute reclaimed</span>
                  </div>
                  <input
                    v-model.number="simRightsizing"
                    type="range"
                    min="0"
                    max="40"
                    step="5"
                    class="custom-slider"
                  />
                  <div class="slider-ticks">
                    <span>0% (As-Is)</span>
                    <span>20% (Rightsized)</span>
                    <span>40% (Aggressive FinOps)</span>
                  </div>
                </div>

                <!-- Slider 3: License Cost Escalation -->
                <div class="sim-slider-group">
                  <div class="slider-header-row">
                    <label class="slider-label">License Contract Negotiation</label>
                    <span class="slider-value-badge">{{ simLicenseEscalation > 0 ? `+${simLicenseEscalation}%` : `${simLicenseEscalation}%` }} renewal delta</span>
                  </div>
                  <input
                    v-model.number="simLicenseEscalation"
                    type="range"
                    min="-20"
                    max="30"
                    step="5"
                    class="custom-slider"
                  />
                  <div class="slider-ticks">
                    <span>-20% (Renegotiated)</span>
                    <span>0% (Flat)</span>
                    <span>+30% (Escalation)</span>
                  </div>
                </div>
              </div>

              <!-- Recalculated Results Column -->
              <div class="sim-results-col">
                <div class="results-box">
                  <span class="res-eyebrow">Projected Annual TCO</span>
                  <div class="res-big-number">${{ (simulatedMetrics.totalSimTco / 1000000).toFixed(3) }}M</div>
                  <div class="res-delta-text" :class="simulatedMetrics.diffDollars <= 0 ? 'is-saving' : 'is-increase'">
                    {{ simulatedMetrics.diffDollars <= 0 ? `-$${Math.abs(simulatedMetrics.diffDollars).toLocaleString()} vs Baseline` : `+$${simulatedMetrics.diffDollars.toLocaleString()} vs Baseline` }}
                  </div>

                  <div class="recalculated-metrics-table">
                    <div class="rec-row">
                      <span>Projected Unit Cost / User</span>
                      <strong>${{ simulatedMetrics.simulatedCostPerUser }}</strong>
                    </div>
                    <div class="rec-row">
                      <span>Projected Cost / 1k Txn</span>
                      <strong>${{ simulatedMetrics.simulatedCostPer1k }}</strong>
                    </div>
                    <div class="rec-row">
                      <span>Infrastructure Spend</span>
                      <strong>${{ simulatedMetrics.simInfra.toLocaleString() }}</strong>
                    </div>
                    <div class="rec-row">
                      <span>Software License Spend</span>
                      <strong>${{ simulatedMetrics.simSoft.toLocaleString() }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 7. Enterprise Scenario Intelligence & Validation Matrix (Scenarios A through Y) -->
      <section class="ref-scenarios-section" id="scenarios-matrix">
        <div class="container">
          <div class="scenarios-matrix-header">
            <div class="header-eyebrow-row">
              <span class="section-tag">Scenario Intelligence · TVI Engine</span>
              <span class="pastel-chip chip-lavender">25 Controlled Scenarios (Basic to Advanced)</span>
              <span class="pastel-chip chip-mint">100% Empirically Validated</span>
            </div>
            <h2 class="section-title">Check Enterprise Scenarios (A through Y)</h2>
            <p class="section-desc">
              Explore and evaluate all 25 controlled enterprise scenarios designed into the TVI analytical truth engine. Each scenario targets a critical real-world pathology—from single points of failure and SaaS shelfware to J-Curve lag and Pareto MCDA frontiers. Check their empirical mathematical assertions or apply them directly to the Reference Application.
            </p>

            <!-- Tier Filter Switcher & Search Bar -->
            <div class="scenarios-filter-bar">
              <div class="tier-pills-row">
                <button
                  type="button"
                  class="tier-pill-btn"
                  :class="{ 'is-active': selectedScenarioTier === 'all' }"
                  @click="selectedScenarioTier = 'all'; playInteractChime(1.1)"
                >
                  All Scenarios (25)
                </button>
                <button
                  type="button"
                  class="tier-pill-btn"
                  :class="{ 'is-active': selectedScenarioTier === 'basic' }"
                  @click="selectedScenarioTier = 'basic'; playInteractChime(1.1)"
                >
                  Basic (A–H) · 8
                </button>
                <button
                  type="button"
                  class="tier-pill-btn"
                  :class="{ 'is-active': selectedScenarioTier === 'intermediate' }"
                  @click="selectedScenarioTier = 'intermediate'; playInteractChime(1.1)"
                >
                  Intermediate (I–Q) · 9
                </button>
                <button
                  type="button"
                  class="tier-pill-btn"
                  :class="{ 'is-active': selectedScenarioTier === 'advanced' }"
                  @click="selectedScenarioTier = 'advanced'; playInteractChime(1.1)"
                >
                  Advanced (R–Y) · 8
                </button>
              </div>

              <!-- Search Box -->
              <div class="scenario-search-box">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <input
                  v-model="scenarioSearchQuery"
                  type="text"
                  placeholder="Filter by scenario name, pathology, or entity (e.g. APP001, J-Curve, Shelfware)..."
                />
                <button
                  v-if="scenarioSearchQuery"
                  type="button"
                  class="clear-search-btn"
                  @click="scenarioSearchQuery = ''"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          <!-- 25 Scenario Cards Grid -->
          <div class="scenarios-grid">
            <div
              v-for="scn in filteredScenarios"
              :key="scn.id"
              class="scenario-card"
              :class="`tier-${scn.tier}`"
              @click="openScenarioModal(scn)"
              @mouseenter="setCursor(`CHECK SCN ${scn.letter}`, 'highlight')"
              @mouseleave="resetCursor"
            >
              <div class="scn-card-top">
                <div class="scn-id-badge">
                  <span class="scn-letter">{{ scn.letter }}</span>
                  <span class="scn-id-text">{{ scn.id }}</span>
                </div>
                <div class="scn-tier-pills">
                  <span
                    class="pastel-chip"
                    :class="scn.tier === 'basic' ? 'chip-mint' : scn.tier === 'intermediate' ? 'chip-lavender' : 'chip-peach'"
                  >
                    {{ scn.tier }}
                  </span>
                  <span class="pass-badge">✓ PASS</span>
                </div>
              </div>

              <h4 class="scn-title">{{ scn.name }}</h4>
              <span class="scn-entity-tag">Target: {{ scn.targetEntity }}</span>
              <p class="scn-desc-snippet">{{ scn.description }}</p>

              <div class="scn-card-footer">
                <span class="scn-cat-text">{{ scn.category }}</span>
                <span class="scn-inspect-link">Check Scenario ↗</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Scenario Inspection & Evaluation Modal -->
      <transition name="modal-fade">
        <div v-if="activeInspectedScenario" class="scenario-modal-overlay" @click.self="closeScenarioModal">
          <div class="scenario-modal-card">
            <div class="modal-header-row">
              <div class="modal-title-group">
                <div class="modal-badges-row">
                  <span class="modal-letter-tag">Scenario {{ activeInspectedScenario.letter }}</span>
                  <span class="modal-id-pill">{{ activeInspectedScenario.id }}</span>
                  <span class="pastel-chip" :class="activeInspectedScenario.tier === 'basic' ? 'chip-mint' : activeInspectedScenario.tier === 'intermediate' ? 'chip-lavender' : 'chip-peach'">
                    {{ activeInspectedScenario.tier }} tier
                  </span>
                  <span class="pass-badge">✓ 100% EMPIRICALLY VERIFIED</span>
                </div>
                <h3 class="modal-scenario-name">{{ activeInspectedScenario.name }}</h3>
                <span class="modal-entity-sub">Target Enterprise Asset: {{ activeInspectedScenario.targetEntity }} · Category: {{ activeInspectedScenario.category }}</span>
              </div>
              <button type="button" class="modal-close-icon-btn" @click="closeScenarioModal">✕</button>
            </div>

            <div class="modal-body-scroll">
              <!-- Section A: Pathology & Executive Hypothesis -->
              <div class="modal-section-block">
                <span class="block-label">1. Architectural Pathology & Executive Hypothesis</span>
                <p class="block-text">{{ activeInspectedScenario.hypothesis }}</p>
                <p class="block-subtext">{{ activeInspectedScenario.description }}</p>
              </div>

              <!-- Section B: Key Empirical Parameters -->
              <div class="modal-section-block">
                <span class="block-label">2. Scenario Configuration & Telemetry Parameters</span>
                <div class="scenario-metrics-grid">
                  <div
                    v-for="(val, key) in activeInspectedScenario.metrics"
                    :key="key"
                    class="scn-metric-cell"
                  >
                    <span class="scn-m-key">{{ key }}</span>
                    <strong class="scn-m-val">{{ val }}</strong>
                  </div>
                </div>
              </div>

              <!-- Section C: Empirical Assertion Verified in DuckDB / NetworkX -->
              <div class="modal-section-block">
                <span class="block-label">3. Automated Test Suite Assertion (tests/test_scenarios.py)</span>
                <div class="code-assertion-box">
                  <code>{{ activeInspectedScenario.mathematicalAssertion }}</code>
                  <span class="code-status-pill">Referential Integrity: PASS</span>
                </div>
              </div>
            </div>

            <!-- Modal Action Footer -->
            <div class="modal-footer-row">
              <div class="modal-footer-info">
                <span>Suggested Archetype: <strong>{{ activeInspectedScenario.suggestedAppId === 'REF-001' ? 'Core Banking Ledger' : activeInspectedScenario.suggestedAppId === 'REF-002' ? 'API Mesh Gateway' : 'Legacy CRM Zombie' }}</strong></span>
              </div>
              <div class="modal-footer-btns">
                <button
                  type="button"
                  class="pill-btn-light"
                  @click="closeScenarioModal"
                >
                  Close
                </button>
                <button
                  type="button"
                  class="pill-btn-dark"
                  @click="applyScenarioToSimulator(activeInspectedScenario)"
                  @mouseenter="setCursor('APPLY SCN', 'highlight')"
                  @mouseleave="resetCursor"
                >
                  <span>Apply to Reference App Simulator ⚡</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </main>

    <FooterSection />
  </div>
</template>

<style scoped>
.ref-app-page {
  background-color: var(--bg-canvas);
  min-height: 100vh;
  padding-top: 7rem;
  width: 100%;
}

.ref-main-container {
  display: flex;
  flex-direction: column;
  gap: 3.5rem;
  padding-bottom: 6rem;
}

/* 1. Page Header */
.ref-hero-header {
  position: relative;
}

.eyebrow-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.ref-title {
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 3.4vw, 2.75rem);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 1rem;
  max-width: 24ch;
}

.ref-subtitle {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.6;
  color: #4f5361;
  max-width: 75ch;
  margin-bottom: 2.5rem;
}

/* Archetype Tabs */
.archetype-tabs-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.archetype-tab-btn {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-card);
  padding: 1.35rem 1.6rem;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 4px 18px -4px rgba(0, 0, 0, 0.04);
}

.archetype-tab-btn:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 0, 0, 0.2);
  box-shadow: var(--glass-card-hover-shadow);
}

.archetype-tab-btn.is-active {
  background: #14151a;
  border-color: #14151a;
  color: #ffffff;
  box-shadow: 0 12px 30px -8px rgba(20, 21, 26, 0.35);
}

.tab-btn-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.tab-code {
  font-family: var(--font-sans);
  font-size: 0.8rem;
  font-weight: 700;
  color: #8c909e;
}

.archetype-tab-btn.is-active .tab-code {
  color: #a1a5b4;
}

.tab-tag {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.55rem;
  border-radius: var(--radius-pill);
}

.tag-mint {
  background: var(--pastel-mint-soft);
  color: #065f46;
}

.tag-lavender {
  background: var(--pastel-lavender-soft);
  color: #5b21b6;
}

.tag-rose {
  background: var(--pastel-rose-soft);
  color: #9f1239;
}

.tab-name {
  display: block;
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.85rem;
}

.archetype-tab-btn.is-active .tab-name {
  color: #ffffff;
}

.tab-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.82rem;
  font-weight: 600;
  color: #555966;
}

.archetype-tab-btn.is-active .tab-footer {
  color: #d1d5db;
}

/* 2. Overview Glass Card */
.overview-glass-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-container);
  padding: 2.2rem 2.8rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2.5rem;
  box-shadow: 0 10px 32px -8px rgba(0, 0, 0, 0.05);
  will-change: transform, opacity;
}

.code-and-tier {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 0.75rem;
}

.app-code-pill {
  font-family: var(--font-sans);
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  background: #14151a;
  color: #ffffff;
  border-radius: var(--radius-pill);
}

.app-tier-text {
  font-size: 0.88rem;
  font-weight: 600;
  color: #555966;
}

.app-health-badge {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-pill);
  background: var(--pastel-mint-soft);
  color: #065f46;
}

.active-app-heading {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 500;
  line-height: 1.25;
  color: #121316;
  margin-bottom: 0.5rem;
}

.active-app-desc {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #4f5361;
  max-width: 70ch;
}

.overview-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 240px;
}

/* 3. Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.metric-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-card);
  padding: 1.8rem 1.6rem;
  box-shadow: 0 6px 20px -6px rgba(0, 0, 0, 0.04);
  will-change: transform, opacity;
}

.metric-label {
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8c909e;
  display: block;
  margin-bottom: 0.65rem;
}

.metric-number-row {
  display: flex;
  align-items: baseline;
  gap: 0.45rem;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 2.4vw, 2.3rem);
  font-weight: 700;
  color: #121316;
}

.metric-unit {
  font-size: 0.88rem;
  font-weight: 600;
  color: #6b7280;
}

.metric-caption {
  font-size: 0.82rem;
  color: #6b7280;
  display: block;
}

/* 4. Subgraph & Cost Stack Split */
.subgraph-split-grid {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 1.8rem;
}

.subgraph-3d-card,
.cost-stack-card,
.capability-attribution-card,
.governance-audit-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-container);
  padding: 2.2rem;
  box-shadow: 0 10px 30px -8px rgba(0, 0, 0, 0.04);
}

.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.4rem;
}

.sub-card-tag {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #8c909e;
  display: block;
  margin-bottom: 0.35rem;
}

.sub-card-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.25;
  color: #121316;
}

.graph-ctrl-btn {
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-pill);
  background: #f0f1f4;
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.graph-ctrl-btn:hover {
  background: #e2e4e9;
}

/* Subgraph Canvas Viewport */
.subgraph-canvas-viewport {
  position: relative;
  width: 100%;
  height: 380px;
  background: radial-gradient(circle at 50% 50%, #fafafc 0%, #f0f1f5 100%);
  border-radius: var(--radius-card);
  overflow: hidden;
  cursor: grab;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.subgraph-canvas-viewport:active {
  cursor: grabbing;
}

.graph-legend-overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  pointer-events: none;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  padding: 0.5rem 0.85rem;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.74rem;
  font-weight: 600;
  color: #374151;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-core { background: #121318; }
.dot-cap { background: #a7f3d0; }
.dot-infra { background: #fed7aa; }
.dot-consumer { background: #93c5fd; }

.drag-hint-pill {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #6b7280;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-pill);
  pointer-events: none;
}

.subgraph-card-footer {
  margin-top: 1.25rem;
}

.node-chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* Cost Segmented Bar */
.cost-segmented-bar {
  display: flex;
  height: 14px;
  border-radius: var(--radius-pill);
  overflow: hidden;
  margin-bottom: 1.6rem;
  background: #e5e7eb;
}

.seg-infra { background-color: var(--pastel-peach); }
.seg-soft { background-color: var(--pastel-lavender); }
.seg-pers { background-color: var(--pastel-mint); }
.seg-over { background-color: var(--pastel-sky); }

.cost-breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.breakdown-item {
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.breakdown-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.b-row-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.b-label {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.92rem;
  font-weight: 700;
  color: #121316;
}

.b-color-sq {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.sq-infra { background: var(--pastel-peach); }
.sq-soft { background: var(--pastel-lavender); }
.sq-pers { background: var(--pastel-mint); }
.sq-over { background: var(--pastel-sky); }

.b-val {
  font-family: var(--font-sans);
  font-size: 0.95rem;
  font-weight: 700;
  color: #121316;
}

.b-detail-text {
  font-size: 0.84rem;
  line-height: 1.5;
  color: #555966;
  padding-left: 1.2rem;
}

/* 5. Capability Attribution & Governance */
.card-desc-text {
  font-size: 0.92rem;
  line-height: 1.6;
  color: #555966;
  margin-bottom: 1.8rem;
}

.capability-bars-stack {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.cap-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.45rem;
  font-size: 0.92rem;
  font-weight: 600;
  color: #121316;
}

.cap-progress-track {
  width: 100%;
  height: 10px;
  background: #f0f1f4;
  border-radius: var(--radius-pill);
  overflow: hidden;
}

.cap-progress-fill {
  height: 100%;
  border-radius: var(--radius-pill);
  transition: width 0.6s ease;
}

/* Audit Matrix Grid */
.audit-matrix-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
}

.audit-cell {
  background: #f8f9fb;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 14px;
  padding: 1.1rem 1.2rem;
}

.full-width-cell {
  grid-column: span 2;
}

.audit-lbl {
  font-size: 0.78rem;
  font-weight: 600;
  color: #8c909e;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.35rem;
}

.audit-val {
  font-size: 0.95rem;
  font-weight: 700;
  color: #121316;
}

.val-green {
  color: #059669;
}

/* 6. Interactive Simulator */
.simulator-main-card {
  background: #14151a;
  border-radius: var(--radius-container);
  padding: 3rem;
  color: #ffffff;
  box-shadow: 0 20px 48px -12px rgba(20, 21, 26, 0.3);
  position: relative;
  will-change: transform, opacity;
}

/* Applied Scenario Banner */
.applied-scenario-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1rem 1.6rem;
  background: rgba(167, 243, 208, 0.12);
  border: 1px solid rgba(167, 243, 208, 0.4);
  border-radius: 16px;
  margin-bottom: 2rem;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.active-pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--pastel-mint);
  box-shadow: 0 0 12px var(--pastel-mint);
  animation: pulseDot 2s infinite;
}

@keyframes pulseDot {
  0% { transform: scale(0.85); opacity: 0.6; }
  50% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(0.85); opacity: 0.6; }
}

.banner-texts {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.banner-top-line {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.active-badge {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--pastel-mint);
}

.active-scn-name {
  font-size: 1rem;
  color: #ffffff;
}

.active-scn-note {
  font-size: 0.82rem;
  color: #d1d5db;
}

.clear-scn-btn {
  padding: 0.4rem 0.9rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.clear-scn-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.sim-header-split {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 2.5rem;
}

.sim-title {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 2.5vw, 2rem);
  font-weight: 500;
  line-height: 1.25;
  color: #ffffff;
  margin-top: 0.5rem;
  margin-bottom: 0.65rem;
  max-width: 24ch;
}

.sim-desc {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #9ca3af;
  font-weight: 400;
  max-width: 65ch;
}

.sim-savings-pill {
  background: rgba(167, 243, 208, 0.15);
  border: 1px solid rgba(167, 243, 208, 0.4);
  padding: 0.85rem 1.4rem;
  border-radius: 16px;
  text-align: right;
  min-width: 220px;
}

.savings-label {
  display: block;
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #a7f3d0;
  margin-bottom: 0.25rem;
}

.savings-amount {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 700;
  color: #ffffff;
}

.sim-body-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 3rem;
}

.sim-controls-col {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sim-slider-group {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.slider-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.slider-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #e5e7eb;
}

.slider-value-badge {
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.custom-slider {
  width: 100%;
  accent-color: var(--pastel-mint);
  cursor: pointer;
  height: 6px;
  border-radius: 3px;
}

.slider-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.74rem;
  color: #6b7280;
}

/* Results Box */
.results-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-card);
  padding: 2rem;
}

.res-eyebrow {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #9ca3af;
  display: block;
  margin-bottom: 0.4rem;
}

.res-big-number {
  font-family: var(--font-display);
  font-size: 2.8rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
  margin-bottom: 0.4rem;
}

.res-delta-text {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 1.8rem;
}

.res-delta-text.is-saving {
  color: #34d399;
}

.res-delta-text.is-increase {
  color: #f87171;
}

.recalculated-metrics-table {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 1.2rem;
}

.rec-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.88rem;
  color: #d1d5db;
}

.rec-row strong {
  color: #ffffff;
}

/* 7. Enterprise Scenario Intelligence Matrix */
.ref-scenarios-section {
  padding: 2rem 0;
}

.scenarios-matrix-header {
  margin-bottom: 2.8rem;
}

.header-eyebrow-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 0.8rem;
}

.scenarios-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.tier-pills-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.tier-pill-btn {
  padding: 0.55rem 1.15rem;
  border-radius: var(--radius-pill);
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 0.82rem;
  font-weight: 600;
  color: #555966;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.03);
}

.tier-pill-btn:hover {
  background: #f0f1f4;
  color: #121316;
}

.tier-pill-btn.is-active {
  background: #14151a;
  border-color: #14151a;
  color: #ffffff;
}

.scenario-search-box {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-pill);
  padding: 0.55rem 1.2rem;
  min-width: 320px;
  flex: 1;
  max-width: 480px;
  color: #6b7280;
}

.scenario-search-box input {
  border: none;
  background: none;
  outline: none;
  font-size: 0.84rem;
  width: 100%;
  color: #121316;
}

.clear-search-btn {
  background: none;
  border: none;
  font-size: 0.75rem;
  color: #9ca3af;
  cursor: pointer;
}

/* Scenarios Grid */
.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.scenario-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-card);
  padding: 1.6rem 1.8rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 240px;
  cursor: pointer;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
  will-change: transform, opacity;
  box-shadow: 0 4px 18px -4px rgba(0, 0, 0, 0.03);
}

.scenario-card:hover {
  border-color: rgba(0, 0, 0, 0.22);
  box-shadow: var(--glass-card-hover-shadow);
}

.scn-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.85rem;
}

.scn-id-badge {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.scn-letter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #14151a;
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 700;
}

.scn-id-text {
  font-size: 0.8rem;
  font-weight: 700;
  color: #8c909e;
}

.scn-tier-pills {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.pass-badge {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #059669;
  background: rgba(167, 243, 208, 0.3);
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-pill);
}

.scn-title {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.25;
  color: #121316;
  margin-bottom: 0.35rem;
}

.scn-entity-tag {
  font-size: 0.78rem;
  font-weight: 600;
  color: #8c909e;
  margin-bottom: 0.65rem;
  display: block;
}

.scn-desc-snippet {
  font-size: 0.875rem;
  line-height: 1.55;
  color: #555966;
  font-weight: 400;
  margin-bottom: 1.2rem;
}

.scn-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.85rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.scn-cat-text {
  font-size: 0.76rem;
  font-weight: 600;
  color: #8c909e;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.scn-inspect-link {
  font-size: 0.8rem;
  font-weight: 700;
  color: #121316;
}

/* Scenario Inspection Modal */
.scenario-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(18, 19, 22, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.scenario-modal-card {
  background: #ffffff;
  border-radius: var(--radius-container);
  width: 100%;
  max-width: 860px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 24px 60px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.modal-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 2.2rem 2.6rem 1.6rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.07);
}

.modal-title-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.modal-badges-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.modal-letter-tag {
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-pill);
  background: #14151a;
  color: #ffffff;
}

.modal-id-pill {
  font-size: 0.8rem;
  font-weight: 700;
  color: #8c909e;
}

.modal-scenario-name {
  font-family: var(--font-display);
  font-size: 1.7rem;
  font-weight: 700;
  color: #121316;
}

.modal-entity-sub {
  font-size: 0.88rem;
  font-weight: 600;
  color: #6b7280;
}

.modal-close-icon-btn {
  background: #f0f1f4;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.modal-close-icon-btn:hover {
  background: #e2e4e9;
  transform: rotate(90deg);
}

.modal-body-scroll {
  padding: 2rem 2.6rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.modal-section-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.block-label {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8c909e;
  margin-bottom: 0.2rem;
}

.block-text {
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.5;
  color: #121316;
}

.block-subtext {
  font-size: 0.92rem;
  line-height: 1.6;
  color: #555966;
}

.scenario-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-top: 0.4rem;
}

.scn-metric-cell {
  background: #f8f9fb;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 0.9rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.scn-m-key {
  font-size: 0.72rem;
  font-weight: 600;
  color: #8c909e;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.scn-m-val {
  font-size: 0.95rem;
  color: #121316;
}

.code-assertion-box {
  background: #14151a;
  border-radius: 12px;
  padding: 1.1rem 1.4rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.code-assertion-box code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.84rem;
  color: #a7f3d0;
  word-break: break-all;
}

.code-status-pill {
  font-size: 0.72rem;
  font-weight: 700;
  color: #34d399;
  background: rgba(52, 211, 153, 0.2);
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-pill);
  white-space: nowrap;
}

.modal-footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.4rem 2.6rem;
  border-top: 1px solid rgba(0, 0, 0, 0.07);
  background: #fafafc;
}

.modal-footer-info {
  font-size: 0.88rem;
  color: #555966;
}

.modal-footer-info strong {
  color: #121316;
}

.modal-footer-btns {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

/* Modal Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Responsive Media Queries */
@media (max-width: 1024px) {
  .archetype-tabs-container,
  .metrics-grid,
  .scenarios-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .subgraph-split-grid,
  .sim-body-grid {
    grid-template-columns: 1fr;
  }

  .overview-glass-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .scenario-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .archetype-tabs-container,
  .metrics-grid,
  .scenarios-grid {
    grid-template-columns: 1fr;
  }

  .audit-matrix-grid {
    grid-template-columns: 1fr;
  }

  .full-width-cell {
    grid-column: span 1;
  }

  .applied-scenario-banner {
    flex-direction: column;
    align-items: flex-start;
  }

  .scenario-metrics-grid {
    grid-template-columns: 1fr;
  }

  .code-assertion-box {
    flex-direction: column;
    align-items: flex-start;
  }

  .modal-footer-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
