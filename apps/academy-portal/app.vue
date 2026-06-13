<script setup lang="ts">
const { session, source, reload } = await useSessionState()

const currentStage = computed(() => session.value?.current_stage)
const nextStage = computed(() => {
  if (!session.value || !currentStage.value) {
    return undefined
  }

  const index = session.value.stages.findIndex(
    stage => stage.code === currentStage.value?.code
  )
  return session.value.stages[index + 1]
})
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" aria-label="Навигация урока">
      <div class="brand">
        <span class="brand-mark">GP</span>
        <div>
          <strong>Academy Experience v5</strong>
          <small>Vue 3 + Nuxt 3 + Vite</small>
        </div>
      </div>

      <nav class="stage-nav" aria-label="Этапы">
        <a
          v-for="stage in session?.stages"
          :key="stage.code"
          class="stage-link"
          :class="{ active: stage.code === currentStage?.code }"
          href="#current-stage"
        >
          <span>{{ stage.timebox }}</span>
          {{ stage.title }}
        </a>
      </nav>
    </aside>

    <main>
      <header class="topbar">
        <div>
          <p class="muted">Greenplum mentor cockpit</p>
          <h1>{{ session?.student_name }} · {{ session?.lab_name }}</h1>
        </div>
        <button class="quiet-button" type="button" @click="reload">
          Обновить state
        </button>
      </header>

      <section id="current-stage" class="hero current-stage" aria-label="current stage">
        <div>
          <p class="muted">current stage</p>
          <h2>{{ currentStage?.title }}</h2>
          <p>{{ currentStage?.mentor_focus }}</p>
        </div>
        <div class="stage-command">
          <span>{{ currentStage?.timebox }}</span>
          <CommandCard
            v-if="currentStage"
            class="copy-command"
            title="Команда этапа"
            :command="currentStage.command"
          />
        </div>
      </section>

      <div class="workspace-grid">
        <section class="panel timeline-panel">
          <div class="panel-heading">
            <p class="muted">timeline</p>
            <h2>Лента занятия</h2>
          </div>
          <ol class="timeline">
            <li v-for="stage in session?.stages" :key="stage.code">
              <span>{{ stage.timebox }}</span>
              <strong>{{ stage.title }}</strong>
              <p>{{ stage.student_action }}</p>
            </li>
          </ol>
        </section>

        <section class="panel">
          <div class="panel-heading">
            <p class="muted">commands</p>
            <h2>Быстрые команды</h2>
          </div>
          <div class="command-list">
            <CommandCard
              v-for="command in session?.commands"
              :key="command"
              class="copy-command"
              title="Скопировать"
              :command="command"
            />
          </div>
        </section>
      </div>

      <div class="workspace-grid lower-grid">
        <section class="panel skill-graph" aria-label="skill graph">
          <div class="panel-heading">
            <p class="muted">skill graph</p>
            <h2>Карта навыков</h2>
          </div>
          <SkillGraph :nodes="session?.skill_graph || []" />
        </section>

        <section class="panel evidence-panel">
          <div class="panel-heading">
            <p class="muted">evidence</p>
            <h2>Проверка понимания</h2>
          </div>
          <ul>
            <li>Ученик отличает QD, QE, gang, slice и Motion.</li>
            <li>Ученик объясняет, почему distribution key не равен partition key.</li>
            <li>Ученик показывает Heap/AO/AOCO через DDL и catalog checks.</li>
            <li>Submission проходит mentor-lab.py autograde-sql.</li>
            <li>Generated dataset готовится через mentor-lab.py dataset.</li>
          </ul>
        </section>
      </div>

      <section class="panel report-panel">
        <div>
          <p class="muted">handoff</p>
          <h2>Финальный отчет и следующий шаг</h2>
          <p>
            После урока запиши события и собери отчет командой
            <code>mentor-lab.py session greenplum report</code>.
          </p>
          <p v-if="nextStage">
            Следующий этап маршрута: <strong>{{ nextStage.title }}</strong>.
          </p>
        </div>
        <CommandCard
          class="copy-command"
          title="Session report"
          command="python3 mentor-lab.py session greenplum report --session artifacts/sessions/<name> --output artifacts/greenplum-session-report.md"
        />
      </section>

      <footer>
        <span>Источник состояния: {{ source }}</span>
        <span>{{ session?.portal.framework }}</span>
      </footer>
    </main>
  </div>
</template>
