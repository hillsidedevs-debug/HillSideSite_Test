"""Add missing columns and Review table

Revision ID: 1630febf9cc3
Revises: b919036372d9
Create Date: 2026-05-07

Captures all schema changes made after the initial migration:
- User: first_name, last_name, is_verified, phone_number, photo, resume,
         address, gender, education_qualification, created_at, updated_at
- Course: video, who_is_this_for, learning_outcomes, course_structure,
           instructor_name, instructor_bio, faqs
- Enrollment: city_town
- Review table (new)
"""
from alembic import op
import sqlalchemy as sa


revision = '1630febf9cc3'
down_revision = 'b919036372d9'
branch_labels = None
depends_on = None


def upgrade():
    # --- User: new columns ---
    op.add_column('user', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='0'))
    op.add_column('user', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('photo', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('resume', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('gender', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('education_qualification', sa.String(length=200), nullable=True))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # --- Course: new columns ---
    op.add_column('course', sa.Column('video', sa.String(length=255), nullable=True))
    op.add_column('course', sa.Column('who_is_this_for', sa.Text(), nullable=True))
    op.add_column('course', sa.Column('learning_outcomes', sa.Text(), nullable=True))
    op.add_column('course', sa.Column('course_structure', sa.Text(), nullable=True))
    op.add_column('course', sa.Column('instructor_name', sa.String(length=150), nullable=True))
    op.add_column('course', sa.Column('instructor_bio', sa.Text(), nullable=True))
    op.add_column('course', sa.Column('faqs', sa.Text(), nullable=True))

    # --- Enrollment: new columns ---
    op.add_column('enrollment', sa.Column('city_town', sa.String(length=100), nullable=True))

    # --- Review table (new) ---
    op.create_table(
        'review',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['course.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'course_id', name='unique_user_course_review'),
    )


def downgrade():
    op.drop_table('review')

    op.drop_column('enrollment', 'city_town')

    op.drop_column('course', 'faqs')
    op.drop_column('course', 'instructor_bio')
    op.drop_column('course', 'instructor_name')
    op.drop_column('course', 'course_structure')
    op.drop_column('course', 'learning_outcomes')
    op.drop_column('course', 'who_is_this_for')
    op.drop_column('course', 'video')

    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'education_qualification')
    op.drop_column('user', 'gender')
    op.drop_column('user', 'address')
    op.drop_column('user', 'resume')
    op.drop_column('user', 'photo')
    op.drop_column('user', 'phone_number')
    op.drop_column('user', 'is_verified')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
