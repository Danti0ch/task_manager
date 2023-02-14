from auxil_table import *
from subtasks    import *
from tasks       import *
import itertools
import math

pNAME_INDEX = 0
pTIME_INDEX = 1
pSTATUS     = 2

CUR_YEAR = 2022

def get_date_action(date):

    conn = sql.connect(DAY_PLANNED_DATA_PATH  + date + '.db')
    cur  = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS planned(
            data   TEXT,
            time   INT);""")
    arr  = cur.execute("SELECT * FROM planned;").fetchall()
    conn.commit()
    
    return arr
#---------------------------------------------------------------------------------------------------------------------#

def add_date_action(date, data, n_hours):

    conn = sql.connect(DAY_PLANNED_DATA_PATH + date + '.db')
    cur  = conn.cursor()

    parameters = (data, n_hours)
    cur.execute("""CREATE TABLE IF NOT EXISTS planned(
                data   TEXT,
                time   INT);""")
    
    cur.execute("INSERT INTO planned VALUES(?, ?)", parameters)
    conn.commit()

    return    
#---------------------------------------------------------------------------------------------------------------------#

def show_date_action(date):
    actions = get_date_action(date)

    for n_action in range(len(actions)):
        print("%d) %s(%s)" % (n_action, actions[n_action][pNAME_INDEX], actions[n_action][pTIME_INDEX]))

    return
#---------------------------------------------------------------------------------------------------------------------#

def delete_date_action(date):
    actions = get_date_action(week_day)

    for n_action in range(len(actions)):
        print("%d) %s(%s)" % (n_action, actions[n_action][pNAME_INDEX], actions[n_action][pTIME_INDEX]))
    
    n_action = input()

    if(n_action == 'N'):
        return
    n_action = int(n_action)

    action_data = actions[n_action][pNAME_INDEX]
    conn = sql.connect(DAY_PLANNED_DATA_PATH  + date + '.db')
    cur  = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE planned='%s'" % (action_data))
    conn.commit()

    return
#---------------------------------------------------------------------------------------------------------------------#

def get_rep_info(week_day):

    conn = sql.connect(DAY_PLANNED_DATA_PATH + REP_DATA_FOLDER_NAME + str(week_day) + '.db')
    cur  = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS repeated_actions(
                data   TEXT,
                time   INT);""")
    arr  = cur.execute("SELECT * FROM repeated_actions;").fetchall()
    conn.commit()
    
    return arr

#---------------------------------------------------------------------------------------------------------------------#

def add_rep_info(week_day, data, n_hours):

    conn = sql.connect(DAY_PLANNED_DATA_PATH + REP_DATA_FOLDER_NAME + week_day + '.db')
    cur  = conn.cursor()

    parameters = (data, n_hours)
    cur.execute("""CREATE TABLE IF NOT EXISTS repeated_actions(
                data   TEXT,
                time   INT);""")
    
    cur.execute("INSERT INTO repeated_actions VALUES(?, ?)", parameters)
    conn.commit()
    
    return
#---------------------------------------------------------------------------------------------------------------------#

def show_rep_info(week_day):
    actions = get_rep_info(week_day)

    for n_action in range(len(actions)):
        print("%d) %s(%s)" % (n_action, actions[n_action][pNAME_INDEX], actions[n_action][pTIME_INDEX]))

    return
#---------------------------------------------------------------------------------------------------------------------#

def delete_rep_info(week_day):

    actions = get_rep_info(week_day)

    for n_action in range(len(actions)):
        print("%d) %s(%s)" % (n_action, actions[n_action][pNAME_INDEX], actions[n_action][pTIME_INDEX]))
    
    n_action = input()

    if(n_action == 'N'):
         return
    n_action = int(n_action)

    action_data = actions[n_action][pNAME_INDEX]
    conn = sql.connect(DAY_PLANNED_DATA_PATH + REP_DATA_FOLDER_NAME + week_day + '.db')
    cur  = conn.cursor()

    cur.execute("DELETE FROM repeated_actions WHERE data='%s'" % (action_data))
    conn.commit()

    return
#---------------------------------------------------------------------------------------------------------------------#

