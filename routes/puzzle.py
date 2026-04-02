from flask import Blueprint, render_template, abort
from db import get_item

puzzle_bp = Blueprint('puzzle', __name__)

DIFFICULTY = {
    'easy':   {'rows': 3, 'cols': 3},
    'medium': {'rows': 4, 'cols': 4},
    'hard':   {'rows': 5, 'cols': 5},
}


@puzzle_bp.route('/puzzle/<photo_id>')
def puzzle(photo_id):
    photo = get_item('sunset_photos', photo_id)
    if not photo:
        abort(404)
    return render_template('puzzle.html',
                           photo=photo,
                           difficulties=list(DIFFICULTY.keys()))


@puzzle_bp.route('/puzzle/<photo_id>/<difficulty>')
def puzzle_play(photo_id, difficulty):
    photo = get_item('sunset_photos', photo_id)
    if not photo:
        abort(404)
    if difficulty not in DIFFICULTY:
        abort(404)
    grid = DIFFICULTY[difficulty]
    return render_template('puzzle_play.html',
                           photo=photo,
                           difficulty=difficulty,
                           rows=grid['rows'],
                           cols=grid['cols'])
