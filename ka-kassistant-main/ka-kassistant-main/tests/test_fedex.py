"""Test FedEx."""

import pytest

from kassistant.fedex import FedExServices


def test_fedex_client_needs_args() -> None:
    """Temp smoke test."""
    with pytest.raises(TypeError):
        FedExServices()
