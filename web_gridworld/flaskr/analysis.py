import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import re

CSV_PATHS = "C:/Users/nick/Documents/1_CU/1_CU_Boulder/3_Research/Mturk_proficency_self_assessment/AWS_Data"

# DB_FILE = CSV_PATHS+"/flaskr_29_13SEP2021.sqlite"
DB_FILE = CSV_PATHS + "/flaskr_19sbj_22SEP2021.sqlite"


def connect():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    return cur, con


def get_data():
    cur, con = connect()
    total = 0
    data = {}
    user_data = cur.execute('SELECT * FROM user;').fetchall()
    for user in user_data:
        if None in user:
            print("dropping user: {}".format(user[0]))
            continue
        print(user)
        total += 1
        user_id = user[0]

        run_data = []
        for run in cur.execute('SELECT * FROM results WHERE user_id=?', (user_id,)):
            run_data.append(run)

        data[user_id] = (user, run_data)
    print("Total " + str(total))
    con.close()

    return data


def dump():
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(DB_FILE)

    cur = con.cursor()

    # The result of a "cursor.execute" can be iterated over by row
    for row in cur.execute('SELECT * FROM user;'):
        print(row)
    # for row in cur.execute('SELECT * FROM results;'):
    #    print(row)

    # Be sure to close the connection
    con.close()


def compute_bonus_score(run_data, user_data):
    """
    for each user, get user code
        scroll through runs, pick out the ones with that code, accumulate score
    print score rounded
    """
    filename = CSV_PATHS+'/bonus_tmp.csv'
    scores = []
    test = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split(',')
            turk_id = line[0]
            hit_code = line[1]
            test.append(line)
            for user in user_data:
                user_code = user[12]
                user_name = user[3]
                if user_name.lower() == turk_id.lower():
                    score = 0
                    for run in run_data:
                        if run[12].strip() == hit_code.strip():
                            score = score + float(run[10])

                    scores.append({user_name: score})
                    break

    with open(filename.replace('.csv', '_out.csv'), 'w') as f:
        for score in scores:
            for k, v in score.items():
                f.write(k + ", " + str(np.round(v) / 100)+'\n')


def control_proportion(h_steps, a_steps):
    diff_sum = (a_steps - h_steps) / (a_steps + h_steps)
    return diff_sum


def control_test(path, map_number):
    maps = {0: [14, 1], 1: [10, 4], 2: [13, 2], 3: [15, 1], 4: [14, 1]} #[x,y]
    h_steps_s1 = 0
    a_steps_s1 = 0
    h_steps_s2 = 0
    a_steps_s2 = 0
    segment = 1
    import json
    path = path.replace(' ',',')
    path = path.replace('[A,','[\"A\",')
    path = path.replace('[H,','[\"H\",')

    path = path.replace('ABORT', '\"ABORT\"')
    path = path.replace('DEAD', '\"DEAD\"')
    path = path.replace('GOAL', '\"GOAL\"')

    path = json.loads(path)
    prev_mover = ''
    for p in path:
        i = p
        if segment == 1:
            if i[0] == 'H' or (i[0] == 'GOAL' and prev_mover == 'H') or (i[0] == 'DEAD' and prev_mover == 'H'):
                h_steps_s1 += 1
                prev_mover = 'H'
            elif i[0] == 'A' or (i[0] == 'GOAL' and prev_mover == 'A') or (i[0] == 'DEAD' and prev_mover == 'A'):
                a_steps_s1 += 1
                prev_mover = 'A'
        else:
            if i[0] == 'H' or (i[0] == 'GOAL' and prev_mover == 'H') or (i[0] == 'DEAD' and prev_mover == 'H'):
                h_steps_s2 += 1
                prev_mover = 'H'
            elif i[0] == 'A' or (i[0] == 'GOAL' and prev_mover == 'A') or (i[0] == 'DEAD' and prev_mover == 'A'):
                a_steps_s2 += 1
                prev_mover = 'H'
        if segment != 2:
            if i[1] >= maps[map_number][0] and i[2] == maps[map_number][1]:
                segment = 2
                print("new segment")

    if h_steps_s1 > 0 or a_steps_s1 > 0:
        p1 = control_proportion(h_steps_s1, a_steps_s1)
    else:
        p1 = ' '
    print("seg1: ", p1)
    if h_steps_s2 > 0 or a_steps_s2 > 0:
        p2 = control_proportion(h_steps_s2, a_steps_s2)
    else:
        p2 = ' '
    print("seg2: ", p2)
    return p1, p2


def optimal_steps(map_level, map_number):
    actions = {0: [-1,0],1: [+1,0],2: [0, -1], 3:[0, +1]}
    if map_level == '0' and map_number == '0':
        filename = 'maps/map'+str(map_number)+'_policy.txt'
    else:
        filename = 'maps/level_'+str(map_level)+'/map'+str(map_number)+'_policy.txt'
    with open(filename, 'r') as f:
        policy = f.readline()
        policy = policy.strip()
        policy = policy.split(',')
        policy = [int(x) for x in policy]

    im = np.zeros([7, 30])
    pos = np.array([1,1])
    counter = 0
    im[pos[1], pos[0]] = 1
    while True:
        if pos[0] >= 28 and pos[1] >= 5:
            break

        i = pos[0] + 30 * pos[1]
        pos = pos+actions[policy[i]]
        im[pos[1], pos[0]] = 1
        counter += 1
        #plt.imshow(im)
    #plt.title(counter)
    #plt.xticks(np.arange(0, 30))
    #plt.xlim([0,30])
    #plt.ylim([7,0])
    #plt.yticks(np.arange(0, 7))
    #plt.grid(True, linewidth=1)
    #plt.show()
    return counter


def read_map(path):
    obstacles = []
    craters = []
    debris = []
    goal = []
    with open(path, 'r') as f:
        for yy, line in enumerate(f.readlines()):
            for xx, c in enumerate(line):
                if c == 'o':
                    obstacles.append([xx+1, 7-yy])
                if c == 'g':
                    debris.append([xx+1,7-yy])
                if c == 'd':
                    craters.append([xx+1,7-yy])
                if c == 'G':
                    goal.append([xx+1,7-yy])

    return obstacles, craters, debris, goal


