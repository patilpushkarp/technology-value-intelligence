<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

const heroContainerRef = ref<HTMLDivElement | null>(null)
const canvasContainerRef = ref<HTMLDivElement | null>(null)
const activeSlide = ref<'01' | '02'>('01')

// Interactive Mouse Parallax coordinates
const mouseX = ref(0)
const mouseY = ref(0)
const smoothMouseX = ref(0)
const smoothMouseY = ref(0)

// Slide Content (Enterprise Technology Value Intelligence)
const slides = {
  '01': {
    title: 'Intelligence that illuminates technology value.',
    desc: 'Every initiative is an opportunity to transform architectural complexity into proven business value. Side by side from infrastructure to executive decision.'
  },
  '02': {
    title: 'Topology that clarifies strategic decisions.',
    desc: 'End-to-end traceability connecting infrastructure, fully burdened costs, and semantic graph dependencies in real time.'
  }
}

// Three.js Scene Variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number | null = null
let graphGroup: THREE.Group
let pulseGroup: THREE.Group
let nodes: THREE.Mesh[] = []
let pulsePoints: { mesh: THREE.Mesh; path: THREE.CatmullRomCurve3; progress: number; speed: number }[] = []
let gsapCtx: gsap.Context | null = null

const setSlide = (slide: '01' | '02') => {
  if (activeSlide.value === slide) return
  activeSlide.value = slide
  playInteractChime(slide === '01' ? 1.1 : 1.35)

  // Animate text transition
  gsap.fromTo(
    '.hero-headline-text',
    { opacity: 0, y: 18 },
    { opacity: 1, y: 0, duration: 0.65, ease: 'power3.out' }
  )
  gsap.fromTo(
    '.hero-subtitle-text',
    { opacity: 0, y: 12 },
    { opacity: 1, y: 0, duration: 0.65, delay: 0.08, ease: 'power3.out' }
  )

  // Camera transition in 3D space
  if (camera) {
    const targetX = slide === '01' ? 1.2 : -0.8
    const targetZ = slide === '01' ? 8.5 : 7.8
    gsap.to(camera.position, {
      x: targetX,
      z: targetZ,
      duration: 1.2,
      ease: 'power2.inOut'
    })
  }
}

const handleMouseMove = (e: MouseEvent) => {
  if (!heroContainerRef.value) return
  const rect = heroContainerRef.value.getBoundingClientRect()
  mouseX.value = ((e.clientX - rect.left) / rect.width - 0.5) * 2
  mouseY.value = ((e.clientY - rect.top) / rect.height - 0.5) * 2
}

const handleMouseLeave = () => {
  mouseX.value = 0
  mouseY.value = 0
}

// Parallax style for background image
const parallaxStyle = computed(() => {
  const px = smoothMouseX.value * -16
  const py = smoothMouseY.value * -10
  return {
    transform: `scale(1.05) translate3d(${px}px, ${py}px, 0)`
  }
})

// Parallax style for floating telemetry badges
const badgeParallaxStyle = computed(() => {
  const px = smoothMouseX.value * 24
  const py = smoothMouseY.value * 18
  return {
    transform: `translate3d(${px}px, ${py}px, 0)`
  }
})

