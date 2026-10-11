<script setup lang="ts">
import Navigation from '~/components/Navigation.vue'
import CustomCursor from '~/components/CustomCursor.vue'
</script>

<template>
  <div class="vedanam-app-shell">
    <!-- Subtle Pastel Gradient Underlayer for Glassmorphism Refraction -->
    <div class="ambient-blobs-layer" aria-hidden="true">
      <div class="ambient-blob blob-1" />
      <div class="ambient-blob blob-2" />
      <div class="ambient-blob blob-3" />
      <div class="ambient-blob blob-4" />
    </div>

    <!-- Interactive Glass Cursor Follower -->
    <CustomCursor />

    <!-- Exact Glassmorphic Floating Header (ledup.pt style) -->
    <Navigation />

    <!-- Active Page Content -->
    <NuxtPage />
  </div>
</template>

<style>
.vedanam-app-shell {
  min-height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  position: relative;
  overflow-x: hidden;
}
</style>
