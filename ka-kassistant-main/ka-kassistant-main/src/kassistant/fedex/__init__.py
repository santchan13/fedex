"""FedEx."""

from kassistant.constants import FedEx

from .client import FedExServices
from .models import (
    AccountNumber,
    Address,
    Contact,
    CustomerReference,
    FedExShipmentRequest,
    LabelSpecification,
    Payor,
    Recipient,
    RequestedPackageLineItem,
    RequestedShipment,
    ResponsibleParty,
    ShipmentSpecialServices,
    Shipper,
    ShippingChargesPayment,
    Weight,
)

fedex_client = FedExServices(FedEx.base_url, FedEx.client_id, FedEx.client_secret)


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
    "fedex_client",
]
