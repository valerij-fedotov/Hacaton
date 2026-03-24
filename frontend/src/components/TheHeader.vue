<script lang="ts">
import { RouterLink } from "vue-router";
export default {
  name: "TheHeader",
  components: { RouterLink }
};
</script>


<template>
  <header class="header">
    <div class="header__container">
      <RouterLink to="/">
        <img
          src="/src/assets/images/image.png"
          alt="logo"
          class="header__logo"
        />
      </RouterLink>
      <div class="header__nav">
        <RouterLink class="header__nav-link" to="/">Home</RouterLink>
        <RouterLink class="header__nav-link" to="/tables">Tables</RouterLink>
        <RouterLink class="header__nav-link" to="/create-form">Create Form</RouterLink>
      </div>
    </div>
  </header>
</template>

<style scoped lang="css">
header {
  margin: 0;
  padding: 0;
  background-color: rgb(87, 87, 87);
  width: 100%;
  position: sticky;
}

a.router-link-exact-active {
  text-decoration: underline;
}

a {
  font-size: 18px;
}

.header__container {
  display: flex;
  justify-content: space-between;
  padding: 20px 30px;
  align-items: center;
  width: 100%;
}

.header__logo {
  background-color: red;
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

.header__nav {
  display: flex;
  gap: 20px;
}
</style>

