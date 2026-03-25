<template>
  <header class="header">
    <div class="header__container">
      <RouterLink to="/" class="header__logo-link">
        <img
          src="/src/assets/images/image.png"
          alt="logo"
          class="header__logo"
        />
      </RouterLink>

      <!-- Бургер-кнопка (только на мобильных) -->
      <button
        class="header__burger"
        :class="{ 'header__burger--active': isMenuOpen }"
        @click="toggleMenu"
        aria-label="Меню"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <!-- Навигация -->
      <nav class="header__nav" :class="{ 'header__nav--open': isMenuOpen }">
        <RouterLink class="header__nav-link" to="/" @click="closeMenu">
          Home
        </RouterLink>
        <RouterLink class="header__nav-link" to="/tables" @click="closeMenu">
          Tables
        </RouterLink>
        <RouterLink
          class="header__nav-link"
          to="/create-form"
          @click="closeMenu"
        >
          Create Form
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";

const isMenuOpen = ref(false);

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

const closeMenu = () => {
  isMenuOpen.value = false;
};
</script>

<style scoped>
.header {
  background-color: #121212;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid #afafaf;
}

.header__container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 30px;
  max-width: 1400px;
  margin: 0 auto;
}

.header__logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.header__logo {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.header__logo:hover {
  transform: scale(1.05);
}

.header__nav {
  display: flex;
  gap: 32px;
  align-items: center;
}

.header__nav-link {
  color: #ffffff;
  text-decoration: none;
  font-size: 18px;
  font-weight: 500;
  transition: color 0.2s ease, border-bottom 0.2s ease;
  padding: 8px 0;
  position: relative;
}

.header__nav-link:hover {
  color: #3ecf8e;
}

.header__nav-link.router-link-active {
  color: #3ecf8e;
  border-bottom: 2px solid #3ecf8e;
}

/* Бургер-кнопка (скрыта на десктопе) */
.header__burger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 30px;
  height: 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 10;
}

.header__burger span {
  width: 100%;
  height: 2px;
  background-color: #ffffff;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.header__burger--active span:nth-child(1) {
  transform: translateY(11px) rotate(45deg);
}

.header__burger--active span:nth-child(2) {
  opacity: 0;
}

.header__burger--active span:nth-child(3) {
  transform: translateY(-11px) rotate(-45deg);
}

/* Адаптивность */
@media (max-width: 768px) {
  .header__container {
    padding: 12px 20px;
  }

  .header__burger {
    display: flex;
  }

  .header__nav {
    position: fixed;
    top: 0;
    right: -100%;
    width: 70%;
    max-width: 300px;
    height: 100vh;
    background-color: #121212;
    flex-direction: column;
    justify-content: center;
    gap: 32px;
    padding: 80px 20px 20px;
    transition: right 0.3s ease;
    box-shadow: -2px 0 10px rgba(0, 0, 0, 0.5);
    z-index: 9;
  }

  .header__nav--open {
    right: 0;
  }

  .header__nav-link {
    font-size: 20px;
    padding: 12px;
    width: 100%;
    text-align: center;
    border-radius: 8px;
  }

  .header__nav-link:hover {
    background-color: #1e1e1e;
  }

  .header__nav-link.router-link-active {
    border-bottom: none;
    background-color: #1e1e1e;
    color: #3ecf8e;
  }
}

/* Дополнительно: затемнение фона при открытом меню (опционально) */
.header__nav::before {
  content: "";
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

@media (max-width: 768px) {
  .header__nav--open::before {
    display: block;
    opacity: 1;
  }
}
</style>