def plot_path_heatmap(run_data):
    """
    TODO Heatmap of:
        routes per map
        takeovers per map
    """
    #for ctr, d in enumerate(run_data):
    for ctr in range(1998, len(run_data)):
        print(ctr)
        d = run_data[ctr]
        im = np.zeros([8, 31, 3], dtype=int)
        if d[6] == '0':
            continue
        map_path = 'C:/Users/nick/Documents/CODE/git/web_gridworld/web_gridworld/flaskr/maps/level_{}/map{}.txt'.format(d[6], d[2])
        obstacles, craters, debris, goal = read_map(map_path)

        for o in obstacles:
            im[o[1], o[0]] = [220, 220, 220]

        path = d[11]
        path = path[1:]
        path = path[:len(path) - 1]
        # path = path.strip('[')
        # path = path.strip(']')
        # path = path.replace('[', '')
        # path = path.replace(']', '')
        # path = path.replace(' ', '')
        path = path.replace('] [', '|')
        path = path.replace(' ', ',')
        path = path.replace('[', '')
        path = path.replace(']', '')
        path = path.split('|')

        hh = []
        aa = []
        xy_path = []
        xy_abort = []
        xy_dead = []
        xy_goal = [goal[0]]
        for p in path:
            p = p.split(',')
            driver = p[0]
            x = int(p[1])+1
            y = 7-int(p[2])
            xy_path.append([x, y])
            # [R, G, B]
            if driver == 'DEAD': # red
                #im[y, x] = [1, 0, 0]
                xy_dead.append([x,y])
            elif driver == 'GOAL': # green
                #im[y, x] = [0, 1, 0]
                xy_goal.append([x, y])
            elif driver == 'ABORT': # yellow
                #im[y, x] = [1, 1, 0]
                xy_abort.append([x, y])
            elif driver == 'A': # agent = white
                #im[y,x] = [1,1,1]
                aa.append([x,y])
            else: # human = blue
                #im[y, x] = [0, 0, 1]
                hh.append([x,y])
        #print(path)
        report = d[5]
        report = report.replace('<b>Report:</b>','')
        substr = re.findall("<b>(.*?)</b>", report)

        reporting = 'informed' if d[3] == '0' else 'uninformed'
        performance = 'high' if d[4] == '0' else 'low'
        s = "map# {}\nReporting: {}\nPerformance: {}\n{}".format(
            d[2],
            reporting,
            performance,
            substr)
        #s = "map# {}\n{}".format(d[2], substr)
        hh = np.array(hh)
        aa = np.array(aa)
        xy_path = np.array(xy_path)
        xy_dead = np.array(xy_dead)
        xy_goal = np.array(xy_goal)
        xy_abort = np.array(xy_abort)
        craters = np.array(craters)
        debris = np.array(debris)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(xy_path[:,0],xy_path[:,1])

        ax.scatter(craters[:,0], craters[:,1], c='crimson', marker='X', label='craters')
        ax.scatter(debris[:,0], debris[:,1], c='darkorange', marker='s', label='debris')

        if len(hh) > 0:
            ax.scatter(hh[:,0],hh[:,1], c='lavender', label='human control')
        if len(aa) > 0:
            ax.scatter(aa[:,0],aa[:,1], c='slateblue', label='robot control')
        if len(xy_dead) > 0:
            ax.scatter(xy_dead[:,0], xy_dead[:,1], c='crimson', label='failure location')
        if len(xy_goal) > 0:
            ax.scatter(xy_goal[:,0], xy_goal[:,1], c='green', label='goal location')
        if len(xy_abort) > 0:
            ax.scatter(xy_abort[:,0], xy_abort[:,1], c='orange', label='abort location')

        ax.set_aspect('equal')
        ax.set_ylim([0.5,7.5])
        ax.set_xlim([0.5,30.5])
        ax.set_xticks([1,30])
        ax.set_yticks([1,7])
        plt.tight_layout()
        #plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
        plt.title(s)
        plt.imshow(im)
        #plt.show()

        # img_[accuracy][competency][level]_[subject]_[counter].png
        path = 'C:/Users/nick/Documents/1_CU/1_CU_Boulder/3_Research/Mturk_proficency_self_assessment/AWS_Data/run_plots/'
        fname = "img_"+d[3]+d[4]+d[6]+"_"+d[12]+'_'+str(ctr)+".png"
        plt.savefig(path+fname,dpi=300)
        plt.close('all')
        #plt.show()


def plot_driving_proportion(run_data):
    """
    TODO plots for performance vs. map difficulty
    proportion of H/A driving vs. confidence for GOALs

    """
    map_type_description = ['No\nCompetencyReport', 'Single\nCompetency Report', 'Segmented\nCompetency Report']
    fig, axs = plt.subplots(5, 1, sharex=True, sharey=False)  # (y,x)
    fig.suptitle('Performance')

    prop_no_sc_vbad = []
    prop_sc_vbad = []
    prop_ssc_vbad = []

    prop_no_sc_bad = []
    prop_sc_bad = []
    prop_ssc_bad = []

    prop_no_sc_fair = []
    prop_sc_fair = []
    prop_ssc_fair = []

    prop_no_sc_good = []
    prop_sc_good = []
    prop_ssc_good = []

    prop_no_sc_vgood = []
    prop_sc_vgood = []
    prop_ssc_vgood = []

    for r in run_data:
        if int(r[3]) != 0 or int(r[4]) != 0:
            continue
        if int(r[2]) == 0:  # ignore the training run
            continue
        if 'GOAL' in r[11]:
            if int(r[6]) == 1:  # no SC
                r[11] = r[11].replace('GOAL', '')
                r[11] = r[11].replace('ABORT', '')
                r[11] = r[11].replace('DEAD', '')
                p = r[11].count('H')  # r[11].count('A')/r[11].count('H') if r[11].count('H') > 0 else 1.0
                prop_no_sc_bad.append(p)
            if int(r[6]) == 2:  # SC
                r[11] = r[11].replace('GOAL', '')
                r[11] = r[11].replace('ABORT', '')
                r[11] = r[11].replace('DEAD', '')
                p = r[11].count('H')  # r[11].count('A') / r[11].count('H') if r[11].count('H') > 0 else 1.0
                if 'very bad' in r[5]:
                    prop_sc_vbad.append(p)
                elif 'bad' in r[5]:
                    prop_sc_bad.append(p)
                elif 'fair' in r[5]:
                    prop_sc_fair.append(p)
                elif 'good' in r[5]:
                    prop_sc_good.append(p)
                elif 'very good' in r[5]:
                    prop_sc_vgood.append(p)
            if int(r[6]) == 3:  # SegC
                r[11] = r[11].replace('GOAL', '')
                r[11] = r[11].replace('ABORT', '')
                r[11] = r[11].replace('DEAD', '')
                p = r[11].count('H')  # r[11].count('A')/r[11].count('H') if r[11].count('H') > 0 else 1.0
                prop_ssc_bad.append(p)

    prop_no_sc_bad = np.average(prop_no_sc_bad)
    prop_sc_vbad = np.average(prop_sc_vbad)
    prop_sc_bad = np.average(prop_sc_bad)
    prop_sc_fair = np.average(prop_sc_fair)
    prop_sc_good = np.average(prop_sc_good)
    prop_sc_vgood = np.average(prop_sc_vgood)
    prop_ssc_bad = np.average(prop_ssc_bad)

    s = "comp={}, acc={}".format(0, 0)
    axs[0].set_ylabel('vbad')
    axs[0].errorbar(np.arange(3), [prop_no_sc_bad, prop_sc_vbad, prop_ssc_bad], yerr=[15, 15, 15], fmt='o-', label=s)
    axs[0].set_ylim([0, 60])
    axs[0].set_xticks([0, 1, 2])
    axs[0].set_xticklabels(map_type_description)
    axs[0].legend()

    axs[1].set_ylabel('bad')
    axs[1].plot(np.arange(3), [prop_no_sc_bad, prop_sc_bad, prop_ssc_bad], 'o-', label=s)
    axs[1].set_ylim([0, 50])
    axs[1].set_xticks([0, 1, 2])
    axs[1].set_xticklabels(map_type_description)

    axs[2].set_ylabel('fair')
    axs[2].plot(np.arange(3), [prop_no_sc_bad, prop_sc_fair, prop_ssc_bad], 'o-', label=s)
    axs[2].set_ylim([0, 50])
    axs[2].set_xticks([0, 1, 2])
    axs[2].set_xticklabels(map_type_description)

    axs[3].set_ylabel('good')
    axs[3].plot(np.arange(3), [prop_no_sc_bad, prop_sc_good, prop_ssc_bad], 'o-', label=s)
    axs[3].set_ylim([0, 50])
    axs[3].set_xticks([0, 1, 2])
    axs[3].set_xticklabels(map_type_description)

    axs[4].set_ylabel('vgood')
    axs[4].plot(np.arange(3), [prop_no_sc_bad, prop_sc_vgood, prop_ssc_bad], 'o-', label=s)
    axs[4].set_ylim([0, 50])
    axs[4].set_xticks([0, 1, 2])
    axs[4].set_xticklabels(map_type_description)

    plt.show()


