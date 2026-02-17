# Руководство по GitHub и деплою веб-сервисов

## Что такое GitHub?

**GitHub — это хостинг кода** (git-репозиторий), а не сервер для запуска приложений.

- ✅ Хранит код (файлы проекта)
- ✅ История изменений (git)
- ✅ Совместная работа (pull requests, issues)
- ✅ GitHub Actions (автоматизация)
- ❌ **НЕ запускает** веб-сервисы с бэкендом

---

## Как запустить проект по ссылке?

### 1. **Статические сайты** (HTML/CSS/JS без бэкенда)

#### GitHub Pages (бесплатно)

**Для простых HTML/CSS/JS проектов:**

1. В репозитории: **Settings** → **Pages**
2. Source: выбери ветку (обычно `main`) и папку (обычно `/root`)
3. Сохрани
4. Через 1-2 минуты сайт будет доступен по адресу:
   ```
   https://твой-username.github.io/название-репо/
   ```

**Пример:** Если репо `one-good-action`, то ссылка будет:
```
https://waplebe.github.io/one-good-action/
```

**Ограничения:**
- Только статика (HTML/CSS/JS)
- Нет бэкенда (нельзя запускать Python/Node серверы)
- Нет баз данных

---

### 2. **Веб-сервисы с бэкендом** (Python/Node/Go и т.д.)

GitHub **не запускает** серверы. Нужны другие платформы:

#### **Vercel** (бесплатно, очень просто)

**Для:** Next.js, React, Node.js, Python, Go

1. Зайди на [vercel.com](https://vercel.com)
2. Войди через GitHub
3. **Add New Project** → выбери репозиторий
4. Vercel сам определит тип проекта и задеплоит
5. Получишь ссылку: `https://твой-проект.vercel.app`

**Автоматический деплой:** Каждый push в GitHub → автоматический деплой на Vercel.

**Пример для Python Flask:**
- Создай файл `vercel.json` в репо:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

---

#### **Netlify** (бесплатно)

**Для:** Статика, JAMstack, функции (serverless)

1. [netlify.com](https://netlify.com) → войди через GitHub
2. **Add new site** → **Import from Git** → выбери репо
3. Build settings (если нужны):
   - Build command: `npm install && npm run build`
   - Publish directory: `dist` или `build`
4. Деплой → ссылка: `https://случайное-имя.netlify.app`

**Автоматический деплой:** Push в GitHub → деплой на Netlify.

---

#### **Railway** (бесплатно с ограничениями)

**Для:** Любые серверы (Python, Node, Go, Rust, Docker)

1. [railway.app](https://railway.app) → войди через GitHub
2. **New Project** → **Deploy from GitHub repo**
3. Выбери репо
4. Railway определит тип проекта (Python/Node/etc)
5. Деплой → ссылка: `https://твой-проект.up.railway.app`

**Особенности:**
- Поддерживает базы данных (PostgreSQL, MySQL, Redis)
- Переменные окружения (.env)
- Логи в реальном времени

**Пример для Python Flask:**
- Создай `Procfile`:
```
web: python app.py
```
или
```
web: gunicorn app:app
```

---

#### **Render** (бесплатно с ограничениями)

**Для:** Веб-сервисы, статика, базы данных

1. [render.com](https://render.com) → войди через GitHub
2. **New** → **Web Service** → выбери репо
3. Настройки:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py` или `gunicorn app:app`
4. Деплой → ссылка: `https://твой-проект.onrender.com`

---

#### **Fly.io** (бесплатно с ограничениями)

**Для:** Docker, любые языки

1. Установи CLI: `curl -L https://fly.io/install.sh | sh`
2. В папке проекта: `fly launch`
3. Следуй инструкциям
4. Деплой: `fly deploy`
5. Ссылка: `https://твой-проект.fly.dev`

---

## Автоматический деплой через GitHub Actions

Можно настроить автоматический деплой при каждом push:

### Пример: деплой на Vercel через Actions

Создай файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

**Секреты** (Settings → Secrets):
- `VERCEL_TOKEN` — токен из Vercel Dashboard → Settings → Tokens
- `VERCEL_ORG_ID` и `VERCEL_PROJECT_ID` — из настроек проекта

---

## Что выбрать?

| Платформа | Для чего | Сложность | Бесплатно |
|-----------|----------|-----------|-----------|
| **GitHub Pages** | Статика (HTML/CSS/JS) | ⭐ Очень просто | ✅ Да |
| **Vercel** | React/Next.js/Node/Python | ⭐⭐ Просто | ✅ Да |
| **Netlify** | Статика + функции | ⭐⭐ Просто | ✅ Да |
| **Railway** | Любые серверы + БД | ⭐⭐⭐ Средне | ✅ Да (лимиты) |
| **Render** | Веб-сервисы + БД | ⭐⭐⭐ Средне | ✅ Да (лимиты) |
| **Fly.io** | Docker, любые языки | ⭐⭐⭐⭐ Сложно | ✅ Да (лимиты) |

---

## Пример: деплой Python Flask приложения

### 1. Структура проекта:
```
my-app/
├── app.py
├── requirements.txt
├── Procfile (для Railway/Render)
└── vercel.json (для Vercel)
```

### 2. `app.py`:
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from deployed app!</h1>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 3. `requirements.txt`:
```
Flask==3.0.0
gunicorn==21.2.0
```

### 4. `Procfile` (для Railway/Render):
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

### 5. Деплой:
- **Railway:** Импортируй репо → автоматически определит Python → деплой
- **Render:** Импортируй репо → Build: `pip install -r requirements.txt` → Start: `gunicorn app:app` → деплой
- **Vercel:** Импортируй репо → автоматически определит → деплой

---

## Итого

1. **GitHub** = хранилище кода, не сервер
2. **GitHub Pages** = для статики (HTML/CSS/JS)
3. **Vercel/Netlify/Railway/Render** = для веб-сервисов с бэкендом
4. **Автоматический деплой:** Push в GitHub → автоматический деплой на платформу

**Самый простой способ:** Vercel или Railway — подключи репо, всё работает автоматически.
