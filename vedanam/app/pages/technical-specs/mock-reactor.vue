<script setup lang="ts">
import MockSpatialHolo from '~/components/specs/MockSpatialHolo.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const handleUpdate = (val: string) => {
  if (val === 'synth') router.push('/technical-specs/mock-synth')
  else if (val === 'tactical') router.push('/technical-specs/mock-tactical')
}
</script>

<template>
  <div class="mock-standalone-page">
    <MockSwitcherBar active-mock="spatial" @update:active-mock="handleUpdate" />
    <MockSpatialHolo />
  </div>
</template>

<style scoped>
.mock-standalone-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #05060a;
}
</style>
