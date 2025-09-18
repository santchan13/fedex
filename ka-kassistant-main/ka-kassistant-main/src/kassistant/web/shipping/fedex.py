"""FedEx shipping integration."""

from typing import Annotated

from litestar import Controller, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Template
from sqlalchemy import select

from kassistant.forms import LabelRequestForm
from kassistant.orm import Session, Settings
from kassistant.run_labels import run_labels


class FedExController(Controller):
    """FedEx controller."""

    path = "/fedex"

    @get("/form")
    async def ship_fedex(self) -> Template | Redirect:
        """FedEx shipping."""
        with Session() as session:
            settings = session.scalars(select(Settings)).first()
            if settings is None:
                return Redirect(path="/settings/setup")
        return Template(template_name="shipping/fedex/form.html")

    @post("/process-cartons")
    async def process_cartons(
        self,
        data: Annotated[LabelRequestForm, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> str:
        """POST route to handle creating labels."""
        return await run_labels(data)
