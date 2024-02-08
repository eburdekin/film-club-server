"""update tables

Revision ID: 60c2e52a7291
Revises: 1ff7491153ad
Create Date: 2024-02-07 18:01:55.639786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60c2e52a7291'
down_revision = '1ff7491153ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movies', 'trailer_link')
    op.drop_column('movies', 'streaming_availability')
    op.drop_column('movies', 'cast')
    op.drop_column('movies', 'director')
    op.drop_column('movies', 'summary')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('summary', sa.VARCHAR(), nullable=True))
    op.add_column('movies', sa.Column('director', sa.VARCHAR(), nullable=True))
    op.add_column('movies', sa.Column('cast', sa.VARCHAR(), nullable=True))
    op.add_column('movies', sa.Column('streaming_availability', sa.VARCHAR(), nullable=True))
    op.add_column('movies', sa.Column('trailer_link', sa.VARCHAR(), nullable=True))
    # ### end Alembic commands ###
