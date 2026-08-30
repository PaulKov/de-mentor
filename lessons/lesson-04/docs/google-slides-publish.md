# Публикация Lesson 04 в Google Slides

Текущая нативная публикация: [Lesson 04 — Apache Spark foundations and
PySpark](https://docs.google.com/presentation/d/1U_u3cwqdCzz2oRoa_w5BT7btbLqUlBSou3rJe2YXni0/edit?usp=sharing).
Владелец — `pavelkov007@gmail.com`, в презентации 66 слайдов.

Историческая миграция 42 → 60 и текущее обновление 60 → 66 выполнены нативными
Google Slides API-объектами, поэтому текст, схемы и матрицы остаются
редактируемыми. Воспроизводимый генератор плана и безопасная последовательность
readback/reorder описаны в `decks/apache-spark-foundations/README.md`.

Публикация защищена проверкой аккаунта: целевой владелец —
`pavelkov007@gmail.com`. CLI сначала запрашивает email через Google Drive API и
останавливается до загрузки, если активен другой аккаунт.

## Что потребуется

1. OAuth client JSON для desktop/web приложения Google Cloud.
2. Refresh token аккаунта `pavelkov007@gmail.com` со scope:
   - `https://www.googleapis.com/auth/drive`;
   - `https://www.googleapis.com/auth/presentations`.
3. Готовый локальный файл
   `lessons/lesson-04/artifacts/apache-spark-foundations-theory.pptx`.

Секреты не хранятся в репозитории. Refresh token передаётся через переменную
`google_personal_refresh_token`, а путь к client JSON — через аргумент CLI.

```bash
export GOOGLE_ACCOUNT='pavelkov007@gmail.com'
export GOOGLE_CLIENT_JSON='/absolute/path/to/oauth-client.json'
export google_personal_refresh_token='1//REDACTED'

python3 mentor-lab.py slides publish spark-foundations \
  --confirm-account "$GOOGLE_ACCOUNT" \
  --oauth-client-json "$GOOGLE_CLIENT_JSON"
```

Публикатор создаст или переиспользует папки:

```text
lessons/Spark/Lesson 04 - Apache Spark foundations and PySpark
```

После публикации URL нужно записать в `docs/lesson.yaml` и
`src/mentor_lab/lesson_routes.py`, затем выполнить:

```bash
python3 mentor-lab.py slides verify spark-foundations \
  --confirm-account "$GOOGLE_ACCOUNT" \
  --oauth-client-json "$GOOGLE_CLIENT_JSON"

python3 mentor-lab.py lesson-release spark-foundations verify
```
