# Meeting Transcription Summary Agent

M365 Copilot custom engine agent that connects to Microsoft Entra, fetches user meeting transcriptions via Microsoft Graph (configurable 7–14 day window), and summarizes them with Azure OpenAI. Uses admin-consented OAuth and Teams application access policy. Code is Dockerized.

## Project structure

| Path | Purpose |
|------|--------|
| `src/` | Python code (agent, Graph client, auth, summarizer) |
| `docs/` | Setup, Azure resources, configuration, Docker, troubleshooting |
| `output/` | Generated summaries (gitignored) |
| `logs/` | Application logs (gitignored) |
| `README.md` | This file |

## Prerequisites

- **Python 3.11+** and [uv](https://docs.astral.sh/uv/) (recommended) or pip
- **Azure resources:** App Registration (Entra), Azure Bot Service, Web App (App Service), Azure OpenAI
- **Teams application access policy** (see [docs/teams-application-access-policy.md](docs/teams-application-access-policy.md))

See [docs/azure-resources.md](docs/azure-resources.md) for what each resource is and how to create them.

## Install

```bash
uv sync
```

## Configure

Copy the example env file and set your values:

```bash
cp .env.example .env
# Edit .env: TENANT_ID, CLIENT_ID, CLIENT_SECRET, MicrosoftAppId, MicrosoftAppPassword,
# AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME,
# TRANSCRIPT_DAYS (7–14), MEETING_ORGANIZER_USER_ID (optional), PORT.
```

See [docs/configuration.md](docs/configuration.md) for all variables.

## Run locally

```bash
uv run python -m meeting_agent
```

The server listens on **PORT** (default **3978**). Bot endpoint: **POST /api/messages**.

## Run with Docker

```bash
docker build -t meeting-agent .
docker run -p 3978:3978 --env-file .env meeting-agent
```

See [docs/docker.md](docs/docker.md) for Docker Compose and Azure deployment.

## Deploy to Azure

1. Create and link **App Registration**, **Azure Bot Service**, **Web App**, and **Azure OpenAI** per [docs/azure-resources.md](docs/azure-resources.md).
2. Deploy the app to the Web App (code or container). For container: build and push the image to ACR, then point the Web App to it (see [docs/docker.md](docs/docker.md)).
3. Set **Application settings** (env vars) in the Web App.
4. Configure the Bot Service messaging endpoint to `https://<webapp>.azurewebsites.net/api/messages`.
5. Create and grant the **Teams application access policy** per [docs/teams-application-access-policy.md](docs/teams-application-access-policy.md).

## Documentation

- [Azure resources](docs/azure-resources.md) – App Registration, Bot Service, Web App, Azure OpenAI
- [Entra setup](docs/entra-setup.md) – App registration and permissions
- [Teams application access policy](docs/teams-application-access-policy.md) – Required for transcript access
- [Configuration](docs/configuration.md) – All environment variables
- [Docker](docs/docker.md) – Build, run, deploy to Azure
- [Running](docs/running.md) – Local, Docker, and Azure
- [Troubleshooting](docs/troubleshooting.md) – Common errors and fixes

## User interaction

In Teams or Copilot, send a message containing **"summary"** or **"summarize"** to get a combined summary of meeting transcripts for the configured user and date range. Set **MEETING_ORGANIZER_USER_ID** (Entra user Object ID) and ensure the Teams application access policy grants the app access for that user.
