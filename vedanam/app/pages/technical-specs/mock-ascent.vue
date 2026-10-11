<script setup lang="ts">
import MockMountainAscent from '~/components/specs/MockMountainAscent.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const onUpdateMock = (newMock: 'ascent' | 'relief' | 'observatory') => {
  if (newMock === 'relief') router.push('/technical-specs/mock-relief')
  else if (newMock === 'observatory') router.push('/technical-specs/mock-observatory')
  else router.push('/technical-specs/mock-ascent')
}
</script>

<template>
  <div class="mock-page-container">
    <MockSwitcherBar
      active-mock="ascent"
      @update:active-mock="onUpdateMock"
    />
    <MockMountainAscent />
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
