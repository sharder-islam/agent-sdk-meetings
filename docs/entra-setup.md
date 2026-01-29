# Microsoft Entra ID (App Registration) Setup

Detailed steps for the App Registration used by the Meeting Transcription Agent for Bot Framework auth and Microsoft Graph.

## Create app registration

1. Sign in to [Azure Portal](https://portal.azure.com).
2. Go to **Microsoft Entra ID** > **App registrations** > **New registration**.
3. **Name:** e.g. `Meeting Transcription Agent`.
4. **Supported account types:** Choose **Accounts in this organizational directory only (single tenant)** (or multi-tenant if required).
5. **Redirect URI:** Leave blank for app-only / Bot Framework; add later if you add interactive sign-in.
6. Click **Register**.

## Note IDs

- **Application (client) ID:** Use as `CLIENT_ID` and `MicrosoftAppId`.
- **Directory (tenant) ID:** Use as `TENANT_ID`.

## Client secret

1. In the app, go to **Certificates & secrets**.
2. **Client secrets** > **New client secret**.
3. Description (e.g. `Bot and Graph`), expiry (e.g. 24 months).
4. Click **Add** and **copy the Value** immediately (it is shown only once). Use as `CLIENT_SECRET` and `MicrosoftAppPassword`.

## API permissions (Microsoft Graph)

1. Go to **API permissions** > **Add a permission**.
2. **Microsoft APIs** > **Microsoft Graph** > **Application permissions**.
3. Search and add:
   - **OnlineMeetingTranscript.Read.All** (read meeting transcripts).
   - Or **OnlineMeetings.Read.All** (broader; see [getAllTranscripts](https://learn.microsoft.com/en-us/graph/api/onlinemeeting-getalltranscripts)).
4. Click **Grant admin consent for [your tenant]**.

## Optional: authority

Default authority is `https://login.microsoftonline.com/<TENANT_ID>`. Override with `AUTHORITY` only if you use a custom or national cloud endpoint.

## Summary

| Setting | Env var | Description |
|--------|--------|-------------|
| Tenant ID | `TENANT_ID` | Directory (tenant) ID |
| Client ID | `CLIENT_ID`, `MicrosoftAppId` | Application (client) ID |
| Client secret | `CLIENT_SECRET`, `MicrosoftAppPassword` | Secret value from Certificates & secrets |

See [configuration.md](configuration.md) for all environment variables.
