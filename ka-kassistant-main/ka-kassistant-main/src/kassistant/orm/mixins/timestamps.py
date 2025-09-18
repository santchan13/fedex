"""mixin: Timestamp."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampsMixin:
    """Add created, updated, and deleted timestamps to a model."""

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="The date and time the object was created",
    )

    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="The date and time the object was last updated",
    )

    deleted: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="The date and time the object was deleted (NULL if not deleted)",
    )
