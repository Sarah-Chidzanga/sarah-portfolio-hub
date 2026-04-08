from flask import Blueprint, render_template
from db import track_visit

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/resume')
def resume():
    track_visit('resume')
    return render_template('resume.html')
