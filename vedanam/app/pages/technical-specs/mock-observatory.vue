<script setup lang="ts">
import MockDualBookObservatory from '~/components/specs/MockDualBookObservatory.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const onUpdateMock = (newMock: 'ascent' | 'relief' | 'observatory') => {
  if (newMock === 'ascent') router.push('/technical-specs/mock-ascent')
  else if (newMock === 'relief') router.push('/technical-specs/mock-relief')
  else router.push('/technical-specs/mock-observatory')
}
</script>

<template>
  <div class="mock-page-container">
    <MockSwitcherBar
      active-mock="observatory"
      @update:active-mock="onUpdateMock"
    />
    <MockDualBookObservatory />
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
