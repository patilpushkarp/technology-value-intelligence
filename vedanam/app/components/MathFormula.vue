<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAudioSynth } from '~/composables/useAudioSynth'

const props = defineProps<{
  latex: string
  formulaHtml?: string
  name?: string
}>()

const { playInteractChime } = useAudioSynth()

const katexHtml = ref<string>('')
const viewMode = ref<'formatted' | 'latex'>('formatted')
const isCopied = ref(false)

const tryRenderKatex = () => {
  if (process.client && (window as any).katex) {
    try {
      katexHtml.value = (window as any).katex.renderToString(props.latex, {
        displayMode: true,
        throwOnError: false
      })
    } catch {
      katexHtml.value = ''
    }
  }
}

watch(() => props.latex, () => {
  tryRenderKatex()
})

const copyLatex = async () => {
  if (process.client && navigator.clipboard) {
    await navigator.clipboard.writeText(props.latex)
    isCopied.value = true
    playInteractChime(1.4)
    setTimeout(() => {
      isCopied.value = false
    }, 1800)
  }
}

onMounted(() => {
  tryRenderKatex()

  // In case deferred script loads after component mount
  if (process.client && !(window as any).katex) {
    let attempts = 0
    const checkTimer = setInterval(() => {
      attempts++
      if ((window as any).katex) {
        tryRenderKatex()
        clearInterval(checkTimer)
      } else if (attempts > 15) {
        clearInterval(checkTimer)
      }
    }, 200)
  }
})
</script>

<template>
  <div class="math-formula-component">
    <div class="math-toolbar">
      <span class="math-label">{{ name || 'Mathematical Formulation' }}</span>
      <div class="toolbar-actions">
        <button
          type="button"
          class="mode-toggle-btn"
          :class="{ active: viewMode === 'formatted' }"
          @click="viewMode = 'formatted'; playInteractChime(1.15)"
        >
          Formatted
        </button>
        <button
          type="button"
          class="mode-toggle-btn"
          :class="{ active: viewMode === 'latex' }"
          @click="viewMode = 'latex'; playInteractChime(1.15)"
        >
          LaTeX Source
        </button>
        <button
          type="button"
          class="copy-latex-btn"
          @click="copyLatex"
          title="Copy LaTeX source code"
        >
          {{ isCopied ? 'Copied ✓' : 'Copy' }}
        </button>
      </div>
    </div>

    <!-- Formatted Math View -->
    <div v-if="viewMode === 'formatted'" class="math-display-viewport">
      <!-- 1. KaTeX Official Render if available -->
      <div v-if="katexHtml" class="katex-rendered-output" v-html="katexHtml" />

      <!-- 2. Semantic MathML / HTML Fallback (Always pristine, instant & offline) -->
      <div v-else-if="formulaHtml" class="semantic-math-output" v-html="formulaHtml" />

      <!-- 3. Clean Styled Math String Fallback -->
      <div v-else class="styled-math-fallback">
        <span class="math-text">{{ latex }}</span>
      </div>
    </div>

    <!-- Raw LaTeX Source View -->
    <div v-else class="latex-source-viewport">
      <pre class="latex-code"><code>{{ latex }}</code></pre>
    </div>
  </div>
</template>

<style scoped>
.math-formula-component {
  background: #ffffff;
  border: 1px solid #e2e6ee;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
  margin: 1rem 0;
}

.math-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.65rem 1rem;
  background: #f8f9fb;
  border-bottom: 1px solid #ebeef5;
}

.math-label {
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #7b8090;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.mode-toggle-btn {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-pill);
  border: 1px solid #dcdfe6;
  background: #ffffff;
  color: #555968;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-toggle-btn.active {
  background: #17181d;
  color: #ffffff;
  border-color: #17181d;
}

.copy-latex-btn {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  background: var(--pastel-mint-soft);
  color: #047857;
  cursor: pointer;
  transition: all 0.15s ease;
}

.copy-latex-btn:hover {
  background: #a7f3d0;
}

.math-display-viewport {
  padding: 1.25rem 1.5rem;
  overflow-x: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafc;
  min-height: 85px;
}

.latex-source-viewport {
  padding: 1rem 1.25rem;
  background: #17181d;
  overflow-x: auto;
}

.latex-code {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  line-height: 1.5;
  color: #e2e8f0;
}

/* Semantic Mathematical Fallback Typography */
:deep(.semantic-math-output),
.styled-math-fallback {
  font-family: 'KaTeX_Math', 'Cambria Math', 'STIX Two Math', 'Times New Roman', Georgia, serif;
  font-size: 1.25rem;
  line-height: 1.9;
  color: #11141a;
  text-align: center;
  letter-spacing: 0.02em;
}

:deep(i) {
  font-style: italic;
  font-family: 'KaTeX_Math', 'Cambria Math', 'Times New Roman', Georgia, serif;
}

:deep(sub) {
  font-size: 0.72em;
  vertical-align: -0.25em;
  line-height: 0;
}

:deep(sup) {
  font-size: 0.72em;
  vertical-align: 0.38em;
  line-height: 0;
}

:deep(.math-op) {
  font-size: 1.4em;
  vertical-align: -0.1em;
  margin: 0 0.15em;
  font-family: 'Cambria Math', 'KaTeX_Size1', serif;
}

:deep(.math-frac) {
  display: inline-flex;
  flex-direction: column;
  vertical-align: -0.65em;
  text-align: center;
  padding: 0 0.25em;
}

:deep(.math-num) {
  border-bottom: 1.5px solid #11141a;
  padding-bottom: 0.12em;
  font-size: 0.88em;
  line-height: 1.1;
}

:deep(.math-denom) {
  padding-top: 0.12em;
  font-size: 0.88em;
  line-height: 1.1;
}

:deep(.math-sqrt-body) {
  border-top: 1.5px solid #11141a;
  padding-top: 0.08em;
  margin-left: 0.05em;
}

:deep(.math-keyword) {
  font-family: var(--font-sans);
  font-size: 0.82em;
  font-weight: 600;
  color: #555968;
}

:deep(.math-note) {
  font-family: var(--font-sans);
  font-size: 0.78em;
  color: #047857;
  font-weight: 600;
  background: var(--pastel-mint-soft);
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-pill);
}

:deep(.math-term) {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  margin: 0 0.35rem;
}

:deep(.math-brace) {
  font-size: 0.95em;
}

:deep(.math-label) {
  font-family: var(--font-sans);
  font-size: 0.68em;
  font-weight: 700;
  color: #8b5cf6;
  border-top: 1px dashed #c4b5fd;
  padding-top: 0.15rem;
  margin-top: 0.2rem;
}

:deep(.math-cal) {
  font-family: 'Brush Script MT', 'KaTeX_Caligraphic', cursive, serif;
  font-size: 1.25em;
  margin-right: 0.1em;
}

:deep(.math-pass) {
  font-family: var(--font-mono);
  font-size: 0.85em;
  font-weight: 800;
  color: #059669;
  background: var(--pastel-mint-soft);
  padding: 0.15rem 0.6rem;
  border-radius: var(--radius-pill);
}

:deep(.math-arrow) {
  font-size: 1.1em;
  margin: 0 0.2em;
  color: #7b8090;
}
</style>
