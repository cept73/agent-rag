# Project RAG API

## Структура

```text
app/
├── main.py    # запуск сервера и CLI-импорт
├── api.py     # REST API и авторизация
├── db.py      # SQLite и CRUD материалов
├── rag.py     # RAG-поиск по слоту
└── schemas.py # модели запросов
```

Сервис хранит материалы в SQLite и разделяет их по слотам (`slot`). RAG-поиск использует только материалы выбранного слота.

## Настройка

В `.env`:

```env
GROQ_API_KEY=your_groq_key
RAG_PORT=8000
RAG_API_TOKEN=your_secret_token
```

Запуск:

```bash
python3 main.py
```

## Консольный импорт

Импорт всех текстовых UTF-8 файлов из папки, включая вложенные папки:

```bash
python3 main.py import --folder ./materials --slot project-a
```

Команда возвращает JSON со списками `imported` и `skipped`. Имя файла сохраняется относительно указанной папки.

## API

Для авторизации используйте заголовок:

```http
X-API-Token: your_secret_token
```

или:

```http
Authorization: Bearer your_secret_token
```

### Добавить материал

```bash
curl -X POST http://localhost:8000/materials \
  -H "X-API-Token: your_secret_token" \
  -H "Content-Type: application/json" \
  -d '{"slot":"project-a","name":"team.md","content":"Проектом руководит Елена."}'
```

### Получить список материалов

```bash
curl "http://localhost:8000/materials?slot=project-a" \
  -H "X-API-Token: your_secret_token"
```

Без `slot` возвращаются материалы всех слотов. Содержимое материалов в списке не возвращается.

### Удалить материал

```bash
curl -X DELETE http://localhost:8000/materials/1 \
  -H "X-API-Token: your_secret_token"
```

### Выполнить RAG-поиск

```bash
curl -X POST http://localhost:8000/rag/search \
  -H "X-API-Token: your_secret_token" \
  -H "Content-Type: application/json" \
  -d '{"slot":"project-a","params":["Кто руководит проектом?"]}'
```

Один запрос:

```json
{"success":true,"answer":"Елена."}
```

Несколько запросов:

```json
{"success":true,"answers":["Елена.","В проекте 5 участников."]}
```

### Проверка состояния

```bash
curl http://localhost:8000/health
```

База данных по умолчанию — `rag.db`. Путь можно изменить переменной `RAG_DB_PATH` в `.env`.

## Запуск в фоне через nuhup

Быстрый временный вариант:
```bash
nohup python3 main.py > rag.log 2>&1 &
```

Но для production лучше systemd: он автоматически перезапустит процесс после сбоя и запустит его после перезагрузки сервера.

## Запуск в фоне через systemd

Создайте unit-файл:

```bash
sudo mcedit /etc/systemd/system/agent-rag.service
```

Содержимое файла:

```ini
[Unit]
Description=Agent RAG API
After=network.target

[Service]
User=cept
WorkingDirectory=/var/www/agent-rag
ExecStart=/home/cept/miniconda3/bin/python /var/www/agent-rag/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now agent-rag
```

Проверка состояния и логов:

```bash
sudo systemctl status agent-rag
journalctl -u agent-rag -f
```

Перезапуск после изменений:

```bash
sudo systemctl restart agent-rag
```
