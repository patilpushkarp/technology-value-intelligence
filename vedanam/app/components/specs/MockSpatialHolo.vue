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
const focusedStepId = ref<number>(1)
const activePhaseIndex = ref<number>(0)
const isCoreShattered = ref<boolean>(false)
const showDetailModal = ref<boolean>(false)
const copiedCode = ref<boolean>(false)

const currentStep = computed<TechSpecStep>(() => {
  return steps.find(s => s.id === focusedStepId.value) || steps[0]
})

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let coreMesh: THREE.Mesh
let coreWireMesh: THREE.Mesh
let coreShards: THREE.Mesh[] = []
let placardsGroup: THREE.Group
let placardMeshes: { id: number; group: THREE.Group; basePos: THREE.Vector3; angle: number; radius: number }[] = []
let laserReticle: THREE.Mesh

// Raycasting
const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2(-999, -999)
let hoveredStepId: number | null = null

// Scrub to phase
const scrubToPhase = (phaseIdx: number) => {
  activePhaseIndex.value = phaseIdx
  const targetPhaseNum = phaseIdx + 1
  const firstStep = steps.find(s => s.phaseNumber === targetPhaseNum)
  if (firstStep) {
    selectStep(firstStep.id)
  }
  playInteractChime(1.1 + phaseIdx * 0.1)

  // Smoothly rotate the placards group in 3D to align with this phase
  if (placardsGroup) {
    const targetRotY = -(phaseIdx / 6) * Math.PI * 2
    gsap.to(placardsGroup.rotation, {
      y: targetRotY,
      duration: 1.2,
      ease: 'power3.out'
    })
  }
}

const selectStep = (stepId: number, openModal = false) => {
  focusedStepId.value = stepId
  playInteractChime(1.2 + (stepId % 6) * 0.08)

  if (openModal) {
    showDetailModal.value = true
  }

  // Elevate selected placard in 3D
  placardMeshes.forEach(pm => {
    if (pm.id === stepId) {
      gsap.to(pm.group.scale, { x: 1.35, y: 1.35, z: 1.35, duration: 0.5, ease: 'back.out(1.5)' })
      gsap.to(pm.group.position, {
        y: pm.basePos.y + 0.8,
        duration: 0.5,
        ease: 'power2.out'
      })
    } else {
      gsap.to(pm.group.scale, { x: 1.0, y: 1.0, z: 1.0, duration: 0.4 })
      gsap.to(pm.group.position, {
        y: pm.basePos.y,
        duration: 0.4
      })
    }
  })
}

