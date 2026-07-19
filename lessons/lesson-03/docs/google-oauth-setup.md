# Как Получить `google_personal_refresh_token`

Публикация в Google Slides использует **личный** OAuth refresh token аккаунта `pavelkov007@gmail.com`. Client JSON уже лежит вне git:

`/Users/macbook/Documents/de-mentor-docs/google-service-account/client_secret_....apps.googleusercontent.com.json`

Redirect URI в client: `https://developers.google.com/oauthplayground`.

## Шаги (OAuth Playground)

1. Открой [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/).
2. Нажми ⚙️ (Settings) → включи **Use your own OAuth credentials**.
3. Вставь `client_id` и `client_secret` из JSON выше.
4. В списке scopes слева выбери:
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/presentations`
5. **Authorize APIs** → войди как `pavelkov007@gmail.com` → разреши доступ.
6. **Exchange authorization code for tokens**.
7. Скопируй `Refresh token` (строка вида `1//...`).

## Сохранить Токен На Mac

В текущей shell-сессии:

```bash
export google_personal_refresh_token='1//ВАШ_REFRESH_TOKEN'
```

Чтобы CLI видел токен через `launchctl` (как ожидает `mentor-lab`):

```bash
launchctl setenv google_personal_refresh_token '1//ВАШ_REFRESH_TOKEN'
```

Проверка:

```bash
launchctl getenv google_personal_refresh_token | wc -c
# должно быть >> 0
```

## Публикация Урока 03

```bash
cd ~/Projects/de-mentor
export google_personal_refresh_token="$(launchctl getenv google_personal_refresh_token)"

python3 mentor-lab.py slides publish greenplum-query-tuning \
  --confirm-account pavelkov007@gmail.com \
  --oauth-client-json /Users/macbook/Documents/de-mentor-docs/google-service-account/client_secret_177388438371-pa06utp6g6j32furdm0k96iphfkdu1vr.apps.googleusercontent.com.json
```

После publish обнови `google_slides_url` в:

- `src/mentor_lab/lesson_routes.py` (`LESSON_03_ROUTE`)
- `lessons/lesson-03/docs/lesson.yaml`
- ссылки в `README.md` и `lessons/lesson-03/docs/README.md`

Затем:

```bash
python3 mentor-lab.py slides verify greenplum-query-tuning \
  --confirm-account pavelkov007@gmail.com \
  --oauth-client-json /Users/macbook/Documents/de-mentor-docs/google-service-account/client_secret_177388438371-pa06utp6g6j32furdm0k96iphfkdu1vr.apps.googleusercontent.com.json

python3 mentor-lab.py lesson-release greenplum-query-tuning verify
```

## Важно

- Не коммить refresh token и client secret в git.
- Рабочий аккаунт `pavel.a.kovalev@1win.pro` для publish запрещён guard'ом CLI.
