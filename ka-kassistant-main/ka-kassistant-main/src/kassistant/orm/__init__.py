"""ORM."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kassistant.constants import App

from .settings import Settings
from .shipments import Shipment

__all__ = [
    "Session",
    "Settings",
    "Shipment",
    "engine",
]


engine = create_engine(App.database_url, connect_args={"options": "-c timezone=utc"})
Session = sessionmaker(engine)
