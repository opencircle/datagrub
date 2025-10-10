"""add group access for projects

Revision ID: d0b4c5f6g7h8
Revises: c9a3b4d5e6f7
Create Date: 2025-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd0b4c5f6g7h8'
down_revision: Union[str, None] = 'c9a3b4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create groups table for future group-based access control
    op.create_table(
        'groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('organization_id', 'name', name='uq_group_org_name')
    )

    # Create user_groups association table
    op.create_table(
        'user_groups',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role', sa.String(50), nullable=False, server_default='member'),  # member, admin
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Create project_groups association table for group-based project access
    op.create_table(
        'project_groups',
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission', sa.String(50), nullable=False, server_default='read'),  # read, write, admin
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Add indexes for performance
    op.create_index('ix_groups_organization_id', 'groups', ['organization_id'])
    op.create_index('ix_user_groups_user_id', 'user_groups', ['user_id'])
    op.create_index('ix_user_groups_group_id', 'user_groups', ['group_id'])
    op.create_index('ix_project_groups_project_id', 'project_groups', ['project_id'])
    op.create_index('ix_project_groups_group_id', 'project_groups', ['group_id'])

    # Add access_level column to projects for future granular control
    op.add_column('projects', sa.Column('access_level', sa.String(50), nullable=False, server_default='organization'))
    # access_level values: 'organization' (all org members), 'groups' (specific groups only), 'private' (creator only)


def downgrade() -> None:
    op.drop_column('projects', 'access_level')

    op.drop_index('ix_project_groups_group_id', table_name='project_groups')
    op.drop_index('ix_project_groups_project_id', table_name='project_groups')
    op.drop_index('ix_user_groups_group_id', table_name='user_groups')
    op.drop_index('ix_user_groups_user_id', table_name='user_groups')
    op.drop_index('ix_groups_organization_id', table_name='groups')

    op.drop_table('project_groups')
    op.drop_table('user_groups')
    op.drop_table('groups')
