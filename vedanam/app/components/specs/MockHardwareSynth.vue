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

const scopeHostRef = ref<HTMLDivElement | null>(null)
const activeStepId = ref<number>(1)
const scopeDisplayMode = ref<'wave' | 'math' | 'code'>('wave')
const isPowerOn = ref<boolean>(true)

// Tactile Knob Values (Rotary Dials)
const knobFrequency = ref<number>(2.4)
const knobHarmonics = ref<number>(1.2)
const knobResonance = ref<number>(0.85)
const knobAttenuation = ref<number>(0.0)

const currentStep = computed<TechSpecStep>(() => {
  return steps.find(s => s.id === activeStepId.value) || steps[0]
})

// Three.js 3D Oscilloscope Variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let waveMesh: THREE.Line | null = null
let wavePoints: THREE.Vector3[] = []
let lissajousMesh: THREE.Line | null = null

const selectStepPad = (id: number) => {
  activeStepId.value = id
  playInteractChime(0.9 + (id % 12) * 0.08)

  // Modulate knobs based on step parameters
  knobFrequency.value = 1.0 + (id % 4) * 0.8
  knobHarmonics.value = 0.5 + (id % 3) * 0.6
  knobResonance.value = 0.4 + (id % 5) * 0.15
}

// Drag Knob Handler
const startKnobDrag = (event: MouseEvent, targetRef: 'freq' | 'harm' | 'res') => {
  const startY = event.clientY
  let startVal = targetRef === 'freq' ? knobFrequency.value : targetRef === 'harm' ? knobHarmonics.value : knobResonance.value

  const onMouseMove = (moveEvent: MouseEvent) => {
    const deltaY = startY - moveEvent.clientY
    const newVal = Math.max(0.2, Math.min(5.0, startVal + deltaY * 0.02))
    if (targetRef === 'freq') knobFrequency.value = newVal
    else if (targetRef === 'harm') knobHarmonics.value = newVal
    else if (targetRef === 'res') knobResonance.value = newVal
    playInteractChime(1.5 + newVal * 0.2)
  }

  const onMouseUp = () => {
    window.removeEventListener('mousemove', onMouseMove)
    window.removeEventListener('mouseup', onMouseUp)
  }

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

onMounted(() => {
  if (!process.client || !scopeHostRef.value) return

  const container = scopeHostRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100)
  camera.position.set(0, 0, 8.5)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  // 1. Build 3D Lissajous Waveform Ribbon
  const numPoints = 250
  for (let i = 0; i < numPoints; i++) {
    wavePoints.push(new THREE.Vector3(0, 0, 0))
  }
  const waveGeom = new THREE.BufferGeometry().setFromPoints(wavePoints)
  const waveMat = new THREE.LineBasicMaterial({
    color: 0x38bdf8,
    linewidth: 2,
    transparent: true,
    opacity: 0.95
  })
  waveMesh = new THREE.Line(waveGeom, waveMat)
  scene.add(waveMesh)

  // Outer Reticle Grid Ring
  const gridRingGeom = new THREE.RingGeometry(3.2, 3.25, 64)
  const gridRingMat = new THREE.MeshBasicMaterial({
    color: 0x1e293b,
    side: THREE.DoubleSide
  })
  const gridRing = new THREE.Mesh(gridRingGeom, gridRingMat)
  scene.add(gridRing)

  let clock = new THREE.Clock()

  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const t = clock.getElapsedTime()

    if (waveMesh && isPowerOn.value) {
      const positions = (waveMesh.geometry as THREE.BufferGeometry).attributes.position
      const freq = knobFrequency.value
      const harm = knobHarmonics.value
      const res = knobResonance.value

      for (let i = 0; i < numPoints; i++) {
        const u = (i / numPoints) * Math.PI * 4
        const x = Math.sin(u * freq + t * 2) * (2.4 * res)
        const y = Math.cos(u * harm + t * 2.5) * 1.8
        const z = Math.sin(u * 3 + t) * 0.8
        positions.setXYZ(i, x, y, z)
      }
      positions.needsUpdate = true
      waveMesh.rotation.z = Math.sin(t * 0.5) * 0.2
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
  <div class="hardware-synth-workbench">
    <div class="synth-console-chassis">
      <!-- 1. Top Brushed Metal Rack Header -->
      <header class="chassis-top-rack">
        <div class="power-toggle-zone">
          <button
            type="button"
            class="mechanical-power-switch"
            :class="{ active: isPowerOn }"
            @click="isPowerOn = !isPowerOn; playInteractChime(isPowerOn ? 1.8 : 0.6)"
          >
            <span class="power-led" />
            <span class="power-label">POWER</span>
          </button>
          <div class="brand-stamp">
            <span class="brand-hed">VEDANAM MODULAR-12</span>
            <span class="brand-sub">ANALYTICAL SIGNAL SYNTHESIZER DECK</span>
          </div>
        </div>

        <!-- VFD Green Fluorescent Displays -->
        <div class="vfd-displays-cluster">
          <div class="vfd-screen">
            <span class="vfd-k">ACTIVE CHANNEL</span>
            <strong class="vfd-digits">{{ currentStep.code }}</strong>
          </div>
          <div class="vfd-screen">
            <span class="vfd-k">EXECUTION SLA</span>
            <strong class="vfd-digits text-amber">{{ currentStep.latencySla }}</strong>
          </div>
          <div class="vfd-screen">
            <span class="vfd-k">MACHINE DRIFT</span>
            <strong class="vfd-digits text-mint">0.0000%</strong>
          </div>
          <div class="vfd-screen">
            <span class="vfd-k">RAM LIMIT</span>
            <strong class="vfd-digits">{{ currentStep.memoryBudget }}</strong>
          </div>
        </div>
      </header>

      <!-- 2. Middle Main Deck (3D Oscilloscope + Rotary Synth Controls) -->
      <main class="chassis-middle-deck">
        <!-- Left: 3D Vector Oscilloscope CRT -->
        <div class="oscilloscope-crt-casing">
          <div class="crt-bezel-bar">
            <div class="crt-tag">
              <span class="crt-dot" />
              <span>CRT SPECTRUM 432Hz</span>
            </div>
            <!-- Scope View Switcher -->
            <div class="scope-mode-rocker">
              <button
                type="button"
                class="rocker-btn"
                :class="{ active: scopeDisplayMode === 'wave' }"
                @click="scopeDisplayMode = 'wave'; playInteractChime(1.1)"
              >
                3D WAVE
              </button>
              <button
                type="button"
                class="rocker-btn"
                :class="{ active: scopeDisplayMode === 'math' }"
                @click="scopeDisplayMode = 'math'; playInteractChime(1.2)"
              >
                MATH PROOF
              </button>
              <button
                type="button"
                class="rocker-btn"
                :class="{ active: scopeDisplayMode === 'code' }"
                @click="scopeDisplayMode = 'code'; playInteractChime(1.3)"
              >
                CODE TRACE
              </button>
            </div>
          </div>

          <!-- CRT Display Viewports -->
          <div class="crt-screen-viewport">
            <!-- Mode A: 3D Oscilloscope Canvas -->
            <div
              v-show="scopeDisplayMode === 'wave'"
              ref="scopeHostRef"
              class="three-scope-canvas"
            />

            <!-- Mode B: Mathematical Proof Screen -->
            <div v-if="scopeDisplayMode === 'math'" class="crt-math-overlay">
              <div class="math-crt-card">
                <span class="crt-screen-kicker">{{ currentStep.formulaName }}</span>
                <MathFormula
                  :latex="currentStep.formulaLatex"
                  :formula-html="currentStep.formulaHtml"
                />
                <p class="crt-formula-expl">{{ currentStep.formulaExplanation }}</p>
              </div>
            </div>

            <!-- Mode C: Code Terminal Screen -->
            <div v-if="scopeDisplayMode === 'code'" class="crt-code-overlay">
              <div class="code-terminal-card">
                <span class="crt-screen-kicker">KERNEL EXECUTION: {{ currentStep.pythonModule }}</span>
                <pre class="terminal-code"><code>{{ currentStep.codeSnippet }}</code></pre>
              </div>
            </div>

            <!-- Oscilloscope Scanlines Overlay -->
            <div class="crt-scanlines-filter" />
          </div>

          <!-- Bottom Scope Controls -->
          <div class="crt-sub-controls">
            <span class="scope-info-text">{{ currentStep.title }}</span>
            <span class="mono-badge">{{ currentStep.category }}</span>
          </div>
        </div>

        <!-- Right: Tactile Physical Modular Knob Channel Strip -->
        <div class="tactile-hardware-rack">
          <div class="rack-section-hed">ANALYTICAL FREQUENCY CHANNELS</div>

          <!-- 4 Rotary Dials -->
          <div class="rotary-knobs-grid">
            <!-- Knob 1 -->
            <div
              class="rotary-knob-unit"
              @mousedown="startKnobDrag($event, 'freq')"
              @mouseenter="setCursor('DRAG TO TUNE FREQ', 'highlight')"
              @mouseleave="resetCursor"
            >
              <span class="knob-label">FREQUENCY</span>
              <div class="knob-dial-wheel" :style="{ transform: `rotate(${(knobFrequency - 1) * 60}deg)` }">
                <span class="dial-notch" />
              </div>
              <strong class="knob-readout">{{ knobFrequency.toFixed(2) }}x</strong>
            </div>

            <!-- Knob 2 -->
            <div
              class="rotary-knob-unit"
              @mousedown="startKnobDrag($event, 'harm')"
              @mouseenter="setCursor('DRAG TO TUNE HARMONICS', 'highlight')"
              @mouseleave="resetCursor"
            >
              <span class="knob-label">HARMONICS</span>
              <div class="knob-dial-wheel" :style="{ transform: `rotate(${(knobHarmonics - 1) * 70}deg)` }">
                <span class="dial-notch" />
              </div>
              <strong class="knob-readout">{{ knobHarmonics.toFixed(2) }}</strong>
            </div>

            <!-- Knob 3 -->
            <div
              class="rotary-knob-unit"
              @mousedown="startKnobDrag($event, 'res')"
              @mouseenter="setCursor('DRAG TO TUNE RESONANCE', 'highlight')"
              @mouseleave="resetCursor"
            >
              <span class="knob-label">RESONANCE</span>
              <div class="knob-dial-wheel" :style="{ transform: `rotate(${(knobResonance - 0.5) * 80}deg)` }">
                <span class="dial-notch" />
              </div>
              <strong class="knob-readout">{{ knobResonance.toFixed(2) }}</strong>
            </div>

            <!-- Attenuation Dial -->
            <div class="rotary-knob-unit">
              <span class="knob-label">GL DRIFT</span>
              <div class="knob-dial-wheel zero-drift">
                <span class="dial-notch" />
              </div>
              <strong class="knob-readout text-mint">0.00%</strong>
            </div>
          </div>

          <!-- Step Mechanics Breakdown inside Channel Strip -->
          <div class="channel-specs-box">
            <span class="specs-hed">CHANNEL EXECUTION SPECS</span>
            <ul class="specs-items-list">
              <li v-for="(detail, idx) in currentStep.executionDetails.slice(0, 3)" :key="idx" class="spec-li">
                <span class="spec-idx">{{ idx + 1 }}</span>
                <span>{{ detail }}</span>
              </li>
            </ul>
          </div>
        </div>
      </main>

      <!-- 3. Bottom Hardware Step Sequencer / MPC Drum Pads -->
      <footer class="chassis-bottom-sequencer">
        <div class="sequencer-hed-row">
          <span class="seq-label">12-STEP CONTINUOUS HARDWARE SEQUENCER (CLICK PAD TO ACTIVATE CHANNEL)</span>
          <span class="seq-clock">CLOCK: 120 BPM · SYNC LOCKED</span>
        </div>

        <div class="mpc-pads-row">
          <button
            v-for="st in steps"
            :key="st.id"
            type="button"
            class="mpc-step-pad"
            :class="{ active: activeStepId === st.id }"
            @click="selectStepPad(st.id)"
            @mouseenter="setCursor(st.code, 'highlight')"
            @mouseleave="resetCursor"
          >
            <div class="pad-led" />
            <span class="pad-id">{{ st.id < 10 ? '0' + st.id : st.id }}</span>
            <strong class="pad-code">{{ st.code }}</strong>
            <span class="pad-label">{{ st.shortTitle }}</span>
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.hardware-synth-workbench {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #0b0c10;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6.5rem 2rem 2.5rem;
  color: #d1d5db;
}

.synth-console-chassis {
  width: 100%;
  max-width: 1350px;
  background: #14161f;
  border: 2px solid #282d3d;
  border-radius: 24px;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 1. Top Rack */
.chassis-top-rack {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1.8rem;
  background: #1b1e2a;
  border-bottom: 2px solid #232736;
}

.power-toggle-zone {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.mechanical-power-switch {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  background: #252a3a;
  border: 1px solid #363c52;
  color: #ffffff;
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  font-weight: 800;
  transition: all 0.2s ease;
}

.mechanical-power-switch.active {
  background: #1f2937;
  border-color: #10b981;
}

.power-led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
}

.mechanical-power-switch.active .power-led {
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
}

.brand-stamp {
  display: flex;
  flex-direction: column;
}

.brand-hed {
  font-family: var(--font-mono);
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #ffffff;
}

.brand-sub {
  font-size: 0.65rem;
  letter-spacing: 0.05em;
  color: #6b7280;
}

.vfd-displays-cluster {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.vfd-screen {
  background: #080a0f;
  border: 1px solid #1a202c;
  border-radius: 8px;
  padding: 0.4rem 0.85rem;
  display: flex;
  flex-direction: column;
}

.vfd-k {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: #6b7280;
}

.vfd-digits {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  color: #38bdf8;
  letter-spacing: 0.05em;
}

.text-amber { color: #f59e0b; }
.text-mint { color: #10b981; }

/* 2. Middle Deck */
.chassis-middle-deck {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  padding: 1.8rem;
  gap: 1.8rem;
  background: #11131a;
}

.oscilloscope-crt-casing {
  background: #08090e;
  border: 2px solid #1f2433;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.crt-bezel-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1rem;
  background: #141724;
  border-bottom: 1px solid #1f2433;
}

.crt-tag {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  color: #38bdf8;
}

.crt-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #38bdf8;
  box-shadow: 0 0 8px #38bdf8;
}

.scope-mode-rocker {
  display: flex;
  gap: 0.25rem;
  background: #0b0d14;
  padding: 0.2rem;
  border-radius: 6px;
}

.rocker-btn {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
}

.rocker-btn.active {
  background: #38bdf8;
  color: #08090e;
}

.crt-screen-viewport {
  position: relative;
  height: 380px;
  overflow: hidden;
  background: #040508;
}

.three-scope-canvas {
  width: 100%;
  height: 100%;
}

.crt-scanlines-filter {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.25) 0px,
    rgba(0, 0, 0, 0.25) 1px,
    transparent 1px,
    transparent 2px
  );
}

.crt-math-overlay,
.crt-code-overlay {
  position: absolute;
  inset: 0;
  padding: 1.5rem;
  overflow-y: auto;
  z-index: 5;
}

.math-crt-card,
.code-terminal-card {
  background: rgba(14, 18, 28, 0.95);
  border: 1px solid #1f273b;
  border-radius: 12px;
  padding: 1.25rem;
}

.crt-screen-kicker {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  color: #38bdf8;
  display: block;
  margin-bottom: 0.8rem;
}

.crt-formula-expl {
  font-size: 0.82rem;
  color: #9ba1b2;
  margin-top: 0.8rem;
}

.terminal-code {
  font-family: var(--font-mono);
  font-size: 0.76rem;
  color: #a7f3d0;
  margin: 0;
}

.crt-sub-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #141724;
  border-top: 1px solid #1f2433;
}

.scope-info-text {
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: 700;
  color: #ffffff;
}

.mono-badge {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #38bdf8;
}

/* Right Modular Knobs Strip */
.tactile-hardware-rack {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.rack-section-hed {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #8c92a4;
  border-bottom: 1px solid #232736;
  padding-bottom: 0.5rem;
}

.rotary-knobs-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.rotary-knob-unit {
  background: #171a25;
  border: 1px solid #272d3e;
  border-radius: 14px;
  padding: 0.85rem 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  cursor: ns-resize;
  user-select: none;
}

.knob-label {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 700;
  color: #8c92a4;
}

.knob-dial-wheel {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: radial-gradient(circle, #30364a 0%, #1c202d 100%);
  border: 2px solid #4a536e;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
  position: relative;
}

.dial-notch {
  position: absolute;
  top: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 3px;
  height: 8px;
  background: #38bdf8;
  border-radius: 2px;
}

.knob-dial-wheel.zero-drift .dial-notch {
  background: #10b981;
}

.knob-readout {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: #38bdf8;
}

.channel-specs-box {
  background: #171a25;
  border: 1px solid #272d3e;
  border-radius: 14px;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.specs-hed {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  color: #8c92a4;
}

.specs-items-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.spec-li {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  font-size: 0.78rem;
  line-height: 1.4;
  color: #d1d5db;
}

.spec-idx {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.15);
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

/* 3. Bottom Sequencer */
.chassis-bottom-sequencer {
  background: #181b26;
  border-top: 2px solid #232736;
  padding: 1.2rem 1.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.sequencer-hed-row {
  display: flex;
  justify-content: space-between;
}

.seq-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  color: #8c92a4;
}

.seq-clock {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #10b981;
}

.mpc-pads-row {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 0.45rem;
}

.mpc-step-pad {
  background: #232838;
  border: 1px solid #363d54;
  border-radius: 10px;
  padding: 0.65rem 0.35rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mpc-step-pad:hover {
  background: #2f3549;
}

.mpc-step-pad.active {
  background: #38bdf8;
  border-color: #38bdf8;
  color: #0b0c10;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.6);
}

.pad-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4b5563;
}

.mpc-step-pad.active .pad-led {
  background: #ffffff;
  box-shadow: 0 0 6px #ffffff;
}

.pad-id {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  opacity: 0.7;
}

.pad-code {
  font-family: var(--font-mono);
  font-size: 0.72rem;
}

.pad-label {
  font-size: 0.62rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 65px;
}

@media (max-width: 1100px) {
  .chassis-middle-deck {
    grid-template-columns: 1fr;
  }
  .mpc-pads-row {
    grid-template-columns: repeat(6, 1fr);
  }
}
</style>
