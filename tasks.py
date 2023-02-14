from auxil_table import *
from subtasks    import *

def create_task_table(path, name, deadline):

    conn = sql.connect(path + "/tasks_data.db")
    cur  = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS tasks(
                name       TEXT,
                deadline   TEXT,
                status     INT,
                time_ratio INT);""")
    
    parameters = (name, deadline, STATUS_EXECUTES, 1)
    
    cur.execute("INSERT INTO tasks VALUES(?, ?, ?, ?)", parameters)
    conn.commit()

    conn = sql.connect(path + "/" + name + ".db")
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS subtasks(
                name         TEXT,
                time         INT,
                status       INT,
                unlock_tasks TEXT,
                diff         TEXT);""")
    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def mark_task_failed(path, glob_task_name):
    conn = sql.connect(path + '/tasks_data.db')
    cur  = conn.cursor()

    cur.execute("UPDATE tasks SET status=%s WHERE name='%s'" % (str(STATUS_FAILED), glob_task_name))

    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def get_tasks_category(categ):

    conn = sql.connect(categ + "/tasks_data.db")
    cur  = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS tasks(
                name       TEXT,
                deadline   TEXT,
                status     INT,
                time_ratio INT);""")
    
    tasks = cur.execute("SELECT * FROM tasks")
    conn.commit()

    ### ! LOOK, HERE IS COSTIL!!!!! !!!!!!!!!!!!!!!!!
    ### !!!!!!!!!!!!!!!!!!!!!!!!!!!
    ### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    tasks = sorted(tasks, key = lambda x: int(list(x[1].split('.'))[0]) + (int(list(x[1].split('.'))[1]) - 9)* 30)
    
    return tasks
#---------------------------------------------------------------------------------------------------------------------#

def get_task(categ, task_name):
    tasks = get_tasks_category(categ)

    for i in tasks:
        if i[NAME_INDEX] == task_name:
            return i
    
    return -1

def get_tasks():
    data = []

    for n_categ in range(len(categories)):
        for i in get_tasks_category(categories[n_categ]):
            data.append(tuple([n_categ, i]))
    return data
#---------------------------------------------------------------------------------------------------------------------#

def delete_task(categ, task_name):
    print("YOU SURE?")
    ans = input()

    if(ans == 'y'):
        conn = sql.connect(categ + '/tasks_data.db')
        cur  = conn.cursor()

        cur.execute("DELETE FROM tasks WHERE name='%s'" % (task_name))
        conn.commit()
    
    return

#---------------------------------------------------------------------------------------------------------------------#

def get_all_subtasks():
    
    data = []
    for categ in categories:
        data.append([])

        for task in get_tasks_category(categ):

            data[-1].append([])
            for subtask in get_subtasks(categ, task[NAME_INDEX]):

                data[-1][-1].append(subtask)

    return data
#---------------------------------------------------------------------------------------------------------------------#
def get_sorted_tasks():
    tasks = get_tasks()
    return sorted(tasks, key=lambda task: date_to_int(task[1][TIME_INDEX]))

#---------------------------------------------------------------------------------------------------------------------#
def form_groups_of_subtasks(time_group_limit):

    data = []
    last_filled = True
    cur_group = [0, 0, []]

    task_iter = 0

    tasks = get_sorted_tasks()
    for n_task in range(len(tasks)):
        if tasks[n_task][1][STATUS_IND] != STATUS_EXECUTES:
            continue
        #data[-1].append([])
        
        cur_subtasks = sorted(get_subtasks(categories[tasks[n_task][0]], tasks[n_task][1][NAME_INDEX]), key = lambda x: float(x[TIME_INDEX]))

        for n_subtask in range(len(cur_subtasks)):

            if(cur_subtasks[n_subtask][STATUS_IND] != STATUS_EXECUTES):
                continue
                
            if last_filled:
                cur_group = [0, 0, 100000000000, []]
                last_filled = False

            if cur_group[0] + cur_subtasks[n_subtask][TIME_INDEX] <= time_group_limit:

                cur_group[0] += float(cur_subtasks[n_subtask][TIME_INDEX])
                cur_group[1] += float(cur_subtasks[n_subtask][DIFF_INDEX]) / cur_group[0]
                cur_group[2] = min(date_to_int(tasks[n_task][1][TIME_INDEX]), cur_group[2])

                err1_koef = cur_subtasks[n_subtask][TIME_INDEX] / (date_to_int(tasks[n_task][1][TIME_INDEX]) - cur_date_val)
                cur_group[-1].append(tuple([tasks[n_task][0], task_iter, tasks[n_task][1][NAME_INDEX], err1_koef, date_to_int(tasks[n_task][1][TIME_INDEX]), cur_subtasks[n_subtask]]))

            else:
                if(cur_group[0] == 0):
                    cur_group[0] += float(cur_subtasks[n_subtask][TIME_INDEX])
                    cur_group[1] += float(cur_subtasks[n_subtask][DIFF_INDEX]) / cur_group[0]
                    cur_group[2] = min(date_to_int(tasks[n_task][1][TIME_INDEX]), cur_group[2])

                    err1_koef = cur_subtasks[n_subtask][TIME_INDEX] / (date_to_int(tasks[n_task][1][TIME_INDEX]) - cur_date_val)
                    cur_group[-1].append(tuple([tasks[n_task][0], task_iter, tasks[n_task][1][NAME_INDEX], err1_koef, date_to_int(tasks[n_task][1][TIME_INDEX]), cur_subtasks[n_subtask]]))

                data.append(cur_group)
                last_filled = True
                if(cur_group[0] != 0):
                    cur_group = [0, 0, 100000000000, []]
                    last_filled = False

                    cur_group[0] += float(cur_subtasks[n_subtask][TIME_INDEX])
                    cur_group[1] += float(cur_subtasks[n_subtask][DIFF_INDEX]) / cur_group[0]
                    cur_group[2] = min(date_to_int(tasks[n_task][1][TIME_INDEX]), cur_group[2])

                    err1_koef = cur_subtasks[n_subtask][TIME_INDEX] / (date_to_int(tasks[n_task][1][TIME_INDEX]) - cur_date_val)
                    cur_group[-1].append(tuple([tasks[n_task][0], task_iter, tasks[n_task][1][NAME_INDEX], err1_koef, date_to_int(tasks[n_task][1][TIME_INDEX]), cur_subtasks[n_subtask]]))


    if not last_filled:
        data.append(cur_group)

    # TODO:
    #while remove_free_space(data):
    #    continue
    
    return data                

#---------------------------------------------------------------------------------------------------------------------#

def change_deadline(categ, task_name, date):

    conn = sql.connect('%s/tasks_data.db' % (categ))
    cur  = conn.cursor()

    print("%s" % str(date))
    cur.execute("UPDATE tasks SET deadline='%s' WHERE name='%s'" % (str(date), task_name))
    
    if date_cmp(date, cur_date):
        cur.execute("UPDATE tasks SET status=%s WHERE name='%s'" % (str(STATUS_EXECUTES), task_name))
    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def total_modify_subtasks_time(categ, task_name, ratio):

    conn = sql.connect(categ + '/' + task_name + '.db')
    cur = conn.cursor()
    subtasks = cur.execute("SELECT * FROM subtasks;").fetchall()

    for subtask in subtasks:    
        if subtask[STATUS_IND] == STATUS_EXECUTES:
            cur.execute("UPDATE subtasks SET time=%g WHERE name='%s'" % (subtask[TIME_INDEX] * ratio, subtask[NAME_INDEX]))
    conn.commit()

    conn = sql.connect("%s/tasks_data.db" % (categ))
    cur  = conn.cursor()

    cur.execute("UPDATE tasks SET time_ratio=1 WHERE name='%s'" % (task_name))
    conn.commit()
    return
#---------------------------------------------------------------------------------------------------------------------#

def recount_time_data(categ, task_name):

    req_task = get_task(categ, task_name)
    if(req_task == -1):
        print("unable to find task")
        return

    ratio = req_task[TIME_RATIO_INDEX]
    total_modify_subtasks_time(categ, task_name, ratioZ)
    return
#---------------------------------------------------------------------------------------------------------------------#
