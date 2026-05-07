from flask import Blueprint, render_template
from flask_login import login_required
from HillSide.models import Course
from HillSide.utils import staff_required


staff_bp = Blueprint('staff', __name__)


@staff_bp.route("/staff-dashboard")
@login_required
@staff_required
def staff_dashboard():
    courses = Course.query.order_by(Course.id.desc()).all()
    return render_template('staff_dashboard.html', courses=courses)
