import sqlite3
import numpy as np
import matplotlib.pyplot as plt

DB_FILE = ""
CSV_PATHS = ""

def connect():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    return cur, con


def get_data():
    cur, con = connect()

    data = {}
    user_data = cur.execute('SELECT * FROM user;').fetchall()
    for user in user_data:
        if None in user:
            print("dropping user: {}".format(user[0]))
            continue
        print(user)
        user_id = user[0]

        run_data = []
        for run in cur.execute('SELECT * FROM results WHERE user_id=?', (user_id,)):
            run_data.append(run)

        data[user_id] = (user, run_data)

    con.close()

    return data


def dump():
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(DB_FILE)

    cur = con.cursor()

    # The result of a "cursor.execute" can be iterated over by row
    for row in cur.execute('SELECT * FROM user;'):
        print(row)
    #for row in cur.execute('SELECT * FROM results;'):
    #    print(row)

    # Be sure to close the connection
    con.close()


def compute_bonus_score(run_data, user_data):
    """
    for each user, get user code
        scroll through runs, pick out the ones with that code, accumulate score
    print score rounded
    """
    scores = {}
    for user in user_data:
        user_code = user[12]
        user_name = user[3]
        scores[user_name] = 0
        for run in run_data:
            if run[12] == user_code:
                scores[user_name] = scores[user_name] + float(run[10])

    for k, v in scores.items():
        print(k + "," + str(np.round(v)/100))


def plot_path_heatmap():
    """
    TODO Heatmap of:
        routes per map
        takeovers per map
    """
    pass


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
            if int(r[6]) == 1: # no SC
                r[11] = r[11].replace('GOAL','')
                r[11] = r[11].replace('ABORT','')
                r[11] = r[11].replace('DEAD','')
                p = r[11].count('H')#r[11].count('A')/r[11].count('H') if r[11].count('H') > 0 else 1.0
                prop_no_sc_bad.append(p)
            if int(r[6]) == 2: # SC
                r[11] = r[11].replace('GOAL','')
                r[11] = r[11].replace('ABORT','')
                r[11] = r[11].replace('DEAD','')
                p = r[11].count('H') # r[11].count('A') / r[11].count('H') if r[11].count('H') > 0 else 1.0
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
            if int(r[6]) == 3: # SegC
                r[11] = r[11].replace('GOAL','')
                r[11] = r[11].replace('ABORT','')
                r[11] = r[11].replace('DEAD','')
                p = r[11].count('H')#r[11].count('A')/r[11].count('H') if r[11].count('H') > 0 else 1.0
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
    axs[0].errorbar(np.arange(3), [prop_no_sc_bad, prop_sc_vbad, prop_ssc_bad], yerr=[15,15,15],fmt='o-', label=s)
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


