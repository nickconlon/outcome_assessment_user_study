from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db
import numpy as np
import os

bp = Blueprint('gridworld_app', __name__)

MAPS_PER_LEVEL = 4
MAX_MAPS_PER_LEVEL = 5

COLORS = ['red', 'green', 'blue']
CONFIDENCES = ["Very Bad", "Bad", "Fair", "Good", "Very good"]
APP_PATH = "/var/www/html/web_gridworld/web_gridworld"

@bp.route('/')
def index():
    if g.user is not None:
        return render_template('gridworld_app/prescreen.html')
    else:
        return render_template('gridworld_app/index.html', posts={})


@bp.route('/prescreen', methods=('POST',))
def prescreen():
    english = request.form['english']
    vision = request.form['vision']
    depth = request.form['depth']
    colorblind = request.form['colorblind']

    db_entry = english + vision + depth + colorblind
    db = get_db()
    db.execute('UPDATE user SET prescreen=? WHERE id = ?', (db_entry, g.user['id'],))
    db.commit()

    total = int(english) + int(vision) + int(depth) + int(colorblind)
    if total != 4:
        return render_template('gridworld_app/end_study.html')
    return base_tutorial()


@bp.route('/playgame', methods=('GET', 'POST'))
@login_required
def playgame():
    db = get_db()
    u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
    accuracy_level = u[2]
    competency_level = u[3]
    report_level = session['level']
    confidence = ""

    if int(report_level) > -1:
        map_number = session['l' + report_level + '_order'][int(session['ctr'])]
        color = int(session['c_order'][int(report_level)])
        map_path = os.path.join(APP_PATH,"flaskr/maps/level_" + report_level + "/map" + map_number)
    else:
        map_number = '0'
        color = int(session['c_order'][0])
        map_path = os.path.join(APP_PATH,"flaskr/maps/map0")

    if int(report_level) == 1:
        if accuracy_level == 0:
            with open(map_path + "_confidence.txt") as file:
                for line in file.readlines():
                    confidence = line.strip()
                    break
        else:
            # randomize confidence statement
            rand_conf = CONFIDENCES[np.random.randint(0, len(CONFIDENCES))]
            confidence = "<b>Report:</b> The robot has <b>" + rand_conf \
                         + " confidence</b> in navigating to the green square."
    elif int(report_level) == 2:
        if accuracy_level == 0:

            with open(map_path + "_confidence.txt") as file:
                for line in file.readlines():
                    confidence = line.strip()
                    break
        else:
            # randomize confidence statement
            rand_conf1 = CONFIDENCES[np.random.randint(0, len(CONFIDENCES))]
            rand_conf2 = CONFIDENCES[np.random.randint(0, len(CONFIDENCES))]
            confidence = "<b>Report:</b> The robot has <b>" + rand_conf1 \
                         + " confidence</b> in navigating to the blue square, and <b>" + rand_conf2 \
                         + " confidence </b> in navigating from the blue square to the green square."

    confidence = confidence.replace('robot', '<u>' + COLORS[color] + ' robot</u>')
    obstacles = []
    dangers = []
    randomizers = []
    subgoal = []
    goal = []
    policy = []
    with open(map_path + "_policy.txt") as file:
        for line in file.readlines():
            line = line.strip()
            for l in line.split(','):
                policy.append(int(l))

    with open(map_path + ".txt") as file:
        for y, line in enumerate(file.readlines()):
            for x, c in enumerate(line):
                if c == 'o':
                    obstacles.append([x, y])
                if c == 'g':
                    randomizers.append([x, y])
                if c == 'd':
                    dangers.append([x, y])
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
    print(session)
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
            '(user_id, tot_mission_time_s, tot_mission_steps, path, map_number, accuracy_level, competency_level, report_level, confidence) '
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (g.user['id'],  js['t_mission_time'], js['t_mission_steps'], str(js['path']), js['map_num'], js['accuracy'],
             js['competency'], js['report'], js['conf'])
        )
        db.commit()
        score = 5.0
        if js['outcome'] == 'ABORT':
            score -= 3.0
        if int(js['human']) > 0:
            score -= int(js['human'])*0.1
        if js['outcome'] == 'DEAD':
            score = 0.0
        if score <= 0.0:
            score = 0.0

        session['score'] = str(score)
        session['ctr'] = str(int(session['ctr']) + 1)
        if int(session['ctr']) % MAPS_PER_LEVEL == 0 or session['level'] == '-1':
            session['level'] = str(int(session['level']) + 1)
            session['ctr'] = '0'
            print("changing level")

    return render_template('gridworld_app/outcome.html', post={'score': session['score']})


