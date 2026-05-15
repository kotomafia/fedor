"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("base_model", sa.String(length=256), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "verdicts",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.String(length=32), nullable=False),
        sa.Column("guild_id", sa.String(length=32), nullable=False),
        sa.Column("channel_id", sa.String(length=32), nullable=False),
        sa.Column("author_id", sa.String(length=32), nullable=False),
        sa.Column("source_kind", sa.String(length=16), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column(
            "categories",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("model_version_id", sa.Integer(), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("ocr_confidence", sa.Float(), nullable=True),
        sa.Column("ocr_engine", sa.String(length=64), nullable=True),
        sa.Column("inference_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("score >= 0 AND score <= 1", name="score_range"),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_verdicts_message_id", "verdicts", ["message_id"])
    op.create_index("ix_verdicts_guild_id", "verdicts", ["guild_id"])
    op.create_index("ix_verdicts_author_id", "verdicts", ["author_id"])
    op.create_index("ix_verdicts_content_hash", "verdicts", ["content_hash"])
    op.create_index("ix_verdicts_created_at", "verdicts", ["created_at"])
    op.create_index("ix_verdicts_guild_created", "verdicts", ["guild_id", "created_at"])

    op.create_table(
        "content_cache",
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("source_kind", sa.String(length=16), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column(
            "categories",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("model_version_id", sa.Integer(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("hit_count", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "last_hit_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"]),
        sa.PrimaryKeyConstraint("content_hash", "source_kind"),
    )

    op.create_table(
        "review_queue",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("verdict_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("review_message_id", sa.String(length=32), nullable=True),
        sa.Column("reviewer_id", sa.String(length=32), nullable=True),
        sa.Column("reviewer_decision_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("corrected_label", sa.String(length=32), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["verdict_id"], ["verdicts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("verdict_id"),
    )
    op.create_index("ix_review_queue_status", "review_queue", ["status"])


def downgrade() -> None:
    op.drop_index("ix_review_queue_status", table_name="review_queue")
    op.drop_table("review_queue")
    op.drop_table("content_cache")
    op.drop_index("ix_verdicts_guild_created", table_name="verdicts")
    op.drop_index("ix_verdicts_created_at", table_name="verdicts")
    op.drop_index("ix_verdicts_content_hash", table_name="verdicts")
    op.drop_index("ix_verdicts_author_id", table_name="verdicts")
    op.drop_index("ix_verdicts_guild_id", table_name="verdicts")
    op.drop_index("ix_verdicts_message_id", table_name="verdicts")
    op.drop_table("verdicts")
    op.drop_table("model_versions")
