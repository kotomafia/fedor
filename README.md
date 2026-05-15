# fed0R

Discord-бот для модерации текста и изображений: бот → FastAPI → Celery → ML (токсичность + OCR).

## Стек

- **bot** — discord.py, отправка контента в API
- **api** — FastAPI, очереди Celery (`inference_text`, `inference_image`)
- **Redis** — брокер Celery
- **Postgres** — вердикты, кеш, статистика
- **ML** — `cointegrated/rubert-tiny-toxicity`, `s-nlp/russian_toxicity_classifier`, EasyOCR

## Быстрый старт

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r api/ml/requirements-ml.txt
copy .env.example .env
# Заполните DISCORD_BOT_TOKEN в .env
docker compose up -d redis postgres
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Запуск (отдельные терминалы или задачи VS Code «Полный запуск»):

```powershell
python -m api
python -m celery -A api.celery_app:celery_app worker -Q inference_text -l info --pool=solo
python -m celery -A api.celery_app:celery_app worker -Q inference_image -l info --pool=solo
python -m bot
```

## Переменные окружения

Скопируйте `.env.example` в `.env`. Обязательно:

| Переменная | Описание |
|------------|----------|
| `DISCORD_BOT_TOKEN` | Токен бота из [Discord Developer Portal](https://discord.com/developers/applications) |
| `DATABASE_URL` | Должен совпадать с `POSTGRES_*` (см. `.env.example`) |
| `REDIS_URL` | Redis для Celery |

Пороги модерации: `THRESHOLD_UNCERTAIN`, `THRESHOLD_TOXIC`, `THRESHOLD_TOXIC_OCR`.

## Безопасность

- **Никогда не коммитьте `.env`** — в репозитории только `.env.example`.
- Если токен мог попасть в git или в чат — **сбросьте его** в Developer Portal.
- API **без аутентификации** — не выставляйте порт 8000 в интернет без reverse proxy, firewall или API key.
- В Postgres сохраняется текст сообщений (`verdicts.content`) — не публикуйте дампы БД.
- Перед `git push`: `git status` и `git check-ignore -v .env`.

## Модели и лицензии

Веса скачиваются с Hugging Face при первом запуске. Проверьте лицензии:

- [rubert-tiny-toxicity](https://huggingface.co/cointegrated/rubert-tiny-toxicity)
- [russian_toxicity_classifier](https://huggingface.co/s-nlp/russian_toxicity_classifier)

Код проекта — MIT (см. `LICENSE`).

## Структура

Монорепозиторий для локальной разработки. На GitHub проект разбит на четыре репозитория, объединённых через `git subtree` (не submodule):

| Репозиторий | Содержимое |
|-------------|------------|
| `fedor` | docker-compose, alembic, `.env.example`, `requirements.txt` |
| `fedor-api` | FastAPI, Celery, БД (subtree `api/` в `fedor`) |
| `fedor-bot` | Discord client (subtree `bot/` в `fedor`) |
| `fedor-ml` | модели токсичности и OCR (subtree `api/ml/` в `fedor` и `ml/` в `fedor-api`) |

```
fedor/                 мета-репозиторий
├── api/               ← subtree fedor-api
│   └── ml/            ← subtree fedor-ml
├── bot/               ← subtree fedor-bot
├── alembic/
└── docker-compose.yml
```

`git clone https://github.com/kotomafia/fedor.git` сразу даёт полное рабочее дерево, флаг `--recurse-submodules` не нужен.

## Синхронизация с под-репозиториями

Named remotes (создаются один раз при клонировании):

```powershell
git remote add fedor-api https://github.com/kotomafia/fedor-api.git
git remote add fedor-bot https://github.com/kotomafia/fedor-bot.git
git remote add fedor-ml  https://github.com/kotomafia/fedor-ml.git
```

Обёртка [`scripts/sync-subtrees.ps1`](scripts/sync-subtrees.ps1):

```powershell
.\scripts\sync-subtrees.ps1 -Direction pull              # подтянуть все три subtree
.\scripts\sync-subtrees.ps1 -Direction push              # запушить все три
.\scripts\sync-subtrees.ps1 -Direction push -Only api/ml # только один
```

Порядок push в скрипте: `bot`, `api/ml`, `api`. **Сначала `api/ml` → `fedor-ml`, потом `api` → `fedor-api`** — иначе очередной `git subtree pull` в `fedor-api` приведёт к merge-конфликту между «ml из api-subtree» и «ml из ml-subtree».