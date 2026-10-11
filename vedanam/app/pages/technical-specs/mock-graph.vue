<script setup lang="ts">
import MockKnowledgeGraphGallery from '~/components/specs/MockKnowledgeGraphGallery.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const handleUpdate = (val: string) => {
  if (val === 'city') router.push('/technical-specs/mock-city')
  else if (val === 'flow') router.push('/technical-specs/mock-flow')
}
</script>

<template>
  <div class="mock-light-page">
    <MockSwitcherBar active-mock="graph" @update:active-mock="handleUpdate" />
    <MockKnowledgeGraphGallery />
  </div>
</template>

<style scoped>
.mock-light-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #f8f9fb;
}
</style>
