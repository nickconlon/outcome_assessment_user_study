from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import numpy as np

bp = Blueprint('gridworld_app', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('gridworld_app/index.html', posts=posts)


@bp.route('/practicegame', methods=('GET', 'POST'))
@login_required
def practicegame():
    # load practice map
    # load practice confidence
    # load practice policy

    data = {}
    return render_template('gridworld_app/index.html', start_data=data)

@bp.route('/playgame', methods=('GET', 'POST'))
@login_required
def playgame():
    print("Hello world")
    confidence = ["N/A",
                  "The agent has low confidence in driving from the current position to the green square",
                  "The agent has high confidence in driving from the current position to the green square"]
    obstacles = []
    dangers = []
    randomizers = []
    with open("flaskr/maps/map.txt") as file:
        for y, line in enumerate(file.readlines()):
            for x, c in enumerate(line):
                if c == 'o':
                    obstacles.append([x,y])
                if c == 'r':
                    randomizers.append([x,y])
                if c == 'd':
                    dangers.append([x,y])
                if c == 'g':
                    goal = [x, y]
                if c == 'a':
                    agent = [x, y]

    data = {
        'conf': confidence[np.random.randint(0,2)],
        'goal': goal,
        'agent': agent,
        'obstacles': obstacles,
        'dangers': dangers,
        'randomizers': randomizers
    }
    return render_template('gridworld_app/gridworld_game.html', start_data=data)


@bp.route('/endgame', methods=('GET', 'POST'))
@login_required
def endgame():
    if request.method == 'POST':
        js = request.get_json()
        js = js['postData']
        print("RECEIVED :" + str(js))
        db = get_db()
        db.execute(
            'INSERT INTO results '
            '(user_id, h_score, a_score,  outcome, tot_mission_time_s, tot_mission_steps, num_interventions, num_steps_interventions, intervention_locations) '
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (g.user['id'], js['human'], js['agent'], js['outcome'], js['t_mission_time'], js['t_mission_steps'], js['n_interventions'], js['n_steps_interventions'], str(js['intervention_loc']))
        )
        db.commit()
    return redirect(url_for('gridworld_app.index'))


@bp.route('/tutorial', methods=('GET', 'POST'))
@login_required
def tutorial():
    post = {'title': 'tutorial'}
    return render_template('gridworld_app/tutorial.html', post=post)

