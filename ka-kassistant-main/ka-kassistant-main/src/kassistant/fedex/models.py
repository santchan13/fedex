"""FedEx models."""

# ruff: noqa: N815

from typing import Literal, Self

from pydantic import BaseModel, model_validator

__all__ = [
    "AccountNumber",
    "Address",
    "Contact",
    "CustomerReference",
    "FedExShipmentRequest",
    "LabelSpecification",
    "Payor",
    "Recipient",
    "RequestedPackageLineItem",
    "RequestedShipment",
    "ResponsibleParty",
    "ShipmentSpecialServices",
    "Shipper",
    "ShippingChargesPayment",
    "Weight",
]


class AccountNumber(BaseModel):
    """AccountNumber."""

    value: str


class Address(BaseModel):
    """Address."""

    streetLines: list[str]
    city: str
    stateOrProvinceCode: str
    postalCode: str
    countryCode: str


class Contact(BaseModel):
    """Contact."""

    personName: str
    phoneNumber: int
    companyName: str


class CustomerReference(BaseModel):
    """CustomerReference."""

    customerReferenceType: Literal[
        "CUSTOMER_REFERENCE",
        "DEPARTMENT_NUMBER",
        "INVOICE_NUMBER",
        "P_O_NUMBER",
        "INTRACOUNTRY_REGULATORY_REFERENCE",
        "RMA_ASSOCIATION",
        "SHIPMENT_INTEGRITY",
    ]
    value: str


class LabelSpecification(BaseModel):
    """LabelSpecification."""

    imageType: Literal[
        "PDF",
        "PNG",
        "ZPLII",
        "EPL2",
    ] = "ZPLII"
    labelStockType: Literal[
        # PNG and PDF
        "PAPER_4X6",
        "PAPER_4X675",
        "PAPER_4X8",
        "PAPER_4X9",
        "PAPER_7X475",
        "PAPER_85X11_BOTTOM_HALF_LABEL",
        "PAPER_85X11_TOP_HALF_LABEL",
        "PAPER_LETTER",
        # ZPLII and EPL2
        "STOCK_4X6",
        "STOCK_4X675_LEADING_DOC_TAB",
        "STOCK_4X675_TRAILING_DOC_TAB",
        "STOCK_4X8",
        "STOCK_4X9",
        "STOCK_4X9_LEADING_DOC_TAB",
        "STOCK_4X9_TRAILING_DOC_TAB",
        "STOCK_4X85_TRAILING_DOC_TAB",
        "STOCK_4X105_TRAILING_DOC_TAB",
    ] = "STOCK_4X6"

    @model_validator(mode="after")
    def check_using_valid_stock_type(self: Self) -> Self:
        """Check that a valid stock type is selected."""
        if self.imageType in {"PNG", "PDF"} and not self.labelStockType.startswith("PAPER_"):
            msg = "PNG and PDF images must use PAPER stock types"
            raise ValueError(msg)

        if self.imageType in {"ZPLII", "EPL2"} and not self.labelStockType.startswith("STOCK_"):
            msg = "ZPLII and EPL2 images must use STOCK stock types"
            raise ValueError(msg)

        return self


class Recipient(BaseModel):
    """Recipient."""

    contact: Contact
    address: Address


class Weight(BaseModel):
    """Weight."""

    value: float
    units: Literal["LB"] = "LB"


class ShipmentSpecialServices(BaseModel):
    """ShipmentSpecialServices."""

    specialServiceTypes: list[Literal["SATURDAY_DELIVERY"]]


class RequestedPackageLineItem(BaseModel):
    """RequestedPackageLineItem."""

    weight: Weight
    customerReferences: list[CustomerReference]
    shipmentSpecialServices: ShipmentSpecialServices | None = None


class ResponsibleParty(BaseModel):
    """ResponsibleParty."""

    accountNumber: AccountNumber
    address: Address | None = None
    contact: Contact | None = None


class Payor(BaseModel):
    """Payor."""

    responsibleParty: ResponsibleParty


class ShippingChargesPayment(BaseModel):
    """ShippingChargesPayment."""

    paymentType: Literal["SENDER", "RECIPIENT", "THIRD_PARTY", "COLLECT"]
    payor: Payor | None = None


class Shipper(BaseModel):
    """Shipper."""

    contact: Contact
    address: Address


class RequestedShipment(BaseModel):
    """RequestedShipment."""

    shipper: Shipper
    recipients: list[Recipient]
    shipDatestamp: str
    serviceType: Literal[
        "FEDEX_INTERNATIONAL_PRIORITY_EXPRESS",
        "INTERNATIONAL_FIRST",
        "FEDEX_INTERNATIONAL_PRIORITY",
        "INTERNATIONAL_ECONOMY",
        "FEDEX_GROUND",
        "FEDEX_CARGO_INTERNATIONAL_PREMIUM",
        "FIRST_OVERNIGHT",
        "FIRST_OVERNIGHT_FREIGHT",
        "FEDEX_1_DAY_FREIGHT",
        "FEDEX_2_DAY_FREIGHT",
        "FEDEX_3_DAY_FREIGHT",
        "INTERNATIONAL_PRIORITY_FREIGHT",
        "INTERNATIONAL_ECONOMY_FREIGHT",
        "FEDEX_CARGO_AIRPORT_TO_AIRPORT",
        "INTERNATIONAL_PRIORITY_DISTRIBUTION",
        "FEDEX_IP_DIRECT_DISTRIBUTION_FREIGHT",
        "INTL_GROUND_DISTRIBUTION",
        "GROUND_HOME_DELIVERY",
        "SMART_POST",
        "PRIORITY_OVERNIGHT",
        "STANDARD_OVERNIGHT",
        "FEDEX_2_DAY",
        "FEDEX_2_DAY_AM",
        "FEDEX_EXPRESS_SAVER",
        "SAME_DAY",
        "SAME_DAY_CITY",
    ]
    shippingChargesPayment: ShippingChargesPayment
    labelSpecification: LabelSpecification
    requestedPackageLineItems: list[RequestedPackageLineItem]
    packagingType: Literal[
        "YOUR_PACKAGING",
        "FEDEX_ENVELOPE",
        "FEDEX_BOX",
        "FEDEX_SMALL_BOX",
        "FEDEX_MEDIUM_BOX",
        "FEDEX_LARGE_BOX",
        "FEDEX_EXTRA_LARGE_BOX",
        "FEDEX_10KG_BOX",
        "FEDEX_25KG_BOX",
        "FEDEX_PAK",
        "FEDEX_TUBE",
    ] = "YOUR_PACKAGING"
    pickupType: Literal[
        "CONTACT_FEDEX_TO_SCHEDULE",
        "DROPOFF_AT_FEDEX_LOCATION",
        "USE_SCHEDULED_PICKUP",
    ] = "USE_SCHEDULED_PICKUP"

    blockInsightVisibility: Literal[True, False] = False


class FedExShipmentRequest(BaseModel):
    """FedExLabelRequest."""

    requestedShipment: RequestedShipment
    accountNumber: AccountNumber
    labelResponseOptions: Literal["URL_ONLY", "LABEL"] = "LABEL"
