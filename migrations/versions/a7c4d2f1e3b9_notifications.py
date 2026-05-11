"""Notifications

Revision ID: a7c4d2f1e3b9
Revises: 2f1485fbd784
Create Date: 2026-05-11 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a7c4d2f1e3b9'
down_revision: Union[str, Sequence[str], None] = '2f1485fbd784'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationkind AS ENUM ('UPCOMING', 'DAILY');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)

    notification_kind = postgresql.ENUM('UPCOMING', 'DAILY', name='notificationkind', create_type=False)

    op.create_table(
        'notifications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('kind', notification_kind, nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notifications_id', 'notifications', ['id'], unique=False)
    op.create_index('ix_notifications_scheduled_at', 'notifications', ['scheduled_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_notifications_scheduled_at', table_name='notifications')
    op.drop_index('ix_notifications_id', table_name='notifications')
    op.drop_table('notifications')
    op.execute("DROP TYPE IF EXISTS notificationkind")
