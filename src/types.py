from typing import Optional, TypedDict


class AuthenticatedUser(TypedDict):
    id: str
    name: str
    picture: Optional[str]
    username: str
    email: str
    locale: str
    emailVerified: bool
    twoFactorEnabled: bool
    provider: str
    createdAt: str
    updatedAt: str


class AuthenticatedResponse(TypedDict):
    status: str
    user: AuthenticatedUser


SignupResponse = AuthenticatedResponse
LoginResponse = AuthenticatedResponse


class LogoutResponse(TypedDict):
    message: str


class ImportResumeResponse(TypedDict):
    id: str
    title: str
    slug: str
    visibility: str
    locked: bool
    userId: str
    createdAt: str
    updatedAt: str


class PrintResumeResponse(TypedDict):
    url: str
