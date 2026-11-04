# AI Research Assistant

A React and Vite frontend backed by FastAPI and a sequential CrewAI workflow:
Research Analyst, Fact Checker, and Content Writer.

## Requirements

- Python 3.11
- Node.js and npm
- OpenRouter and Serper API keys for live research requests

Live research requests use your configured providers and may incur charges.
Keep API keys in `backend/.env`; never place them in frontend files.

## Run the application

The backend and frontend run in separate PowerShell terminals.

### Backend

From the project directory:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

If needed, install dependencies and create the environment file:

```powershell
python -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Set `OPENROUTER_API_KEY` and `SERPER_API_KEY` in `backend/.env`, then start
the API:

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn ai_research.main:app --reload --host 127.0.0.1 --port 8000
```

The health endpoint is `http://127.0.0.1:8000/`; interactive API
documentation is available at `http://127.0.0.1:8000/docs`.

### Frontend

In another PowerShell terminal, from the project directory:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173/`. The frontend API base URL is configured in
`frontend/.env` and defaults to `http://127.0.0.1:8000`.

## Verify

Run backend tests from the project directory:

```powershell
$env:PYTHONPATH = "backend/src"
backend\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
```

Run frontend checks from `frontend`:

```powershell
npm run lint
npm run build
```

The research API accepts `POST /api/research` with a topic and run ID. Subscribe
to `GET /api/research/events?run_id=<run-id>` to receive the agents' progress
events while the report is generated.
