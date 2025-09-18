"""Model: Shipment."""

import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins.timestamps import TimestampsMixin


class Shipment(Base, TimestampsMixin):
    """Shipment."""

    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
        comment="Unique ID for this shipment",
    )

    carton_number: Mapped[str] = mapped_column(comment="K-ERP carton number")
    tracking_number: Mapped[str | None] = mapped_column(comment="FedEx tracking number")

    status: Mapped[str] = mapped_column(comment="Shipment status")

    fedex_create_label_request: Mapped[dict | None] = mapped_column(  # type: ignore[type-arg]
        default=None,
        comment="FedEx label creation request data",
    )

    fedex_create_label_response: Mapped[dict | None] = mapped_column(  # type: ignore[type-arg]
        default=None,
        comment="FedEx label creation response data",
    )

    kerp_tracking_upload_response: Mapped[dict | None] = mapped_column(default=None)  # type: ignore[type-arg]
