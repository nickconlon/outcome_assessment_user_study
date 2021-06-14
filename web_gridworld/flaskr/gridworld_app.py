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
    colors = ['red', 'green', 'blue']
    map_number = 0
    db = get_db()
    u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
    if u[1] == -1:
        db = get_db()
        db.execute('UPDATE user SET run_counter = 0 WHERE id = ?', (g.user['id'],))
        db.commit()
        map_number = 0
    else:
        map_number = u[1]
    #if u is not None and len(u) >= 2:
    #    map_number = u[1] % 3
    confidence = ""

    with open("flaskr/maps/confidence"+str(map_number)+".txt") as file:
        for line in file.readlines():
            confidence = line.strip()
            break

    confidence = confidence.replace('robot', '<u>'+colors[map_number]+' robot</u>')
    obstacles = []
    dangers = []
    randomizers = []
    subgoal = []
    goal = []
    with open("flaskr/maps/map"+str(map_number)+".txt") as file:
        for y, line in enumerate(file.readlines()):
            for x, c in enumerate(line):
                if c == 'o':
                    obstacles.append([x,y])
                if c == 'r':
                    randomizers.append([x,y])
                if c == 'd':
                    dangers.append([x,y])
                if c == 'G':
                    goal = [x, y]
                if c == 'g':
                    subgoal = [x, y]
                if c == 'a':
                    agent = [x, y]
    data = {
        'conf': confidence,
        'goal': goal,
        'subgoal': subgoal,
        'agent': agent,
        'obstacles': obstacles,
        'dangers': dangers,
        'randomizers': randomizers,
        'robot_color': colors[map_number]
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
        run_number = 55
        run_level = 876
        db.execute(
            'INSERT INTO results '
            '(user_id, h_score, a_score,  outcome, tot_mission_time_s, tot_mission_steps, num_interventions, num_steps_interventions, intervention_locations, run_number, level_number) '
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)',
            (g.user['id'], js['human'], js['agent'], js['outcome'], js['t_mission_time'],
             js['t_mission_steps'], js['n_interventions'], js['n_steps_interventions'], str(js['intervention_loc']),
             run_number, run_level)
        )
        db.commit()

        db = get_db()
        db.execute('UPDATE user SET run_counter = run_counter+1 WHERE id = ?', (g.user['id'],))
        db.commit()

    db = get_db()
    u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
    print("U " + str(u[1]))
    if u[1] == 1:
        post = {}
        return render_template('gridworld_app/tutorial1.html', post=post)
    elif u[1] == 2:
        post = {}
        return render_template('gridworld_app/tutorial2.html', post=post)
    if u[1] > 2 or u[1] == -1:
        # TODO delete me
        db = get_db()
        db.execute('UPDATE user SET run_counter = -1 WHERE id = ?', (g.user['id'],))
        db.commit()
        post = {}
        return render_template('gridworld_app/thank_you.html', post=post)

    else:
        return playgame()


@bp.route('/base_tutorial', methods=('GET', 'POST'))
@login_required
def base_tutorial():
    post = {'title': 'tutorial'}
    return render_template('gridworld_app/base_tutorial.html', post=post)

