<script setup>
const sampleDays = [
  { date: '2026-10-01', slots: [{ shift_name: 'Дневная', role_required: 'valet_day', employees: ['Иван'] }] },
  { date: '2026-10-02', slots: [{ shift_name: 'Ночная', role_required: 'valet_night', employees: ['Петр'] }] },
]
</script>

<template>
  <section class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Расписание</h1>
      <button class="rounded-lg border border-slate-300 bg-white px-3 py-2 hover:bg-slate-50">Фильтр</button>
    </div>
    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <article v-for="day in sampleDays" :key="day.date" class="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
        <h2 class="mb-3 text-lg font-semibold">{{ day.date }}</h2>
        <div v-for="slot in day.slots" :key="slot.shift_name" class="rounded-lg bg-slate-50 p-3">
          <div class="font-medium">{{ slot.shift_name }}</div>
          <div class="text-sm text-slate-600">Роль: {{ slot.role_required }}</div>
          <ul class="mt-2 text-sm">
            <li v-for="employee in slot.employees" :key="employee">{{ employee }}</li>
          </ul>
        </div>
      </article>
    </div>
  </section>
</template>
