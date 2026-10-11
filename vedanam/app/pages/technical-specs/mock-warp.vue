<script setup lang="ts">
import MockTacticalWarRoom from '~/components/specs/MockTacticalWarRoom.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const handleUpdate = (val: string) => {
  if (val === 'spatial') router.push('/technical-specs/mock-spatial')
  else if (val === 'synth') router.push('/technical-specs/mock-synth')
}
</script>

<template>
  <div class="mock-standalone-page">
    <MockSwitcherBar active-mock="tactical" @update:active-mock="handleUpdate" />
    <MockTacticalWarRoom />
  </div>
</template>

<style scoped>
.mock-standalone-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #05080f;
}
</style>
