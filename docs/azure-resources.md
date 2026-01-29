# Required Azure Resources

This solution requires four Azure resources. Create them in the order below and wire them together as described.

## Overview

| Resource | Purpose |
|----------|---------|
| **App Registration (Microsoft Entra ID)** | Identity for the bot and for calling Microsoft Graph. One app serves both: (1) Bot channels (Teams, Copilot) use **Application (client) ID** and **client secret** for Bot Framework auth; (2) the same app is granted Graph permission `OnlineMeetingTranscript.Read.All` (admin consent) and is listed in the Teams application access policy. |
| **Azure Bot Service** | Registers the bot with the Bot Framework, provides the messaging endpoint URL (your Web App), and connects channels (Teams, Direct Line for Copilot). Configure the bot with the App Registration’s **Microsoft App ID** and **client secret**. |
| **Web App (App Service)** | Hosts the agent code (Python). The bot’s messaging endpoint points to this Web App (e.g. `https://<webapp>.azurewebsites.net/api/messages`). Use Linux container (Docker) or custom handler; Dockerized Python app is recommended. |
| **Azure OpenAI** | Provides the model (e.g. gpt-4o, gpt-4o-mini) for summarization. Create an Azure OpenAI resource, deploy a chat model, and configure the app with endpoint, API key, and deployment name. |

## Flow

1. User talks to Copilot or Teams.
2. Bot Service routes the request to your Web App (`POST /api/messages`).
3. Web App runs the agent logic (fetch transcripts via Graph, summarize with Azure OpenAI).
4. Agent uses the **App Registration** token to call Microsoft Graph (transcripts) and Azure OpenAI (summaries).

## 1. App Registration (Microsoft Entra ID)

1. In [Azure Portal](https://portal.azure.com), go to **Microsoft Entra ID** > **App registrations** > **New registration**.
2. Name the app (e.g. `Meeting Transcription Agent`), choose **Accounts in this organizational directory only**, and register.
3. Note the **Application (client) ID** and **Directory (tenant) ID**.
4. Go to **Certificates & secrets** > **New client secret**; note the **Value** (client secret). It is shown only once.
5. Go to **API permissions** > **Add a permission** > **Microsoft Graph** > **Application permissions**.
6. Add **OnlineMeetingTranscript.Read.All** (or **OnlineMeetings.Read.All** per [getAllTranscripts](https://learn.microsoft.com/en-us/graph/api/onlinemeeting-getalltranscripts)).
7. Click **Grant admin consent for [your tenant]**.
8. No redirect URIs are required for app-only / Bot Framework; add any if you use interactive sign-in later.

**Output:** `CLIENT_ID`, `TENANT_ID`, `CLIENT_SECRET` (same as `MicrosoftAppId` and `MicrosoftAppPassword` for the bot).

## 2. Azure Bot Service

1. In Azure Portal, create a resource: **Azure Bot** (Bot Services).
2. Under **Microsoft App ID**, choose **Use existing app registration** and select (or enter) the **Application (client) ID** from the App Registration you created above. Choose **Single tenant** (recommended) or Multi-tenant as needed.
3. Create the bot; then open the resource.
4. Go to **Configuration** and set:
   - **Messaging endpoint:** `https://<your-webapp>.azurewebsites.net/api/messages` (replace with your Web App URL). You can set this after the Web App exists.
   - **Microsoft App ID:** should already be set from step 2. There is **no field in the portal to paste the Microsoft App Password**—Azure Bot Service does not store or display the password.
5. Under **Channels**, add **Microsoft Teams** (and **Direct Line** if used for Copilot).

**Where does the app password go?** The password (client secret) is **not** entered in the Azure Bot resource. You create it in the **App Registration** (Certificates & secrets). You then put that same value in **your Web App’s** Application settings as `MicrosoftAppPassword`. Your bot code uses it to validate incoming requests and to call the channel API. So: **App Registration** = create the secret; **Web App** = store `MicrosoftAppId` and `MicrosoftAppPassword` in config.

**To create or rotate the secret:** In the Bot resource, go to **Configuration** and click **Manage** next to **Microsoft App ID**. That opens the App Registration’s **Certificates & secrets** blade. Create a new client secret there, copy the value once, and add it to your Web App’s Application settings as `MicrosoftAppPassword`.

**Output:** Bot is configured. Your Web App must have `MicrosoftAppId` and `MicrosoftAppPassword` (and `TENANT_ID`, etc.) in its configuration.

## 3. Web App (App Service): Web App vs Web App for Containers

**Which one to create?**

- **Web App for Containers** (or **App Service** with **Docker** as the publish option): Use this when you deploy the agent as a **Docker image** (e.g. from Azure Container Registry). This matches this project’s Dockerfile. Create the resource, then in **Deployment Center** set **Container** as the source and point to your ACR (or other registry) and the image (see [docker.md](docker.md)).
- **Web App** (code deployment): Use this when you deploy **source code** and let Azure run it with a runtime (e.g. **Python**). No container; you publish code (e.g. via GitHub Actions or ZIP deploy). Choose **Linux** and **Python** as the runtime, then deploy your repo or package.

**Recommendation for this project:** Because the repo includes a **Dockerfile** and is set up for containerized runs, **Web App for Containers** (App Service with Docker/container) is the natural choice if you want to run the same image locally and in Azure. If you prefer not to manage containers, create a regular **Web App** with **Python** and deploy the code; you will need to ensure the startup command runs `python -m meeting_agent` and that all dependencies are installed (e.g. via `requirements.txt` or the build step).

**Steps (either type):**

1. Create **App Service** (Web App). For containers: choose **Docker** as the publish option and **Linux**. For code: choose **Code**, **Python**, and **Linux**.
2. If using Docker: in **Deployment Center**, set **Container** and point to ACR (or other registry) and the image for this agent (see [docker.md](docker.md)). Set **WEBSITES_PORT** to the port your app listens on (e.g. `3978`).
3. In **Configuration** > **Application settings**, add all required environment variables (see [configuration.md](configuration.md)), including **MicrosoftAppId** and **MicrosoftAppPassword** (the client secret from the App Registration).
4. Ensure **HTTPS Only** is on so the bot’s messaging endpoint uses `https://`.

**Output:** Web App URL, e.g. `https://<webapp>.azurewebsites.net`. Use `/api/messages` as the bot messaging endpoint in the Azure Bot resource.

## 4. Azure OpenAI

1. Create an **Azure OpenAI** resource in your subscription.
2. Go to **Model deployments** (or **Azure OpenAI Studio**) and deploy a chat model (e.g. **gpt-4o** or **gpt-4o-mini**).
3. Note the **Endpoint** (e.g. `https://<resource>.openai.azure.com/`), **API key** (Keys), and **Deployment name**.

**Output:** `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME`.

## Linking summary

- **Bot Service** → **Web App:** Messaging endpoint = `https://<webapp>/api/messages`.
- **Bot Service** → **App Registration:** Microsoft App ID and client secret from the same App Registration.
- **App Registration** → **Graph:** Application permission `OnlineMeetingTranscript.Read.All` (admin consent).
- **App Registration** → **Teams:** Application access policy must be created and granted (see [teams-application-access-policy.md](teams-application-access-policy.md)).
- **Web App** → **Azure OpenAI:** Endpoint, API key, and deployment name in app settings.

## References

- [Azure Bot Service](https://learn.microsoft.com/en-us/azure/bot-service/)
- [App Service / Web App](https://learn.microsoft.com/en-us/azure/app-service/)
- [Azure OpenAI service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Application access policy for online meetings](https://learn.microsoft.com/en-us/graph/cloud-communication-online-meeting-application-access-policy)
