from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import numpy as np

bp = Blueprint('gridworld_app', __name__)

FIRST = 2
SECOND = 4
THIRD = 6

COLORS = ['red', 'green', 'blue']
CONFIDENCES = ["Very Bad", "Bad", "Fair", "Good", "Very good"]

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
    db = get_db()
    u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
    accuracy_level = u[5]
    competency_level = u[6]

    if u[1] == -1:
        db = get_db()
        db.execute('UPDATE user SET run_counter = 0 WHERE id = ?', (g.user['id'],))
        db.commit()
        map_number = 0
    else:
        map_number = u[1]
    confidence = ""

    print(accuracy_level)
    if map_number < FIRST:
        report_level = 0
        color = int(u[2])
    elif map_number < SECOND:
        report_level = 1
        color = int(u[3])
    else:
        report_level = 2
        color = int(u[4])

    if FIRST <= map_number < SECOND:
        if accuracy_level == 0:
            with open("flaskr/maps/map"+str(map_number)+"_confidence.txt") as file:
                for line in file.readlines():
                    confidence = line.strip()
                    break
        else:
            # randomize confidence statement
            rand_conf = CONFIDENCES[np.random.randint(0, len(CONFIDENCES))]
            confidence = "<b>Report:</b> The robot has <b>"+rand_conf\
                         +" confidence</b> in navigating to the green square."
    elif map_number >= SECOND:
        map_number = 21 - map_number
        if accuracy_level == 0:

            with open("flaskr/maps/map"+str(map_number)+"_confidence.txt") as file:
                for line in file.readlines():
                    confidence = line.strip()
                    break
        else:
            # randomize confidence statement
            rand_conf1 = CONFIDENCES[np.random.randint(0, len(CONFIDENCES))]
            rand_conf2 = CONFIDENCES[np.random.randint(0, len(CONFIDENCES))]
            confidence = "<b>Report:</b> The robot has <b>"+rand_conf1\
                         +" confidence</b> in navigating to the blue square, and <b>"+ rand_conf2 \
                         + " confidence </b> in navigating to the green square."

        confidence = confidence.replace('robot', '<u>' + COLORS[color] + ' robot</u>')
    obstacles = []
    dangers = []
    randomizers = []
    subgoal = []
    goal = []
    policy = []
    with open("flaskr/maps/map"+str(map_number)+"_policy.txt") as file:
        for line in file.readlines():
            line = line.strip()
            for l in line.split(','):
                policy.append(int(l))

    with open("flaskr/maps/map"+str(map_number)+".txt") as file:
        for y, line in enumerate(file.readlines()):
            for x, c in enumerate(line):
                if c == 'o':
                    obstacles.append([x,y])
                if c == 'g':
                    randomizers.append([x,y])
                if c == 'd':
                    dangers.append([x,y])
                if c == 'G':
                    goal = [x, y]
                if c == 'r':
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
        'robot_color': COLORS[color],  # just color
        'report': report_level,  # level: no report, report, segmented report
        'competency': competency_level,  # level: competent (good), incompetent (random)
        'accuracy': accuracy_level,  # level: accurate, random
        'map_number': map_number,  # The reference number for this map
        'policy': policy  # The policy to execute
    }
    print("Rendering new map:")
    print("  map_number={}".format(map_number))
    print("  color={}".format(COLORS[color]))
    print("  report={}".format(report_level))
    print("  competency={}".format(competency_level))
    print("  accuracy={}".format(accuracy_level))
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
            '(user_id, h_score, a_score,  outcome, tot_mission_time_s, tot_mission_steps, num_interventions, num_steps_interventions, intervention_locations, map_number, accuracy_level, competency_level, report_level, confidence) '
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (g.user['id'], js['human'], js['agent'], js['outcome'], js['t_mission_time'],
             js['t_mission_steps'], js['n_interventions'], js['n_steps_interventions'], str(js['intervention_loc']),
             js['map_num'], js['accuracy'], js['competency'], js['report'], js['conf'])
        )
        db.commit()

        db = get_db()
        db.execute('UPDATE user SET run_counter = run_counter+1 WHERE id = ?', (g.user['id'],))
        db.commit()

    db = get_db()
    u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
    print("U " + str(u[1]))
    if u[1] == FIRST:
        return trust()
    elif u[1] == SECOND:
        return trust()
    if u[1] >= THIRD or u[1] == -1:
        db = get_db()
        db.execute('UPDATE user SET run_counter = -1 WHERE id = ?', (g.user['id'],))
        db.commit()
        return trust()

    else:
        return playgame()


@bp.route('/trust', methods=('GET', 'POST'))
@login_required
def trust():
    post = {}
    if request.method == 'POST':
        color = ""
        db = get_db()
        u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
        if u[1] == FIRST:
            color = COLORS[int(u[2])]
        elif u[1] == SECOND:
            color = COLORS[int(u[3])]
        else:
            color = COLORS[int(u[4])]
        post = {"color": color}
    return render_template('gridworld_app/trust.html', post=post)


@bp.route('/trust_question', methods=('GET', 'POST'))
@login_required
def trust_question():
    if request.method == 'POST':
        js = request.form['mark']
        print(js)
        post = {}
        db = get_db()
        u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
        print("U " + str(u[1]))
        if u[1] == FIRST:
            db = get_db()
            db.execute('UPDATE user SET first_trust = ? WHERE id = ?', (js, g.user['id'],))
            db.commit()
            return render_template('gridworld_app/tutorial1.html', post=post)
        elif u[1] == SECOND:
            db = get_db()
            db.execute('UPDATE user SET second_trust = ? WHERE id = ?', (js, g.user['id'],))
            db.commit()
            return render_template('gridworld_app/tutorial2.html', post=post)
        else:
            db = get_db()
            db.execute('UPDATE user SET third_trust = ? WHERE id = ?', (js, g.user['id'],))
            db.commit()
            return render_template('gridworld_app/open_question.html', post=post)
    return trust()


@bp.route('/open_question', methods=('GET', 'POST'))
@login_required
def open_question():
    if request.method == 'POST':
        js = request.form['open_text']
        db = get_db()
        db.execute('UPDATE user SET open_question = ? WHERE id = ?', (js, g.user['id'],))
        db.commit()
    return render_template('gridworld_app/thank_you.html', post={})


@bp.route('/base_tutorial', methods=('GET', 'POST'))
@login_required
def base_tutorial():
    # choose color order from [red, green, blue]
    color_order = np.random.choice([0, 1, 2], 3, replace=False)
    # choose accuracy level from [accurate, random]
    accuracy_level = np.random.randint(0, 2)
    # choose competency level from [competent, random]
    competency_level = np.random.randint(0, 2)
    db = get_db()
    db.execute('UPDATE user SET run_counter=?, first_color=?, second_color=?, third_color=?, accuracy=?, competency=? WHERE id = ?', (0, int(color_order[0]), int(color_order[1]), int(color_order[2]), accuracy_level, competency_level, g.user['id'],))
    db.commit()
    print("Starting new round:")
    print("  color_order={}".format([set_color(x) for x in color_order]))
    print("  accuracy_level={}".format("accurate" if accuracy_level is 0 else "random"))
    print("  competency_level={}".format("accurate" if competency_level is 0 else "random"))

    post = {'title': 'tutorial'}
    return render_template('gridworld_app/base_tutorial.html', post=post)


def set_color(x):
    if x == 0:
        return "red"
    elif x == 1:
        return "green"
    else:
        return "blue"