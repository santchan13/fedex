"""Initialize UUID extension.

Revision ID: 8213cad99c06
Revises:
Create Date: 2024-03-18 14:40:46.010478+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8213cad99c06"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text('CREATE EXTENSION "uuid-ossp";'))


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text('DROP EXTENSION "uuid-ossp";'))