def plot_performance_with_difficulty(run_data):
    """
     2 plots: report type vs. average time, steps, score, outcome? for rr, ra, ar, aa
    """
    map_type_description = ['No\nCompetency\nReport', 'Single\nCompetency\nReport', 'Segmented\nCompetency\nReport']
    fig, axs = plt.subplots(4, 2, sharex=False, sharey=False)  # (y,x)
    fig.suptitle('Performance')

    for c in [0, 1]:
        for a in [0, 1]:
            competency_type = c
            accuracy_type = a

            steps_l1 = []
            secs_l1 = []
            score_l1 = []
            outcome_l1 = []

            steps_l2 = []
            secs_l2 = []
            score_l2 = []
            outcome_l2 = []

            steps_l3 = []
            secs_l3 = []
            score_l3 = []
            outcome_l3 = []

            for r in run_data:
                if int(r[3]) != accuracy_type or int(r[4]) != competency_type:
                    continue
                if int(r[2]) == 0:  # ignore the training run
                    continue
                if int(r[6]) == 1:  # no SC
                    if 'GOAL' in r[11]:
                        steps_l1.append(int(r[9]))
                        secs_l1.append(int(r[8]))
                    score_l1.append(float(r[10]))
                    outcome_l1.append(int(float(r[10]) > 0))
                if int(r[6]) == 2:  # SC
                    if 'GOAL' in r[11]:
                        steps_l2.append(int(r[9]))
                        secs_l2.append(int(r[8]))
                    score_l2.append(float(r[10]))
                    outcome_l2.append(int(float(r[10]) > 0))
                if int(r[6]) == 3:  # SegC
                    if 'GOAL' in r[11]:
                        steps_l3.append(int(r[9]))
                        secs_l3.append(int(r[8]))
                    score_l3.append(float(r[10]))
                    outcome_l3.append(int(float(r[10]) > 0))

            steps_l1_stddev = np.std(steps_l1)
            secs_l1_stddev = np.std(secs_l1)
            score_l1_stddev = np.std(score_l1)
            outcome_l1_stddev = np.std(outcome_l1)

            steps_l1 = np.average(steps_l1)
            secs_l1 = np.average(secs_l1)
            score_l1 = np.average(score_l1)
            outcome_l1 = np.average(outcome_l1)

            steps_l2_stddev = np.std(steps_l2)
            secs_l2_stddev = np.std(secs_l2)
            score_l2_stddev = np.std(score_l2)
            outcome_l2_stddev = np.std(outcome_l2)

            steps_l2 = np.average(steps_l2)
            secs_l2 = np.average(secs_l2)
            score_l2 = np.average(score_l2)
            outcome_l2 = np.average(outcome_l2)

            steps_l3_stddev = np.std(steps_l3)
            secs_l3_stddev = np.std(secs_l3)
            score_l3_stddev = np.std(score_l3)
            outcome_l3_stddev = np.std(outcome_l3)

            steps_l3 = np.average(steps_l3)
            secs_l3 = np.average(secs_l3)
            score_l3 = np.average(score_l3)
            outcome_l3 = np.average(outcome_l3)

            s = "comp={}, acc={}".format(c, a)
            axs[0, 0].set_ylabel('Average\nTime to Goal\nSeconds')
            axs[0, 0].errorbar(np.arange(2), [secs_l1, secs_l2], yerr=[secs_l1_stddev, secs_l2_stddev], fmt='o-',
                               label=s)
            axs[0, 0].set_ylim([0, 100])
            axs[0, 0].set_xticks([0, 1])
            axs[0, 0].get_xaxis().set_visible(False)
            axs[0, 0].annotate("{:+.1f}".format(secs_l2 - secs_l1), (1, secs_l2))
            axs[0, 0].legend()

            axs[1, 0].set_ylabel('Average\nTime to Goal\nSteps')
            axs[1, 0].errorbar(np.arange(2), [steps_l1, steps_l2], yerr=[steps_l1_stddev, steps_l2_stddev], fmt='o-',
                               label=s)
            axs[1, 0].set_ylim([0, 100])
            axs[1, 0].set_xticks([0, 1])
            axs[1, 0].annotate("{:+.1f}".format(steps_l2 - steps_l1), (1, steps_l2))
            axs[1, 0].get_xaxis().set_visible(False)

            axs[2, 0].set_ylabel('Average\nScore')
            axs[2, 0].errorbar(np.arange(2), [score_l1, score_l2], yerr=[score_l1_stddev, score_l2_stddev], fmt='o-',
                               label=s)
            axs[2, 0].set_ylim([0, 8])
            axs[2, 0].set_xticks([0, 1])
            axs[2, 0].annotate("{:+.1f}".format(score_l2 - score_l1), (1, score_l2))
            axs[2, 0].get_xaxis().set_visible(False)

            axs[3, 0].set_ylabel('Average\nOutcome')
            axs[3, 0].errorbar(np.arange(2), [outcome_l1, outcome_l2], yerr=[outcome_l1_stddev, outcome_l2_stddev],
                               fmt='o-', label=s)
            axs[3, 0].set_ylim([0, 1.5])
            axs[3, 0].set_xticks([0, 1])
            axs[3, 0].annotate("{:+.1f}".format(outcome_l2 - outcome_l1), (1, outcome_l2))
            axs[3, 0].set_xticklabels([map_type_description[0], map_type_description[1]])

            axs[0, 1].set_ylabel('Average\nTime to Goal\nSeconds')
            axs[0, 1].errorbar(np.arange(2), [secs_l1, secs_l3], yerr=[secs_l1_stddev, secs_l3_stddev], fmt='o-',
                               label=s)
            axs[0, 1].set_ylim([0, 100])
            axs[0, 1].set_xticks([0, 1])
            axs[0, 1].annotate("{:+.1f}".format(secs_l3 - secs_l1), (1, secs_l3))
            axs[0, 1].get_xaxis().set_visible(False)

            # axs[1, 1].set_ylabel('Average\nTime to Goal\nSteps')
            axs[1, 1].errorbar(np.arange(2), [steps_l1, steps_l3], yerr=[steps_l1_stddev, steps_l3_stddev], fmt='o-',
                               label=s)
            axs[1, 1].set_ylim([0, 100])
            axs[1, 1].set_xticks([0, 1])
            axs[1, 1].annotate("{:+.1f}".format(steps_l3 - steps_l1), (1, steps_l3))
            axs[1, 1].get_xaxis().set_visible(False)

            # axs[2, 1].set_ylabel('Average\nScore')
            axs[2, 1].errorbar(np.arange(2), [score_l1, score_l3], yerr=[score_l1_stddev, score_l3_stddev], fmt='o-',
                               label=s)
            axs[2, 1].set_ylim([0, 8])
            axs[2, 1].set_xticks([0, 1])
            axs[2, 1].annotate("{:+.1f}".format(score_l3 - score_l1), (1, score_l3))
            axs[2, 1].get_xaxis().set_visible(False)

            # axs[3, 1].set_ylabel('Average\nOutcome')
            axs[3, 1].errorbar(np.arange(2), [outcome_l1, outcome_l3], yerr=[outcome_l1_stddev, outcome_l3_stddev],
                               fmt='o-', label=s)
            axs[3, 1].set_ylim([0, 1.5])
            axs[3, 1].set_xticks([0, 1])
            axs[3, 1].annotate("{:+.1f}".format(outcome_l3 - outcome_l1), (1, outcome_l3))
            axs[3, 1].set_xticklabels([map_type_description[0], map_type_description[2]])

    plt.show()


