"""Web shipping."""

from litestar import Router

from .fedex import FedExController
from .history import HistoryController
from .shipments import ShipmentController

router = Router(
    path="/shipping",
    route_handlers=[
        HistoryController,
        ShipmentController,
        FedExController,
    ],
)
