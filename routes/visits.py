from flask import Blueprint, render_template
from db import get_global_visit_count

visits_bp = Blueprint('visits', __name__)


@visits_bp.route('/visits/global')
def global_visits():
    count = get_global_visit_count()
    return render_template('partials/visit_count.html', count=count)
