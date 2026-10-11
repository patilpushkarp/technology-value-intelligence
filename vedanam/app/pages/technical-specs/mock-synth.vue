<script setup lang="ts">
import MockCapitalFlowRibbon from '~/components/specs/MockCapitalFlowRibbon.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const handleUpdate = (val: string) => {
  if (val === 'city') router.push('/technical-specs/mock-city')
  else if (val === 'graph') router.push('/technical-specs/mock-graph')
}
</script>

<template>
  <div class="mock-light-page">
    <MockSwitcherBar active-mock="flow" @update:active-mock="handleUpdate" />
    <MockCapitalFlowRibbon />
  </div>
</template>

<style scoped>
.mock-light-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
}
</style>
