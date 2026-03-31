"""
Login request and response view models.
"""

from dataclasses import dataclass


@dataclass
class LoginRequest:
    email: str
    password: str

    def to_dict(self) -> dict:
        return {"email": self.email, "password": self.password}


@dataclass
class UserInfo:
    id: str
    email: str
    user_name: str
    first_name: str
    last_name: str

    @classmethod
    def from_dict(cls, data: dict) -> "UserInfo":
        return cls(
            id=data.get("id", ""),
            email=data.get("email", ""),
            user_name=data.get("userName", ""),
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "userName": self.user_name,
            "firstName": self.first_name,
            "lastName": self.last_name,
        }

    @property
    def display_name(self) -> str:
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.user_name or self.email


@dataclass
class LoginResponse:
    access_token: str
    refresh_token: str
    user: UserInfo

    @classmethod
    def from_dict(cls, data: dict) -> "LoginResponse":
        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            user=UserInfo.from_dict(data.get("user", {})),
        )

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "user": self.user.to_dict(),
        }
