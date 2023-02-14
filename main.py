# победа это не абстрактное понятие, но уравнение, на котором основывается стратегия

from handler import *

mark_failed_tasks()
deadlines_remind(STATUS_EXECUTES)

cmd_name  = ""
cur_categ = ""
cur_task  = ""

# TODO: функций перерасчёт времени на основе сделанных задач
# TODO: фиксация сделанных задач в конце дня

# TODO: попробовать вмонтировать пом (помножить на 0.75 free time)
while 1:
    parse_data = input().split()

    if parse_data[0] == "plan":
        get_best_plan(parse_data[1])

    if parse_data[0] == "categs":
        handle_show_categs(parse_data)

    if parse_data[0] == "add":
        handle_add_cmd(parse_data)
        cmd_name  = parse_data[0]
        cur_categ = parse_data[1]
        cur_task  = parse_data[2]

    elif parse_data[0] == "add_mul":
        handle_addMul_cmd(parse_data)
    
    elif parse_data[0] == "mark":
        handle_mark_cmd(parse_data)

    elif parse_data[0] == "show":
        handle_show_cmd(parse_data)

    elif parse_data[0] == "show_all":
        handle_show_all_cmd(parse_data)
        
    elif parse_data[0] == "show_failed":
        handle_show_failed_cmd(parse_data)

    elif parse_data[0] == "delete":
        handle_delete_cmd(parse_data)

    elif parse_data[0] == "change_deadline":
        handle_change_deadline_cmd(parse_data)

    elif parse_data[0] == "padd":
        handle_plan_add_cmd(parse_data)

    elif parse_data[0] == "pdelete":
        handle_plan_delete_cmd(parse_data)

    elif parse_data[0] == "pshow":
        handle_plan_show_cmd(parse_data)

    elif parse_data[0] == "show_free":
        handle_show_free_time_cmd(parse_data)
    
    elif parse_data[0] == "recount_hours":
        handle_change_time_data(parse_data)

    elif parse_data[0] == "total_modify_time":
        handle_total_modify_time(parse_data)
    
    else:
        if cmd_name == "add":
            name = ""
            for i in parse_data:
                name += i + ' '
            handle_add_cmd_short(cur_categ, cur_task, name)
        else:
            print("PARSING FAILED")    
    print("_____________________________________\n")
