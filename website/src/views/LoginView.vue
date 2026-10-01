<script setup>
import { ref } from 'vue'
import { validateToken } from '../utils/auth'

const password = ref('')
const emit = defineEmits(['logged-in'])

function submit() {
  if (validateToken(password.value)) {
    sessionStorage.setItem('valet-access-token', password.value)
    emit('logged-in')
  } else {
    alert('Неверный пароль')
  }
}
</script>

<template>
  <section class="flex min-h-screen items-center justify-center p-6">
    <div class="w-full max-w-md rounded-xl bg-white p-8 shadow-lg">
      <h1 class="mb-6 text-2xl font-bold">Вход в график</h1>
      <label class="mb-2 block text-sm font-medium">Пароль</label>
      <input v-model="password" type="password" class="mb-4 w-full rounded-lg border border-slate-300 p-3 focus:outline-none focus:ring-2 focus:ring-sky-500" placeholder="Введите пароль" />
      <button @click="submit" class="w-full rounded-lg bg-sky-600 px-4 py-3 font-semibold text-white hover:bg-sky-700">Войти</button>
    </div>
  </section>
</template>
