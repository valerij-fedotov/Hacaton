<template>
  <div class="app">
    <TheHeader />
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import TheHeader from "./components/TheHeader.vue";
</script>

<style>
h1,
h2,
h3,
h4,
h5,
h6 {
  color: #3ecf8e;
}

* {
  box-sizing: border-box;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
body {
  margin: 0;
  background: #f3f4f6;
}
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
<script lang="ts">
export default {};
</script>