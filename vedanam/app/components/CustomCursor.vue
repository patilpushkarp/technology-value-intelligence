<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useCursor } from '~/composables/useCursor'

const { cursorState } = useCursor()

const cursorX = ref(-100)
const cursorY = ref(-100)
const targetX = ref(-100)
const targetY = ref(-100)
const isVisible = ref(false)

let rafId: number | null = null

const onMouseMove = (e: MouseEvent) => {
  targetX.value = e.clientX
  targetY.value = e.clientY
  if (!isVisible.value) isVisible.value = true
}

const onMouseLeave = () => {
  isVisible.value = false
}

const loop = () => {
  const ease = 0.2
  cursorX.value += (targetX.value - cursorX.value) * ease
  cursorY.value += (targetY.value - cursorY.value) * ease

  rafId = requestAnimationFrame(loop)
}

onMounted(() => {
  if (process.client && window.matchMedia('(pointer: fine)').matches) {
    window.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseleave', onMouseLeave)
    rafId = requestAnimationFrame(loop)
  }
})

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseleave', onMouseLeave)
    if (rafId) cancelAnimationFrame(rafId)
  }
})
</script>

<template>
  <div
    v-if="isVisible"
    class="vedanam-cursor"
    :class="{
      'is-active': cursorState.isActive,
      [`variant-${cursorState.variant}`]: true
    }"
    :style="{
      transform: `translate3d(${cursorX}px, ${cursorY}px, 0)`
    }"
  >
    <div class="cursor-dot" />
    <div v-if="cursorState.isActive && cursorState.label" class="cursor-glass-pill">
      <span class="cursor-label">{{ cursorState.label }}</span>
    </div>
  </div>
</template>

<style scoped>
.vedanam-cursor {
  position: fixed;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: var(--z-cursor);
  mix-blend-mode: normal;
  will-change: transform;
}

.cursor-dot {
  width: 8px;
  height: 8px;
  background-color: #121316;
  border: 1.5px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.2s var(--ease-expo), height 0.2s var(--ease-expo), opacity 0.2s ease;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.2);
}

.is-active .cursor-dot {
  width: 4px;
  height: 4px;
  opacity: 0.2;
}

/* Frosted Glass Pill Cursor (ledup.pt style) */
.cursor-glass-pill {
  position: absolute;
  top: 0;
  left: 0;
  transform: translate(-50%, -50%);
  padding: 0.4rem 1.1rem;
  background: rgba(18, 19, 22, 0.88);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 9999px;
  white-space: nowrap;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
  animation: pillIn 0.2s var(--ease-expo) forwards;
}

.cursor-label {
  font-family: var(--font-sans);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #ffffff;
  display: block;
}

.variant-danger .cursor-glass-pill {
  border-color: rgba(254, 205, 211, 0.5);
  background: rgba(45, 16, 22, 0.9);
}

.variant-danger .cursor-label {
  color: var(--pastel-rose);
}

.variant-highlight .cursor-glass-pill {
  border-color: rgba(196, 181, 253, 0.6);
  background: rgba(28, 22, 45, 0.92);
}

.variant-highlight .cursor-label {
  color: var(--pastel-lavender);
}

@keyframes pillIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.85);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

@media (pointer: coarse) {
  .vedanam-cursor {
    display: none;
  }
}
</style>
