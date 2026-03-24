<template>
  <div class="form-constructor__container">
    <BlockList />
    <FormField />
  </div>
</template>

<script setup>
//import FormField from "@/components/FormField.vue";
import BlockList from "@/components/BlockList.vue";
</script>

<style lang="css">
.form-constructor__container {
  display: flex;
  justify-content: center;
  width: 100%;
}
</style>