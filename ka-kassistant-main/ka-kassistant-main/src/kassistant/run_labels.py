"""Run labels for cartons."""

from base64 import b64decode
from collections.abc import Sequence
from datetime import datetime
from http import HTTPStatus
from io import BytesIO
from logging import getLogger

import xlsxwriter
from kerp_sdk.api_models import Carton, TrackingUpdateRequest
from sqlalchemy import select

from .constants import FedEx
from .fedex import (
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
    fedex_client,
)
from .forms import LabelRequestForm
from .kerp import kerp_client
from .orm import Session, Settings, Shipment

ERROR_LABEL_TEMPLATE = r"""
^XA

^CFA,90
^FB800,1,0,C
^FO15,60
^FDDO NOT SHIP\&^FS

^CFA,50
^FB800,1,0,C
^FO15,150
^FD{carton_number}\&^FS

^CFA,30
^FB800,20,0,C
^FO15,210
^FD{error_message}\&^FS

^XZ
"""

API_SERVICE_NAME_TO_WRITEBACK_SERVICE_NAME = {
    "FEDEX_2_DAY": "FedEx 2Day",
    "FEDEX_EXPRESS_SAVER": "FedEx Express Saver",
    "FEDEX_GROUND": "FedEx Ground Service",
    "PRIORITY_OVERNIGHT": "FedEx Priority Overnight",
    "STANDARD_OVERNIGHT": "FedEx Standard Overnight",
}
API_BILLING_NAME_TO_WRITEBACK_BILLING_NAME = {
    "COLLECT": "Collect",
    "RECIPIENT": "Recipient",
    "SENDER": "Sender",
    "THIRD_PARTY": "Third Party",
}

REPORT_COLUMN_HEADERS = [
    "CartonNumber",
    "TrackingNumber",
]
logger = getLogger(__name__)


def build_label_request_body(carton: Carton, form_data: LabelRequestForm) -> FedExShipmentRequest:
    """Build a label creation request."""
    with Session() as session:
        settings = session.scalars(select(Settings)).first()
        if settings is None:
            # This SHOULD be unreachable,
            # because the shipping route is redirected to the settings setup page if settings are not found.
            msg = (
                "Settings not found in database. "
                "Please set up the settings in the application. "
                "See https://impressdesigns.dev/knights-apparel-kerp-shipping/user/setup/getting-started"
            )
            raise ValueError(msg)

        shipping_charges_payment = ShippingChargesPayment(
            paymentType=form_data.billing,
            payor=Payor(
                responsibleParty=ResponsibleParty(
                    accountNumber=AccountNumber(value=form_data.third_party_account_number),
                ),
            ),
        )

        shipment_special_services = ShipmentSpecialServices(
            specialServiceTypes=[],
        )
        if form_data.saturday_delivery:
            shipment_special_services.specialServiceTypes.append("SATURDAY_DELIVERY")

        street_lines = [settings.ship_from_address_1]
        if settings.ship_from_address_2:
            street_lines.append(settings.ship_from_address_2)

        return FedExShipmentRequest(
            requestedShipment=RequestedShipment(
                shipper=Shipper(
                    contact=Contact(
                        personName=settings.ship_from_name,
                        phoneNumber=settings.ship_from_phone,
                        companyName=settings.ship_from_company,
                    ),
                    address=Address(
                        streetLines=street_lines,
                        city=settings.ship_from_city,
                        stateOrProvinceCode=settings.ship_from_state,
                        postalCode=settings.ship_from_postal_code,
                        countryCode=settings.ship_from_country_code,
                    ),
                ),
                recipients=[
                    Recipient(
                        contact=Contact(
                            personName=carton.company,
                            phoneNumber=1234567890,
                            companyName=carton.company,
                        ),
                        address=Address(
                            streetLines=[
                                carton.address1,
                                carton.address2,
                            ],
                            city=carton.city,
                            stateOrProvinceCode=carton.state,
                            postalCode=carton.postal_code,
                            countryCode="US",
                        ),
                    ),
                ],
                shipDatestamp=form_data.ship_date,
                serviceType=form_data.service,
                shippingChargesPayment=shipping_charges_payment,
                labelSpecification=LabelSpecification(labelStockType=settings.fedex_label_size),
                requestedPackageLineItems=[
                    RequestedPackageLineItem(
                        weight=Weight(value=carton.weight),
                        customerReferences=[
                            CustomerReference(
                                customerReferenceType="CUSTOMER_REFERENCE",
                                value=form_data.air_auth if form_data.air_auth else carton.carton_number,
                            ),
                            CustomerReference(
                                customerReferenceType="DEPARTMENT_NUMBER",
                                value=carton.carton_number,
                            ),
                            CustomerReference(
                                customerReferenceType="INVOICE_NUMBER",
                                value=f"{carton.control_number}-LN {carton.ps_line}",
                            ),
                            CustomerReference(
                                customerReferenceType="P_O_NUMBER",
                                value=carton.customer_purchase_order,
                            ),
                        ],
                        shipmentSpecialServices=shipment_special_services,
                    ),
                ],
            ),
            accountNumber=AccountNumber(
                value=FedEx.account,
            ),
        )


