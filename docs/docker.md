# Docker

The agent is containerized for local runs and for deployment to Azure (e.g. Web App for Containers).

## Build

From the project root:

```bash
docker build -t meeting-agent .
```

## Run locally

Use an env file with required variables (see [configuration.md](configuration.md)):

```bash
docker run -p 3978:3978 --env-file .env meeting-agent
```

Or pass variables explicitly:

```bash
docker run -p 3978:3978 \
  -e TENANT_ID="..." \
  -e CLIENT_ID="..." \
  -e CLIENT_SECRET="..." \
  -e MicrosoftAppId="..." \
  -e MicrosoftAppPassword="..." \
  -e AZURE_OPENAI_ENDPOINT="..." \
  -e AZURE_OPENAI_API_KEY="..." \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini" \
  -e MEETING_ORGANIZER_USER_ID="..." \
  meeting-agent
```

The bot endpoint is **http://localhost:3978/api/messages** (POST). For the Bot Framework Emulator or Azure Bot Service, use this URL as the messaging endpoint when testing locally (with ngrok or similar if the bot is not on localhost).

## Docker Compose

For local development with persisted `output/` and `logs/`:

```bash
docker-compose up --build
```

Stop with `Ctrl+C` or `docker-compose down`.

## Deploy image to Azure

1. **Build and push to Azure Container Registry (ACR):**
   - Create an ACR, then:
   ```bash
   az acr login --name <acr-name>
   docker tag meeting-agent <acr-name>.azurecr.io/meeting-agent:latest
   docker push <acr-name>.azurecr.io/meeting-agent:latest
   ```

2. **Web App for Containers:**
   - Create App Service with **Docker** (Linux); in **Deployment Center** set **Registry source** to Azure Container Registry and choose the image `meeting-agent:latest`.
   - Set **Application settings** (env vars) as in [configuration.md](configuration.md).
   - The container exposes port **3978**; configure the Web App to use that port (e.g. **WEBSITES_PORT=3978** or set in Dockerfile/Custom container settings).

3. **Bot Service:** Set the messaging endpoint to `https://<webapp>.azurewebsites.net/api/messages`.

## .dockerignore

The build excludes `output/`, `logs/`, `.git`, `.venv`, `.env`, and similar to keep the image small and avoid shipping secrets.