def plot_performance(run_data):
    """
    2 plots: report type vs. average time, steps, score, outcome? for rr, ra, ar, aa
    """
    map_type_description = ['Training\n(with well performing robot)', 'No\nCompetency\nReport',
                            'Single\nCompetency\nReport', 'Segmented\nCompetency\nReport']
    fig, axs = plt.subplots(4, 1, sharex=False, sharey=False)  # (y,x)
    fig.suptitle('Performance')

    for c in [0, 1]:
        for a in [0, 1]:
            competency_type = c
            accuracy_type = a

            steps_l0 = []
            secs_l0 = []
            score_l0 = []
            outcome_l0 = []

            steps_l1 = []
            secs_l1 = []
            score_l1 = []
            outcome_l1 = []

            steps_l2 = []
            secs_l2 = []
            score_l2 = []
            outcome_l2 = []

            steps_l3 = []
            secs_l3 = []
            score_l3 = []
            outcome_l3 = []

            for r in run_data:
                if int(r[3]) != accuracy_type or int(r[4]) != competency_type:
                    continue
                if int(r[6]) == 0:
                    if 'GOAL' in r[11]:
                        steps_l0.append(int(r[9]))
                        secs_l0.append(int(r[8]))
                    score_l0.append(float(r[10]))
                    outcome_l0.append(int(float(r[10]) > 0))
                elif int(r[6]) == 1:  # no SC
                    if 'GOAL' in r[11]:
                        steps_l1.append(int(r[9]))
                        secs_l1.append(int(r[8]))
                    score_l1.append(float(r[10]))
                    outcome_l1.append(int(float(r[10]) > 0))
                elif int(r[6]) == 2:  # SC
                    if 'GOAL' in r[11]:
                        steps_l2.append(int(r[9]))
                        secs_l2.append(int(r[8]))
                    score_l2.append(float(r[10]))
                    outcome_l2.append(int(float(r[10]) > 0))
                elif int(r[6]) == 3:  # SegC
                    if 'GOAL' in r[11]:
                        steps_l3.append(int(r[9]))
                        secs_l3.append(int(r[8]))
                    score_l3.append(float(r[10]))
                    outcome_l3.append(int(float(r[10]) > 0))

            steps_l0_stddev = np.std(steps_l0)
            secs_l0_stddev = np.std(secs_l0)
            score_l0_stddev = np.std(score_l0)
            outcome_l0_stddev = np.std(outcome_l0)

            steps_l0 = np.average(steps_l0)
            secs_l0 = np.average(secs_l0)
            score_l0 = np.average(score_l0)
            outcome_l0 = np.average(outcome_l0)

            steps_l1_stddev = np.std(steps_l1)
            secs_l1_stddev = np.std(secs_l1)
            score_l1_stddev = np.std(score_l1)
            outcome_l1_stddev = np.std(outcome_l1)

            steps_l1 = np.average(steps_l1)
            secs_l1 = np.average(secs_l1)
            score_l1 = np.average(score_l1)
            outcome_l1 = np.average(outcome_l1)

            steps_l2_stddev = np.std(steps_l2)
            secs_l2_stddev = np.std(secs_l2)
            score_l2_stddev = np.std(score_l2)
            outcome_l2_stddev = np.std(outcome_l2)

            steps_l2 = np.average(steps_l2)
            secs_l2 = np.average(secs_l2)
            score_l2 = np.average(score_l2)
            outcome_l2 = np.average(outcome_l2)

            steps_l3_stddev = np.std(steps_l3)
            secs_l3_stddev = np.std(secs_l3)
            score_l3_stddev = np.std(score_l3)
            outcome_l3_stddev = np.std(outcome_l3)

            steps_l3 = np.average(steps_l3)
            secs_l3 = np.average(secs_l3)
            score_l3 = np.average(score_l3)
            outcome_l3 = np.average(outcome_l3)

            performance = "high" if c == 0 else "random"
            statement = "accurate" if a == 0 else "random"
            s = "performance={}, accuracy={}".format(performance, statement)
            axs[0].set_ylabel('Average\nTime to Goal\nSeconds')
            x_size = np.arange(4)
            axs[0].errorbar(x_size, [secs_l0, secs_l1, secs_l2, secs_l3],
                            yerr=[secs_l0_stddev, secs_l1_stddev, secs_l2_stddev, secs_l3_stddev], fmt='o-', label=s)
            axs[0].set_ylim([0, 100])
            axs[0].set_xticks(x_size)
            axs[0].get_xaxis().set_visible(False)
            axs[0].annotate("{:+.1f}".format(secs_l1 - secs_l0), (1, secs_l1))
            axs[0].annotate("{:+.1f}".format(secs_l2 - secs_l0), (2, secs_l2))
            axs[0].annotate("{:+.1f}".format(secs_l3 - secs_l0), (3, secs_l3))
            axs[0].legend()

            axs[1].set_ylabel('Average\nTime to Goal\nSteps')
            axs[1].errorbar(x_size, [steps_l0, steps_l1, steps_l2, steps_l3],
                            yerr=[steps_l0_stddev, steps_l1_stddev, steps_l2_stddev, steps_l3_stddev], fmt='o-',
                            label=s)
            axs[1].set_ylim([0, 75])
            axs[1].set_xticks(x_size)
            axs[1].annotate("{:+.1f}".format(steps_l1 - steps_l0), (1, steps_l1))
            axs[1].annotate("{:+.1f}".format(steps_l2 - steps_l0), (2, steps_l2))
            axs[1].annotate("{:+.1f}".format(steps_l3 - steps_l0), (3, steps_l3))
            axs[1].get_xaxis().set_visible(False)

            axs[2].set_ylabel('Average\nScore')
            axs[2].errorbar(x_size, [score_l0, score_l1, score_l2, score_l3],
                            yerr=[score_l0_stddev, score_l1_stddev, score_l2_stddev, score_l3_stddev], fmt='o-',
                            label=s)
            axs[2].set_ylim([0, 6])
            axs[2].set_xticks(x_size)
            axs[2].annotate("{:+.1f}".format(score_l1 - score_l0), (1, score_l1))
            axs[2].annotate("{:+.1f}".format(score_l2 - score_l0), (2, score_l2))
            axs[2].annotate("{:+.1f}".format(score_l3 - score_l0), (3, score_l3))
            axs[2].get_xaxis().set_visible(False)

            axs[3].set_ylabel('Average\nOutcome')
            axs[3].errorbar(x_size, [outcome_l0, outcome_l1, outcome_l2, outcome_l3],
                            yerr=[outcome_l0_stddev, outcome_l1_stddev, outcome_l2_stddev, outcome_l3_stddev], fmt='o-',
                            label=s)
            axs[3].set_ylim([0, 1.5])
            axs[3].set_xticks(x_size)
            axs[3].annotate("{:+.1f}".format(outcome_l1 - outcome_l0), (1, outcome_l1))
            axs[3].annotate("{:+.1f}".format(outcome_l2 - outcome_l0), (2, outcome_l2))
            axs[3].annotate("{:+.1f}".format(outcome_l3 - outcome_l0), (3, outcome_l3))
            axs[3].set_xticklabels(
                [map_type_description[0], map_type_description[1], map_type_description[2], map_type_description[3]])
    plt.show()


