# Running the Agent

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Required Azure resources and configuration (see [azure-resources.md](azure-resources.md) and [configuration.md](configuration.md))

## Install (uv)

```bash
uv sync
```

## Configure

Copy and edit environment variables:

```bash
cp .env.example .env
# Edit .env with TENANT_ID, CLIENT_ID, CLIENT_SECRET, MicrosoftAppId, MicrosoftAppPassword,
# AZURE_OPENAI_*, TRANSCRIPT_DAYS, MEETING_ORGANIZER_USER_ID (optional), PORT.
```

## Run locally (Python)

```bash
uv run python -m meeting_agent
```

Or with explicit Python:

```bash
source .venv/bin/activate  # or: uv venv && source .venv/bin/activate
python -m meeting_agent
```

The server listens on **PORT** (default **3978**). The Bot Framework endpoint is **POST /api/messages**.

## Run with Docker

```bash
docker build -t meeting-agent .
docker run -p 3978:3978 --env-file .env meeting-agent
```

See [docker.md](docker.md) for more options.

## Run in Azure

1. Deploy the app to **Azure Web App** (code or container). See [azure-resources.md](azure-resources.md) and [docker.md](docker.md).
2. Set **Application settings** (env vars) in the Web App.
3. Configure **Azure Bot Service** with messaging endpoint `https://<webapp>.azurewebsites.net/api/messages`.

## Testing

- **Bot Framework Emulator:** Point the bot endpoint to `http://localhost:3978/api/messages` (use ngrok if the emulator is remote). Use the same Microsoft App ID and password as in `.env`.
- **Microsoft Teams:** Add the bot to Teams via the Bot Service channel; ensure the app is sideloaded or published as needed.
- **M365 Copilot:** Register and connect the custom engine agent per [Create and deploy an agent with Microsoft 365 Agents SDK](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/create-deploy-agents-sdk).

## User interaction

Send a message containing **"summary"** or **"summarize"** to get a combined summary of meeting transcripts for the configured user and date range. Ensure **MEETING_ORGANIZER_USER_ID** is set (and that the Teams application access policy grants the app access for that user).
