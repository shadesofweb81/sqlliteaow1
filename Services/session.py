"""
Session – stores auth tokens and user info in memory and persists to disk.
The session file lives in data/session.json alongside the SQLite database.
"""

import json
import os
from ViewModels.auth.login_models import LoginResponse, UserInfo

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SESSION_FILE = os.path.join(_DATA_DIR, "session.json")


class Session:
    """Class-level (singleton-style) auth session."""

    _access_token: str = ""
    _refresh_token: str = ""
    _user: UserInfo | None = None
    _selected_company: dict | None = None  # {id, name, ...} from local DB

    # ── Persist ───────────────────────────────────────────────────────────────

    @classmethod
    def save(cls, response: LoginResponse) -> None:
        """Save a successful login response to memory and disk."""
        cls._access_token = response.access_token
        cls._refresh_token = response.refresh_token
        cls._user = response.user

        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(response.to_dict(), f, indent=2)

    @classmethod
    def load(cls) -> bool:
        """Load a saved session from disk.

        Returns:
            True if a valid session was found and loaded.
        """
        if not os.path.exists(SESSION_FILE):
            return False
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            response = LoginResponse.from_dict(data)
            cls._access_token = response.access_token
            cls._refresh_token = response.refresh_token
            cls._user = response.user
            return bool(cls._refresh_token)
        except (json.JSONDecodeError, KeyError, TypeError):
            return False

    @classmethod
    def clear(cls) -> None:
        """Log out – wipe memory and delete the session file."""
        cls._access_token = ""
        cls._refresh_token = ""
        cls._user = None
        cls._selected_company = None
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    # ── Accessors ─────────────────────────────────────────────────────────────

    @classmethod
    def get_access_token(cls) -> str:
        return cls._access_token

    @classmethod
    def get_refresh_token(cls) -> str:
        return cls._refresh_token

    @classmethod
    def get_user(cls) -> UserInfo | None:
        return cls._user

    @classmethod
    def is_logged_in(cls) -> bool:
        return bool(cls._refresh_token)

    @classmethod
    def set_selected_company(cls, company: dict | None) -> None:
        cls._selected_company = company

    @classmethod
    def get_selected_company(cls) -> dict | None:
        return cls._selected_company

    @classmethod
    def get_selected_company_id(cls) -> str | None:
        return cls._selected_company["id"] if cls._selected_company else None

    @classmethod
    def get_auth_headers(cls) -> dict:
        """Return Authorization header dict ready for API requests."""
        if cls._access_token:
            return {"Authorization": f"Bearer {cls._access_token}"}
        return {}

    @classmethod
    def update_access_token(cls, access_token: str) -> None:
        """Update the access token (e.g. after a token refresh)."""
        cls._access_token = access_token
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["access_token"] = access_token
                with open(SESSION_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except (json.JSONDecodeError, OSError):
                pass
