### Setup a database

```bash
cd scripts/
docker compose up postgres17
```

### Running the development server

```bash
echo 'APP_DATABASE_URL="postgresql+psycopg://postgres:shadow@localhost/kerp_shipping"' > .env
uv run alembic upgrade head
LITESTAR_APP=core.web.server:app uv run litestar run --debug
```
