# Required Azure Resources

This solution requires four Azure resources. **Create them in this order** so you have the Web App URL before configuring the Bot Service.

## Creation order

1. **App Registration** – identity and client secret  
2. **Web App** (or Web App for Containers) – host the agent; you need its URL next  
3. **Azure Bot Service** – set messaging endpoint to the Web App URL  
4. **Azure OpenAI** – model for summarization  

## Overview

| Resource | Purpose |
|----------|---------|
| **App Registration (Microsoft Entra ID)** | Identity for the bot and for calling Microsoft Graph. One app serves both: (1) Bot channels use **Application (client) ID** and **client secret**; (2) same app gets Graph permission `OnlineMeetingTranscript.Read.All` (admin consent) and is in the Teams application access policy. |
| **Web App (App Service)** | Hosts the agent (Python). The Bot Service messaging endpoint is this Web App’s URL + `/api/messages`. Create this **before** the Bot so you can paste the URL when configuring the bot. |
| **Azure Bot Service** | Registers the bot with the Bot Framework and connects channels (Teams, etc.). You set **Messaging endpoint** to your Web App URL (from step 2). |
| **Azure OpenAI** | Model (e.g. gpt-4o-mini) for summarization. App settings in the Web App reference endpoint, API key, and deployment name. |

---

## 1. App Registration (Microsoft Entra ID)