onMounted(() => {
  if (!process.client || !canvasContainerRef.value) return

  const container = canvasContainerRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  // 1. Three.js Scene Setup (Transparent overlay for 3D topology constellation)
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100)
  camera.position.set(1.2, 0.5, 8.5)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  // Subtle ambient illumination
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.2)
  scene.add(ambientLight)

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8)
  dirLight.position.set(5, 10, 7)
  scene.add(dirLight)

  graphGroup = new THREE.Group()
  pulseGroup = new THREE.Group()
  scene.add(graphGroup)
  scene.add(pulseGroup)

  // 2. Build 3D Enterprise Topology Constellation
  const pastelColors = [
    new THREE.Color(0xa7f3d0), // Mint (Value Realization)
    new THREE.Color(0xc4b5fd), // Lavender (Semantic Graph)
    new THREE.Color(0x7dd3fc), // Sky (Cloud Infrastructure)
    new THREE.Color(0xfed7aa)  // Peach (DuckDB OLAP)
  ]

  const nodePositions: THREE.Vector3[] = []
  const clusterCenters = [
    new THREE.Vector3(2.5, 0.8, -0.5),   // Enterprise Core Hub
    new THREE.Vector3(3.8, 1.8, -1.2),   // Analytical Cluster
    new THREE.Vector3(1.2, -0.6, -0.2),  // Ingestion Gateway
    new THREE.Vector3(3.2, -1.2, -1.0),  // Governance & Value Stream
    new THREE.Vector3(4.8, 0.2, -1.5)    // Cloud Mesh
  ]

  // Generate 26 interconnected topology nodes
  clusterCenters.forEach((center, cIdx) => {
    const nodeCount = 5 + (cIdx % 2)
    for (let i = 0; i < nodeCount; i++) {
      const offset = new THREE.Vector3(
        (Math.random() - 0.5) * 1.8,
        (Math.random() - 0.5) * 1.4,
        (Math.random() - 0.5) * 1.2
      )
      const pos = center.clone().add(offset)
      nodePositions.push(pos)

      const color = pastelColors[(cIdx + i) % pastelColors.length]
      const radius = i === 0 ? 0.16 : 0.08 + Math.random() * 0.05

      // Glossy translucent sphere
      const sphereMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: color,
        emissiveIntensity: 0.65,
        roughness: 0.15,
        metalness: 0.2,
        transparent: true,
        opacity: 0.92
      })

      const sphereGeo = new THREE.SphereGeometry(radius, 20, 20)
      const nodeMesh = new THREE.Mesh(sphereGeo, sphereMat)
      nodeMesh.position.copy(pos)
      graphGroup.add(nodeMesh)
      nodes.push(nodeMesh)

      // Surrounding halo ring on primary cluster nodes
      if (i === 0) {
        const ringGeo = new THREE.RingGeometry(radius * 1.4, radius * 1.6, 28)
        const ringMat = new THREE.MeshBasicMaterial({
          color: color,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.4
        })
        const ringMesh = new THREE.Mesh(ringGeo, ringMat)
        ringMesh.position.copy(pos)
        ringMesh.rotation.x = Math.PI / 4
        graphGroup.add(ringMesh)
      }
    }
  })

  // 3. Connect Nodes with Flowing Bezier Spline Edges
  const edgeMaterial = new THREE.LineBasicMaterial({
    color: 0xd1d5db,
    transparent: true,
    opacity: 0.45
  })

  for (let i = 0; i < nodePositions.length; i++) {
    for (let j = i + 1; j < nodePositions.length; j++) {
      const dist = nodePositions[i].distanceTo(nodePositions[j])
      if (dist < 2.0 && Math.random() > 0.35) {
        // Curve with mid offset
        const mid = new THREE.Vector3()
          .addVectors(nodePositions[i], nodePositions[j])
          .multiplyScalar(0.5)
        mid.y += (Math.random() - 0.5) * 0.25
        mid.z += (Math.random() - 0.5) * 0.25

        const curve = new THREE.CatmullRomCurve3([nodePositions[i], mid, nodePositions[j]])
        const points = curve.getPoints(24)
        const edgeGeo = new THREE.BufferGeometry().setFromPoints(points)
        const edgeLine = new THREE.Line(edgeGeo, edgeMaterial)
        graphGroup.add(edgeLine)

        // Add traveling telemetry data pulse along this edge
        if (Math.random() > 0.6) {
          const pulseColor = pastelColors[Math.floor(Math.random() * pastelColors.length)]
          const pMat = new THREE.MeshBasicMaterial({ color: pulseColor })
          const pGeo = new THREE.SphereGeometry(0.045, 12, 12)
          const pMesh = new THREE.Mesh(pGeo, pMat)
          pulseGroup.add(pMesh)

          pulsePoints.push({
            mesh: pMesh,
            path: curve,
            progress: Math.random(),
            speed: 0.003 + Math.random() * 0.004
          })
        }
      }
    }
  }

  // 4. Resize Listener
  const handleResize = () => {
    if (!canvasContainerRef.value) return
    const w = canvasContainerRef.value.clientWidth
    const h = canvasContainerRef.value.clientHeight
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
  }
  window.addEventListener('resize', handleResize)

  // 5. Render Loop with Smooth Inertia
  let time = 0
  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    time += 0.015

    // Smooth mouse lerp
    smoothMouseX.value += (mouseX.value - smoothMouseX.value) * 0.05
    smoothMouseY.value += (mouseY.value - smoothMouseY.value) * 0.05

    // Gentle camera parallax in 3D
    camera.position.x = 1.2 + smoothMouseX.value * 0.55
    camera.position.y = 0.5 + smoothMouseY.value * -0.35
    camera.lookAt(2.2, 0.4, -0.6)

    // Subtle graph drift
    if (graphGroup) {
      graphGroup.rotation.y = Math.sin(time * 0.4) * 0.04
      graphGroup.rotation.x = Math.cos(time * 0.3) * 0.03
    }

    // Animate traveling data pulses
    pulsePoints.forEach(p => {
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
    // 1. Initial Story Entry Animation on page arrival
    const enterTl = gsap.timeline({ delay: 0.15 })

    enterTl.fromTo(
      '.hero-headline-text',
      { opacity: 0, y: 40, filter: 'blur(6px)' },
      { opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.2, ease: 'power4.out' }
    )
    .fromTo(
      ['.hero-subtitle-text', '.hero-slider-nav'],
      { opacity: 0, y: 25 },
      { opacity: 1, y: 0, duration: 1.0, ease: 'power3.out', stagger: 0.15 },
      '-=0.8'
    )
    .fromTo(
      '.telemetry-pill-badge',
      { opacity: 0, y: 24, scale: 0.9 },
      { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: 'back.out(1.5)', stagger: 0.18 },
      '-=0.7'
    )

    // 2. Scroll Exit Animation (as user scrolls down past the hero viewport)
    // Synchronized scrubbed exit: text glides up and dissolves, badges disperse, 3D graph recedes into depth
    if (heroContainerRef.value) {
      const exitTl = gsap.timeline({
        scrollTrigger: {
          trigger: heroContainerRef.value,
          start: 'top top',
          end: 'bottom top',
          scrub: 0.6,
          invalidateOnRefresh: true
        }
      })

      exitTl.to('.hero-text-block', {
        y: -80,
        opacity: 0,
        filter: 'blur(4px)',
        ease: 'power2.in'
      }, 0)

      exitTl.to('.hero-floating-badges', {
        y: -60,
        opacity: 0,
        scale: 0.85,
        ease: 'power2.in'
      }, 0)

      if (graphGroup) {
        exitTl.to(graphGroup.position, {
          y: 1.4,
          z: -2.2,
          ease: 'power1.inOut'
        }, 0)
      }
    }
  }, heroContainerRef.value ?? undefined)
})

