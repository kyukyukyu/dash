"""Initial revision

Revision ID: 5225efebb497
Revises: None
Create Date: 2015-11-20 01:50:16.208396

"""

# revision identifiers, used by Alembic.
revision = '5225efebb497'
down_revision = None

from alembic import op
import sqlalchemy as sa

import dash


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campuses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', dash.database.UTCDateTime(timezone=True), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('scraper', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('scraper')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('first_name', sa.String(length=30), nullable=True),
    sa.Column('last_name', sa.String(length=30), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('gen_edu_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', dash.database.UTCDateTime(timezone=True), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subjects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', dash.database.UTCDateTime(timezone=True), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('courses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', dash.database.UTCDateTime(timezone=True), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('type', sa.String(length=40), nullable=False),
    sa.Column('instructor', sa.String(length=80), nullable=True),
    sa.Column('credit', sa.Float(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', dash.database.UTCDateTime(timezone=True), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('campus_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['campus_id'], ['campuses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('major_courses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('target_grade', sa.Integer(), nullable=True),
    sa.CheckConstraint(u'target_grade IS NULL OR target_grade >= 0', name='ck_general_courses_target_grade'),
    sa.ForeignKeyConstraint(['id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('department_course',
    sa.Column('department_id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
    sa.PrimaryKeyConstraint('department_id', 'course_id')
    )
    op.create_table('general_courses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['gen_edu_categories.id'], ),
    sa.ForeignKeyConstraint(['id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('course_classes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', dash.database.UTCDateTime(timezone=True), nullable=False),
    sa.Column('day_of_week', sa.Integer(), nullable=False),
    sa.Column('start_period', sa.Integer(), nullable=False),
    sa.Column('end_period', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.CheckConstraint(u'day_of_week >= 0 AND day_of_week < 7', name='ck_course_classes_day_of_week'),
    sa.CheckConstraint(u'start_period >= 0 AND end_period >= 0 AND start_period <= end_period', name='ck_course_classes_start_end_period'),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('course_classes')
    op.drop_table('general_courses')
    op.drop_table('department_course')
    op.drop_table('major_courses')
    op.drop_table('departments')
    op.drop_table('roles')
    op.drop_table('courses')
    op.drop_table('subjects')
    op.drop_table('gen_edu_categories')
    op.drop_table('users')
    op.drop_table('campuses')
    ### end Alembic commands ###