def plot_trust_distribution_MDMT(user_data):
    """
     4 plots: report type vs. MDMT for combinations of performance/statements
     """
    for c in [0, 1]:
        for a in [0, 1]:
            performance = "high" if c == 0 else "random"
            statement = "accurate" if a == 0 else "random"
            s = "performance={}, accuracy={}".format(performance, statement)
            fig, axs = plt.subplots(4, 8, sharex=True, sharey=True)  # (y,x)
            fig.suptitle('Multidimensional Measure of Trust (MDMT)\n' + s)
            competency_type = c
            accuracy_type = a
            for i in range(4):
                reliable = []
                capable = []
                predictable = []
                skilled = []
                count_on = []
                competent = []
                consistent = []
                meticulous = []
                reliability_trust = []
                capability_trust = []
                for r in user_data:
                    if r[1] != accuracy_type or r[2] != competency_type:
                        continue
                    map_type = i
                    if i >= 1:
                        idx = r[21].index(str(map_type))
                    else:
                        idx = -1
                    t = r[5 + idx]  # 5,6,7
                    t.replace('8', '0')
                    reliable.append(int(t[0]))
                    capable.append(int(t[1]))
                    predictable.append(int(t[2]))
                    skilled.append(int(t[3]))
                    count_on.append(int(t[4]))
                    competent.append(int(t[5]))
                    consistent.append(int(t[6]))
                    meticulous.append(int(t[7]))

                    reliability_trust.append(np.average([float(t[0]), float(t[2]), float(t[4]), float(t[6])]))
                    capability_trust.append(np.average([float(t[1]), float(t[3]), float(t[5]), float(t[7])]))
                if i == 0:
                    s = "Training"
                elif i == 1:
                    s = "No SC Displayed"
                elif i == 2:
                    s = "Single SC Displayed"
                else:
                    s = "Segmented SC Displayed"
                axs[i, 0].set_ylabel('Frequency')
                axs[i, 0].hist(reliable, bins=np.arange(0, 8))
                axs[i, 0].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(reliable), np.std(reliable)), (1, 10))
                axs[i, 0].set_ylabel(s)
                axs[i, 0].set_ylim([0, 20])

                # axs[i,8].set_ylim([0, 7])

                axs[i, 1].hist(capable, bins=np.arange(0, 8), label=s)
                axs[i, 1].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(capable), np.std(capable)), (1, 10))

                axs[i, 2].hist(predictable, bins=np.arange(0, 8), label=s)
                axs[i, 2].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(predictable), np.std(predictable)),
                                   (1, 10))

                axs[i, 3].hist(skilled, bins=np.arange(0, 8), label=s)
                axs[i, 3].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(skilled), np.std(skilled)), (1, 10))

                axs[i, 4].hist(count_on, bins=np.arange(0, 8), label=s)
                axs[i, 4].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(count_on), np.std(count_on)), (1, 10))

                axs[i, 5].hist(competent, bins=np.arange(0, 8), label=s)
                axs[i, 5].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(competent), np.std(competent)), (1, 10))

                axs[i, 6].hist(consistent, bins=np.arange(0, 8), label=s)
                axs[i, 6].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(consistent), np.std(consistent)),
                                   (1, 10))

                axs[i, 7].hist(meticulous, bins=np.arange(0, 8), label=s)
                axs[i, 7].annotate("ave:{:+.1f}\nstd:{:+.1f}".format(np.average(meticulous), np.std(meticulous)),
                                   (1, 10))

                # axs[i, 8].hist(reliability_trust, bins=np.arange(0, 8), color='green')
                # axs[i, 9].hist(capability_trust, bins=np.arange(0, 8), color='green')

            arr = ['reliable', 'capable', 'predictable', 'skilled', 'someone you can\ncount on', 'competent',
                   'consistent', 'meticulous', 'reliability', 'capability']
            for i in range(8):
                axs[0, i].set_title(arr[i])

            plt.show()


