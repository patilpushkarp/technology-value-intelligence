<script setup lang="ts">
import MockArchitecturalCity from '~/components/specs/MockArchitecturalCity.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const handleUpdate = (val: string) => {
  if (val === 'flow') router.push('/technical-specs/mock-flow')
  else if (val === 'graph') router.push('/technical-specs/mock-graph')
}
</script>

<template>
  <div class="mock-light-page">
    <MockSwitcherBar active-mock="city" @update:active-mock="handleUpdate" />
    <MockArchitecturalCity />
  </div>
</template>

<style scoped>
.mock-light-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #fafafc;
}
</style>
