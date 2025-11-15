from flask import Blueprint, render_template, redirect, url_for, session
from HillSide.models import Enrollment
from flask_login import current_user



staff_bp = Blueprint('staff', __name__)


@staff_bp.route("/staff-dashboard")
def staff_dashboard():
    courses = Enrollment.query.filter_by(user_id=current_user.id).all()
    return render_template('staff_dashboard.html', courses=courses)