def plot_performance(run_data):
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
            axs[0,0].set_ylabel('Average\nTime to Goal\nSeconds')
            axs[0,0].errorbar(np.arange(2), [secs_l1, secs_l2], yerr=[secs_l1_stddev, secs_l2_stddev], fmt='o-', label=s)
            axs[0,0].set_ylim([0, 100])
            axs[0,0].set_xticks([0, 1])
            axs[0,0].get_xaxis().set_visible(False)
            axs[0,0].annotate("{:+.1f}".format(secs_l2 - secs_l1), (1, secs_l2))
            axs[0,0].legend()

            axs[1,0].set_ylabel('Average\nTime to Goal\nSteps')
            axs[1,0].errorbar(np.arange(2), [steps_l1, steps_l2], yerr=[steps_l1_stddev, steps_l2_stddev], fmt='o-', label=s)
            axs[1,0].set_ylim([0, 100])
            axs[1,0].set_xticks([0, 1])
            axs[1,0].annotate("{:+.1f}".format(steps_l2 - steps_l1), (1, steps_l2))
            axs[1,0].get_xaxis().set_visible(False)

            axs[2,0].set_ylabel('Average\nScore')
            axs[2,0].errorbar(np.arange(2), [score_l1, score_l2], yerr=[score_l1_stddev, score_l2_stddev], fmt='o-', label=s)
            axs[2,0].set_ylim([0, 8])
            axs[2,0].set_xticks([0, 1])
            axs[2,0].annotate("{:+.1f}".format(score_l2 - score_l1), (1, score_l2))
            axs[2,0].get_xaxis().set_visible(False)

            axs[3,0].set_ylabel('Average\nOutcome')
            axs[3,0].errorbar(np.arange(2), [outcome_l1, outcome_l2], yerr=[outcome_l1_stddev, outcome_l2_stddev], fmt='o-', label=s)
            axs[3,0].set_ylim([0, 1.5])
            axs[3,0].set_xticks([0, 1])
            axs[3,0].annotate("{:+.1f}".format(outcome_l2 - outcome_l1), (1, outcome_l2))
            axs[3,0].set_xticklabels([map_type_description[0], map_type_description[1]])

            axs[0, 1].set_ylabel('Average\nTime to Goal\nSeconds')
            axs[0, 1].errorbar(np.arange(2), [secs_l1, secs_l3], yerr=[secs_l1_stddev, secs_l3_stddev], fmt='o-', label=s)
            axs[0, 1].set_ylim([0, 100])
            axs[0, 1].set_xticks([0, 1])
            axs[0, 1].annotate("{:+.1f}".format(secs_l3 - secs_l1), (1, secs_l3))
            axs[0, 1].get_xaxis().set_visible(False)

            #axs[1, 1].set_ylabel('Average\nTime to Goal\nSteps')
            axs[1, 1].errorbar(np.arange(2), [steps_l1, steps_l3], yerr=[steps_l1_stddev, steps_l3_stddev], fmt='o-', label=s)
            axs[1, 1].set_ylim([0, 100])
            axs[1, 1].set_xticks([0, 1])
            axs[1, 1].annotate("{:+.1f}".format(steps_l3 - steps_l1), (1, steps_l3))
            axs[1, 1].get_xaxis().set_visible(False)

            #axs[2, 1].set_ylabel('Average\nScore')
            axs[2, 1].errorbar(np.arange(2), [score_l1, score_l3], yerr=[score_l1_stddev, score_l3_stddev], fmt='o-', label=s)
            axs[2, 1].set_ylim([0, 8])
            axs[2, 1].set_xticks([0, 1])
            axs[2, 1].annotate("{:+.1f}".format(score_l3 - score_l1), (1, score_l3))
            axs[2, 1].get_xaxis().set_visible(False)

            #axs[3, 1].set_ylabel('Average\nOutcome')
            axs[3, 1].errorbar(np.arange(2), [outcome_l1, outcome_l3], yerr=[outcome_l1_stddev, outcome_l3_stddev], fmt='o-', label=s)
            axs[3, 1].set_ylim([0, 1.5])
            axs[3, 1].set_xticks([0, 1])
            axs[3, 1].annotate("{:+.1f}".format(outcome_l3 - outcome_l1), (1, outcome_l3))
            axs[3, 1].set_xticklabels([map_type_description[0], map_type_description[2]])

    plt.show()


