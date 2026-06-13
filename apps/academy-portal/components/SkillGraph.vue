<script setup lang="ts">
import type { SkillNode } from '~/composables/useSessionState'

defineProps<{
  nodes: SkillNode[]
}>()
</script>

<template>
  <div class="skill-list">
    <article v-for="node in nodes" :key="node.code" class="skill-node">
      <span>{{ node.level }}</span>
      <strong>{{ node.title }}</strong>
      <p>{{ node.evidence }}</p>
    </article>
  </div>
</template>
