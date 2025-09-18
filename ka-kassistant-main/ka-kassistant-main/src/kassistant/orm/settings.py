"""Model: Settings."""

import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from kassistant._types import LABEL_SIZE

from .base import Base
from .mixins.timestamps import TimestampsMixin


class Settings(Base, TimestampsMixin):
    """Settings."""

    __tablename__ = "settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
        comment="Unique ID for this setting",
    )

    ship_from_company: Mapped[str] = mapped_column(comment="Ship from company name")
    ship_from_name: Mapped[str] = mapped_column(comment="Ship from contact name")
    ship_from_phone: Mapped[str] = mapped_column(comment="Ship from contact phone")
    ship_from_address_1: Mapped[str] = mapped_column(comment="Ship from address line 1")
    ship_from_address_2: Mapped[str] = mapped_column(comment="Ship from address line 2")
    ship_from_city: Mapped[str] = mapped_column(comment="Ship from city")
    ship_from_state: Mapped[str] = mapped_column(comment="Ship from state")
    ship_from_postal_code: Mapped[str] = mapped_column(comment="Ship from postal code")
    ship_from_country_code: Mapped[str] = mapped_column(comment="Ship from country code")

    fedex_label_size: Mapped[LABEL_SIZE] = mapped_column(comment="FedEx label size")
