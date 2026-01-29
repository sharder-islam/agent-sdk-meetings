# Securing Azure Resources and the Bot Endpoint

The bot’s messaging endpoint (`/api/messages`) is publicly reachable so the Bot Framework / Teams / Copilot can POST activities. This doc covers how to secure it and the rest of your Azure setup, including aligning with Entra Conditional Access where possible.

## Why the endpoint is “public”

- **Bot Framework** and **Teams** call your Web App from Microsoft’s cloud. There is no fixed IP range you can lock to; the channel service must be able to reach your URL.
- So the **URL is public** in the sense that it’s on the internet. Security is achieved by **authentication and authorization**, not by hiding the URL.

## Core security model (what you already have)

- **Bot Framework authentication:** Incoming requests are validated using the **Bot Framework token service**. The connector (Teams, etc.) signs requests with your app’s identity; your app validates the JWT using **Microsoft App ID** and **Microsoft App Password** (client secret). Requests without a valid token are rejected.
- So “publicly accessible” does **not** mean “unauthenticated.” Only the Bot Framework / channels that know your app’s credentials can successfully call your endpoint.

## Hardening and defense in depth

### 1. Protect and rotate secrets

- **App Registration client secret:** Store in **Azure Key Vault**. Reference from App Service via **Key Vault references** in Application settings (e.g. `@Microsoft.KeyVault(SecretUri=...)`). Rotate the secret periodically; use a new secret in Key Vault and update the reference.
- **Azure OpenAI API key:** Also in Key Vault and referenced from the Web App. Rotate when required by policy.
- **No secrets in code or in Docker images.** Use env vars / App settings / Key Vault only.

### 2. Lock down the Web App (App Service)

- **HTTPS only:** Enable “HTTPS Only” so the bot endpoint is only served over TLS.
- **Minimum TLS version:** Set to 1.2 (or your org’s standard) in the Web App configuration.
- **Managed identity:** Use a **system- or user-assigned managed identity** for the Web App to read from Key Vault (no client secrets in config). Grant the identity “Get” on the relevant secrets.
- **Restrict outbound traffic (optional):** If you move to a VNet-injected Web App, you can restrict outbound traffic to only the endpoints your app needs (e.g. Graph, Azure OpenAI, Bot Framework). This doesn’t change the fact that the endpoint is still *reachable* from the internet, but it limits what the app can call.

### 3. Network-level options (optional)

- **Azure Front Door or Application Gateway:** Put the Web App behind a WAF. You can add rate limiting, geo-filtering, or custom rules. Bot Framework uses Microsoft IPs; if Microsoft publishes an allow list, you could theoretically restrict to those IPs at the WAF, but in practice many teams allow all and rely on JWT validation. WAF is still useful for DDoS and common web attacks.
- **Private endpoint for the Web App:** A private endpoint gives the Web App a private IP in a VNet. **However**, the Bot Framework channel must still reach your app over the **public** URL (e.g. `https://<webapp>.azurewebsites.net`). So the public hostname remains; private endpoint mainly helps when *other* services (e.g. internal APIs) call your app privately. It does not remove the need for strong auth on the public endpoint.

### 4. Entra Conditional Access (CA) and the bot

- **What Conditional Access applies to:** CA policies apply to **user sign-in** (e.g. browser, Teams client, Office apps). They do **not** apply to the **server-to-server** call from the Bot Framework / channel service to your Web App. That call is **app-only** (client credentials): no user context, so CA cannot be evaluated for that request.
- **How to involve Conditional Access anyway:**
  - **User-facing clients:** The **user** who talks to the bot (in Teams or Copilot) has already signed in. That sign-in **is** subject to Conditional Access. So ensuring users must use compliant devices, MFA, or allowed locations to use Teams/Copilot indirectly protects “who” can use the bot. Harden Entra and CA for your users; the bot benefits from that.
  - **Narrow who can use the bot:** In **Teams**, restrict the app to certain users or groups (Teams app setup policies / permission policies). In **Entra**, restrict which users can consent or use apps. That way only users who already passed CA (and app assignment) can interact with the bot.
  - **Future “user context” in the bot:** If you later add a flow where the **user** signs in (e.g. OAuth to Graph on behalf of the user), that user sign-in **will** be subject to Conditional Access. So designing any future user-delegated auth with Entra will let CA apply to that part of the flow.

### 5. Bot Service and channel configuration

- **Azure Bot Service:** Keep the bot’s **Configuration** (Microsoft App ID and password) aligned with a single App Registration and rotate the secret in Entra + Key Vault together.
- **Channels:** Only enable the channels you need (e.g. Teams, Direct Line). Disable unused channels.
- **Teams:** Use **Teams app permission policies** and **app setup policies** to control which users can install or use the bot. That’s your main lever to “who can talk to the bot” in line with identity policy.

### 6. Azure OpenAI and App Registration

- **Azure OpenAI:** Use **private endpoint** and **managed identity** where possible. The Web App can use managed identity to get a token for Azure OpenAI (if you switch from API key to RBAC). That reduces exposure of keys and keeps traffic off the public internet for that leg.
- **App Registration:** Restrict **who can manage the app** (e.g. owner group). Use **admin consent** for Graph and any other APIs so only admins grant permissions. Review **API permissions** periodically; remove unused permissions.

### 7. Logging and monitoring

- **App Service:** Enable **Application Logging** and/or **Application Insights** to detect anomalies, failures, and abuse patterns.
- **Entra:** Audit **sign-in** and **app credential** use. Monitor for unexpected token or secret usage.
- **Azure Bot Service:** Use **Analytics** and channel-specific logs to see who is using the bot and from where.

### 8. Summary: “public endpoint” vs “secure”

| Concern | Approach |
|--------|----------|
| Endpoint is reachable by URL | Accept; secure via Bot Framework JWT validation (App ID + secret). |
| Secrets in config | Move to Key Vault; use managed identity; rotate secrets. |
| Who can use the bot | Teams/Copilot: restrict by app setup and permission policies; users already subject to Entra/CA at sign-in. |
| Conditional Access | Applies to **user** sign-in (Teams, etc.), not to the server-to-server POST to your bot. Harden user sign-in and app assignment so only compliant users can use the bot. |
| Extra hardening | HTTPS only, TLS 1.2+, WAF (Front Door/App Gateway), managed identity, private endpoint for Azure OpenAI, logging and monitoring. |

In short: the bot endpoint stays publicly *addressable* so the channel can call it; security comes from **strong auth (Bot Framework JWT)**, **secret management (Key Vault, rotation)**, **restricting who can use the bot (Teams/Entra)**, and **hardening the rest of the Azure resources**. Conditional Access will apply to the user side (sign-in to Teams/Copilot), not to the server-to-server call to your Web App.
