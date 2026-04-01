"""empty message

Revision ID: f59096e51e98
Revises: 
Create Date: 2026-04-02 00:54:14.070196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f59096e51e98'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Создаем типы Enum
    status_enum = sa.Enum('TODO', 'PROGRESS', 'DONE', name='taskstatus')
    priority_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority')
    status_enum.create(op.get_bind(), checkfirst=True)
    priority_enum.create(op.get_bind(), checkfirst=True)

    # 2. Создаем таблицу USER (базовая)
    op.create_table(
        'user',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 3. Создаем таблицу PROJECT
    op.create_table(
        'project',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Создаем таблицу TASK (теперь она видит и user, и project)
    op.create_table(
        'task',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=40), nullable=False),
        sa.Column('description', sa.String(length=300), nullable=True),
        sa.Column('status', postgresql.ENUM('TODO', 'PROGRESS', 'DONE', name='taskstatus', create_type=False), server_default='TODO', nullable=False),
        sa.Column('priority', postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', name='taskpriority', create_type=False), server_default='LOW', nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('author_id', sa.UUID(), nullable=False),
        sa.Column('assignee_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('update_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assignee_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Создаем таблицу TASK_HISTORY
    op.create_table(
        'task_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('change_by', sa.UUID(), nullable=False),
        sa.Column('field_name', sa.String(), nullable=False),
        sa.Column('old_value', sa.String(), nullable=True),
        sa.Column('new_value', sa.String(), nullable=False),
        sa.Column('create_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['change_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
def downgrade() -> None:
    op.drop_table('task_history')
    op.drop_table('task')
    # Удаляем типы
    sa.Enum(name='taskpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='taskstatus').drop(op.get_bind(), checkfirst=True)