def plot_trust_MDMT(user_data):
    """
    2 plots: report type vs. trust subscale (capability, reliability) for rr, ra, ar, aa
    """
    map_type_description = ['Training\n(with well performing robot)', 'No\nCompetency\nReport',
                            'Single\nCompetency\nReport', 'Segmented\nCompetency\nReport']

    fig, axs = plt.subplots(2, 1, sharex=False, sharey=True)  # (y,x)
    fig.suptitle('Multidimensional Measure of Trust (MDMT)')

    for c in [0, 1]:
        for a in [0, 1]:
            competency_type = c
            accuracy_type = a
            reliability_trust_points = []
            capability_trust_points = []
            reliability_trust_stddev = []
            capability_trust_stddev = []
            for i in range(4):
                map_type = i  # +1
                reliable = []
                capable = []
                predictable = []
                skilled = []
                count_on = []
                competent = []
                consistent = []
                meticulous = []
                for r in user_data:
                    if r[1] != accuracy_type or r[2] != competency_type:
                        continue
                    if i >= 1:
                        idx = r[21].index(str(map_type))
                    else:
                        idx = -1
                    t = r[5 + idx]  # 5,6,7
                    t.replace('8', '0')
                    reliable.append(int(t[0]))
                    capable.append(int(t[1]))
                    predictable.append(int(t[2]))
                    skilled.append(int(t[3]))
                    count_on.append(int(t[4]))
                    competent.append(int(t[5]))
                    consistent.append(int(t[6]))
                    meticulous.append(int(t[7]))
                reliable = np.sum(reliable) / len(reliable)
                capable = np.sum(capable) / len(capable)
                predictable = np.sum(predictable) / len(predictable)
                skilled = np.sum(skilled) / len(skilled)
                count_on = np.sum(count_on) / len(count_on)
                competent = np.sum(competent) / len(competent)
                consistent = np.sum(consistent) / len(consistent)
                meticulous = np.sum(meticulous) / len(meticulous)

                reliability_trust_stddev.append(np.std([reliable, predictable, count_on, consistent]))
                capability_trust_stddev.append(np.std([capable, skilled, competent, meticulous]))

                reliability_trust = np.average([reliable, predictable, count_on, consistent])
                capability_trust = np.average([capable, skilled, competent, meticulous])

                reliability_trust_points.append(reliability_trust)
                capability_trust_points.append(capability_trust)

            performance = "high" if c == 0 else "random"
            statement = "accurate" if a == 0 else "random"
            s = "performance={}, accuracy={}".format(performance, statement)
            axs[0].set_ylabel('Reliability Trust')
            axs[0].errorbar([0, 1, 2, 3],
                            [reliability_trust_points[0], reliability_trust_points[1], reliability_trust_points[2],
                             reliability_trust_points[3]],
                            yerr=[reliability_trust_stddev[0], reliability_trust_stddev[1], reliability_trust_stddev[2],
                                  reliability_trust_stddev[3]], fmt='o-', label=s)
            axs[0].set_ylim([0, 6.5])
            axs[0].set_xticks([0, 1, 2, 3])
            axs[0].get_xaxis().set_visible(False)
            axs[0].annotate("{:+.1f}".format(reliability_trust_points[1] - reliability_trust_points[0]),
                            (1, reliability_trust_points[1]))
            axs[0].annotate("{:+.1f}".format(reliability_trust_points[2] - reliability_trust_points[0]),
                            (2, reliability_trust_points[2]))
            axs[0].annotate("{:+.1f}".format(reliability_trust_points[3] - reliability_trust_points[0]),
                            (3, reliability_trust_points[3]))

            axs[1].set_ylabel('Capability Trust')
            axs[1].errorbar([0, 1, 2, 3],
                            [capability_trust_points[0], capability_trust_points[1], capability_trust_points[2],
                             capability_trust_points[3]],
                            yerr=[capability_trust_stddev[0], capability_trust_stddev[1], capability_trust_stddev[2],
                                  capability_trust_stddev[3]], fmt='o-', label=s)
            axs[1].set_ylim([0, 6.5])
            axs[1].set_xticks([0, 1, 2, 3])
            axs[1].set_xticklabels(
                [map_type_description[0], map_type_description[1], map_type_description[2], map_type_description[3]])
            axs[1].annotate("{:+.1f}".format(capability_trust_points[1] - capability_trust_points[0]),
                            (1, capability_trust_points[1]))
            axs[1].annotate("{:+.1f}".format(capability_trust_points[2] - capability_trust_points[0]),
                            (2, capability_trust_points[2]))
            axs[1].annotate("{:+.1f}".format(capability_trust_points[3] - capability_trust_points[0]),
                            (3, capability_trust_points[3]))

    plt.legend()
    plt.show()


def plot_demographics(user_data):
    age = []
    gender = []
    education = []
    comp = []
    level_order = []
    genders = ['male', 'female']
    educations = ['no college', 'some college', 'associates', 'bachelors', 'graduate']
    comps = ['11', '10', '01', '00']
    comps_human = ['performance=random\nstatement=random', 'performance=random\nstatement=accurate',
                   'performance=high\nstatement=random', 'performance=high\nstatement=accurate']
    level_orders = ['123', '132', '213', '231', '312', '321']

    for user in user_data:
        age.append(float(user[15]))
        gender.append(user[16])
        education.append(user[17])
        comp.append(str(int(user[1])) + str(int(user[2])))
        level_order.append(user[21])

    total = len(gender)
    gender = [gender.count(x) for x in genders]
    education = [education.count(x) for x in educations]
    comp = [comp.count(x) for x in comps]
    level_order = [level_order.count(x) for x in level_orders]

    plt.figure(figsize=(10, 5))

    plt.subplot(151)
    plt.title('Participant Gender\ntotal={}'.format(total))
    plt.bar(genders, gender)
    plt.ylabel('Frequency')
    plt.xticks(range(len(gender)), genders, rotation=45)
    plt.yticks(np.arange(0, np.max(gender) + 5, 5))

    plt.subplot(152)
    plt.title("Participant Age\nmean={:.2f} STD={:.2f}".format(np.mean(age), np.std(age)))
    plt.hist(age)  # , np.ones(len(age)))  # TODO histogram w/ more data
    plt.yticks(np.arange(0, 40, 5))

    plt.subplot(153)
    plt.title('Participant Education')
    plt.bar(educations, education)
    plt.xticks(range(len(education)), educations, rotation=45)
    plt.yticks(np.arange(0, np.max(education) + 5, 5))

    plt.subplot(154)
    plt.title('Agent Proficiency')
    plt.bar(comps_human, comp)
    plt.xticks(range(len(comp)), comps_human, rotation=45)
    plt.yticks(np.arange(0, np.max(comp) + 5, 5))

    plt.subplot(155)
    plt.title('Level Ordering')
    plt.bar(level_orders, level_order)
    plt.xticks(range(len(level_order)), level_orders, rotation=45)
    plt.yticks(np.arange(0, np.max(level_order) + 5, 5))

    plt.show()


def csv_write(user_data, run_data, user_filename, run_filename):
    with open(user_filename, 'w') as user_f:
        user_f.write(
            'id,accuracy,competency,username,practice_trust,first_trust,second_trust,third_trust,base_quiz,quiz1,quiz2,quiz3,code,time_start,prescreen,age,gender,education,open_quextion,client_ip,study_version,level_order,password' + '\n')
        with open(run_filename, 'a') as run_f:
            run_f.write(
                'id,user_id,map_number,accuracy_level,competency_level,confidence,report_level,run_timestamp,tot_mission_time_s,tot_mission_time_steps,score,path,code' + '\n')
            for user in user_data:
                u = list(user)
                # put dots on stuff so excel doesn't use number :(
                for i in range(4, 12):
                    u[i] = '.' + u[i] + '.'
                # remove references to the training round and end of game
                u[21] = u[21].replace('4', '')
                u[21] = u[21].replace('0', '')
                u[18] = u[18].replace(',', '')
                user_f.write(",".join([str(x) for x in u]) + "\n")
                for run in run_data:
                    for r in run:
                        if r[1] == user[0]:
                            r = list(r)
                            r[5] = r[5].replace(",", "")
                            r[11] = r[11].replace("'", "")
                            r[11] = r[11].replace(",", "")
                            # make sure training rounds reflect the actual competency level for plotting
                            # (since in the game training competency = 0 always)
                            if u[2] == 1:
                                if r[6] == 0 and r[4] == 0:
                                    r[4] = 1
                            r.append(user[12])
                            run_f.write(",".join([str(x) for x in r]) + "\n")


def csv_read(user_filename, run_filename):
    user_data = []
    run_data = []
    with open(user_filename, 'r') as user_f:
        for line in user_f.readlines()[1:]:
            line = line.strip()
            data = []
            ints = [0, 1, 2, 15]
            periods = np.arange(4, 12)
            for idx, l in enumerate(line.split(',')):
                if idx in ints:
                    l = float(l)
                if idx in periods:
                    l = l.replace('.', '')
                data.append(l)
            user_data.append(data)

    with open(run_filename, 'r') as run_f:
        for line in run_f.readlines()[1:]:
            line = line.strip()
            data = []
            ints = [0, 1, 2, 3, 4, 6, 8, 9, 10]
            for l in line.split(','):
                if idx in ints:
                    l = float(l)
                data.append(l)
            run_data.append(data)

    return run_data, user_data


