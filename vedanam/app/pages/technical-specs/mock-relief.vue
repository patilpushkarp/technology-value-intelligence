<script setup lang="ts">
import MockTopographicRelief from '~/components/specs/MockTopographicRelief.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const onUpdateMock = (newMock: 'ascent' | 'relief' | 'observatory') => {
  if (newMock === 'ascent') router.push('/technical-specs/mock-ascent')
  else if (newMock === 'observatory') router.push('/technical-specs/mock-observatory')
  else router.push('/technical-specs/mock-relief')
}
</script>

<template>
  <div class="mock-page-container">
    <MockSwitcherBar
      active-mock="relief"
      @update:active-mock="onUpdateMock"
    />
    <MockTopographicRelief />
  </div>
</template>

<style scoped>
.mock-page-container {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: #f8fafc;
  overflow: hidden;
}
</style>
