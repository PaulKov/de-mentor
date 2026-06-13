<script setup lang="ts">
const props = defineProps<{
  title: string
  command: string
}>()

const copied = ref(false)

const copy = async () => {
  await navigator.clipboard.writeText(props.command)
  copied.value = true
  window.setTimeout(() => {
    copied.value = false
  }, 1200)
}
</script>

<template>
  <article class="command-card">
    <div>
      <span>{{ title }}</span>
      <code>{{ command }}</code>
    </div>
    <button type="button" @click="copy">
      {{ copied ? 'Скопировано' : 'Копировать' }}
    </button>
  </article>
</template>