@bp.route('/outcome', methods=('GET', 'POST'))
@login_required
def outcome():
    if session['ctr'] == '0':
        color_idx = int(np.max(int(session['level']) - 1, 0))
        color = int(session['c_order'][color_idx])
        color = COLORS[color]
        post = {"color": color}
        return render_template('gridworld_app/trust.html', post=post)
    return playgame()


@bp.route('/trust_question', methods=('POST',))
@login_required
def trust_question():
    js = request.form['mark']
    post = {}
    if session['level'] == '0':
        return playgame()
    elif session['level'] == '1':
        db = get_db()
        db.execute('UPDATE user SET first_trust = ? WHERE id = ?', (js, g.user['id'],))
        db.commit()
        return render_template('gridworld_app/tutorial1.html', post=post)
    elif session['level'] == '2':
        db = get_db()
        db.execute('UPDATE user SET second_trust = ? WHERE id = ?', (js, g.user['id'],))
        db.commit()
        return render_template('gridworld_app/tutorial2.html', post=post)
    elif session['level'] == '3':
        db = get_db()
        db.execute('UPDATE user SET third_trust = ? WHERE id = ?', (js, g.user['id'],))
        db.commit()
        return render_template('gridworld_app/open_question.html', post=post)


@bp.route('/open_question', methods=('GET', 'POST'))
@login_required
def open_question():
    if request.method == 'POST':
        open_q = request.form['open_text']
        age = request.form['age']
        gender = request.form['gender']
        education = request.form['education']
        games = request.form['games']

        db = get_db()
        db.execute('UPDATE user SET open_question=?, age=?, gender=?, education=?, games=? WHERE id = ?',
                   (open_q, age, gender, education, games, g.user['id'],))
        db.commit()

    db = get_db()
    u = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
    completion_code = u[9]
    session.clear()
    return render_template('gridworld_app/thank_you.html', post={'code': completion_code})


@bp.route('/base_tutorial', methods=('GET', 'POST'))
@login_required
def base_tutorial():
    # choose color order from [red, green, blue]
    color_order = np.random.choice([0, 1, 2, ], 3, replace=False)
    # choose accuracy level from [accurate, random]
    accuracy_level = np.random.randint(0, 2)
    # choose competency level from [competent, random]
    competency_level = np.random.randint(0, 2)
    # choose a completion code for the user (hopefully this is random enough)
    completion_code = "NC-"+str(np.random.randint(111111111, 999999999))+"-HRT"
    # get the client IP address
    client_ip = str(request.remote_addr)

    level_0_map_order = np.random.choice(np.arange(0, MAX_MAPS_PER_LEVEL), MAPS_PER_LEVEL, replace=False)
    level_1_map_order = np.random.choice(np.arange(0, MAX_MAPS_PER_LEVEL), MAPS_PER_LEVEL, replace=False)
    level_2_map_order = np.random.choice(np.arange(0, MAX_MAPS_PER_LEVEL), MAPS_PER_LEVEL, replace=False)
    session['l0_order'] = "".join([str(x) for x in level_0_map_order])
    session['l1_order'] = "".join([str(x) for x in level_1_map_order])
    session['l2_order'] = "".join([str(x) for x in level_2_map_order])
    session['c_order'] = "".join([str(x) for x in color_order])
    session['level'] = '-1'
    session['ctr'] = '0'
    session['score'] = '0'

    db = get_db()
    db.execute(
        'UPDATE user SET accuracy=?, competency=?, code=?, client_ip=? WHERE id = ?',
        (accuracy_level, competency_level, completion_code, client_ip, g.user['id'],))
    db.commit()
    print("Setting up new participant:")
    print("  IP addr={}".format(client_ip))
    print("  color_order={}".format([COLORS[x] for x in color_order]))
    print("  accuracy_level={}".format("accurate" if accuracy_level is 0 else "random"))
    print("  competency_level={}".format("accurate" if competency_level is 0 else "random"))
    print("  completion_code={}".format(completion_code))

    post = {'title': 'tutorial'}
    return render_template('gridworld_app/base_tutorial.html', post=post)


@bp.route('/end_study', methods=('GET', 'POST'))
def end_study():
    return render_template('gridworld_app/end_study.html', post={})
