# Configuration

All configuration is via environment variables. Use a `.env` file locally (see `.env.example`) and Application settings (or Key Vault references) in Azure.

## Environment variables

### Entra / App Registration

| Variable | Description | Example |
|----------|-------------|---------|
| `TENANT_ID` | Microsoft Entra ID tenant (directory) ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `CLIENT_ID` | Application (client) ID | Same as `MicrosoftAppId` |
| `CLIENT_SECRET` | Client secret value | From Certificates & secrets |

### Bot / Azure Bot Service

| Variable | Description | Example |
|----------|-------------|---------|
| `MicrosoftAppId` | Same as `CLIENT_ID` (Bot Framework) | Same as `CLIENT_ID` |
| `MicrosoftAppPassword` | Same as `CLIENT_SECRET` (Bot Framework) | Same as `CLIENT_SECRET` |

### Transcript window

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSCRIPT_DAYS` | Number of days to look back for transcripts (1–14) | `7` |

### Azure OpenAI

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | `https://myresource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | API key (Keys in Azure OpenAI) | `...` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Deployment name of the chat model | `gpt-4o-mini` |
| `AZURE_OPENAI_API_VERSION` | (Optional) API version | `2024-02-15-preview` |

### Web server

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port for the HTTP server | `3978` |

### Optional: default user for transcripts

| Variable | Description | Example |
|----------|-------------|---------|
| `MEETING_ORGANIZER_USER_ID` | User (object) ID whose meetings to fetch when user sends “summary” | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |

If not set, the agent will ask the user to configure it when they request a summary.

### Optional: authority

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTHORITY` | Entra authority URL | `https://login.microsoftonline.com/<TENANT_ID>` |

## .env.example

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
# Edit .env with your tenant ID, client ID, client secret, OpenAI endpoint/key/deployment, and optionally MEETING_ORGANIZER_USER_ID.
```

## Production (Azure Web App)

- Set all variables in **App Service** > **Configuration** > **Application settings**.
- For secrets, use **Key Vault references** (e.g. `@Microsoft.KeyVault(SecretUri=...)`) or store secrets in Key Vault and reference them in Application settings.