onUnmounted(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId)
  if (renderer && renderer.domElement) {
    renderer.domElement.remove()
    renderer.dispose()
  }
  gsapCtx?.revert()
})
</script>

<template>
  <section
    ref="heroContainerRef"
    class="ledup-hero-viewport"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- 1. Background Architectural Technology Layers with Parallax & Crossfade -->
    <div class="hero-bg-parallax-stage" :style="parallaxStyle">
      <div
        class="hero-bg-slide slide-01"
        :class="{ 'is-active': activeSlide === '01' }"
      />
      <div
        class="hero-bg-slide slide-02"
        :class="{ 'is-active': activeSlide === '02' }"
      />
      <!-- Bottom-Left Contrast Scrim for Pristine Text Readability -->
      <div class="hero-subtle-scrim" />
    </div>

    <!-- 2. Transparent Interactive 3D WebGL Knowledge Graph Constellation -->
    <div ref="canvasContainerRef" class="hero-three-canvas-layer" />

    <!-- 3. Floating Glassmorphic Telemetry Chips -->
    <div class="hero-floating-badges" :style="badgeParallaxStyle">
      <div class="telemetry-pill-badge badge-top-right">
        <span class="badge-dot dot-mint" />
        <span class="badge-label">102 Enterprise Nodes Active</span>
      </div>
      <div class="telemetry-pill-badge badge-mid-right">
        <span class="badge-dot dot-lavender" />
        <span class="badge-label">DuckDB OLAP // Analytical Truth</span>
      </div>
      <div class="telemetry-pill-badge badge-lower-center">
        <span class="badge-dot dot-peach" />
        <span class="badge-label">Value Realization // 94.2%</span>
      </div>
    </div>

    <!-- 4. Pinned Bottom-Left Architectural Typography (Exact ledup.pt layout in English) -->
    <div class="hero-pinned-content">
      <div class="hero-text-block">
        <h1 class="hero-headline-text">
          {{ slides[activeSlide].title }}
        </h1>
        <p class="hero-subtitle-text">
          {{ slides[activeSlide].desc }}
        </p>

        <!-- Slide Indicators (01 | 02 with active underline) -->
        <div class="hero-slider-nav">
          <button
            type="button"
            class="slide-btn"
            :class="{ 'is-active': activeSlide === '01' }"
            @click="setSlide('01')"
            @mouseenter="setCursor('SLIDE 01', 'default')"
            @mouseleave="resetCursor"
          >
            <span>01</span>
            <div class="slide-indicator-line" />
          </button>

          <button
            type="button"
            class="slide-btn"
            :class="{ 'is-active': activeSlide === '02' }"
            @click="setSlide('02')"
            @mouseenter="setCursor('SLIDE 02', 'default')"
            @mouseleave="resetCursor"
          >
            <span>02</span>
            <div class="slide-indicator-line" />
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ledup-hero-viewport {
  position: relative;
  width: 100%;
  height: 100vh;
  min-height: 700px;
  overflow: hidden;
  background-color: #f1f1f3;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

/* 1. Background Parallax Stage & Crossfading Slides */
.hero-bg-parallax-stage {
  position: absolute;
  inset: -4%;
  width: 108%;
  height: 108%;
  z-index: 1;
  pointer-events: none;
  transition: transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  will-change: transform;
}

.hero-bg-slide {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  opacity: 0;
  transform: scale(1.02);
  transition: opacity 0.85s cubic-bezier(0.4, 0, 0.2, 1), transform 1.2s ease-out;
}

.hero-bg-slide.is-active {
  opacity: 1;
  transform: scale(1);
}

.slide-01 {
  background-image: url('/images/hero_slide_01.jpg');
}

.slide-02 {
  background-image: url('/images/hero_slide_02.jpg');
}

/* Scrim for maximum contrast behind headline */
.hero-subtle-scrim {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    115deg,
    rgba(245, 245, 247, 0.88) 0%,
    rgba(245, 245, 247, 0.55) 38%,
    rgba(245, 245, 247, 0.15) 65%,
    rgba(245, 245, 247, 0) 100%
  );
  pointer-events: none;
}

