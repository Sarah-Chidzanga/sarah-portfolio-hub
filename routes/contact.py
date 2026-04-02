from flask import Blueprint, render_template
from db import track_visit

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact')
def contact():
    track_visit('contact')
    return render_template('contact.html')
