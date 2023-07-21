"""initial_migration

Revision ID: cd6f78358781
Revises: 
Create Date: 2023-07-18 13:29:53.922013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "v0.1.0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "books",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("subtitle", sa.String(length=300), nullable=True),
        sa.Column("published_date", sa.String(length=30), nullable=True),
        sa.Column("publisher", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image", sa.Text(), nullable=True),
        sa.Column("original_source", sa.String(length=30), nullable=False),
        sa.Column("external_id", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("title", "books", ["title"], mysql_prefix='FULLTEXT')
    op.create_index("subtitle", "books", ["subtitle"], mysql_prefix='FULLTEXT')
    op.create_index("published_date", "books", ["published_date"], mysql_prefix='FULLTEXT')
    op.create_index("publisher", "books", ["publisher"], mysql_prefix='FULLTEXT')
    op.create_index("description", "books", ["description"], mysql_prefix='FULLTEXT')
    op.create_table(
        "authors",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("name", "authors", ["name"], mysql_prefix='FULLTEXT')
    op.create_table(
        "categories",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("name", "categories", ["name"], mysql_prefix='FULLTEXT')
    op.create_table(
        "book_authors",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey('books.id', ondelete='CASCADE'), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey('authors.id'), nullable=False),
        sa.UniqueConstraint("book_id", "author_id")
    )
    op.create_table(
        "book_categories",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey('books.id', ondelete='CASCADE'), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey('categories.id'), nullable=False),
        sa.UniqueConstraint("book_id", "category_id")
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("books")
    op.drop_table("authors")
    op.drop_table("categories")
    op.drop_table("book_authors")
    op.drop_table("book_categories")
    # ### end Alembic commands ###