/* 2. Three.js Overlay Layer */
.hero-three-canvas-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

/* 3. Floating Glassmorphic Telemetry Badges */
.hero-floating-badges {
  position: absolute;
  inset: 0;
  z-index: 4;
  pointer-events: none;
  transition: transform 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.telemetry-pill-badge {
  position: absolute;
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 1.15rem;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.85);
  border-radius: var(--radius-pill);
  box-shadow: 0 12px 32px -6px rgba(0, 0, 0, 0.08);
  font-family: var(--font-sans);
  font-size: 0.82rem;
  font-weight: 600;
  color: #1a1b1f;
  animation: floatBob 5s ease-in-out infinite alternate;
  pointer-events: auto;
}

.badge-top-right {
  top: 18%;
  right: 12%;
  animation-delay: 0s;
}

.badge-mid-right {
  top: 42%;
  right: 6%;
  animation-delay: 1.6s;
}

.badge-lower-center {
  bottom: 28%;
  right: 28%;
  animation-delay: 2.8s;
}

@keyframes floatBob {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-9px);
  }
}

.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
}

.dot-mint {
  background-color: var(--pastel-mint);
  color: var(--pastel-mint);
}

.dot-lavender {
  background-color: var(--pastel-lavender);
  color: var(--pastel-lavender);
}

.dot-peach {
  background-color: var(--pastel-peach);
  color: var(--pastel-peach);
}

/* 4. Pinned Bottom-Left Content (Exact ledup.pt framing) */
.hero-pinned-content {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 var(--container-padding) 4.5rem;
  pointer-events: none;
}

.hero-text-block {
  max-width: 1050px;
  pointer-events: auto;
}

.hero-headline-text {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 4.75rem);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 1.25rem;
  max-width: 24ch;
}

.hero-subtitle-text {
  font-family: var(--font-sans);
  font-size: clamp(0.75rem, 5vw, 1rem);
  font-weight: 400;
  line-height: 1.6;
  color: #3b3f4d;
  max-width: 80ch;
  margin-bottom: 2rem;
}

/* Slide Indicators: 01 / 02 */
.hero-slider-nav {
  display: flex;
  align-items: center;
  gap: 1.8rem;
}

.slide-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  cursor: pointer;
  padding: 0;
  background: none;
  border: none;
}

.slide-btn span {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 500;
  color: #8c909e;
  transition: color 0.2s ease;
}

.slide-indicator-line {
  width: 28px;
  height: 2px;
  background-color: transparent;
  transition: background-color 0.25s ease, width 0.25s ease;
}

.slide-btn.is-active span {
  color: #121316;
}

.slide-btn.is-active .slide-indicator-line {
  background-color: #121316;
}

.slide-btn:hover span {
  color: #121316;
}

@media (max-width: 900px) {
  .hero-floating-badges {
    display: none;
  }
}

@media (max-width: 768px) {
  .hero-pinned-content {
    padding-bottom: 3rem;
  }
}
</style>