1. In [Azure Portal](https://portal.azure.com), open the left menu and go to **Microsoft Entra ID** (or search “Entra”).
2. In the left blade, click **App registrations**.
3. Click **+ New registration** at the top.
4. **Name:** e.g. `Meeting Transcription Agent`.
5. **Supported account types:** Select **Accounts in this organizational directory only (Single tenant)**.
6. **Redirect URI:** Leave blank. Click **Register**.
7. On the app’s **Overview** page, copy and save **Application (client) ID** and **Directory (tenant) ID**.
8. In the left blade, click **Certificates & secrets**.
9. Click **+ New client secret**. Add a description (e.g. `Bot and Graph`), choose an expiry (e.g. 24 months), click **Add**. Copy the **Value** immediately (it is shown only once)—this is your client secret (same as Microsoft App Password for the bot). Store it securely; you will add it to the Web App’s Application settings later.
10. In the left blade, click **API permissions**.
11. Click **+ Add a permission**. Choose **Microsoft APIs** > **Microsoft Graph** > **Application permissions**. Search for **OnlineMeetingTranscript** and check **OnlineMeetingTranscript.Read.All** (or **OnlineMeetings.Read.All**). Click **Add permissions**.
12. Click **Grant admin consent for [your tenant]**. Confirm. You should see a green check for the permission.

**You now have:** Application (client) ID, Directory (tenant) ID, and client secret value. Use the same ID and secret for the Web App (`MicrosoftAppId`, `MicrosoftAppPassword`) and for Entra/Graph (`CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID`).

---

## 2. Web App (App Service)

Create the Web App **before** the Bot Service so you have the URL to set as the bot’s messaging endpoint. You can use either a **Web App** (code deploy with Python runtime) or **Web App for Containers** (Docker image); see [docker.md](docker.md) for container build and push. The steps below cover the common path.

1. In Azure Portal, click **Create a resource**. Search for **Web App** (or **App Service**) and open it.
2. **Basics** tab:
   - **Subscription** and **Resource group:** Choose or create (e.g. same group as the bot).
   - **Name:** e.g. `meeting-transcription-agent`. This becomes `<name>.azurewebsites.net`.
   - **Publish:** Choose **Code** (to run Python from repo/ZIP) or **Docker** (to run a container from ACR).
   - **Runtime stack:** If Code, choose **Python 3.11** (or 3.12). If Docker, choose **Docker** and **Linux**.
   - **Operating System:** **Linux**.
   - **Region:** Choose one. Click **Next : Docker>** (if Docker) or **Next : Networking>** (if Code); you can skip optional tabs with **Review + create**.
3. If you chose **Docker:** In **Docker** tab, set **Options** to **Single Container**, **Image Source** to **Azure Container Registry** (or your registry), then select the registry, image, and tag. Set **Startup Command** if needed (e.g. `python -m meeting_agent`). Optional: set **WEBSITES_PORT** in **Application settings** later (e.g. `3978`).
4. Click **Review + create**, then **Create**. Wait for deployment.
5. Open the Web App resource. Copy the **URL** (e.g. `https://meeting-transcription-agent.azurewebsites.net`). The bot messaging endpoint will be **`<URL>/api/messages`** (e.g. `https://meeting-transcription-agent.azurewebsites.net/api/messages`). Save it for the next section.
6. In the Web App’s left blade, go to **Configuration** > **Application settings**. Click **+ New application setting** and add each of the required variables (see [configuration.md](configuration.md)), including:
   - `MicrosoftAppId` = Application (client) ID from the App Registration
   - `MicrosoftAppPassword` = the client secret value from the App Registration (the one you copied in step 9 above)
   - `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET` (same as above if using one app)
   - `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME` (you can add these after creating the Azure OpenAI resource)
   - `TRANSCRIPT_DAYS`, `PORT` (e.g. `3978`), and optionally `MEETING_ORGANIZER_USER_ID`
   Click **Save** and confirm.
7. In **Settings** > **General settings**, ensure **HTTPS Only** is **On**.

**You now have:** Web App URL. Use **`<Web App URL>/api/messages`** as the Bot Service messaging endpoint in the next step.

---

## 3. Azure Bot Service

Create the Bot **after** the Web App so you can set the messaging endpoint to the Web App URL.

1. In Azure Portal, click **Create a resource**. Search for **Azure Bot** and open it.
2. **Basics** (or **Bot handle**):
   - **Subscription** and **Resource group:** e.g. same as the Web App.
   - **Bot handle:** e.g. `meeting-transcription-bot`. Must be globally unique.
   - **Pricing:** Choose **F0** (free) or **S1** as needed.
3. **Microsoft App ID** (or **Identity**):
   - Select **Use existing app registration**.
   - **App ID:** Paste the **Application (client) ID** from the App Registration (section 1).
   - **App tenant ID:** Paste the **Directory (tenant) ID** from the App Registration.
   - If asked for app type, choose **Single tenant** (recommended).
4. Click **Review + create**, then **Create**. Wait for deployment.
5. Open the Azure Bot resource. In the left blade, go to **Configuration**.
6. Set **Messaging endpoint** to **`https://<your-webapp-name>.azurewebsites.net/api/messages`** (the URL from section 2, step 5, with `/api/messages` appended). Click **Apply**.
7. **Microsoft App ID** is already set; there is no field for the password here. The password is only in the Web App’s Application settings (see section 2, step 6).
8. In the left blade, go to **Channels**. Click **Microsoft Teams**. Accept the terms if shown and enable. Optionally add **Direct Line** if you use it for Copilot.

**You now have:** Bot registered with the Bot Framework, messaging endpoint pointing to your Web App, and Teams channel enabled.

---

## 4. Azure OpenAI

1. In Azure Portal, click **Create a resource**. Search for **Azure OpenAI** and open it.
2. **Basics:** Subscription, resource group, region, name (e.g. `meeting-agent-openai`). **Pricing tier:** Choose a tier that includes chat models. Create.
3. When the resource is ready, open it. Go to **Keys and Endpoint** (or **Endpoint and keys**). Copy **Endpoint** (e.g. `https://meeting-agent-openai.openai.azure.com/`) and **Key 1** (or Key 2). You will put these in the Web App’s Application settings as `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`.
4. Open **Azure OpenAI Studio** (link in the resource or go to [oai.azure.com](https://oai.azure.com)). Select this resource. Go to **Deployments** (or **Model deployments**). Create a deployment: choose a **model** (e.g. **gpt-4o-mini** or **gpt-4o**), set a **Deployment name** (e.g. `gpt-4o-mini`). This name is `AZURE_OPENAI_DEPLOYMENT_NAME` in the Web App settings.
5. Back in the Web App’s **Configuration** > **Application settings**, add or update: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME`. Save.

---

## Linking summary

- **App Registration** → **Web App:** `MicrosoftAppId` and `MicrosoftAppPassword` (and `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`) in Web App settings.
- **Web App** → **Bot Service:** Messaging endpoint = `https://<webapp>.azurewebsites.net/api/messages`.
- **Bot Service** → **App Registration:** Same Microsoft App ID (no password in the Bot blade).
- **App Registration** → **Graph:** Permission `OnlineMeetingTranscript.Read.All` (admin consent); **Teams:** Application access policy (see [teams-application-access-policy.md](teams-application-access-policy.md)).
- **Web App** → **Azure OpenAI:** `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME` in Web App settings.

## References

- [Azure Bot Service](https://learn.microsoft.com/en-us/azure/bot-service/)
- [App Service / Web App](https://learn.microsoft.com/en-us/azure/app-service/)
- [Azure OpenAI service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Application access policy for online meetings](https://learn.microsoft.com/en-us/graph/cloud-communication-online-meeting-application-access-policy)