def csv_write_for_analysis(user_data, run_data, user_filename, run_filename, performanc=0, accuracy=0):
    ID = 12
    ACC = 1
    PERF = 2
    TRAIN = 4
    # statement accuracy, robot performance
    # accurate:high; accurate:random; random:high; random:random
    LEVELS = {'00': 0, '01': 1, '10': 2, '11': 3}
    SC_CONDITION = ['training', 'no self-confidence', 'self-confidence', 'segmented self-confidence']
    columns = ['hrt_id', 'performance_level', 'trust_level', 'reliable','capable','predictable','skilled','dependable',
               'competent','consistent','meticulous','reliability_scale', 'capability_scale']
    with open(user_filename, 'w') as user_f:
        user_f.writelines(','.join(columns) + '\n')
        for user in user_data:
            if user[PERF] == performanc and user[ACC] == accuracy:
                for i in range(4):
                    data = []
                    data.append(str(user[ID]))

                    data.append(str(LEVELS[str(int(user[ACC])) + str(int(user[PERF]))]))
                    data.append(SC_CONDITION[i])
                    score = user[TRAIN+i]
                    score = score.replace('8', '0')
                    data.append(score[0])
                    data.append(score[1])
                    data.append(score[2])
                    data.append(score[3])
                    data.append(score[4])
                    data.append(score[5])
                    data.append(score[6])
                    data.append(score[7])
                    reliability = [int(score[0]), int(score[2]), int(score[4]), int(score[6])]
                    capability = [int(score[1]), int(score[3]), int(score[5]), int(score[7])]
                    data.append(str(np.average(reliability)))
                    data.append(str(np.average(capability)))
                    user_f.write(','.join(data) + '\n')


    ID = 12
    MAP = 2
    ACC = 3
    PERF = 4
    LEVEL = 6
    TIME_SECS = 8
    TIME_STEPS = 9
    SCORE = 10
    PATH = 11
    #TODO confidence, if given. Similar confidence maps between no SC & SC
    CONFIDENCE = ['very good', 'good', 'fair', 'bad', 'very bad']

    LEVEL_CONFIDENCE = [['very good'],
                        ['very good confidence', 'good confidence', 'very bad confidence', 'bad confidence',
                         'very good confidence'],
                        ['good confidence', 'very good confidence', 'bad confidence', 'very good confidence',
                         'very bad confidence'],
                        ['fair confidence,fair confidence', 'very bad confidence,very good confidence',
                         'good confidence,very good confidence', 'very good confidence,very Bad confidence',
                         'very good confidence,very bad confidence']]

    columns = ['hrt_id', 'performance_level', 'map_level', 'displayed_confidence', 'actual_confidence', 'outcome',
               'bonus_score', 'time_secs', 'time_steps', 'number_h_steps', 'number_a_steps', 'optimal_steps',
               'control_proportion', 'normalized_h_steps', 'normalized_a_steps']
    with open(run_filename, 'w') as run_f:
        run_f.writelines(','.join(columns) + '\n')
        for run in run_data:
            if run[LEVEL] == '0': # skip training rounds
                continue
            if run[LEVEL] == '3':
                continue
            if run[PERF] == str(performanc) and run[ACC] == str(accuracy):
                data = []
                data.append(str(run[ID]))
                data.append(str(LEVELS[str(int(run[ACC])) + str(int(run[PERF]))]))
                data.append(str(run[LEVEL]))

                report = run[5]
                report = report.replace('<b>Report:</b>', '')
                substr = re.findall("<b>(.*?)</b>", report)
                displayed = 'none' if len(substr) == 0 else ",".join(substr)
                displayed = displayed.replace(',', ': ')
                data.append(displayed.lower())
                actual = LEVEL_CONFIDENCE[int(run[LEVEL])][int(run[MAP])]
                if displayed == 'none':
                    actual = '.'+actual
                actual = actual.replace(',',': ')
                if str(str(LEVELS[str(int(run[ACC])) + str(int(run[PERF]))])) == '1' and str(run[LEVEL]) == '1':
                    actual = '.very bad confidence'
                elif str(str(LEVELS[str(int(run[ACC])) + str(int(run[PERF]))])) == '1' and str(run[LEVEL]) == '2':
                    actual = 'very bad confidence'
                data.append(actual.lower())

                outcome = ''
                outcome = '1' if 'GOAL' in run[PATH] else outcome
                outcome = '0' if 'ABORT' in run[PATH] else outcome
                outcome = '-1' if 'DEAD' in run[PATH] else outcome
                data.append(outcome)

                data.append(str(run[SCORE]))

                data.append(str(run[TIME_SECS]))

                data.append(str(run[TIME_STEPS]))

                path = run[PATH]
                path.replace('ABORT', '')
                path.replace('DEAD', '')
                path.replace('DEAD', '')

                h_steps = path.count('H')
                data.append(str(h_steps))

                a_steps = path.count('A')
                data.append(str(a_steps))

                optimal_s = optimal_steps(map_level=str(run[LEVEL]), map_number=str(run[MAP]))
                data.append(str(optimal_s))

                control_prop = control_proportion(h_steps, a_steps, optimal_s)
                data.append(str(control_prop))

                normalized_steps = h_steps/optimal_s
                data.append(str(normalized_steps))

                normalized_steps = a_steps / optimal_s
                data.append(str(normalized_steps))

                run_f.writelines(','.join(data) + '\n')


