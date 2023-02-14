from auxil_table import *

def add_subtask(glob_task_full_path, local_task_name, time_val, unlock_task_list, diff):
    
    if(time_val == '-d'):
        time_val = count_n_hours_on_task(glob_task_full_path)
    if(time_val == 0):
        return 0
    
    conn = sql.connect(glob_task_full_path + ".db")
    cur = conn.cursor()
    
    unlock_task_str = ""
    for task in unlock_task_list:
        unlock_task_str += '\"%s\"(%s) ' % (task[1], task[0])
    
    parameters = (local_task_name, time_val, STATUS_EXECUTES, unlock_task_str, diff)

    cur.execute("INSERT INTO subtasks VALUES(?, ?, ?, ?, ?)", parameters)
    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def mark_subtask_failed(glob_task_full_path, task_name):

    conn = sql.connect(glob_task_full_path + '.db')
    cur  = conn.cursor()

    cur.execute("UPDATE subtasks SET status=%s WHERE name='%s'" % (str(STATUS_FAILED), task_name))

    conn.commit()
#---------------------------------------------------------------------------------------------------------------------#

def get_subtasks(categ, task_name):
    conn = sql.connect(categ + '/' + task_name + '.db')
    cur = conn.cursor()
    arr = cur.execute("SELECT * FROM subtasks;").fetchall()
    conn.commit()
    
    return sorted(arr, key = lambda x: x[DIFF_INDEX])

#---------------------------------------------------------------------------------------------------------------------#

def count_n_hours_on_task(categ, task_name):

    arr = get_subtasks(categ, task_name)

    data = []
    for i in arr:
        if(i[STATUS_IND] == STATUS_DONE):
            data.append(int(i[TIME_INDEX]))
    conn.commit()

    if(len(data) == 0):
        print("no time data avalubale")
        return 0
    return sum(data) / len(data)

#---------------------------------------------------------------------------------------------------------------------#

def count_time_required(categ, task_name):

    tasks = get_subtasks(categ, task_name)

    total_time = 0
    for task in tasks:
        if task[STATUS_IND] == STATUS_EXECUTES:
            total_time += task[TIME_INDEX]
    return total_time
#---------------------------------------------------------------------------------------------------------------------#
