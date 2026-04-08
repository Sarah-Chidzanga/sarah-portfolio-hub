from flask import Blueprint, render_template
from db import track_visit

skills_bp = Blueprint('skills', __name__)


@skills_bp.route('/skills')
def skills():
    track_visit('skills')
    return render_template('skills.html')