def plot_trust_MDMT(user_data):
    """
    2 plots: report type vs. trust subscale (capability, reliability) for rr, ra, ar, aa
    """
    map_type_description = ['No\nCompetency\nReport', 'Single\nCompetency\nReport', 'Segmented\nCompetency\nReport']

    fig, axs = plt.subplots(2, 2, sharex=False, sharey=True) #(y,x)
    fig.suptitle('Multidimensional Measure of Trust (MDMT)')

    for c in [0,1]:
        for a in [0,1]:
            competency_type = c
            accuracy_type = a
            reliability_trust_points = []
            capability_trust_points = []
            reliability_trust_stddev = []
            capability_trust_stddev = []
            for i in range(3):
                map_type = i+1
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
                    TEST = r[21].index(str(map_type))
                    t = r[5+TEST] # 5,6,7
                    t.replace('8', '0')
                    reliable.append(int(t[0]))
                    capable.append(int(t[1]))
                    predictable.append(int(t[2]))
                    skilled.append(int(t[3]))
                    count_on.append(int(t[4]))
                    competent.append(int(t[5]))
                    consistent.append(int(t[6]))
                    meticulous.append(int(t[7]))
                reliable = np.sum(reliable)/len(reliable)
                capable = np.sum(capable)/len(capable)
                predictable = np.sum(predictable)/len(predictable)
                skilled = np.sum(skilled)/len(skilled)
                count_on = np.sum(count_on)/len(count_on)
                competent = np.sum(competent)/len(competent)
                consistent = np.sum(consistent)/len(consistent)
                meticulous = np.sum(meticulous)/len(meticulous)

                reliability_trust_stddev.append(np.std([reliable, predictable, count_on, consistent]))
                capability_trust_stddev.append(np.std([capable, skilled, competent, meticulous]))

                reliability_trust = np.average([reliable, predictable, count_on, consistent])
                capability_trust = np.average([capable, skilled, competent, meticulous])

                reliability_trust_points.append(reliability_trust)
                capability_trust_points.append(capability_trust)

            s = "comp={}, acc={}".format(c, a)
            axs[0,0].set_ylabel('Reliability Trust')
            axs[0,0].errorbar([0,1], [reliability_trust_points[0], reliability_trust_points[1]], yerr=[reliability_trust_stddev[0], reliability_trust_stddev[1]], fmt='o-', label=s)
            axs[0,0].set_ylim([0,6.5])
            axs[0,0].set_xticks([0,1])
            axs[0,0].get_xaxis().set_visible(False)
            axs[0,0].annotate("{:+.1f}".format(reliability_trust_points[1]-reliability_trust_points[0]), (1, reliability_trust_points[1]))
            #axs[0,0].legend()

            axs[1,0].set_ylabel('Capability Trust')
            axs[1,0].errorbar([0,1], [capability_trust_points[0], capability_trust_points[1]], yerr=[capability_trust_stddev[0], capability_trust_stddev[1]], fmt='o-', label=s)
            axs[1,0].set_ylim([0,6.5])
            axs[1,0].set_xticks([0,1])
            axs[1,0].set_xticklabels([map_type_description[0], map_type_description[1]])
            axs[1, 0].annotate("{:+.1f}".format(capability_trust_points[1] - capability_trust_points[0]), (1, capability_trust_points[1]))

            #axs[0,1].set_ylabel('Reliability Trust')
            axs[0,1].errorbar([0,1], [reliability_trust_points[0], reliability_trust_points[2]], yerr=[reliability_trust_stddev[0], reliability_trust_stddev[2]], fmt='o-', label=s)
            axs[0,1].set_ylim([0,6.5])
            axs[0,1].set_xticks([0,1])
            axs[0,1].get_xaxis().set_visible(False)
            axs[0, 1].annotate("{:+.1f}".format(reliability_trust_points[2] - reliability_trust_points[0]), (1, reliability_trust_points[2]))

            #axs[1,1].set_ylabel('Capability Trust')
            axs[1,1].errorbar([0,1], [capability_trust_points[0], capability_trust_points[2]], yerr=[capability_trust_stddev[0], capability_trust_stddev[2]], fmt='o-', label=s)
            axs[1,1].set_ylim([0,6.5])
            axs[1,1].set_xticks([0,1])
            axs[1,1].set_xticklabels([map_type_description[0], map_type_description[2]])
            axs[1, 1].annotate("{:+.1f}".format(capability_trust_points[2] - capability_trust_points[0]),(1, capability_trust_points[2]))
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
    comps_human = ['rand,rand', 'rand,act', 'act,rand', 'act,act']
    level_orders = ['123', '132', '213', '231', '312', '321']

    for user in user_data:
        age.append(float(user[15]))
        gender.append(user[16])
        education.append(user[17])
        comp.append(str(int(user[1]))+str(int(user[2])))
        level_order.append(user[21])

    gender = [gender.count(x) for x in genders]
    education = [education.count(x) for x in educations]
    comp = [comp.count(x) for x in comps]
    level_order = [level_order.count(x) for x in level_orders]

    plt.figure(figsize=(10, 5))

    plt.subplot(151)
    plt.title('Subject Gender')
    plt.bar(genders, gender)
    plt.ylabel('Count')
    plt.xticks(range(len(gender)), genders, rotation=45)
    plt.yticks(np.arange(0, np.max(gender)+1))

    plt.subplot(152)
    plt.title('Subject Age')
    plt.hist(age)#, np.ones(len(age)))  # TODO histogram w/ more data
    plt.yticks(np.arange(0, 5
                         + 1))
    plt.subplot(153)
    plt.title('Subject Education')
    plt.bar(educations, education)
    plt.xticks(range(len(education)), educations, rotation=45)
    plt.yticks(np.arange(0, np.max(education) + 1))

    plt.subplot(154)
    plt.title('Agent accuracy,competency\n(random or actual)')
    plt.bar(comps_human, comp)
    plt.xticks(range(len(comp)), comps_human, rotation=45)
    plt.yticks(np.arange(0, np.max(comp) + 1))

    plt.subplot(155)
    plt.title('Level ordering\n1=no SC, 2=single SC, 3=segmented SC')
    plt.bar(level_orders, level_order)
    plt.xticks(range(len(level_order)), level_orders, rotation=45)
    plt.yticks(np.arange(0, np.max(level_order) + 1))

    plt.show()