const toggleShatterCore = () => {
  isCoreShattered.value = !isCoreShattered.value
  playInteractChime(isCoreShattered.value ? 1.6 : 0.9)

  if (isCoreShattered.value) {
    // Hide solid core, explode shards outward
    gsap.to(coreMesh.scale, { x: 0, y: 0, z: 0, duration: 0.4 })
    coreShards.forEach((shard, idx) => {
      const dir = shard.position.clone().normalize()
      const dist = 3.5 + Math.random() * 2.0
      gsap.to(shard.position, {
        x: dir.x * dist,
        y: dir.y * dist,
        z: dir.z * dist,
        duration: 1.2,
        ease: 'power3.out'
      })
      gsap.to(shard.rotation, {
        x: Math.random() * 6,
        y: Math.random() * 6,
        duration: 1.5
      })
    })
  } else {
    // Reassemble core
    coreShards.forEach(shard => {
      gsap.to(shard.position, {
        x: (Math.random() - 0.5) * 0.8,
        y: (Math.random() - 0.5) * 0.8,
        z: (Math.random() - 0.5) * 0.8,
        duration: 0.9,
        ease: 'power3.inOut'
      })
    })
    gsap.to(coreMesh.scale, { x: 1, y: 1, z: 1, duration: 0.6, delay: 0.3 })
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

const onMouseMove = (event: MouseEvent) => {
  if (!canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  // Update laser reticle in 3D plane
  if (laserReticle && camera) {
    const vector = new THREE.Vector3(mouse.x, mouse.y, 0.5).unproject(camera)
    const dir = vector.sub(camera.position).normalize()
    const distance = 10
    const pos = camera.position.clone().add(dir.multiplyScalar(distance))
    laserReticle.position.copy(pos)
  }
}

const onCanvasClick = () => {
  if (hoveredStepId !== null) {
    selectStep(hoveredStepId, true)
  }
}

onMounted(() => {
  if (!process.client || !canvasRef.value) return

  const container = canvasRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x05060a, 0.03)

  camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100)
  camera.position.set(0, 2.5, 13)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.3
  container.appendChild(renderer.domElement)

  // Subtle ambient illumination
  const ambient = new THREE.AmbientLight(0xffffff, 1.2)
  scene.add(ambient)

  const lightCyan = new THREE.DirectionalLight(0x38bdf8, 2.5)
  lightCyan.position.set(10, 15, 10)
  scene.add(lightCyan)

  const lightLavender = new THREE.DirectionalLight(0xc4b5fd, 2.0)
  lightLavender.position.set(-10, -5, 5)
  scene.add(lightLavender)

  // 1. Central Refractive Crystal Diamond Core (DuckDB Truth)
  const coreGeom = new THREE.OctahedronGeometry(1.6, 0)
  const coreMat = new THREE.MeshPhysicalMaterial({
    color: 0x38bdf8,
    emissive: 0x0284c7,
    emissiveIntensity: 0.6,
    roughness: 0.1,
    metalness: 0.1,
    transmission: 0.85,
    ior: 1.5,
    transparent: true,
    opacity: 0.9
  })
  coreMesh = new THREE.Mesh(coreGeom, coreMat)
  scene.add(coreMesh)

  const coreWireGeom = new THREE.OctahedronGeometry(1.62, 0)
  const coreWireMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    transparent: true,
    opacity: 0.5
  })
  coreWireMesh = new THREE.Mesh(coreWireGeom, coreWireMat)
  coreMesh.add(coreWireMesh)

  // Core Shatter Shards
  const shardCount = 36
  for (let s = 0; s < shardCount; s++) {
    const shardGeom = new THREE.TetrahedronGeometry(0.35 + Math.random() * 0.35, 0)
    const shardMat = new THREE.MeshStandardMaterial({
      color: s % 2 === 0 ? 0x38bdf8 : 0xa7f3d0,
      emissive: 0x0369a1,
      roughness: 0.2,
      metalness: 0.8
    })
    const shardMesh = new THREE.Mesh(shardGeom, shardMat)
    shardMesh.position.set(
      (Math.random() - 0.5) * 1.0,
      (Math.random() - 0.5) * 1.0,
      (Math.random() - 0.5) * 1.0
    )
    scene.add(shardMesh)
    coreShards.push(shardMesh)
  }

  // 2. 12 Volumetric Spatial Placards in 3D
  placardsGroup = new THREE.Group()
  scene.add(placardsGroup)

  const orbitRadius = 6.8
  const phaseColors = [0x10b981, 0x8b5cf6, 0xf97316, 0x0284c7, 0xf43f5e, 0xa855f7]

  steps.forEach((st, idx) => {
    const angle = (idx / steps.length) * Math.PI * 2
    const x = Math.cos(angle) * orbitRadius
    const z = Math.sin(angle) * orbitRadius
    const y = Math.sin(angle * 2) * 0.9

    const placardGroup = new THREE.Group()
    placardGroup.position.set(x, y, z)
    placardGroup.lookAt(0, y * 0.5, 0)
    placardGroup.userData = { stepId: st.id }

    // Glass placard slab
    const slabGeom = new THREE.BoxGeometry(1.5, 0.9, 0.06)
    const slabMat = new THREE.MeshStandardMaterial({
      color: 0x141824,
      emissive: phaseColors[st.phaseNumber - 1] || 0x38bdf8,
      emissiveIntensity: 0.4,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.85
    })
    const slabMesh = new THREE.Mesh(slabGeom, slabMat)
    slabMesh.userData = { stepId: st.id }
    placardGroup.add(slabMesh)

    // Glowing border frame
    const edgeGeom = new THREE.BoxGeometry(1.54, 0.94, 0.04)
    const edgeMat = new THREE.MeshBasicMaterial({
      color: phaseColors[st.phaseNumber - 1] || 0x38bdf8,
      wireframe: true
    })
    const edgeMesh = new THREE.Mesh(edgeGeom, edgeMat)
    placardGroup.add(edgeMesh)

    // Holographic top beacon dot
    const dotGeom = new THREE.SphereGeometry(0.08, 12, 12)
    const dotMat = new THREE.MeshBasicMaterial({ color: 0xffffff })
    const dotMesh = new THREE.Mesh(dotGeom, dotMat)
    dotMesh.position.set(0, 0.55, 0)
    placardGroup.add(dotMesh)

    placardsGroup.add(placardGroup)
    placardMeshes.push({
      id: st.id,
      group: placardGroup,
      basePos: new THREE.Vector3(x, y, z),
      angle,
      radius: orbitRadius
    })
  })

  // 3. 3D Spatial Laser Reticle
  const reticleGeom = new THREE.RingGeometry(0.12, 0.16, 24)
  const reticleMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.8
  })
  laserReticle = new THREE.Mesh(reticleGeom, reticleMat)
  scene.add(laserReticle)

  // Animation Loop
  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const elapsedTime = clock.getElapsedTime()

    // Rotate core
    if (coreMesh && !isCoreShattered.value) {
      coreMesh.rotation.y = elapsedTime * 0.4
      coreMesh.rotation.x = Math.sin(elapsedTime * 0.3) * 0.2
    }

    // Placards subtle floating drift
    placardMeshes.forEach((pm, i) => {
      pm.group.position.y = pm.basePos.y + Math.sin(elapsedTime * 1.5 + i) * 0.12
    })

    // Reticle pulse
    if (laserReticle) {
      const s = 1 + Math.sin(elapsedTime * 6) * 0.15
      laserReticle.scale.set(s, s, s)
    }

    // Raycast hover detection
    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObjects(placardsGroup.children, true)
    if (intersects.length > 0) {
      let hit: THREE.Object3D | null = intersects[0].object
      while (hit && !hit.userData.stepId && hit.parent) {
        hit = hit.parent
      }
      if (hit && hit.userData.stepId) {
        hoveredStepId = hit.userData.stepId
        setCursor(`TOUCH STEP 0${hoveredStepId}`, 'highlight')
      }
    } else {
      hoveredStepId = null
      resetCursor()
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
  <div class="spatial-holo-experience">
    <!-- 3D Spatial Canvas -->
    <div
      ref="canvasRef"
      class="spatial-canvas"
      @mousemove="onMouseMove"
      @click="onCanvasClick"
    />

    <!-- Ambient Spatial Header (VisionOS Top Capsule) -->
    <header class="vision-top-capsule">
      <div class="capsule-left">
        <span class="vision-badge">VisionOS Spatial Hologram</span>
        <h2 class="vision-title">Spatial Execution Twin</h2>
      </div>
      <div class="capsule-stats">
        <div class="v-stat">
          <span class="v-k">FOCUSED NODE</span>
          <strong class="v-v text-sky">{{ currentStep.code }}</strong>
        </div>
        <div class="v-stat">
          <span class="v-k">QUERY SLA</span>
          <strong class="v-v text-mint">{{ currentStep.latencySla }}</strong>
        </div>
        <div class="v-stat">
          <span class="v-k">GL LOSS</span>
          <strong class="v-v text-lavender">0.00% Drift</strong>
        </div>
      </div>
    </header>

    <!-- Floating 3D Node Quick-Peek Card (Always pinned in spatial periphery) -->
    <div class="spatial-focus-billboard" @click="showDetailModal = true">
      <div class="billboard-top">
        <span class="step-pill">{{ currentStep.code }}</span>
        <span class="category-pill">{{ currentStep.category }}</span>
        <span class="touch-hint">Tap to Expand ↗</span>
      </div>
      <h3 class="billboard-name">{{ currentStep.title }}</h3>
      <p class="billboard-summary">{{ currentStep.summary }}</p>
      <div class="billboard-foot">
        <span class="foot-param">Module: <code class="mono">{{ currentStep.pythonModule }}</code></span>
        <span class="foot-mem">{{ currentStep.memoryBudget }}</span>
      </div>
    </div>

    <!-- VisionOS Bottom Floating Island Controller -->
    <nav class="vision-island-dock">
      <!-- 6-Phase Horizon Scrub Arc -->
      <div class="phase-horizon-scrub">
        <button
          v-for="(p, idx) in phases"
          :key="p.number"
          type="button"
          class="phase-scrub-pip"
          :class="{ active: activePhaseIndex === idx }"
          @click="scrubToPhase(idx)"
          @mouseenter="setCursor(`SCRUB PHASE 0${p.number}`, 'highlight')"
          @mouseleave="resetCursor"
        >
          <span class="pip-num">0{{ p.number }}</span>
          <span class="pip-label">{{ p.shortName }}</span>
        </button>
      </div>

      <!-- Action Toggles -->
      <div class="dock-actions-row">
        <button
          type="button"
          class="island-action-btn"
          :class="{ active: isCoreShattered }"
          @click="toggleShatterCore"
          @mouseenter="setCursor('SHATTER HOLOGRAPHIC CORE', 'default')"
          @mouseleave="resetCursor"
        >
          <span class="btn-icon">💠</span>
          <span>{{ isCoreShattered ? 'Assemble Core' : 'Shatter Hologram' }}</span>
        </button>

        <button
          type="button"
          class="island-action-btn"
          @click="showDetailModal = true"
          @mouseenter="setCursor('OPEN SPATIAL DOSSIER', 'highlight')"
          @mouseleave="resetCursor"
        >
          <span class="btn-icon">📑</span>
          <span>Open Spatial Dossier</span>
        </button>
      </div>
    </nav>

    <!-- Full Spatial Dossier Modal (Floating Glass Card with Depth) -->
    <transition name="vision-pop">
      <div v-if="showDetailModal" class="spatial-modal-backdrop" @click.self="showDetailModal = false">
        <div class="vision-modal-glass">
          <div class="modal-glass-header">
            <div class="modal-badge-group">
              <span class="glass-chip chip-sky">{{ currentStep.code }}</span>
              <span class="glass-chip chip-mint">{{ currentStep.category }}</span>
              <span class="glass-chip-mono">{{ currentStep.latencySla }} SLA</span>
            </div>
            <button type="button" class="close-glass-btn" @click="showDetailModal = false">✕</button>
          </div>

          <h2 class="modal-step-title">{{ currentStep.title }}</h2>
          <p class="modal-step-lead">{{ currentStep.summary }}</p>

          <div class="modal-spatial-body">
            <!-- Left: Execution Mechanics & Formula -->
            <div class="body-col">
              <span class="col-kicker">Execution Mechanics</span>
              <ul class="spatial-mech-list">
                <li v-for="(item, i) in currentStep.executionDetails" :key="i" class="mech-item">
                  <span class="mech-dot">{{ i + 1 }}</span>
                  <span>{{ item }}</span>
                </li>
              </ul>

              <div class="spatial-formula-wrap">
                <span class="col-kicker">Mathematical Formulation</span>
                <MathFormula
                  :latex="currentStep.formulaLatex"
                  :formula-html="currentStep.formulaHtml"
                  :name="currentStep.formulaName"
                />
                <p class="formula-expl">{{ currentStep.formulaExplanation }}</p>
              </div>
            </div>

            <!-- Right: Code Lineage & Parameter Specifications -->
            <div class="body-col">
              <span class="col-kicker">Parameter Specifications</span>
              <div class="spatial-params-grid">
                <div v-for="param in currentStep.keyParameters" :key="param.name" class="param-box">
                  <span class="p-name">{{ param.name }}</span>
                  <strong class="p-v">{{ param.value }}</strong>
                  <span class="p-d">{{ param.desc }}</span>
                </div>
              </div>

              <div class="spatial-terminal-window">
                <div class="term-title-bar">
                  <span>Python Source Lineage: {{ currentStep.pythonModule }}</span>
                  <button type="button" class="copy-btn" @click="copyCode">
                    {{ copiedCode ? 'Copied ✓' : 'Copy' }}
                  </button>
                </div>
                <pre class="term-pre"><code>{{ currentStep.codeSnippet }}</code></pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.spatial-holo-experience {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: radial-gradient(circle at 50% 40%, #0d111d 0%, #05060a 100%);
  color: #ffffff;
  overflow: hidden;
}

.spatial-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* VisionOS Top Capsule */
.vision-top-capsule {
  position: absolute;
  top: 7rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 0.65rem 1.6rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(32px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
}

.capsule-left {
  display: flex;
  flex-direction: column;
}

.vision-badge {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #38bdf8;
}

.vision-title {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 800;
  margin: 0;
}

.capsule-stats {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  border-left: 1px solid rgba(255, 255, 255, 0.12);
  padding-left: 1.25rem;
}

.v-stat {
  display: flex;
  flex-direction: column;
}

.v-k {
  font-size: 0.62rem;
  color: #8c92a4;
  letter-spacing: 0.04em;
}

.v-v {
  font-size: 0.84rem;
}

.text-sky { color: #7dd3fc; }
.text-mint { color: #a7f3d0; }
.text-lavender { color: #c4b5fd; }

/* Spatial Focus Billboard Card */
.spatial-focus-billboard {
  position: absolute;
  bottom: 8.5rem;
  right: 3rem;
  z-index: 10;
  width: 360px;
  background: rgba(20, 24, 38, 0.75);
  backdrop-filter: blur(28px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 24px;
  padding: 1.3rem;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.6);
  cursor: pointer;
  transition: all 0.25s ease;
}

.spatial-focus-billboard:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: #38bdf8;
}

.billboard-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.6rem;
}

.step-pill {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 800;
  background: #38bdf8;
  color: #05060a;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.category-pill {
  font-size: 0.68rem;
  color: #a0a6b7;
}

.touch-hint {
  font-size: 0.7rem;
  font-weight: 700;
  color: #38bdf8;
}

.billboard-name {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0 0 0.4rem;
}

.billboard-summary {
  font-size: 0.82rem;
  color: #c5cbd8;
  line-height: 1.45;
  margin-bottom: 0.8rem;
}

.billboard-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #8c92a4;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 0.6rem;
}

.foot-mem {
  color: #a7f3d0;
  font-weight: 700;
}

/* VisionOS Bottom Floating Island */
.vision-island-dock {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  background: rgba(18, 22, 34, 0.85);
  backdrop-filter: blur(36px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 28px;
  padding: 0.65rem 1.2rem;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.6);
}

.phase-horizon-scrub {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.phase-scrub-pip {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-pill);
  background: transparent;
  border: 1px solid transparent;
  color: #9ba1b2;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.phase-scrub-pip:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.phase-scrub-pip.active {
  background: #ffffff;
  color: #05060a;
  font-weight: 800;
  box-shadow: 0 4px 16px rgba(255, 255, 255, 0.3);
}

.pip-num {
  font-family: var(--font-mono);
  font-size: 0.68rem;
}

.dock-actions-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 0.45rem;
  width: 100%;
  justify-content: center;
}

.island-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.95rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #d1d5db;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.island-action-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  color: #ffffff;
}

.island-action-btn.active {
  background: #38bdf8;
  color: #05060a;
  font-weight: 800;
}

/* Spatial Modal */
.spatial-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(5, 6, 10, 0.75);
  backdrop-filter: blur(24px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.5rem;
}

.vision-modal-glass {
  width: 100%;
  max-width: 1050px;
  max-height: 85vh;
  overflow-y: auto;
  background: rgba(22, 26, 42, 0.92);
  backdrop-filter: blur(48px);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 32px;
  box-shadow: 0 36px 90px rgba(0, 0, 0, 0.75);
  padding: 2.5rem;
  color: #ffffff;
}

.modal-glass-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}

