# Troubleshooting

## "No application access policy found for this app"

**Symptom:** Graph API returns **403 Forbidden** with message "No application access policy found for this app."

**Cause:** The app is using application permissions to access online meeting transcripts, but no Teams application access policy has been created/granted for this app and the target user(s).

**Fix:** Follow [teams-application-access-policy.md](teams-application-access-policy.md). Create a policy with your app’s client ID and grant it to the user (or Global). Allow up to 30 minutes for changes to apply.

---

## 403 on Microsoft Graph (other)

- Confirm **admin consent** was granted for `OnlineMeetingTranscript.Read.All` (or `OnlineMeetings.Read.All`) in the App Registration.
- Confirm **TENANT_ID**, **CLIENT_ID**, and **CLIENT_SECRET** are correct and the secret has not expired.
- For transcript APIs, the **application access policy** (see above) is required in addition to Graph permissions.

---

## Bot returns 401 or 502

- **401:** Check **MicrosoftAppId** and **MicrosoftAppPassword** in configuration. They must match the App Registration used in Azure Bot Service. Ensure no extra spaces and the secret is current.
- **502:** The Web App may be crashing or timing out. Check App Service logs (Log stream, Application Insights). Ensure all required env vars are set in the Web App (see [configuration.md](configuration.md)).

---

## Azure OpenAI errors

- **401:** Invalid or missing **AZURE_OPENAI_API_KEY**.
- **404:** Wrong **AZURE_OPENAI_ENDPOINT** or **AZURE_OPENAI_DEPLOYMENT_NAME**. Confirm the deployment name in Azure OpenAI Studio.
- **429:** Rate limiting; reduce request rate or choose a higher quota.

Ensure **AZURE_OPENAI_ENDPOINT** ends with a slash (e.g. `https://myresource.openai.azure.com/`) and **AZURE_OPENAI_DEPLOYMENT_NAME** matches the deployed model name.

---

## No transcripts returned

- **Date range:** Transcripts are created **after** the meeting ends. Use **TRANSCRIPT_DAYS** (e.g. 7–14) and ensure meetings in that window had **transcription enabled**.
- **User ID:** **MEETING_ORGANIZER_USER_ID** must be the Entra **Object ID** of the user (meeting organizer). The API returns transcripts for meetings **organized** by that user.
- **Application access policy:** Must be granted for that user (or Global). See "No application access policy found" above.
- **Channel meetings:** `getAllTranscripts` for online meetings may not support all channel meeting scenarios; confirm with [Graph docs](https://learn.microsoft.com/en-us/graph/api/onlinemeeting-getalltranscripts).

---

## VTT parsing issues

Transcript content is returned as **VTT**. If summaries are empty or odd, the parser may not match the exact format. Check `src/meeting_agent/transcript_parser.py` and the raw content from Graph (e.g. log the response body) to adjust regex for `<v Speaker>...</v>` and cues.

---

## Docker: container exits or port not reachable

- Ensure **PORT** is set (default **3978**) and the container exposes it (`EXPOSE 3978` in Dockerfile).
- For Azure Web App, set **WEBSITES_PORT=3978** (or the port your app uses) so the platform routes correctly.
- Run with `--env-file .env` and confirm required variables are set (no empty values for secrets).

---

## Logs

- Logs go to stdout/stderr. For local runs, set **LOG_LEVEL** if your app supports it.
- In Azure, use **Log stream** or **Application Insights** to inspect crashes and errors.
