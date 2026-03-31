"""
Auth Service – handles login and logout against the cloud auth API.
All public methods are async and must be awaited or scheduled via AsyncRunner.
"""

import asyncio
import json
import urllib.request
import urllib.error
from ViewModels.auth.login_models import LoginRequest, LoginResponse
from Services.session import Session

AUTH_BASE_URL = "https://auth.accountingonweb.com"
LOGIN_ENDPOINT = "/api/auth/User/login"


class AuthService:

    @staticmethod
    async def login(email: str, password: str) -> tuple[bool, str, LoginResponse | None]:
        """Async – POST credentials to the auth server and persist the session.

        Returns:
            (success, message, LoginResponse | None)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, AuthService._sync_login, email, password)

    @staticmethod
    def _sync_login(email: str, password: str) -> tuple[bool, str, LoginResponse | None]:
        """Blocking HTTP call – runs in a thread-pool executor."""
        payload = json.dumps(LoginRequest(email, password).to_dict()).encode("utf-8")

        req = urllib.request.Request(
            url=f"{AUTH_BASE_URL}{LOGIN_ENDPOINT}",
            data=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                response = LoginResponse.from_dict(body)
                Session.save(response)
                return True, "Login successful", response

        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read().decode("utf-8"))
                message = (
                    error_body.get("message")
                    or error_body.get("title")
                    or f"HTTP {e.code}"
                )
            except Exception:
                message = f"HTTP {e.code}: {e.reason}"
            return False, message, None

        except urllib.error.URLError as e:
            return False, f"Cannot connect to server: {e.reason}", None

        except Exception as e:
            return False, str(e), None

    @staticmethod
    def logout() -> None:
        """Clear the local session."""
        Session.clear()
