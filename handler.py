from auxil_table import *
from subtasks import *
from tasks import *
from plans import *

N_DAYS_DEADLINE_REMIND = 5

TIME_PROJ_TASK_ERROR =  0.5
FLAG_PROJ_STYLE    = 0
FLAG_DEFAULT_STYLE = 1
INIT_DATE_DAY   = 14
INIT_DATE_MONTH = 9

# помечает просроченные задачи
def mark_failed_tasks():
    
    year, cur_month, cur_day = str(date.today()).split('-')
    
    for categ in categories:
        tasks = get_tasks_category(categ)
        for task in tasks:

            day, month = task[TIME_INDEX].split('.')
            if (month == cur_month) and (day <= cur_day):
                mark_task_failed(categ + "/", task[0])
            elif (month < cur_month):
                mark_task_failed(categ + "/", task[0])
#---------------------------------------------------------------------------------------------------------------------#

# ??
def mark_dates():

    year, cur_month, cur_day = str(date.today()).split('-')    

    start_date = date(2022, INIT_DATE_MONTH, INIT_DATE_DAY)
    end_date   = date(2022, int(cur_month), int(cur_day))

    delta = timedelta(days = 1)
    while start_date < end_date:
        
        str_date = start_date.strftime("%d.%m")
        print(str_date)
        
        if str_date in find_all(DAYS_DONE_DATA_PATH):
            continue
        
        cur_week_day  = start_date.weekday()
        rep_data      = get_rep_info(cur_week_day)
        actions_done = []

        for action in rep_data:
            print(str_date + ') ' + str(action[0]) + ': ', end = '')
            if input() == 'y':
                actions_done.append(action)
        
        if str_date in find_all(DAY_PLANNED_DATA_PATH):

            planned_data = get_date_action(str_date)

            for action in planned_data:
                if input() == 'y':
                    actions_done.append(action)

        conn = sql.connect(DAYS_DONE_DATA_PATH + str_date + '.db')
        cur  = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS done_day(
                    data   TEXT,
                    time   INT);""")
        
        for action in actions_done:
            cur.execute("INSERT INTO done_day VALUES(?, ?)", action)
        conn.commit()

        start_date += delta

    return

#---------------------------------------------------------------------------------------------------------------------#

def show_deadline(path, task_name):
    conn = sql.connect(path + "/tasks_data.db")
    cur  = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS tasks(
                name     TEXT,
                deadline TEXT,
                status   INT);""")
    
    deadlines = list(cur.execute("SELECT * FROM tasks"))

    for task in deadlines:
        if(task[STATUS_IND] == STATUS_EXECUTES and task[0] == task_name):
            out_red("Deadline: " + task[1])
    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def show_data(path, task_name):

    show_deadline(path, task_name)

    conn = sql.connect(path + "/" + task_name + '.db')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS subtasks(
                name         TEXT,
                time         INT,
                status       INT,
                unlock_tasks TEXT,
                diff         TEXT);""")

    arr = cur.execute("SELECT * FROM subtasks").fetchall()
    
    ind = 0

    n_hours = 0
    for i in arr:
        if(i[STATUS_IND] == STATUS_EXECUTES):
            n_hours += i[TIME_INDEX]
    
    out_blue("%d hours" % n_hours)

    for i in arr:
        if(i[STATUS_IND] == STATUS_EXECUTES):
            if len(i[UNLOCK_INDEX]) > 0:
                print(str(ind) + ") " + str(i[NAME_INDEX]) + ": " + str(i[TIME_INDEX]) + ", required: " + i[UNLOCK_INDEX])
            else:
                print(str(ind) + ") " + str(i[NAME_INDEX]) + ": " + str(i[TIME_INDEX]))
            ind += 1
    
    conn.commit()
#---------------------------------------------------------------------------------------------------------------------# 

def handle_show_cmd(parse_data):
    cur_category       = parse_data[1]
    cur_glob_task_name = parse_data[2]

    show_data(cur_category, cur_glob_task_name)

#---------------------------------------------------------------------------------------------------------------------#

def handle_show_failed_cmd(parse_data):
    deadlines_remind(STATUS_FAILED)
    
    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_add_cmd_short(cur_categ, cur_task, parse_data):
    
    local_task_name = parse_data

    print("time, diff: ", end = '')
    time_val, diff  = input().split()

    cur_subtasks = get_subtasks(cur_categ, cur_task)
    unlock_names = []
    
    print("Needed pre tasks?")

    if(input() != 'y'):
        add_subtask(cur_categ + "/" + cur_task, local_task_name, time_val, unlock_names, diff)
        return

    tasks = get_tasks_category(cur_categ)

    itera = 0
    for task in tasks:
        print("%d) %s" % (itera, task[NAME_INDEX]))
        itera += 1
    
    chosen_glob = list(map(int, input().split()))

    for glob in chosen_glob:
        if glob >= len(tasks):
                print("overflow, wtf dude")
                return
        show_data(cur_categ, tasks[glob][NAME_INDEX])
        chosen = list(map(int, input().split()))

        for task in chosen:
            if task >= len(cur_subtasks):
                print("overflow, wtf dude")
                return
            unlock_names.append(tuple([tasks[glob][NAME_INDEX] ,cur_subtasks[task][NAME_INDEX]]))
        
    add_subtask(cur_categ + "/" + cur_task, local_task_name, time_val, unlock_names, diff)
    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_add_cmd(parse_data):
    cur_category       = parse_data[1]
    cur_glob_task_name = parse_data[2]
    
    if len(parse_data) == 4:
        create_task_table(cur_category, cur_glob_task_name, parse_data[3])
        return
    
    if not (cur_glob_task_name + ".db" in find_all(cur_category + "/")):
        print("ERROR, no table found")

    print("name: ", end = '')
    local_task_name = input()

    handle_add_cmd_short(cur_category, cur_glob_task_name, local_task_name)

    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_mark_cmd(parse_data):
    cur_category       = parse_data[1]
    cur_glob_task_name = parse_data[2]

    glob_task_full_path = cur_category + "/" + cur_glob_task_name

    conn = sql.connect(glob_task_full_path + '.db')
    cur  = conn.cursor()

    tasks = get_tasks_category(cur_category)
    subtasks = get_subtasks(cur_category, cur_glob_task_name)

    for n_task in range(len(subtasks)):
        if subtasks[n_task][STATUS_IND] == STATUS_EXECUTES:
            print("%d) %s" %(n_task, subtasks[n_task][NAME_INDEX]))
    
    print("name: ", end = '')
    cur_loc_task_id = input()

    if(cur_loc_task_id == 'n'):
        return

    cur_loc_task_id = int(cur_loc_task_id)

    print("time: ", end = '')
    time_req = input()

    if cur_loc_task_id >= len(subtasks):
        return

    ratio = float(time_req) / subtasks[cur_loc_task_id][TIME_INDEX]
    cur.execute("UPDATE subtasks SET status=%s WHERE name='%s'" % (str(STATUS_DONE), subtasks[cur_loc_task_id][NAME_INDEX]))
    cur.execute("UPDATE subtasks SET time=%s WHERE name='%s'" % (time_req, subtasks[cur_loc_task_id][NAME_INDEX]))

    conn.commit()

    conn = sql.connect("%s/tasks_data.db" % (cur_category))
    cur  = conn.cursor()

    for task in tasks:
        if task[NAME_INDEX] == cur_glob_task_name:
            ratio += task[TIME_RATIO_INDEX]
            break
            
    cur.execute("UPDATE tasks SET time_ratio=%g WHERE name='%s'" % (ratio, cur_glob_task_name))
    conn.commit()

    return
#---------------------------------------------------------------------------------------------------------------------#

def show_deadline_category(category):
    conn = sql.connect("tasks_data.db")
    cur  = conn.cursor()

    deadlines = cur.execute("SELECT * FROM tasks")

    if(len(deadlines) > 0):
        print(category)

    for task in deadlines:
            print(task[0] + ": " + task[1])
    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def handle_show_deadlines(parse_data):

    for i in categories:
        show_deadline_category(i)
#---------------------------------------------------------------------------------------------------------------------#

def handle_fail_cmd(parse_data):
    cur_category       = parse_data[1]
    cur_glob_task_name = parse_data[2]

    if(len(parse_data) == 3):
        mark_task_failed(cur_category, cur_glob_task_name)
    elif(len(parse_data) == 4):
        mark_subtask_failed(cur_category + "/" + cur_glob_task_name, parse_data[3])
#---------------------------------------------------------------------------------------------------------------------#
# TODO: update failed status ???

def handle_change_deadline(parse_data):
    cur_category       = parse_data[1]
    cur_glob_task_name = parse_data[2]
    deadline_str       = parse_data[3]
    
    conn = sql.connect(cur_category + '/tasks.db')
    cur  = conn.cursor()

    cur.execute("UPDATE tasks SET deadline=%s WHERE name='%s'" % (deadline_str, cur_glob_task_name))

    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def deadlines_remind(status):

    year, cur_month, cur_day = list(map(int, str(date.today()).split('-')))

    for categ in categories:
        tasks = get_tasks_category(categ)
        categ_outed = 0
        for task in tasks:

            day, month = list(map(int, task[1].split('.')))
            if task[STATUS_IND] == status:
                if not categ_outed:
                    categ_outed = 1
                    out_red(categ)
                
                diff = (int(month) - int(cur_month)) * 30 + int(day) - int(cur_day)
                print("     %s: %d left" % (task[NAME_INDEX], diff))
#---------------------------------------------------------------------------------------------------------------------# 

def handle_delete_cmd(parse_data):
    cur_category       = parse_data[1]
    cur_glob_task_name = parse_data[2]

    if len(parse_data) == 3:
        delete_task(cur_category, cur_glob_task_name)
    elif len(parse_data) == 4:

        subtasks = get_subtasks(cur_category, cur_glob_task_name)

        for n_task in range(len(subtasks)):
            if subtasks[n_task][STATUS_IND] == STATUS_EXECUTES:
                print("%d) %s" %(n_task, subtasks[n_task][NAME_INDEX]))

        print("name: ", end = '')

        loc_task_name = input()
        if loc_task_name == 'n':
            return

        conn = sql.connect(cur_category + '/' + cur_glob_task_name + '.db')
        cur  = conn.cursor()

        cur.execute("DELETE FROM subtasks WHERE name='%s'" % (subtasks[int(loc_task_name)][NAME_INDEX]))
        conn.commit()

        if(len(get_subtasks(cur_category, cur_glob_task_name)) == 0):
            print("no other tasks on glob_task " + cur_glob_task_name + ", remove it?")

            ans = input()

            if(ans == 'Y'):
                delete_task(cur_category, cur_glob_task_name)
#---------------------------------------------------------------------------------------------------------------------#

def get_proj_plan_vars(dats_expected, categ):
    days_expected = float(days_expected)
    data = []

    tasks = get_tasks_category(categ)

    for task in tasks:
        days_req = count_task_days_required(categ, task[NAME_INDEX])

        if (days_req <= days_expected + TIME_PROJ_TASK_ERROR and days_req >= days_expected - TIME_PROJ_TASK_ERROR):
            data.append(tuple(categ, task[NAME_INDEX], days_req))

    return data
#---------------------------------------------------------------------------------------------------------------------#

def get_proj_plan_vars(days_expected):

    days_expected = float(days_expected)
    data = []

    for categ in categories:
        tasks = get_tasks_category(categ)

        for task in tasks:
            days_req = count_task_days_required(categ, task[NAME_INDEX])

            if (days_req <= days_expected + TIME_PROJ_TASK_ERROR and days_req >= days_expected - TIME_PROJ_TASK_ERROR):
                data.append(tuple(categ, task[NAME_INDEX], days_req))
    
    return data
        
#---------------------------------------------------------------------------------------------------------------------#

def handle_make_plan_cmd(parse_data):
    flag_val = parse_data[1]
    
    # NOT READY
    if flag_val == '-p':
        days_expected  = float(parse_data[2])
        
        data = []
        if len(parse_data) > 4:
            preffer_categ  = parse_data[3]
            data = get_proj_plan_vars(days_expected, preffer_categ)
        else:
            data = get_proj_plan_vars(days_expected)

        for var in data:
            print("%d) %s(%d)", data[0], data[1], data[2])

        n_chosen = input()

        if(n_chosen == 'n'):
            return

        n_chosen = int(n_chosen)
    #else:
        

    return
        
#---------------------------------------------------------------------------------------------------------------------#

def handle_plan_add_cmd(parse_data):
    
    date    = parse_data[1]
    mod     = parse_data[2]
    n_hours = float(parse_data[3])

    data = get_data_in_scopes(parse_data)
    
    if(mod == '-rep'):
        add_rep_info(date, data, n_hours)
    elif(mod == '-ed'):
        add_date_action(date, data, n_hours)
    else:
        print("unable to recognize mod")
    
    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_plan_delete_cmd(parse_data):
    
    date = parse_data[1]
    mod  = parse_data[2]

    if(mod == '-rep'):
        delete_rep_info(date)
    elif(mod == '-ed'): 
        delete_date_action(date)
    else:
        print("unable to recognize mod")
        
    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_plan_show_cmd(parse_data):

    date = parse_data[1]
    mod  = parse_data[2]

    if(mod == '-rep'):
        show_rep_info(date)
    elif(mod == '-ed'): 
        show_date_action(date)
    else:
        print("unable to recognize mod")
#---------------------------------------------------------------------------------------------------------------------#

def handle_change_deadline_cmd(parse_data):

    change_deadline(parse_data[1], parse_data[2], parse_data[3])
    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_show_free_time_cmd(parse_data):

    free_hours_arr = get_free_time_arr()

    n_days = int(parse_data[1])

    start_date = date(2022, tmp_cur_month, tmp_cur_day)
    delta = timedelta(days = 1)
        
    for n_day in range(n_days):
        year, cur_month, cur_day = str(start_date).split('-')
        start_date += delta

        print("%s: %d" % (str(start_date), free_hours_arr[n_day]))

    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_change_time_data(parse_data):

    categ     = parse_data[1]
    task_name = parse_data[2]

    recount_time_data(categ, task_name)

    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_total_modify_time(parse_data):

    categ = parse_data[1]
    task_name = parse_data[2]
    ratio = float(parse_data[3])

    total_modify_subtasks_time(categ, task_name, ratio)
    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_addMul_cmd(parse_data):

    print("time, diff: ", end = '')
    time_val, diff  = input().split()

    cur_categ = parse_data[1]
    cur_task  = parse_data[2]

    local_task_name = input()
    while(local_task_name != "n"):
        add_subtask(cur_categ + "/" + cur_task, local_task_name, time_val, [], diff)
        local_task_name = input()

    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_show_categs(parse_data):

    for categ in categories:
        out_blue("- " + categ)
    return
#---------------------------------------------------------------------------------------------------------------------#

def handle_show_all_cmd(parse_data):

    for categ in categories:
        out_yellow(categ)
        for task in get_tasks_category(categ):
            if(task[STATUS_IND] == STATUS_EXECUTES):
                out_red(task[NAME_INDEX])
                show_data(categ, task[NAME_INDEX])
        print("____________________________________")
    return
#---------------------------------------------------------------------------------------------------------------------#