async def run_labels(
    form_data: LabelRequestForm,
) -> str:
    """Create labels for cartons."""
    label_strs = []

    raw_text = form_data.carton_numbers
    carton_numbers = [line.strip() for line in raw_text.split("\n") if line.strip()]
    if len(carton_numbers) != len(set(carton_numbers)):
        msg = "Duplicate cartons scanned!"
        raise ValueError(msg)

    cartons_header = kerp_client.shipping.get_cartons(carton_numbers)
    cartons_map = {carton.carton_number: carton for carton in cartons_header.data}

    # Maintain insertion order for users
    cartons = []
    not_found_carton_numbers = []
    for carton_number in carton_numbers:
        if carton_number in cartons_map:
            cartons.append(cartons_map[carton_number])
        else:
            not_found_carton_numbers.append(carton_number)

    with Session() as session:
        for carton_number in not_found_carton_numbers:
            session.add(
                Shipment(
                    carton_number=carton_number,
                    tracking_number=None,
                    status="not_found_in_kerp",
                ),
            )
        session.commit()

    for carton in cartons:
        with Session() as session:
            existing_shipment = session.scalars(
                select(Shipment).where(Shipment.carton_number == carton.carton_number, Shipment.status == "shipped"),
            ).first()
            if existing_shipment is not None:
                label_strs.append(
                    ERROR_LABEL_TEMPLATE.format(
                        carton_number=existing_shipment.carton_number,
                        error_message=f"Label already created for this carton: {existing_shipment.tracking_number}",
                    ),
                )
                continue

            request_body = build_label_request_body(carton, form_data)
            label_response = fedex_client.create_label(request_body)
            if label_response.status_code == HTTPStatus.OK:
                status = "shipped"
                headless_label_data = label_response.json()["output"]["transactionShipments"][0]["pieceResponses"][0]
                tracking_number = headless_label_data["trackingNumber"]
                label_zpl_str = b64decode(headless_label_data["packageDocuments"][0]["encodedLabel"]).decode("utf-8")
                label_strs.append(label_zpl_str)

                kerp_update = TrackingUpdateRequest(
                    tracking_number=tracking_number,
                    reference=form_data.air_auth if form_data.air_auth else carton.carton_number,
                    department=carton.carton_number,
                    ship_date=datetime.strptime(form_data.ship_date, "%Y-%m-%d").date(),  # noqa: DTZ007
                    service=API_SERVICE_NAME_TO_WRITEBACK_SERVICE_NAME[form_data.service],
                    payment_type=API_BILLING_NAME_TO_WRITEBACK_BILLING_NAME[form_data.billing],
                )
                kerp_update_response = kerp_client.shipping.publish_tracking([kerp_update]).model_dump()

            else:
                status = "fedex_error"
                tracking_number = None

                if label_response.status_code == HTTPStatus.BAD_REQUEST:
                    try:
                        error_code = label_response.json()["errors"][0]["code"]
                        error_message = label_response.json()["errors"][0]["message"]
                        label_strs.append(
                            ERROR_LABEL_TEMPLATE.format(
                                carton_number=carton.carton_number,
                                error_message=f"{error_code}: {error_message}",
                            ),
                        )
                    # Don't bail on printing the valid labels if there's an error in the error label template
                    except Exception:
                        logger.exception("Could not format error label template")

                kerp_update_response = None

            session.add(
                Shipment(
                    carton_number=carton.carton_number,
                    tracking_number=tracking_number,
                    status=status,
                    fedex_create_label_request=request_body.model_dump(),
                    fedex_create_label_response=label_response.json(),
                    kerp_tracking_upload_response=kerp_update_response,
                ),
            )

            session.commit()

    return "\n".join(label_strs)


def build_excel_export(shipments: Sequence[Shipment]) -> BytesIO:
    """Build an excel export."""
    bytes_io = BytesIO()
    workbook = xlsxwriter.Workbook(bytes_io)
    worksheet = workbook.add_worksheet(name="Shipments")

    for column_index, header in enumerate(REPORT_COLUMN_HEADERS):
        worksheet.write(0, column_index, header)

    for row_index, shipment in enumerate(shipments, start=1):
        worksheet.write(row_index, 0, shipment.carton_number)
        worksheet.write(row_index, 1, shipment.tracking_number or "")

    # Create a table in the sheet
    column_settings = [{"header": header} for header in REPORT_COLUMN_HEADERS]
    worksheet.add_table(0, 0, len(shipments), len(REPORT_COLUMN_HEADERS) - 1, {"columns": column_settings})

    workbook.close()
    bytes_io.seek(0, 0)
    return bytes_io
