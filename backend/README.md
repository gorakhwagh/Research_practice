# AI Research Backend

The backend contains the `ai_research` CrewAI project and the FastAPI service.
Use Python 3.11 or newer (below 3.14).

## Set up

From this directory, create and activate a virtual environment, then install
the project dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set valid OpenRouter and Serper API keys
before running a live research workflow. Keep `.env` private.

## Run the API

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn ai_research.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Submit JSON containing
`topic` and a client-generated `run_id` to `POST /api/research`. Connect to
`GET /api/research/events?run_id=<same-run-id>` before submitting to receive
the three agents' task start/completion events. The request returns the final
report as JSON. `GET /` is a backend health check.

## Test the CrewAI workflow independently

```powershell
$env:PYTHONPATH = "src"
python -m ai_research.cli "Your research topic"
```

Independent runs require valid API keys and may incur provider charges.
