"""Add cover_url to book (manual)

Revision ID: 708a636a3d15
Revises: 
Create Date: 2025-11-25 22:27:29.736039

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy


# revision identifiers, used by Alembic.
revision = '708a636a3d15'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sqlalchemy.inspect(conn)
    if 'book' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('book')]
        if 'cover_url' not in cols:
            op.add_column('book', sa.Column('cover_url', sa.String(512), nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = sqlalchemy.inspect(conn)
    if 'book' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('book')]
        if 'cover_url' in cols:
            try:
                op.drop_column('book', 'cover_url')
            except Exception:
                # SQLite older versions do not support DROP COLUMN; ignore gracefully
                pass