def get_planned_day_time(date):

    conn = sql.connect(DAY_PLANNED_DATA_PATH + date + '.db')

    cur  = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS planned(
            data   TEXT,
            time   INT);""")
    arr  = cur.execute("SELECT * FROM planned;").fetchall()
    conn.commit()
    
    n_hours = 0
    
    for action in arr:
        n_hours += action[pTIME_INDEX]
    
    week_day = datetime.date(CUR_YEAR, int(date.split('.')[1]), int(date.split('.')[0])).weekday()
    
    rep_actions = get_rep_info(week_day)

    for action in rep_actions:
        n_hours += action[pTIME_INDEX]
    
    if n_hours < 0:
        print(date + ': wrong actions data, > 24 hours required')
    
    return n_hours

#---------------------------------------------------------------------------------------------------------------------#

def get_planned_days_hours():

    dates = find_all(DAY_PLANNED_DATA_PATH)

    dates = sorted(dates, key = lambda x: date_to_int(x))

    days_data = []
    for date in dates:
        days_data.append(tuple(date, get_planned_day_time(date)))
    
    return days_data

#---------------------------------------------------------------------------------------------------------------------#

def count_task_days_required(categ, task_name):

    hours = count_time_required(categ, task_name)

    days_data = get_planned_days_ours()
    
    n_days_req = 0

    for day_data in days_data:
        if(date_to_int(day_data[0]) <= date_to_int(cur_date)):
            continue

        hours_required = day_data[1]

        if hours - cur_hours <= 0:
            n_days_req += hours / cur_hours
            break
        
        n_days_req += 1
        hours -= cur_hours

    return n_days_req
#---------------------------------------------------------------------------------------------------------------------#

def get_free_time_arr():

    n_days_until_last_deadline = 0

    year, cur_month, cur_day = list(map(int, str(date.today()).split('-')))

    cur_date_val = date_to_int(str(cur_day) + '.' + str(cur_month))
    
    for categ in categories:
        tasks = get_tasks_category(categ)

        for task in tasks:
            cur_deadline_val = date_to_int(task[TIME_INDEX])

            if(cur_deadline_val - cur_date_val > n_days_until_last_deadline):
                n_days_until_last_deadline = cur_deadline_val - cur_date_val
    
    free_time_arr = [(24 - N_SLEEP_HOURS - N_FREE_TIME) for i in range(n_days_until_last_deadline)]

    start_date = date(2022, cur_month, cur_day)

    delta = timedelta(days = 1)
    for i in range(n_days_until_last_deadline):
        
        year, cur_month, cur_day = str(start_date).split('-')

        n_working_hours = get_planned_day_time((cur_day) + '.' + (cur_month))

        free_time_arr[i] -= n_working_hours
        if(free_time_arr[i] < 0):
            print("not enough free time on date: " + str(start_date))
        
        start_date += delta

    return free_time_arr
#---------------------------------------------------------------------------------------------------------------------#

def get_distr(perm, tasks, time_arr):

    n_day             = 0
    cur_n_hours       = 0

    distr = [[] for i in range(len(time_arr))]
    last_task = 0

    for n_task in range(len(tasks)):

        if n_day >= len(time_arr):
            break
        
        if tasks[perm[n_task]][2][1] + cur_n_hours <= time_arr[n_day] + TIME_GROUPING_ERR:
            cur_n_hours += tasks[perm[n_task]][2][1]
            distr[n_day].append(tasks[perm[n_task]])
            last_task = n_task

        else:
            cur_n_hours  = 0
            n_day       += 1

            while n_day < len(time_arr) and tasks[perm[n_task]][2][1] > time_arr[n_day]:
                n_day += 1

    if last_task < len(tasks) - 1:
        return []
    return distr
#---------------------------------------------------------------------------------------------------------------------#

def validate(distr):
    year, cur_month, cur_day = list(map(int, str(date.today()).split('-')))
    cur_date_val = date_to_int(str(cur_day) + '.' + str(cur_month))

    for n_day in range(len(distr)):
        for task in distr[n_day]:
            if date_to_int(task[1][TIME_INDEX]) <= cur_date_val + n_day:
                return 0
    return 1
#---------------------------------------------------------------------------------------------------------------------#

M_min = 3
M_max = 4

P_dif = 0.5
import copy
year, cur_month, cur_day = list(map(int, str(date.today()).split('-')))
cur_date_val = date_to_int(str(cur_day) + '.' + str(cur_month))

best_err = 1000000000000
best_cmb = []
tmp_days = []

err1     = 0
err2_arr = []
err3_arr = []
err5_arr = []

err1_max = []
err2_max = []
err3_max = []
err4_max = []
err5_max = []

count_err_mod = 0
err_koefs = [0, 0, 0, 0, 0]

def count_error(time_arr):

    global err1
    global err2_arr
    global err3_arr
    global err5_arr

    global err1_max
    global err2_max
    global err3_max
    global err4_max
    global err5_max

    global count_err_mod
    global err_koefs

    err2_val = 0
    err3_val = 0
    err4_val = 0

    n_task = 0

    len_err2_arr = len(err2_arr)

    while n_task < len_err2_arr:

        # TODO: optimize this
        while n_task < len_err2_arr and len(err2_arr[n_task]) == 0:
            n_task += 1

        if n_task >= len_err2_arr:
            break
        increase_val = 0

        len_task = len(err2_arr[n_task])
        for n_info in range(len_task):
            while n_info < len_task and err2_arr[n_task][n_info][0] == err2_arr[n_task][n_info - 1][0]:
                increase_val += err2_arr[n_task][n_info][1]
                n_info += 1
            
            increase_val += err2_arr[n_task][n_info - 1][1]
            err4_val += 1.0005 ** (increase_val)

            if(n_info < len_task):
                err2_val += (increase_val + err2_arr[n_task][n_info][1]) / (err2_arr[n_task][n_info][0] + err2_arr[n_task][n_info - 1][0]) 
            n_info += 1
        n_task += 1

    err5_val = 0
    n_busy_days = 0
    for n_day in range(len(time_arr)):
        if err5_arr[n_day] == 0:
            continue
        if(err5_arr[n_day] - 0.005 > time_arr[n_day]):
            print("ERROR")
            exit(0)
        if err5_arr[n_day] == time_arr[n_day]:
            err5_val += 8        
        else:
            err5_val += 1 / (err5_arr[n_day] - time_arr[n_day])
        n_busy_days += 1
    
    err5_val *= 1 / n_busy_days

    for diff in err3_arr:
        
        #print(diff)
        if diff[0] > 0 and diff[0] / diff[1] > DAY_DIFF_OPTIMAL_VAL:
            err3_val += diff[0] / diff[1] - DAY_DIFF_OPTIMAL_VAL

    if count_err_mod == 0:
        err1_max.append(err1)
        err2_max.append(err2_val)
        err3_max.append(err3_val)
        err4_max.append(err4_val)
        err5_max.append(err5_val)
        return 0
    else:
        return err_koefs[0] * err1 + err_koefs[1] * err2_val + err_koefs[2] * err3_val + err_koefs[3] * err4_val + err_koefs[4] * err5_val

#---------------------------------------------------------------------------------------------------------------------#

from progress.bar import IncrementalBar

bar = IncrementalBar('Countdown', max = len([]))

bar_count = 0
bar_count_max = 1000

days_on_subtasks = [[0 for i in range(500)] for j in range(500)]
# TODO: to c++
def combinate(tasks, n_tasks, time_arr, visited, n_left_tasks, n_day, n_days, cur_time_offset):

    global tmp_days
    global err1
    global best_cmb
    global best_err
    global debug_last_day_output
    global bar
    global bar_count
    global bar_count_max
    global err2_arr
    global err3_arr
    global count_err_mod
    global days_on_subtasks

    if n_left_tasks == 0:
        bar_count += 1
        if bar_count == bar_count_max:
            
            bar.next()
            bar_count = 0
        if n_day >= n_days:
            return
        if len(tmp_days[0]) == 0:
            return
        err = count_error(time_arr)

        global best_err
        if err < best_err:
            best_err = err
            
            best_cmb = copy.deepcopy(tmp_days)
            #print(best_cmb)
        return
    
    for n_task in range(n_tasks):
        if visited[n_task]:
            continue

        #if tasks[n_task][2] <= (cur_date_val + n_day):
         #   return

        saved_n_day = n_day
        saved_offset = cur_time_offset
        s_iter = 0
        for subtask in tasks[n_task][-1]:
            time_val = subtask[-1][TIME_INDEX]

            if time_val + cur_time_offset > time_arr[n_day]:
                cur_time_offset = 0
                n_day += 1
            
                while n_day < n_days and time_arr[n_day] < time_val:
                    n_day += 1
                
                if n_day >= n_days:
                    s_iter2 = 0
                    for subtask in tasks[n_task][-1][:s_iter]:
                        
                        n_day = days_on_subtasks[n_task][s_iter2]
                        tmp_days[n_day].pop()

                        err2_arr[subtask[1]].pop()        
                        err1 -= n_day * subtask[3]

                        err3_arr[n_day][0] -= float(subtask[-1][DIFF_INDEX])

                        if abs(err3_arr[n_day][0]) < 0.001:
                            err3_arr[n_day][0] = 0
                        err3_arr[n_day][1] -= 1

                        err5_arr[n_day] -= float(subtask[-1][TIME_INDEX])
                        s_iter2 += 1
                    return

            if subtask[-2] <= (cur_date_val + n_day):
                s_iter2 = 0
                for subtask in tasks[n_task][-1][:s_iter]:
                    
                    n_day = days_on_subtasks[n_task][s_iter2]
                    tmp_days[n_day].pop()

                    err2_arr[subtask[1]].pop()        
                    err1 -= n_day * subtask[3]

                    err3_arr[n_day][0] -= float(subtask[-1][DIFF_INDEX])

                    if abs(err3_arr[n_day][0]) < 0.001:
                        err3_arr[n_day][0] = 0
                    err3_arr[n_day][1] -= 1

                    err5_arr[n_day] -= float(subtask[-1][TIME_INDEX])
                    s_iter2 += 1 
                return

            cur_time_offset += time_val
            
            tmp_days[n_day].append(tuple([n_task, s_iter]))

            a = sum([tasks[i[0]][-1][i[1]][-1][TIME_INDEX] for i in tmp_days[n_day]])
            if a > time_arr[n_day]:
                print(n_day, time_val, time_arr[n_day], a, cur_time_offset, tmp_days[n_day])

            days_on_subtasks[n_task][s_iter] = n_day

            err2_arr[subtask[1]].append(tuple([n_day, subtask[-1][TIME_INDEX]]))
            
            err1 += n_day * subtask[3]

            err3_arr[n_day][0] += float(subtask[-1][DIFF_INDEX])
            err3_arr[n_day][1] += 1

            err5_arr[n_day] += float(subtask[-1][TIME_INDEX])
            s_iter += 1
        
        visited[n_task] = 1
        combinate(tasks, n_tasks, time_arr, visited, n_left_tasks - 1, n_day, n_days, cur_time_offset)
        visited[n_task] = 0

        s_iter = 0
        for subtask in tasks[n_task][-1]:
            
            n_day = days_on_subtasks[n_task][s_iter]
            tmp_days[n_day].pop()

            err2_arr[subtask[1]].pop()        
            err1 -= n_day * subtask[3]

            err3_arr[n_day][0] -= float(subtask[-1][DIFF_INDEX])

            err5_arr[n_day] -= float(subtask[-1][TIME_INDEX])
            if abs(err3_arr[n_day][0]) < 0.001:
                err3_arr[n_day][0] = 0
            err3_arr[n_day][1] -= 1

            s_iter += 1
        n_day = saved_n_day   
        cur_time_offset = saved_offset
    return

#---------------------------------------------------------------------------------------------------------------------#

def count_err_koefs():
    
    if len(err1_max) == 0:
        return False
    
    avg1 = sum(err1_max) / len(err1_max)
    avg2 = sum(err2_max) / len(err2_max)
    avg3 = sum(err3_max) / len(err3_max)
    avg4 = sum(err4_max) / len(err4_max)
    avg5 = sum(err5_max) / len(err5_max)

    savg = avg1 + avg2 + avg3 + avg4 + avg5
    global err_koefs
    
    err_koefs[0] = savg / avg1 * 0.2
    err_koefs[1] = savg / avg2 * 0.3
    err_koefs[2] = savg / avg3 * 0.5
    err_koefs[3] = savg / avg4 * 0.1
    err_koefs[4] = savg / avg5 * 5

    return True
#---------------------------------------------------------------------------------------------------------------------#

def get_best_plan(cur_day_free_hours_done):

    free_hours_arr = get_free_time_arr()
    free_hours_arr[0] -= float(cur_day_free_hours_done)

    core_free_hours_arr = [i for i in free_hours_arr]
    pomodoro_koef = POMODORO_START_KOEF

    plan_generatio_success = False
    while(not plan_generatio_success):
        free_hours_arr = [i * pomodoro_koef for i in core_free_hours_arr]
        if free_hours_arr[0] < 0:
            free_hours_arr[0] = 0

        group_time_lim = TIME_LOWER_LIMIT
        tasks          = form_groups_of_subtasks(group_time_lim)

        while len(tasks) > 16:
            group_time_lim += 0.5
            tasks = form_groups_of_subtasks(group_time_lim)

        best_error     = 1
        best_var       = []

        global tmp_days
        global best_cmb
        global bar
        global bar_count_max
        global err3_arr
        global err2_arr
        global count_err_mod
        global best_err
        global err5_arr

        best_cmb = []
        tmp_days = []

        err1     = 0
        err2_arr = []
        err3_arr = []
        err5_arr = []

        err1_max = []
        err2_max = []
        err3_max = []
        err4_max = []
        err5_max = []

        count_err_mod = 0
        err_koefs = [0, 0, 0, 0, 0]

        print(free_hours_arr)
        print("HERE IS %d tasks, time limit: %d, pomodoro_koef: %f" % (len(tasks), group_time_lim, pomodoro_koef))
        #for task in tasks:
        #    print(task[1][NAME_INDEX], task[2][1])

        #for task in tasks:
        #    print(task)
        #    print("_____________________________________________")
        bar = IncrementalBar('progress', max = math.factorial(len(tasks)) / bar_count_max)

        err3_arr = [[0, 0] for i in range(len(free_hours_arr))]
        err2_arr = [[] for i in range(len(get_tasks()))]
        tmp_days = [[] for i in range(len(free_hours_arr))]

        err5_arr = [0 for i in range(len(free_hours_arr))]

        count_err_mod = 0
        combinate(tasks, len(tasks), free_hours_arr, [0 for i in range(len(tasks))], len(tasks), 0, len(free_hours_arr), 0)

        bar = IncrementalBar('progress', max = math.factorial(len(tasks)) / bar_count_max)

        err3_arr = [[0, 0] for i in range(len(free_hours_arr))]
        err2_arr = [[] for i in range(len(get_tasks()))]
        tmp_days = [[] for i in range(len(free_hours_arr))]

        err5_arr = [0 for i in range(len(free_hours_arr))]
        
        err1     = 0
        best_err = 1000000000000000
        plan_generatio_success = count_err_koefs()

        if not plan_generatio_success:
            pomodoro_koef += 0.05

            if(pomodoro_koef > 0.91):
                print("unable to make plan, too many tasks")
                return
            continue
    
        count_err_mod = 1
        combinate(tasks, len(tasks), free_hours_arr, [0 for i in range(len(tasks))], len(tasks), 0, len(free_hours_arr), 0)

        bar.finish()
        #print(free_hours_arr)

        for i in range(len(best_cmb)):

            if len(best_cmb[i]) == 0:
                continue
            print("on the %d day you have (%.2g + %.2g)/%.2g working hours" % (i, sum([tasks[j[0]][-1][j[1]][-1][TIME_INDEX] for j in best_cmb[i]]), free_hours_arr[i] * (1 - pomodoro_koef), free_hours_arr[i] / pomodoro_koef))
            print("best combination:")

            print(best_cmb[i])
            categ_printed = False
            task_printed  = False

            for categ in categories:
                categ_printed = False
                for task in get_tasks_category(categ):
                    task_printed = False
                    for cur_info in best_cmb[i]: # (task_id, subtask_id)

                        itera = 0

                        if len(cur_info) == 0:
                            continue
                        for subtask_data in tasks[cur_info[0]][-1]:
                            
                            if cur_info[1] == itera and categories[subtask_data[0]] == categ and subtask_data[2] == task[NAME_INDEX]:
                                if not categ_printed:
                                    categ_printed = True
                                    print(categ)
                                if not task_printed:
                                    task_printed = True
                                    print("-----%s" % task[NAME_INDEX])
                                print("         %s(%.3f)" % (subtask_data[-1][0], subtask_data[-1][TIME_INDEX]))
                            itera += 1
        
    return
#---------------------------------------------------------------------------------------------------------------------#
