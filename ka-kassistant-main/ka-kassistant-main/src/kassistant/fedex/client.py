"""Interacting with FedEx."""

from datetime import UTC, datetime, timedelta
from typing import Self

import httpx
from httpx import Response

from .models import FedExShipmentRequest


class FedExServices:
    """A class wrapping FedEx's API."""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        """Initialize the FedExServices class."""
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = ""
        self.token_expires_at = datetime.now(tz=UTC)

    def _update_token(self: Self) -> None:
        """Update the OAUTH token."""
        if self.token_expires_at > datetime.now(tz=UTC):
            return

        auth_dict = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = httpx.post(self.base_url + "/oauth/token", data=auth_dict)
        data = response.json()
        self.token = data["access_token"]
        self.token_expires_at = datetime.now(tz=UTC) + timedelta(seconds=data["expires_in"])

    def make_request(
        self,
        method: str,
        path: str,
        params: dict | None = None,  # type: ignore[type-arg]
        json: dict | None = None,  # type: ignore[type-arg]
    ) -> Response:
        """Make a request to FedEx's API."""
        self._update_token()

        headers = {"Authorization": "Bearer " + self.token}

        args = {
            "url": self.base_url + path,
            "method": method,
            "headers": headers,
        }

        if params is not None:
            args["params"] = params

        if json is not None:
            args["json"] = json

        return httpx.request(**args)  # type: ignore[arg-type]

    def create_label(self, request: FedExShipmentRequest) -> Response:
        """Create a label."""
        return self.make_request(
            "POST",
            "/ship/v1/shipments",
            json=request.model_dump(),
        )
