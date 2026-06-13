# Academy Portal

Nuxt-портал для `Academy Experience v5`: один экран для ментора и ученика с current stage, timeline, skill graph, copy-command кнопками, evidence checklist и командами проверки.

## Запуск

```bash
python3 mentor-lab.py session greenplum start --student Иван --output artifacts/sessions/ivan
MENTOR_LAB_SESSION=artifacts/sessions/ivan/session.json npm --prefix apps/academy-portal run dev
```

Портал написан на Vue 3 + Nuxt 3 + Vite. Если переменная `MENTOR_LAB_SESSION` не задана, приложение использует `public/session.sample.json`.

## Проверка

```bash
npm --prefix apps/academy-portal install
npm --prefix apps/academy-portal run build
python3 mentor-lab.py lesson-doctor greenplum
```
