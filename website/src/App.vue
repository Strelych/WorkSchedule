<script setup>
import { ref } from 'vue'
import LoginView from './views/LoginView.vue'
import ScheduleView from './views/ScheduleView.vue'

const isAuthenticated = ref(Boolean(sessionStorage.getItem('valet-access-token')))

function handleLogin() {
  isAuthenticated.value = true
}
</script>

<template>
  <main class="min-h-screen bg-slate-100 text-slate-800">
    <LoginView v-if="!isAuthenticated" @logged-in="handleLogin" />
    <ScheduleView v-else />
  </main>
</template>