.modal-badge-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.glass-chip {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
}
.chip-sky { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
.chip-mint { background: rgba(16, 185, 129, 0.2); color: #a7f3d0; }

.glass-chip-mono {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #9ba1b2;
}

.close-glass-btn {
  font-size: 1.2rem;
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: #c5cbd8;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-glass-btn:hover {
  background: #ffffff;
  color: #05060a;
}

.modal-step-title {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0 0 0.5rem;
}

.modal-step-lead {
  font-size: 0.95rem;
  color: #9ba1b2;
  line-height: 1.55;
  margin-bottom: 2rem;
}

.modal-spatial-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.body-col {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.col-kicker {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #6d7385;
}

.spatial-mech-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mech-item {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.82rem;
  color: #d1d5db;
  line-height: 1.45;
}

.mech-dot {
  font-size: 0.68rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.18);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

.formula-expl {
  font-size: 0.78rem;
  color: #8c92a4;
  margin-top: 0.4rem;
}

.spatial-params-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
}

.param-box {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 0.65rem 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.p-name {
  font-size: 0.68rem;
  color: #8c92a4;
}

.p-v {
  font-size: 0.85rem;
  color: #38bdf8;
}

.p-d {
  font-size: 0.66rem;
  color: #656b7c;
}

.spatial-terminal-window {
  background: #090b12;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
}

.term-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.85rem;
  background: rgba(255, 255, 255, 0.05);
  font-size: 0.7rem;
  color: #8c92a4;
  font-family: var(--font-mono);
}

.copy-btn {
  font-size: 0.7rem;
  color: #38bdf8;
  background: transparent;
  border: none;
  cursor: pointer;
}

.term-pre {
  margin: 0;
  padding: 0.85rem;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  color: #93c5fd;
  line-height: 1.45;
  max-height: 180px;
  overflow-y: auto;
}

@media (max-width: 900px) {
  .modal-spatial-body {
    grid-template-columns: 1fr;
  }
  .spatial-focus-billboard {
    display: none;
  }
}
</style>
