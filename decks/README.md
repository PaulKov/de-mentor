# Каталог Презентаций

Этот каталог фиксирует ту же таксономию, которую используем в Google Drive: корневая папка `lessons`, затем направление, затем конкретный урок. Так презентации можно развивать независимо от учебных документов и не переименовывать старые пути без отдельной миграции.

## Drive-Таксономия

| Направление | Урок | Папка В Drive | Git Source | Артефакт |
| --- | --- | --- | --- | --- |
| Greenplum | Lesson 01 | `lessons/Greenplum/Lesson 01 - MPP foundations` | [greenplum-theory](https://github.com/PaulKov/de-mentor/tree/master/decks/greenplum-theory) | [greenplum-theory.pptx](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx) |
| Greenplum | Lesson 02 | `lessons/Greenplum/Lesson 02 - Partitioning, statistics and incremental loads` | [greenplum-partitioning-theory](https://github.com/PaulKov/de-mentor/tree/master/decks/greenplum-partitioning-theory) | [greenplum-partitioning-theory.pptx](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-partitioning-theory.pptx) |

## Публикация В Google Slides

Публикация разрешена только в личный аккаунт `pavelkov007@gmail.com`. CLI сначала проверяет `--confirm-account`, затем фактический Google Drive account, и только потом делает операции в Drive.

Dry-run без сетевых операций:

```bash
python3 mentor-lab.py slides publish greenplum-partitioning \
  --dry-run \
  --confirm-account pavelkov007@gmail.com
```

Организовать существующую Lesson 02 презентацию в Drive-папке направления:

```bash
python3 mentor-lab.py slides publish greenplum-partitioning \
  --confirm-account pavelkov007@gmail.com \
  --oauth-client-json /Users/macbook/Documents/de-mentor-docs/google-service-account/client_secret_177388438371-pa06utp6g6j32furdm0k96iphfkdu1vr.apps.googleusercontent.com.json
```

Проверить папку, доступ “anyone with link: reader” и количество слайдов:

```bash
python3 mentor-lab.py slides verify greenplum-partitioning \
  --confirm-account pavelkov007@gmail.com \
  --oauth-client-json /Users/macbook/Documents/de-mentor-docs/google-service-account/client_secret_177388438371-pa06utp6g6j32furdm0k96iphfkdu1vr.apps.googleusercontent.com.json
```

Refresh token читается из `google_personal_refresh_token`; можно переопределить имя переменной через `--refresh-token-env`.

## Правило Для Новых Направлений

Для ClickHouse, Hadoop, Spark и Postgres добавляем новые direction folders рядом с `Greenplum`, например `lessons/ClickHouse/Lesson 01 - ...`. В git сначала добавляем source deck в `decks/<direction>-<lesson>-...`, затем регистрируем маршрут в `SlideAssetCatalog`, и только после этого публикуем в Google Slides.
