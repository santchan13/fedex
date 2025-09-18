"""API server definition."""

from pathlib import Path

import sentry_sdk
from litestar import Litestar, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.response import Template
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

from kassistant.constants import Sentry
from kassistant.web.settings import SettingsController
from kassistant.web.shipping import router as shipping_router

from . import __version__
from .constants import GIT_SHA

sentry_sdk.init(
    dsn=Sentry.dsn,
    environment=Sentry.environment,
    send_default_pii=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
    enable_logs=True,
    release=f"{Sentry.release_prefix}@{GIT_SHA}",
)


@get("/")
async def homepage() -> Template:
    """Homepage."""
    return Template(
        template_name="home.html",
        context={
            "version": __version__,
            "git_sha": GIT_SHA,
        },
    )


app = Litestar(
    route_handlers=[
        # Home
        homepage,
        # Shipping
        shipping_router,
        # Settings
        SettingsController,
        # Static files
        create_static_files_router(path="/static", directories=["static"]),
    ],
    debug=True,
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
    ),
    openapi_config=OpenAPIConfig(
        title="KAssistant",
        version=__version__,
        render_plugins=[ScalarRenderPlugin()],
    ),
)
