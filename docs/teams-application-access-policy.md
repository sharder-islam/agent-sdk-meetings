# Teams Application Access Policy

For the app to call Microsoft Graph and access **online meeting transcripts** with **application permissions**, a tenant administrator must create and grant a **Teams application access policy**. Without it, Graph returns **403 "No application access policy found."**

## Why this is needed

Graph APIs for online meeting transcripts (e.g. `getAllTranscripts`) support application permissions. When using app-only (no signed-in user), the tenant must explicitly allow the app to access meetings **on behalf of** specific users (or the whole tenant). This is done via a Teams (Skype for Business) application access policy.

Reference: [Configure application access to online meetings](https://learn.microsoft.com/en-us/graph/cloud-communication-online-meeting-application-access-policy).

## Prerequisites

- Administrator account in the tenant.
- **Skype for Business PowerShell** module (for Microsoft 365). Install and connect as described in [Manage Skype for Business Online with PowerShell](https://learn.microsoft.com/en-us/microsoft-365/enterprise/manage-skype-for-business-online-with-microsoft-365-powershell).

## Steps

### 1. Get the app and user IDs

- **Application (client) ID** of your App Registration: from Azure Portal > App registrations > your app (same as `MicrosoftAppId`).
- **User ID(s)** (object ID in Entra ID) of the user(s) whose meetings the app may access. Find in Entra ID > Users > user > Object ID.

### 2. Create the application access policy

In PowerShell (Skype for Business Online):

```powershell
New-CsApplicationAccessPolicy -Identity "MeetingTranscriptAgent-Policy" -AppIds "<your-app-client-id>" -Description "Allows Meeting Transcription Agent to read transcripts for specified users"
```

Replace `<your-app-client-id>` with the Application (client) ID (GUID).

### 3. Grant the policy to users

**Option A – Grant to specific user(s):**

```powershell
Grant-CsApplicationAccessPolicy -PolicyName "MeetingTranscriptAgent-Policy" -Identity "<user-object-id>"
```

Replace `<user-object-id>` with the user's Object ID (GUID). Repeat for each user.

**Option B – Grant to the whole tenant (all users):**

```powershell
Grant-CsApplicationAccessPolicy -PolicyName "MeetingTranscriptAgent-Policy" -Global
```

### 4. Verify

- Policy changes can take up to **30 minutes** to apply.
- Ensure the app has **admin consent** for `OnlineMeetingTranscript.Read.All` (or `OnlineMeetings.Read.All`) in the App Registration.
- Set `MEETING_ORGANIZER_USER_ID` in the agent config to the user ID (object ID) for whom you want to fetch transcripts.

## Summary

| What | Value |
|------|--------|
| Policy identity | Name you give (e.g. `MeetingTranscriptAgent-Policy`) |
| AppIds | Your App Registration's Application (client) ID |
| Identity (when granting) | User Object ID for a user, or `Global` for tenant-wide |

Without this policy, the Graph call to `getAllTranscripts` (or transcript content) returns **403 Forbidden** with message **"No application access policy found for this app"**.
