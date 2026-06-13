# Academy Session v1

`academy-session/v1` — стабильный JSON-контракт между core CLI `de-mentor` и frontend-сервисом `de-mentor-portal`.

Core генерирует `session.json`, портал только читает его через `MENTOR_LAB_SESSION`.

Минимальные требования:

- `contract_version = academy-session/v1`;
- `current_stage` соответствует одному из `stages`;
- `portal.repository = https://github.com/PaulKov/de-mentor-portal`;
- команды остаются обычными строками и могут копироваться из UI;
- `skill_graph` описывает наблюдаемые навыки и evidence.
