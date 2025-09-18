"""K-ERP."""

from kerp_sdk import KERPClient

from kassistant.constants import KERP

kerp_client = KERPClient(
    username="",
    password="",
    cartons_api_key=KERP.api_key,
)
