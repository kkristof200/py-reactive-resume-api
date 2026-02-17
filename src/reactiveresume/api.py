from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Self, Union
import httpx

from .types import (
    ImportResumeResponse,
    LoginResponse,
    LogoutResponse,
    PrintResumeResponse,
    SignupResponse
)


class ReactiveResumeAPI:
    """Small helper around the Reactive Resume HTTP API."""

    def __init__(
        self,
        base_url: str,
        client: Optional[httpx.Client] = None,
        timeout: float = 30.0
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(base_url=self.base_url, timeout=timeout, follow_redirects=True)
        self._client.base_url = self.base_url
        self._owns_client = client is None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    @property
    def client(self) -> httpx.Client:
        return self._client

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def signup(
        self,
        name: str,
        username: str,
        email: str,
        password: str
    ) -> SignupResponse:
        response = self._client.post(
            "/api/auth/register",
            json={
                "name": name,
                "email": email,
                "username": username,
                "locale": "en-US",
                "password": password,
            },
        )
        response.raise_for_status()
        payload: SignupResponse = response.json()
        return payload

    def login(self, identifier: str, password: str) -> LoginResponse:
        response = self._client.post(
            "/api/auth/login",
            json={"identifier": identifier, "password": password},
        )
        response.raise_for_status()
        payload: LoginResponse = response.json()
        return payload

    def logout(self) -> LogoutResponse:
        response = self._client.post("/api/auth/logout")
        response.raise_for_status()
        payload: LogoutResponse = response.json()
        return payload

    def import_resume(self, resume: dict[str, Any]) -> ImportResumeResponse:
        if 'data' not in resume:
            resume['data'] = resume

        response = self._client.post("/api/resume/import", json=resume)
        response.raise_for_status()
        payload: ImportResumeResponse = response.json()
        return payload

    def import_resume_from_path(self, path: Union[Path, str]) -> ImportResumeResponse:
        data = json.loads(Path(path).read_text())
        return self.import_resume(data)

    def print_resume(self, resume_id: str) -> PrintResumeResponse:
        response = self._client.get(f"/api/resume/print/{resume_id}")
        response.raise_for_status()
        payload: PrintResumeResponse = response.json()
        return payload

    def delete_resume(self, resume_id: str) -> None:
        response = self._client.delete(f"/api/resume/{resume_id}")
        response.raise_for_status()

    def export_resume(self, resume_path: Union[Path, str]) -> str:
        created = self.import_resume_from_path(resume_path)
        resume_id = created["id"]
        print_response = self.print_resume(resume_id)
        return print_response["url"]

    def download_pdf(
        self,
        url: str,
        destination: Union[Path, str]
    ) -> Path:
        response = self._client.get(url)
        response.raise_for_status()
        dest_path = Path(destination)
        dest_path.write_bytes(response.content)

        return dest_path

    def resume_json_to_pdf(
        self,
        resume_json: dict[str, Any],
        resume_path: Union[Path, str],
        cleanup: bool = True
    ) -> Path:
        import_response = self.import_resume(resume_json)
        resume_id = import_response["id"]
        export_response = self.export_resume(resume_id)
        self.download_pdf(export_response, resume_path)

        if cleanup:
            self.delete_resume(resume_id)

        return Path(resume_path)
