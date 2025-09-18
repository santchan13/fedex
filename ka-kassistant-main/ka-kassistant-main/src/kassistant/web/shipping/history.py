"""Web shipping history."""

from datetime import date
from typing import Annotated

from litestar import Controller, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Stream, Template
from sqlalchemy import Date, cast, func, select

from kassistant.constants import App
from kassistant.forms import HistoryForm
from kassistant.orm import Session, Shipment
from kassistant.run_labels import build_excel_export


class HistoryController(Controller):
    """History controller."""

    path = "/history"

    @post("/date-form")
    async def history_date(
        self,
        data: Annotated[HistoryForm, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        """History route to redirect to a date page."""
        path = f"/shipping/history/{data.ship_date}"
        if data.detailed:
            path += "?detailed"
        return Redirect(path=path)

    @get("/{ship_date: date}")
    async def history(self, ship_date: date, detailed: str | None) -> Template:
        """Shipment history."""
        with Session() as session:
            shipments = session.scalars(
                select(Shipment)
                .where(cast(func.timezone(App.time_zone, Shipment.created), Date) == ship_date)
                .order_by(Shipment.created.desc()),
            ).all()

            return Template(
                template_name="shipping/history.html",
                context={"shipments": shipments, "detailed": detailed, "ship_date": ship_date},
            )

    @get("/{ship_date: date}/excel")
    async def history_export(self, ship_date: date) -> Stream:
        """Create an Excel export of the shipment history."""
        with Session() as session:
            shipments = session.scalars(
                select(Shipment)
                .where(cast(func.timezone(App.time_zone, Shipment.created), Date) == ship_date)
                .order_by(Shipment.created.desc()),
            ).all()

            return Stream(
                content=build_excel_export(shipments),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=shipment_history_{ship_date}.xlsx"},
            )
