<script setup lang="ts">
import MockHardwareSynth from '~/components/specs/MockHardwareSynth.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const handleUpdate = (val: string) => {
  if (val === 'spatial') router.push('/technical-specs/mock-spatial')
  else if (val === 'tactical') router.push('/technical-specs/mock-tactical')
}
</script>

<template>
  <div class="mock-standalone-page">
    <MockSwitcherBar active-mock="synth" @update:active-mock="handleUpdate" />
    <MockHardwareSynth />
  </div>
</template>

<style scoped>
.mock-standalone-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #0b0c10;
}
</style>
