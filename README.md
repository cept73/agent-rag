# Project RAG API

## Structure

```text
app/
├── main.py    # server entry point and CLI import
├── api.py     # REST API and authentication
├── db.py      # SQLite and material CRUD
├── rag.py     # slot-based RAG search
└── schemas.py # request models
```

The service stores materials in SQLite and separates them by `slot`. RAG search uses only the materials from the selected slot.

## Configuration

In `.env`:

```env
GROQ_API_KEY=your_groq_key
RAG_PORT=8000
RAG_API_TOKEN=your_secret_token
```

Start the server:

```bash
python3 main.py
```

## CLI import

Import all UTF-8 text files from a directory, including nested directories:

```bash
python3 main.py import --folder ./materials --slot project-a
```

The command returns JSON with `imported` and `skipped` lists. File names are stored relative to the selected directory.

## API

Use this header for authentication:

```http
X-API-Token: your_secret_token
```

### Add a material

```bash
curl -X POST http://localhost:8000/materials \
  -H "X-API-Token: your_secret_token" \
  -H "Content-Type: application/json" \
  -d '{"slot":"project-a","name":"team.md","content":"Elena leads the project."}'
```

### List materials

```bash
curl "http://localhost:8000/materials?slot=project-a" \
  -H "X-API-Token: your_secret_token"
```

Without `slot`, materials from all slots are returned. Material contents are not included in the list.

### Delete a material

```bash
curl -X DELETE http://localhost:8000/materials/1 \
  -H "X-API-Token: your_secret_token"
```

### Run a RAG search

```bash
curl -X POST http://localhost:8000/rag/search \
  -H "X-API-Token: your_secret_token" \
  -H "Content-Type: application/json" \
  -d '{"slot":"project-a","params":["Who leads the project?"]}'
```

For one query:

```json
{"success":true,"answer":"Elena."}
```

For multiple queries:

```json
{"success":true,"answers":["Elena.","There are 5 people in the project."]}
```

### Health check

```bash
curl http://localhost:8000/health
```

The default database is `rag.db`. Change its location with `RAG_DB_PATH` in `.env`.

## Run in the background with nohup

Quick temporary option:

```bash
nohup python3 main.py > rag.log 2>&1 &
```

For production, use systemd so the process restarts after failures and starts automatically after a reboot.

## Run in the background with systemd

Create the unit file:

```bash
sudo mcedit /etc/systemd/system/agent-rag.service
```

File contents:

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

Enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now agent-rag
```

Check status and logs:

```bash
sudo systemctl status agent-rag
journalctl -u agent-rag -f
```

Restart after changes:

```bash
sudo systemctl restart agent-rag
```
