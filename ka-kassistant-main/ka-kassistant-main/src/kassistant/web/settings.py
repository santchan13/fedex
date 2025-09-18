"""Web settings."""

from typing import Annotated

from litestar import Controller, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Template
from sqlalchemy import select

from kassistant.forms import SettingsForm
from kassistant.orm import Session, Settings


class SettingsController(Controller):
    """Settings controller."""

    path = "/settings"

    @get("/setup")
    async def setup_settings(self) -> Template:
        """Create settings."""
        with Session() as session:
            settings = session.scalars(select(Settings)).first()
            if settings is None:
                settings = Settings()

            return Template(
                template_name="settings.html",
                context={"settings": settings},
            )

    @post("/setup")
    async def persist_settings(
        self,
        data: Annotated[SettingsForm, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        """Create settings."""
        with Session() as session:
            settings = session.scalars(select(Settings)).first()
            if settings is None:
                settings = Settings()

            settings.ship_from_company = data.ship_from_company
            settings.ship_from_name = data.ship_from_name
            settings.ship_from_phone = data.ship_from_phone
            settings.ship_from_address_1 = data.ship_from_address_1
            settings.ship_from_address_2 = data.ship_from_address_2
            settings.ship_from_city = data.ship_from_city
            settings.ship_from_state = data.ship_from_state
            settings.ship_from_postal_code = data.ship_from_postal_code
            settings.ship_from_country_code = data.ship_from_country_code
            settings.fedex_label_size = data.fedex_label_size

            session.add(settings)
            session.commit()

            return Redirect(path="/")
