# Setup Guide

## 1. Create and activate a virtual environment (Windows PowerShell)

```powershell
cd C:\Users\4329967\VSCode\practice
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If activation is blocked by execution policy, run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 2. Configure your AI provider

Copy the example env file and fill in your key:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`. Pick **one** provider.

### Option A — OpenAI
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
```

### Option B — Azure OpenAI (common for data engineers on Azure)
```
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
```

> Tip: With Azure you can also use **keyless auth** (Entra ID / Managed Identity)
> instead of an API key. Ask Copilot to help switch to `DefaultAzureCredential`
> when you're comfortable — it's the more secure production pattern.

## 3. Run a server

Each problem is its own folder. From that folder:

```powershell
uvicorn main:app --reload
```

Then open http://localhost:8000/docs for the interactive Swagger UI.

## 4. Security rules (always)

- Never hardcode keys. Always `os.getenv(...)` from `.env`.
- `.env` is git-ignored (see `.gitignore`). Never commit it.
- Treat all user/document text passed to the LLM as **untrusted** (prompt injection).
- Validate inputs at the API boundary with Pydantic.
