"""The base classes for ORM models."""

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classes that inherit this class will be automatically mapped using declarative mapping."""

    type_annotation_map = {  # noqa: RUF012
        dict: MutableDict.as_mutable(JSONB),
    }
