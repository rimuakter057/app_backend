"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("buyer", "owner", "admin", name="user_role"),
            nullable=False,
        ),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("company", sa.String(200), nullable=True),
        sa.Column(
            "verification_status",
            sa.Enum("unverified", "pending", "verified", name="verification_status"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("bio", sa.String(2000), nullable=True),
        sa.Column("city", sa.String(120), nullable=True),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("reviews_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("kind", sa.Enum("sale", "rent", name="property_kind"), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "apartment", "house", "villa", "land", "office", "shop", "commercial", name="property_type"
            ),
            nullable=False,
        ),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("area_sqft", sa.Float(), nullable=True),
        sa.Column("floor", sa.Integer(), nullable=True),
        sa.Column("furnished", sa.Boolean(), nullable=False),
        sa.Column("property_age", sa.Integer(), nullable=True),
        sa.Column("amenities", sa.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "pending", "active", "rejected", "sold", name="property_status"),
            nullable=False,
        ),
        sa.Column("featured", sa.Boolean(), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_properties_owner_id", "properties", ["owner_id"])
    op.create_index("ix_properties_city", "properties", ["city"])
    op.create_index("ix_properties_status", "properties", ["status"])

    op.create_table(
        "property_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_cover", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_property_images_property_id", "property_images", ["property_id"])

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
        ),
        sa.UniqueConstraint("user_id", "property_id", name="uq_favorite_user_property"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_property_id", "favorites", ["property_id"])

    op.create_table(
        "visits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time_slot", sa.String(50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "completed", "cancelled", name="visit_status"),
            nullable=False,
        ),
        sa.Column("visitor_name", sa.String(120), nullable=True),
        sa.Column("visitor_phone", sa.String(30), nullable=True),
        sa.Column("note", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_visits_property_id", "visits", ["property_id"])
    op.create_index("ix_visits_buyer_id", "visits", ["buyer_id"])
    op.create_index("ix_visits_status", "visits", ["status"])

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("new", "contacted", "negotiating", "closed", "lost", name="lead_status"),
            nullable=False,
        ),
        sa.Column("message", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_leads_property_id", "leads", ["property_id"])
    op.create_index("ix_leads_buyer_id", "leads", ["buyer_id"])
    op.create_index("ix_leads_owner_id", "leads", ["owner_id"])
    op.create_index("ix_leads_status", "leads", ["status"])

    op.create_table(
        "chat_conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("user_a_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_b_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chat_conversations_property_id", "chat_conversations", ["property_id"])
    op.create_index("ix_chat_conversations_user_a_id", "chat_conversations", ["user_a_id"])
    op.create_index("ix_chat_conversations_user_b_id", "chat_conversations", ["user_b_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.Integer(),
            sa.ForeignKey("chat_conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chat_messages_conversation_id", "chat_messages", ["conversation_id"])
    op.create_index("ix_chat_messages_sender_id", "chat_messages", ["sender_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.String(2000), nullable=True),
        sa.Column(
            "kind",
            sa.Enum(
                "message", "visit", "favorite", "price", "system", "lead", "approval", name="notification_kind"
            ),
            nullable=False,
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(200), nullable=False),
        sa.Column("details", sa.String(2000), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "resolved", "dismissed", name="report_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reports_property_id", "reports", ["property_id"])
    op.create_index("ix_reports_reporter_id", "reports", ["reporter_id"])
    op.create_index("ix_reports_status", "reports", ["status"])


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("notifications")
    op.drop_table("chat_messages")
    op.drop_table("chat_conversations")
    op.drop_table("leads")
    op.drop_table("visits")
    op.drop_table("favorites")
    op.drop_table("property_images")
    op.drop_table("properties")
    op.drop_table("users")
    op.drop_table("categories")

    for enum_name in (
        "user_role",
        "verification_status",
        "property_kind",
        "property_type",
        "property_status",
        "visit_status",
        "lead_status",
        "notification_kind",
        "report_status",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
