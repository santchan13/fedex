"""File to hold the form by itself to avoid circular imports."""

from typing import Literal

from pydantic import BaseModel, Field

from ._types import LABEL_SIZE

type APIServiceName = Literal[
    "FEDEX_2_DAY",
    "FEDEX_EXPRESS_SAVER",
    "FEDEX_GROUND",
    "PRIORITY_OVERNIGHT",
    "STANDARD_OVERNIGHT",
]
type APIBillingName = Literal[
    "COLLECT",
    "RECIPIENT",
    "SENDER",
    "THIRD_PARTY",
]


class LabelRequestForm(BaseModel):
    """FormData."""

    ship_date: str
    service: APIServiceName
    billing: APIBillingName
    third_party_account_number: str
    air_auth: str | None
    carton_numbers: str
    saturday_delivery: bool | None = None


class HistoryForm(BaseModel):
    """HistoryForm."""

    ship_date: str = Field(alias="ship_date_history")
    detailed: str | None = None


class SettingsForm(BaseModel):
    """SettingsForm."""

    ship_from_company: str
    ship_from_name: str
    ship_from_phone: str
    ship_from_address_1: str
    ship_from_address_2: str
    ship_from_city: str
    ship_from_state: str
    ship_from_postal_code: str
    ship_from_country_code: str

    fedex_label_size: LABEL_SIZE
