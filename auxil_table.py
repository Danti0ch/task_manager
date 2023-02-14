import os
import sqlite3 as sql
from datetime import date, timedelta
import datetime

NAME_INDEX   = 0
TIME_INDEX   = 1
STATUS_IND   = 2
UNLOCK_INDEX = 3
DIFF_INDEX = 4

TIME_RATIO_INDEX = 3

STATUS_DONE     = 0
STATUS_EXECUTES = 1
STATUS_FAILED   = 2

N_SLEEP_HOURS = 5
N_FREE_TIME   = 0

DAY_PLANNED_DATA_PATH = 'def/'
REP_DATA_FOLDER_NAME  = 'rep/'
DAYS_DONE_DATA_PATH   = 'done/' 

TIME_LOWER_LIMIT = 0 #hours

DAY_DIFF_OPTIMAL_VAL = 0.6

POMODORO_START_KOEF = 0.6

tmp_year, tmp_cur_month, tmp_cur_day = list(map(int, str(date.today()).split('-')))

cur_date = str(tmp_cur_day) + '.' + str(tmp_cur_month)

# automatic
# при уменьшения числа подзадач эта хуйня уменьшается сама
TIME_GROUP_LIMIT = 6  #-//-

TIME_GROUPING_ERR = 0.5

categories = ["babichev", "calculus", "discret", "oop", "os", "ovitm", "diffur"]

def find_all(path):
    result = []
    for root, dirs, files in os.walk(path):
        for file_name in files:
            result.append(file_name)
    return result
#---------------------------------------------------------------------------------------------------------------------#

def get_data_in_scopes(parse_data):

    data = ""

    was_scope = 0
    for block in parse_data:
        if '"' in block:
            if was_scope:
                data += block + " "
                break
            was_scope = 1

        if was_scope:
            data += block + " "
    
    return data
#---------------------------------------------------------------------------------------------------------------------#

def date_to_int(date):
    return int(list(date.split('.'))[0]) + (int(list(date.split('.'))[1]) - 9)* 30
#---------------------------------------------------------------------------------------------------------------------#

def date_cmp(date1, date2):
    print(date_to_int(date1), date_to_int(date2))
    return date_to_int(date1) - date_to_int(date2) > 0
#---------------------------------------------------------------------------------------------------------------------#

cur_date_val = date_to_int(cur_date)

def out_red(text):
    print("\033[31m{}\033[0m " .format(text))
def out_yellow(text):
    print("\033[33m{}\033[0m " .format(text))
def out_blue(text):
    print("\033[34m{}\033[0m " .format(text))
#---------------------------------------------------------------------------------------------------------------------#
