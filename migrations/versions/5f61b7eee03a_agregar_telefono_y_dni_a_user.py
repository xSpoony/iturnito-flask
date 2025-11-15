"""Agregar telefono y dni a User

Revision ID: 5f61b7eee03a
Revises: 00a0c8a5f9e8
Create Date: 2025-11-14 15:15:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f61b7eee03a'
down_revision = '00a0c8a5f9e8' # Asegúrate que 'Revises:' coincida con este
branch_labels = None
depends_on = None


def upgrade():
    # ### Comandos auto-generados con corrección ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('telefono', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('dni', sa.String(length=20), nullable=True))

        # --- ¡LA CORRECCIÓN ESTÁ AQUÍ! ---
        # Le damos un nombre a la restricción 'unique'
        batch_op.create_unique_constraint("uq_users_dni", ['dni'])

    # ### end Alembic commands ###


def downgrade():
    # ### Comandos auto-generados con corrección ###
    with op.batch_alter_table('users', schema=None) as batch_op:

        # --- ¡LA CORRECCIÓN ESTÁ AQUÍ! ---
        # Le decimos qué restricción por nombre debe eliminar
        batch_op.drop_constraint("uq_users_dni", type_='unique')
        batch_op.drop_column('dni')
        batch_op.drop_column('telefono')

    # ### end Alembic commands ###

