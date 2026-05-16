"""guild settings, whitelist, ignore lists; ReviewQueue.corrected_score

Revision ID: 002
Revises: 001
Create Date: 2026-05-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "guild_settings",
        sa.Column("guild_id", sa.String(length=32), nullable=False),
        sa.Column("review_channel_id", sa.String(length=32), nullable=True),
        sa.Column("log_channel_id", sa.String(length=32), nullable=True),
        sa.Column(
            "log_level",
            sa.String(length=16),
            server_default=sa.text("'block_flag'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("guild_id"),
    )

    op.create_table(
        "guild_whitelist",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.String(length=32), nullable=False),
        sa.Column("phrase", sa.Text(), nullable=False),
        sa.Column("added_by", sa.String(length=32), nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guild_id", "phrase", name="uq_guild_whitelist_phrase"),
    )
    op.create_index("ix_guild_whitelist_guild_id", "guild_whitelist", ["guild_id"])

    op.create_table(
        "guild_ignored_channels",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.String(length=32), nullable=False),
        sa.Column("channel_id", sa.String(length=32), nullable=False),
        sa.Column("added_by", sa.String(length=32), nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "guild_id", "channel_id", name="uq_guild_ignored_channel",
        ),
    )
    op.create_index(
        "ix_guild_ignored_channels_guild_id",
        "guild_ignored_channels",
        ["guild_id"],
    )

    op.create_table(
        "guild_ignored_roles",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.String(length=32), nullable=False),
        sa.Column("role_id", sa.String(length=32), nullable=False),
        sa.Column("added_by", sa.String(length=32), nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guild_id", "role_id", name="uq_guild_ignored_role"),
    )
    op.create_index(
        "ix_guild_ignored_roles_guild_id",
        "guild_ignored_roles",
        ["guild_id"],
    )

    op.add_column(
        "review_queue",
        sa.Column("corrected_score", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("review_queue", "corrected_score")

    op.drop_index(
        "ix_guild_ignored_roles_guild_id",
        table_name="guild_ignored_roles",
    )
    op.drop_table("guild_ignored_roles")

    op.drop_index(
        "ix_guild_ignored_channels_guild_id",
        table_name="guild_ignored_channels",
    )
    op.drop_table("guild_ignored_channels")

    op.drop_index("ix_guild_whitelist_guild_id", table_name="guild_whitelist")
    op.drop_table("guild_whitelist")

    op.drop_table("guild_settings")
