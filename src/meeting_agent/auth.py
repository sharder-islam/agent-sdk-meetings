"""Microsoft Entra ID app-only authentication for Microsoft Graph."""

import logging
from typing import Any

import msal

from meeting_agent.config import Config

logger = logging.getLogger(__name__)


class GraphAuth:
    """Acquire and cache tokens for Microsoft Graph (app-only)."""

    def __init__(self, config: Config):
        self._config = config
        self._app = msal.ConfidentialClientApplication(
            client_id=config.client_id,
            client_credential=config.client_secret,
            authority=config.authority,
        )
        self._scope = [config.graph_scope()]

    def get_token(self) -> dict[str, Any]:
        """Acquire token for Graph (cached by MSAL)."""
        result = self._app.acquire_token_for_client(scopes=self._scope)
        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "unknown"))
            raise RuntimeError(f"Failed to acquire Graph token: {error}")
        return result

    @property
    def access_token(self) -> str:
        """Current access token for Graph."""
        return self.get_token()["access_token"]
