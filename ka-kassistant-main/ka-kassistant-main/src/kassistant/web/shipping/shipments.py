"""Web shipping."""

import json
from base64 import b64decode
from uuid import UUID

from litestar import Controller, get
from litestar.exceptions import HTTPException
from litestar.response import Stream
from sqlalchemy import select

from kassistant.orm import Session, Shipment


class ShipmentController(Controller):
    """Shipment controller."""

    path = "/shipment"

    @get("/{shipment_id: uuid}/fedex/create-label-request")
    async def show_create_label_request_data(self, shipment_id: UUID) -> str:
        """Show label request data."""
        with Session() as session:
            shipment = session.scalars(select(Shipment).filter_by(id=shipment_id)).first()

            if shipment is None:
                msg = "shipment not found"
                raise HTTPException(msg, status_code=404)

            if shipment.fedex_create_label_request is None:
                msg = "label not created"
                raise HTTPException(msg, status_code=404)

            return json.dumps(shipment.fedex_create_label_request, indent=4)

    @get("/{shipment_id: uuid}/fedex/create-label-response")
    async def show_create_label_response_data(self, shipment_id: UUID) -> str:
        """Show label response data."""
        with Session() as session:
            shipment = session.scalars(select(Shipment).filter_by(id=shipment_id)).first()

            if shipment is None:
                msg = "shipment not found"
                raise HTTPException(msg, status_code=404)

            if shipment.fedex_create_label_response is None:
                msg = "label not created"
                raise HTTPException(msg, status_code=404)

            return json.dumps(shipment.fedex_create_label_response, indent=4)

    @get("/{shipment_id: uuid}/zpl")
    async def label(self, shipment_id: UUID) -> str:
        """Render label ZPL."""
        with Session() as session:
            shipment = session.scalars(select(Shipment).filter_by(id=shipment_id)).first()

            if shipment is None:
                msg = "shipment not found"
                raise HTTPException(msg, status_code=404)

            if shipment.fedex_create_label_response is None:
                msg = "label not created"
                raise HTTPException(msg, status_code=404)

            first_package = shipment.fedex_create_label_response["output"]["transactionShipments"][0]["pieceResponses"][
                0
            ]
            return b64decode(first_package["packageDocuments"][0]["encodedLabel"]).decode("utf-8")

    @get("/{shipment_id: uuid}/support-data")
    async def support_data(self, shipment_id: UUID) -> Stream:
        """Render support data."""
        with Session() as session:
            shipment = session.scalars(select(Shipment).filter_by(id=shipment_id)).first()

            if shipment is None:
                msg = "shipment not found"
                raise HTTPException(msg, status_code=404)

            data = {
                "id": str(shipment.id),
                "carton_number": shipment.carton_number,
                "tracking_number": shipment.tracking_number,
                "status": shipment.status,
                "fedex_create_label_request": shipment.fedex_create_label_request,
                "fedex_create_label_response": shipment.fedex_create_label_response,
                "kerp_tracking_upload_response": shipment.kerp_tracking_upload_response,
            }

            return Stream(
                content=json.dumps(data, indent=4),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=kassistant-shipment-{shipment.id}.json"},
            )
