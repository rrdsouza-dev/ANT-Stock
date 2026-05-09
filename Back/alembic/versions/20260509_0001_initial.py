"""initial modern schema

Revision ID: 20260509_0001
Revises:
Create Date: 2026-05-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "20260509_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "escopos",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column("scope_type", sa.Enum("SCHOOL_MANAGEMENT", "LOGISTICS_CLASS", name="scopetype"), nullable=False),
        sa.Column("school_id", sa.Uuid(), nullable=True),
        sa.Column("class_id", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_escopos_id"), "escopos", ["id"], unique=False)
    op.create_index(op.f("ix_escopos_scope_type"), "escopos", ["scope_type"], unique=False)

    op.create_table(
        "usuarios",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True),
        sa.Column("password_hash", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("provider", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=True),
        sa.Column("profile", sa.Enum("MANAGEMENT", "TEACHER", "STUDENT", name="userprofile"), nullable=True),
        sa.Column("scope_id", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["scope_id"], ["escopos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)

    op.create_table(
        "categorias",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope_id", sa.Uuid(), nullable=False),
        sa.Column("scope_type", sa.Enum("SCHOOL_MANAGEMENT", "LOGISTICS_CLASS", name="scopetype"), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["scope_id"], ["escopos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_id", "name", name="uq_categorias_escopo_nome"),
    )
    op.create_index(op.f("ix_categorias_id"), "categorias", ["id"], unique=False)
    op.create_index(op.f("ix_categorias_name"), "categorias", ["name"], unique=False)
    op.create_index(op.f("ix_categorias_scope_id"), "categorias", ["scope_id"], unique=False)

    op.create_table(
        "localizacoes",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope_id", sa.Uuid(), nullable=False),
        sa.Column("scope_type", sa.Enum("SCHOOL_MANAGEMENT", "LOGISTICS_CLASS", name="scopetype"), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column("aisle", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("shelf", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("position", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["scope_id"], ["escopos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_id", "name", name="uq_localizacoes_escopo_nome"),
    )
    op.create_index(op.f("ix_localizacoes_id"), "localizacoes", ["id"], unique=False)
    op.create_index(op.f("ix_localizacoes_name"), "localizacoes", ["name"], unique=False)
    op.create_index(op.f("ix_localizacoes_scope_id"), "localizacoes", ["scope_id"], unique=False)

    op.create_table(
        "produtos",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope_id", sa.Uuid(), nullable=False),
        sa.Column("scope_type", sa.Enum("SCHOOL_MANAGEMENT", "LOGISTICS_CLASS", name="scopetype"), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=160), nullable=False),
        sa.Column("sku", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=True),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("location_id", sa.Uuid(), nullable=True),
        sa.Column("minimum_quantity", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categorias.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["localizacoes.id"]),
        sa.ForeignKeyConstraint(["scope_id"], ["escopos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_id", "sku", name="uq_produtos_escopo_sku"),
    )
    op.create_index(op.f("ix_produtos_id"), "produtos", ["id"], unique=False)
    op.create_index(op.f("ix_produtos_name"), "produtos", ["name"], unique=False)
    op.create_index(op.f("ix_produtos_scope_id"), "produtos", ["scope_id"], unique=False)
    op.create_index(op.f("ix_produtos_sku"), "produtos", ["sku"], unique=False)

    op.create_table(
        "estoques",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope_id", sa.Uuid(), nullable=False),
        sa.Column("scope_type", sa.Enum("SCHOOL_MANAGEMENT", "LOGISTICS_CLASS", name="scopetype"), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("location_id", sa.Uuid(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["localizacoes.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["produtos.id"]),
        sa.ForeignKeyConstraint(["scope_id"], ["escopos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_id", "product_id", "location_id", name="uq_estoques_escopo_produto_local"),
    )
    op.create_index(op.f("ix_estoques_id"), "estoques", ["id"], unique=False)
    op.create_index(op.f("ix_estoques_product_id"), "estoques", ["product_id"], unique=False)
    op.create_index(op.f("ix_estoques_scope_id"), "estoques", ["scope_id"], unique=False)

    op.create_table(
        "movimentacoes",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope_id", sa.Uuid(), nullable=False),
        sa.Column("scope_type", sa.Enum("SCHOOL_MANAGEMENT", "LOGISTICS_CLASS", name="scopetype"), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("movement_type", sa.Enum("IN", "OUT", name="movementtype"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("origin", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True),
        sa.Column("destination", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True),
        sa.Column("note", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("moved_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["produtos.id"]),
        sa.ForeignKeyConstraint(["scope_id"], ["escopos.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_movimentacoes_id"), "movimentacoes", ["id"], unique=False)
    op.create_index(op.f("ix_movimentacoes_product_id"), "movimentacoes", ["product_id"], unique=False)
    op.create_index(op.f("ix_movimentacoes_scope_id"), "movimentacoes", ["scope_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_movimentacoes_scope_id"), table_name="movimentacoes")
    op.drop_index(op.f("ix_movimentacoes_product_id"), table_name="movimentacoes")
    op.drop_index(op.f("ix_movimentacoes_id"), table_name="movimentacoes")
    op.drop_table("movimentacoes")
    op.drop_index(op.f("ix_estoques_scope_id"), table_name="estoques")
    op.drop_index(op.f("ix_estoques_product_id"), table_name="estoques")
    op.drop_index(op.f("ix_estoques_id"), table_name="estoques")
    op.drop_table("estoques")
    op.drop_index(op.f("ix_produtos_sku"), table_name="produtos")
    op.drop_index(op.f("ix_produtos_scope_id"), table_name="produtos")
    op.drop_index(op.f("ix_produtos_name"), table_name="produtos")
    op.drop_index(op.f("ix_produtos_id"), table_name="produtos")
    op.drop_table("produtos")
    op.drop_index(op.f("ix_localizacoes_scope_id"), table_name="localizacoes")
    op.drop_index(op.f("ix_localizacoes_name"), table_name="localizacoes")
    op.drop_index(op.f("ix_localizacoes_id"), table_name="localizacoes")
    op.drop_table("localizacoes")
    op.drop_index(op.f("ix_categorias_scope_id"), table_name="categorias")
    op.drop_index(op.f("ix_categorias_name"), table_name="categorias")
    op.drop_index(op.f("ix_categorias_id"), table_name="categorias")
    op.drop_table("categorias")
    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_index(op.f("ix_escopos_scope_type"), table_name="escopos")
    op.drop_index(op.f("ix_escopos_id"), table_name="escopos")
    op.drop_table("escopos")
    op.execute("DROP TYPE IF EXISTS movementtype")
    op.execute("DROP TYPE IF EXISTS userprofile")
    op.execute("DROP TYPE IF EXISTS scopetype")
