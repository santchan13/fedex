#!/bin/sh

uv run --no-sync python -m alembic upgrade head
uv run --no-sync python -m uvicorn kassistant.server:app --host 0.0.0.0 --port 8000 --workers 4 --timeout-keep-alive 600
