<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MockMountainAscent from '~/components/specs/MockMountainAscent.vue'
import MockTopographicRelief from '~/components/specs/MockTopographicRelief.vue'
import MockDualBookObservatory from '~/components/specs/MockDualBookObservatory.vue'
import MockSwitcherBar from '~/components/specs/MockSwitcherBar.vue'

const route = useRoute()
const router = useRouter()

const activeMock = ref<'ascent' | 'relief' | 'observatory'>('ascent')

onMounted(() => {
  if (route.query.mock === 'relief' || route.query.mock === 'observatory' || route.query.mock === 'ascent') {
    activeMock.value = route.query.mock as any
  }
})

const onUpdateMock = (newMock: 'ascent' | 'relief' | 'observatory') => {
  activeMock.value = newMock
  router.replace({ query: { ...route.query, mock: newMock } })
}

const activeComponent = computed(() => {
  switch (activeMock.value) {
    case 'relief':
      return MockTopographicRelief
    case 'observatory':
      return MockDualBookObservatory
    case 'ascent':
    default:
      return MockMountainAscent
  }
})
</script>

<template>
  <div class="technical-specs-alpine-hub">
    <!-- Top Floating Alpine Studio Switcher Dock -->
    <MockSwitcherBar
      :active-mock="activeMock"
      @update:active-mock="onUpdateMock"
    />

    <!-- Active 3D Mountain Climb Mock Experience -->
    <transition name="mock-fade" mode="out-in">
      <component :is="activeComponent" :key="activeMock" />
    </transition>
  </div>
</template>

<style scoped>
.technical-specs-alpine-hub {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background-color: #f8fafc;
  overflow: hidden;
}

.mock-fade-enter-active,
.mock-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.mock-fade-enter-from {
  opacity: 0;
  transform: scale(0.98);
}

.mock-fade-leave-to {
  opacity: 0;
  transform: scale(1.02);
}
</style>
