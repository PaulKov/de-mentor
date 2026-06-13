# Student Prep: Greenplum Lesson 01

Этот runbook нужен ученику до первого урока. Цель простая: прийти не с борьбой за Docker, а сразу с готовым Greenplum-стендом и открытым `psql`.

Связанные материалы:

- рабочая тетрадь: [рабочая тетрадь ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md)
- план урока: [план урока](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/README.md)
- README стенда: [README стенда Greenplum](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/README.md)
- упрощенный маршрут ментора: [упрощенный маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/simple-path.md)

## Что Подготовить

Минимально:

- ноутбук с 8 GB RAM или больше, лучше 16 GB;
- 10-15 GB свободного места под Docker image, container и volume;
- стабильный интернет для `git clone` и `docker pull`;
- свободный локальный порт `15432`;
- Git;
- Python 3.9+;
- Docker с Docker Compose v2;
- терминал: Terminal/iTerm на macOS, PowerShell на Windows, shell на Linux.

Не нужно ставить локальный PostgreSQL или `psql`: команда `mentor-lab.py psql greenplum` открывает `psql` внутри контейнера.

## Stage 1: Общая Проверка Для Всех ОС

Команды:

```bash
git --version
docker --version
docker compose version
python3 --version
```

На Windows:

```powershell
git --version
docker --version
docker compose version
py --version
```

Что должно получиться:

- `docker compose version` показывает Compose v2;
- Docker Desktop или Docker Engine уже запущен;
- Python запускается из терминала;
- Git доступен из терминала.

## Stage 2: macOS

Установи:

- Docker Desktop for Mac;
- Git, если его еще нет;
- Python 3.9+.

Проверка:

```bash
docker compose version
git --version
python3 --version
```

Подготовка репозитория:

```bash
git clone https://github.com/PaulKov/de-mentor.git
cd de-mentor
python3 mentor-lab.py doctor
python3 mentor-lab.py info greenplum
```

Smoke-check перед уроком:

```bash
docker pull docker.io/woblerr/greenplum:7.1.0
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

Внутри `psql`:

```sql
SELECT 1;
\q
```

Остановить стенд до урока, если хочешь освободить ресурсы:

```bash
python3 mentor-lab.py down greenplum
```

## Stage 3: Windows

Установи:

- Docker Desktop for Windows;
- WSL 2 backend должен быть включен в Docker Desktop;
- Git for Windows;
- Python 3.9+ или Python Launcher `py`.

Проверь в PowerShell:

```powershell
docker compose version
git --version
py --version
```

Подготовка репозитория:

```powershell
git clone https://github.com/PaulKov/de-mentor.git
cd de-mentor
py mentor-lab.py doctor
py mentor-lab.py info greenplum
```

Smoke-check перед уроком:

```powershell
docker pull docker.io/woblerr/greenplum:7.1.0
py mentor-lab.py up greenplum
py mentor-lab.py check greenplum
py mentor-lab.py psql greenplum
```

Внутри `psql`:

```sql
SELECT 1;
\q
```

Типовые причины проблем на Windows:

- Docker Desktop не запущен;
- WSL 2 backend выключен;
- virtualization отключена в BIOS/UEFI;
- PowerShell открыт не в папке `de-mentor`;
- корпоративный VPN/proxy блокирует Docker Hub.

## Stage 4: Linux

Установи:

- Docker Engine;
- Docker Compose plugin;
- Git;
- Python 3.9+.

Проверь:

```bash
docker --version
docker compose version
git --version
python3 --version
```

Проверь, что Docker доступен без `sudo`:

```bash
docker ps
```

Если команда требует `sudo`, заранее добавь пользователя в docker group и перелогинься:

```bash
sudo usermod -aG docker "$USER"
```

Подготовка репозитория:

```bash
git clone https://github.com/PaulKov/de-mentor.git
cd de-mentor
python3 mentor-lab.py doctor
python3 mentor-lab.py info greenplum
```

Smoke-check перед уроком:

```bash
docker pull docker.io/woblerr/greenplum:7.1.0
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

Внутри `psql`:

```sql
SELECT 1;
\q
```

## Stage 5: Что Принести Ментору, Если Не Завелось

Скопируй вывод этих команд:

```bash
python3 mentor-lab.py doctor
docker compose version
docker ps
python3 mentor-lab.py status greenplum
python3 mentor-lab.py logs greenplum
```

На Windows замени `python3` на `py`:

```powershell
py mentor-lab.py doctor
docker compose version
docker ps
py mentor-lab.py status greenplum
py mentor-lab.py logs greenplum
```

## Быстрая Самопроверка Готовности

Ученик готов к уроку, если:

- `mentor-lab.py doctor` отработал;
- `mentor-lab.py up greenplum` поднял контейнер;
- `mentor-lab.py check greenplum` показывает `PASS`;
- `mentor-lab.py psql greenplum` открывает `psql`;
- порт `15432` не занят другим сервисом;
- есть понимание, как остановить стенд: `mentor-lab.py down greenplum`.

Полезная команда для повтора этого runbook:

```bash
python3 mentor-lab.py runbook greenplum prep
```

Windows:

```powershell
py mentor-lab.py runbook greenplum prep
```