def write_all(user_data, run_data, run_filename):
    PARTICIPANT_ID = 12
    MAP_NUMBER = 2
    REPORTING_ACCURACY = 3
    AGENT_PERFORMANCE = 4
    DISPLAY_LEVEL = 6
    TIME_SECS = 8
    TIME_STEPS = 9
    SCORE = 10
    PATH = 11
    GENDER = 16
    AGE=15
    # TODO confidence, if given. Similar confidence maps between no SC & SC
    CONFIDENCE = ['very good', 'good', 'fair', 'bad', 'very bad']
    LEVELS = {'00': 0, '01': 1, '10': 2, '11': 3}
    LEVEL_CONFIDENCE = [['very good'],
                        ['very good confidence', 'good confidence', 'very bad confidence', 'bad confidence',
                         'very good confidence'],
                        ['good confidence', 'very good confidence', 'bad confidence', 'very good confidence',
                         'very bad confidence'],
                        ['fair confidence,fair confidence', 'very bad confidence,very good confidence',
                         'good confidence,very good confidence', 'very good confidence,very Bad confidence',
                         'very good confidence,very bad confidence']]
    '''
    Data:
        participant id (alphnumeric)
        performance level (accurate, random)
        reporting accuracy (accurate, random)
        information report presence (present, absent)
        displayed report (vbad, bad, vgood, good)
        actual confidence (i.e. agent map rating) (vbad, bad, vgood, good)
        map_level (0,1,2,3) (training, no sc, sc, segmented sc)
        map_number (0,1,2,3,4)
        outcome (fail, succeed, abort)
        bonus score (R+)
        time seconds (Z+)
        time steps (Z+)
        number human steps (Z+)
        normalized human steps (R+)
        number agent steps (Z+)
        normalized agent steps (R+)
        optimal policy steps (Z+)
        control proportion (R+)
        MDMT
    '''
    columns = ['participant id', 'gender', 'age', 'performance level', 'reporting accuracy',
               'information report presence',
               'displayed report', 'displayed segment', 'actual report', 'actual segment',
               'information displayed',
               'outcome', 'map number', 'map level', 'map counter', 'bonus score',
               'time seconds', 'time steps',
               'total human steps', 'normalized human steps', 'total agent steps', 'normalized agent steps',
               'optimal policy steps',
               'control proportion', 'control proportion segment', 'failure control', 'outcome loc x', 'outcome loc y',
               'reliable', 'capable', 'predictable', 'skilled', 'dependable', 'competent', 'consistent', 'meticulous',
               'reliability scale', 'capability scale']
    map_ctr = 0
    map_ctr_usr = ''
    with open(run_filename, 'w') as run_f:#TODO apend
        run_f.writelines(','.join(columns) + '\n')
        for run in run_data:
            if run[DISPLAY_LEVEL] == '0':  # skip training rounds
                continue
            #if run[LEVEL] == '3':
            #    continue

            data = []

            if run[PARTICIPANT_ID] != map_ctr_usr:
                map_ctr_usr = run[PARTICIPANT_ID]
                map_ctr = 0
            else:
                map_ctr += 1

            data.append(str(run[PARTICIPANT_ID]))


            age = 'nf'
            gender = 'nf'
            for user in user_data:
                if user[12] == run[PARTICIPANT_ID]:
                    age = user[AGE]
                    gender = user[GENDER]
                    break

            data.append(gender)
            data.append(str(age))

            data.append("high" if run[AGENT_PERFORMANCE] == '0' else "random")
            data.append("informed" if run[REPORTING_ACCURACY] == '0' else "random")
            # Information display
            report = run[5]
            report = report.replace('<b>Report:</b>', '')
            substr = re.findall("<b>(.*?)</b>", report)
            if len(substr) == 0:
                data[-1] = "absent"
                data.append('absent')
                data.append('absent')
            else:
                data.append('present')
                displayed = ",".join(substr)
                #displayed = displayed.replace(',', ': ')
                data.append(displayed.lower())

            if str(run[DISPLAY_LEVEL]) != '3':
                data.append(' ')

            actual = LEVEL_CONFIDENCE[int(run[DISPLAY_LEVEL])][int(run[MAP_NUMBER])]
            #actual = actual.replace(',', ': ')
            if str(int(run[AGENT_PERFORMANCE])) == '1' and str(run[DISPLAY_LEVEL]) == '3':
                actual = 'very bad confidence,very bad confidence'
            elif str(int(run[AGENT_PERFORMANCE])) == '1':
                actual = 'very bad confidence'
            data.append(actual.lower())

            if str(run[DISPLAY_LEVEL]) != '3':
                data.append('test')

            # map info
            if str(run[DISPLAY_LEVEL]) == '0':
                data.append("training")
            elif str(run[DISPLAY_LEVEL]) == '1':
                data.append("no report")
            elif str(run[DISPLAY_LEVEL]) == '2':
                data.append("single report")
            elif str(run[DISPLAY_LEVEL]) == '3':
                data.append("segmented report")
            #data.append(str(run[MAP_NUMBER]))

            #TODO outcome
            outcome = ''
            outcome = 'success' if 'GOAL' in run[PATH] else outcome
            outcome = 'abort' if 'ABORT' in run[PATH] else outcome
            outcome = 'fail' if 'DEAD' in run[PATH] else outcome
            data.append(outcome)


            #TODO map number
            data.append(run[MAP_NUMBER])

            #TODO  map level
            data.append(run[DISPLAY_LEVEL])

            #TODO map counter (lets us get ordering of maps)
            data.append(str(map_ctr))

            #TODO bonus
            data.append(str(run[SCORE]))

            # TODO time seconds
            data.append(str(run[TIME_SECS]))

            # TODO time steps
            data.append(str(run[TIME_STEPS]))

            # steps
            optimal_s = optimal_steps(map_level=str(run[DISPLAY_LEVEL]), map_number=str(run[MAP_NUMBER]))

            # h_steps
            path = run[PATH]
            path.replace('ABORT', '')
            path.replace('DEAD', '')
            path.replace('GOAL', '')
            h_steps = path.count('H')
            data.append(str(h_steps))

            # norm_h_steps
            normalized_steps = h_steps / optimal_s
            data.append(str(normalized_steps))

            # a_steps
            a_steps = path.count('A')
            data.append(str(a_steps))

            # norm_a_steps
            normalized_steps = a_steps / optimal_s
            data.append(str(normalized_steps))

            # optimal_policy_steps
            data.append(str(optimal_s))

            # control_proportion
            if str(run[DISPLAY_LEVEL]) == '3':# and str(run[REPORTING_ACCURACY]) == '0':
                print("FOUND SEGMENTED MAP {}, {}".format(run[MAP_NUMBER], displayed))
                p1, p2 = control_test(path, int(run[MAP_NUMBER]))
            else:
                p1 = control_proportion(h_steps, a_steps)
                p2 = ' '
            data.append(str(p1))
            data.append(str(p2))
            
            #if failed, who was in control
            path = run[PATH]
            if 'DEAD' in path:
                path = path.split('] [')
                p = path[-2]
                if 'A' in p:
                    data.append('autonomy control at failure')
                elif 'H' in p:
                    data.append('human control at failure')
            else:
                data.append('non-failure')

            #TODO outcome location
            path = run[PATH]
            path = path.split('] [')
            p = path[-1]
            p = p.replace(']]', '')
            p = p.replace(']', '')
            p = p.replace('[[', '')
            p = p.replace('[', '')
            p  = p.split(' ')
            lx = p[1]
            ly = p[2]
            data.append(lx)
            data.append(ly)

            for user in user_data:
                if user[12] == run[PARTICIPANT_ID]:
                    #MDMT Stuff
                    score = user[4+int(run[DISPLAY_LEVEL])]
                    score = score.replace('8', '0')
                    data.append(score[0])
                    data.append(score[1])
                    data.append(score[2])
                    data.append(score[3])
                    data.append(score[4])
                    data.append(score[5])
                    data.append(score[6])
                    data.append(score[7])

                    reliability = [int(score[0]), int(score[2]), int(score[4]), int(score[6])]
                    capability = [int(score[1]), int(score[3]), int(score[5]), int(score[7])]
                    data.append(str(np.average(reliability)))
                    data.append(str(np.average(capability)))
                    break

            run_f.writelines(','.join(data) + '\n')

if __name__ == "__main__":
    # dump()
    #data = get_data()
    # del data[1]
    #just_user_data = [y[0] for x, y in data.items()]
    #just_run_data = [y[1] for x, y in data.items()]

    just_run_data, just_user_data = csv_read(CSV_PATHS + '/subjects.csv', CSV_PATHS + '/runs.csv')
    #csv_write(just_user_data, just_run_data, CSV_PATHS+'/subjects1.csv', CSV_PATHS+'/runs1.csv')

    write_all(user_data=just_user_data, run_data=just_run_data,
              run_filename=CSV_PATHS+'/processed_all_v4.csv')
    #dd = []
    #for d in just_run_data:
    #    if 'NC-22720' in d[12]:
    #        dd.append(d)

    #plot_path_heatmap(just_run_data)

