from flask import Blueprint, render_template
from db import track_visit

family_bp = Blueprint('family', __name__)


@family_bp.route('/family')
def family():
    track_visit('family')
    return render_template('family.html')