def csv_write(user_data, run_data, user_filename, run_filename):
    with open(user_filename, 'a') as user_f:
        user_f.write('id,accuracy,competency,username,practice_trust,first_trust,second_trust,third_trust,base_quiz,quiz1,quiz2,quiz3,code,time_start,prescreen,age,gender,education,open_quextion,client_ip,study_version,level_order,password'+'\n')
        with open(run_filename, 'a') as run_f:
            run_f.write('id,user_id,map_number,accuracy_level,competency_level,confidence,report_level,run_timestamp,tot_mission_time_s,tot_mission_time_steps,score,path,code' + '\n')
            for user in user_data:
                u = list(user)
                for i in range(4, 12):
                    u[i] = '.'+u[i]+'.'
                u[21] = u[21].replace('4', '')
                u[21] = u[21].replace('0', '')
                u[18] = u[18].replace(',', '')
                user_f.write(",".join([str(x) for x in u])+"\n")
                for run in run_data:
                    for r in run:
                        if r[1] == user[0]:
                            r = list(r)
                            r[5] = r[5].replace(",", "")
                            r[11] = r[11].replace("'", "")
                            r[11] = r[11].replace(",", "")
                            r.append(user[12])
                            run_f.write(",".join([str(x) for x in r])+"\n")


def csv_read(user_filename, run_filename):
    user_data = []
    run_data = []
    with open(user_filename, 'r') as user_f:
        for line in user_f.readlines()[1:]:
            line = line.strip()
            data = []
            ints = [0, 1, 2, 15]
            periods = np.arange(4,12)
            for idx, l in enumerate(line.split(',')):
                if idx in ints:
                    l = float(l)
                if idx in periods:
                    l = l.replace('.','')
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


if __name__ == "__main__":
    #dump()
    #data = get_data()
    #del data[1]
    #just_user_data = [y[0] for x, y in data.items()]
    #just_run_data = [y[1] for x, y in data.items()]

    just_run_data, just_user_data = csv_read('subjects.csv', 'runs.csv')
    #csv_write(just_user_data, just_run_data, 'subjects1.csv', 'runs1.csv')

    plot_demographics(just_user_data)
    plot_trust_MDMT(just_user_data)
    plot_performance(just_run_data)

    #plot_driving_proportion(just_run_data)
    #compute_bonus_score(just_run_data, just_user_data)

