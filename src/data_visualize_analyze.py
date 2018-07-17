#
# File data_visualize_analyze.py
# Author: Muhammad Mushfiqur Rahman
# Description: Medical app data visualization tool - summary info, churn rate, retention rate etc.
# Email:mushfiq.rahman@tum.de
# Date 2018-05-22


from __future__ import division
from os import listdir, makedirs
from os.path import isfile, join, dirname, exists, basename
import os
import shutil
import itertools
import xml.etree.ElementTree as ET
import numpy as np
import math
import scipy.misc
import colorsys
import csv
import re
import pydotplus
import pyparsing
import json
from graphviz import Source
from operator import itemgetter
import time
import pandas as pd
from scipy import sparse
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import signal
from datetime import datetime, date, timedelta
from collections import defaultdict
import seaborn as sns
sns.set(style='white')

class DatasetVisualize():
    def __init__(self):
        self.filepath = '~/medical_data_science.csv'
        self.column_names = ['DATE_JOINED',	'USER_ID',	'DATE_ACTIVITY', 'USER_LTD', 'VERSION_DATE_JOINED', 'VERSION_DATE_ACTIVITY', 'USER_ACTIVITY']
        self.dataset = pd.read_csv(self.filepath)
        print('Reading Dataset... ' + self.filepath)

        self.user_id_dist_arr = []
        self.all_user_ids_list = []
        self.user_ltd_dist_arr = []
        self.user_activity_arr = []
        self.version_arr = ['Version 1.3', 'Version 1.4', 'Version 1.4.1', 'Version 1.5', 'Version 1.6']
        self.registered_user_total = 0
        self.user_date_activity = []
        self.date_format = "%Y-%m-%d"
        self.start_date = '2017-01-13'
        self.end_date = '2017-06-17'
        diff = abs(datetime.strptime(self.end_date, self.date_format)-datetime.strptime(self.start_date, self.date_format))
        self.number_of_days = diff.days
        self.number_of_weeks = int(self.number_of_days/7)
        self.number_of_months = int(self.number_of_days/30)
        #print('number_of_days> ', self.number_of_days)

        self.no_of_user_registered_by_version = []
        self.number_of_users_register_per_month = []
        self.monthly_activity_app_version_1_3 = []
        self.monthly_activity_app_version_1_4 = []
        self.monthly_activity_app_version_1_4_1 = []
        self.monthly_activity_app_version_1_5 = []
        self.monthly_activity_app_version_1_6 = []
        self.number_of_active_action_per_month = []
        self.number_of_inactive_action_per_month = []
        self.total_entries_per_month = []

        self.activity_version_user_active_count = []
        self.activity_version_user_not_active_count = []
        self.activity_version_total_entries_count = []
        self.activity_version_user_active_percentage = []
        self.activity_version_user_not_active_percentage = []

        self.app_version_1_3_date_activity_total = 0
        self.app_version_1_4_date_activity_total = 0
        self.app_version_1_4_1_date_activity_total = 0
        self.app_version_1_5_date_activity_total = 0
        self.app_version_1_6_date_activity_total = 0

        self.activity_version_total_entries = 0
        self.activity_version_total_active_count = 0
        self.activity_version_total_inactive_count = 0

        self.user_active_days_list_percentage = []
        self.user_active_days_list = [0] * self.number_of_days
        self.user_not_active_days_list = [0] * self.number_of_days
        self.user_ltd_entries_list = [0] * self.number_of_days
        self.user_retention_list = [0] * self.number_of_days
        self.user_churn_list = [0] * self.number_of_days
        self.monthly_active_user_list = []
        self.number_of_user_active = []
        self.weekly_active_users = []
        self.monthly_active_users = []
        self.month_names = ['Jan, 2017', 'Feb, 2017', 'Mar, 2017', 'Apr, 2017', 'May, 2017', 'Jun, 2017']
        self.months = ['2017-01-31', '2017-02-28', '2017-03-31', '2017-04-30', '2017-05-31', '2017-06-16']
        self.app_retention_cohort_by_7_day_analysis_dict = {}
        self.app_retention_cohort_by_30_day_analysis_dict = {}

    # initialize dataset variables
    def init_process_dataset(self):
        print('Initializing dataset values & loading ...')
        self.dataset['DATE_JOINED'] = pd.to_datetime(self.dataset['DATE_JOINED'], format="%m/%d/%Y")
        self.dataset['DATE_JOINED'] = self.dataset['DATE_JOINED'].dt.date
        user_registration_date_arr = self.dataset['DATE_JOINED'].tolist()

        self.dataset['DATE_ACTIVITY'] = pd.to_datetime(self.dataset['DATE_ACTIVITY'], format="%m/%d/%Y")
        self.dataset['DATE_ACTIVITY'] = self.dataset['DATE_ACTIVITY'].dt.date
        self.user_date_activity = self.dataset['DATE_ACTIVITY'].tolist()

        self.all_user_ids_list = self.dataset.USER_ID.tolist()
        self.user_id_dist_arr = self.dataset.USER_ID.unique()
        self.registered_user_total = len(self.user_id_dist_arr)
        self.all_user_ids_list = list(map(int, self.all_user_ids_list))

        user_ltd_arr = self.dataset.USER_LTD.tolist()
        self.user_ltd_dist_arr = self.dataset.USER_LTD.unique()
        self.user_ltd_dist_arr = list(map(int, self.user_ltd_dist_arr))
        #print(self.user_ltd_dist_arr)
        user_ltd_arr = list(map(int, user_ltd_arr))

        version_reg_arr = self.dataset.VERSION_DATE_JOINED.unique()
        #print(version_reg_arr)
        version_update_arr = self.dataset.VERSION_DATE_ACTIVITY.unique()
        self.user_activity_arr = self.dataset.USER_ACTIVITY.tolist()
        #self.user_activity_arr = list(map(int, self.user_activity_arr))

    # Summarizing a data set in a few expressive diagrams or key figures is an important ability.
    # Chose 1-3 own diagrams or key figures which, in your opinion, adequately describe the data set
    # For each of the above: Why is this diagram/figure generally a good summary?
    # What does it reveal to you about our data set in particular?
    def process_dataset_for_general_summary_1(self):
        print('Processing calculation on dataset for general summary information ...\n')
        # grouping data monthly
        for mon in range(len(self.months)):
            stop_date = self.months[mon]
            stop = datetime.strptime(stop_date, "%Y-%m-%d")
            user = []
            v13c = 0
            v14c = 0
            v141c = 0
            v15c = 0
            v16c = 0
            uact_count = 0
            total = 0
            monthly_user = []
            print('Month - ', stop.month)
            for index, row in self.dataset.iterrows():
                # get no of users register per month
                if row['DATE_JOINED'].month == stop.month:
                    if int(row['USER_ID']) not in user:
                        user.append(int(row['USER_ID']))

                # total no. of active/inactive action in each month.
                if row['DATE_ACTIVITY'].month == stop.month:
                    total += 1

                # count monthly active activities (active =1) number of different app versions
                if row['DATE_ACTIVITY'].month == stop.month and row['USER_ACTIVITY'] == 1:
                    if int(row['USER_ID']) not in monthly_user:
                        monthly_user.append(int(row['USER_ID']))
                    if row['VERSION_DATE_ACTIVITY'] == self.version_arr[0]:
                        v13c += 1
                    if row['VERSION_DATE_ACTIVITY'] == self.version_arr[1]:
                        v14c += 1
                    if row['VERSION_DATE_ACTIVITY'] == self.version_arr[2]:
                        v141c += 1
                    if row['VERSION_DATE_ACTIVITY'] == self.version_arr[3]:
                        v15c += 1
                    if row['VERSION_DATE_ACTIVITY'] == self.version_arr[4]:
                        v16c += 1
                    # get number of user active activity per month.
                    uact_count += 1

            self.number_of_users_register_per_month.append(len(user))
            self.monthly_activity_app_version_1_3.append(v13c)
            self.monthly_activity_app_version_1_4.append(v14c)
            self.monthly_activity_app_version_1_4_1.append(v141c)
            self.monthly_activity_app_version_1_5.append(v15c)
            self.monthly_activity_app_version_1_6.append(v16c)
            self.number_of_active_action_per_month.append(uact_count)
            self.number_of_inactive_action_per_month.append(total - uact_count)
            self.total_entries_per_month.append(total)
            self.monthly_active_user_list.append(len(monthly_user))

            self.app_version_1_3_date_activity_total += v13c
            self.app_version_1_4_date_activity_total += v14c
            self.app_version_1_4_1_date_activity_total += v141c
            self.app_version_1_5_date_activity_total += v15c
            self.app_version_1_6_date_activity_total += v16c

            self.activity_version_total_active_count += uact_count
            self.activity_version_total_inactive_count += (total - uact_count)
            self.activity_version_total_entries += total

        print('\nNumber of User Registered Monthly - ', self.number_of_users_register_per_month)
        print('Monthly User Activity AppV1.3 - ', self.monthly_activity_app_version_1_3)
        print('Monthly User Activity AppV1.4 - ', self.monthly_activity_app_version_1_4)
        print('Monthly User Activity AppV1.4.1 - ', self.monthly_activity_app_version_1_4_1)
        print('Monthly User Activity AppV1.5 - ', self.monthly_activity_app_version_1_5)
        print('Monthly User Activity AppV1.6 - ', self.monthly_activity_app_version_1_6)

        print('\nNumber of active action per month - ', self.number_of_active_action_per_month)
        print('number of inactive action per month - ', self.number_of_inactive_action_per_month)
        #print('total entries per month> ', self.total_entries_per_month)

        print('\nDate Activity version total entries - ', self.activity_version_total_entries)
        print('Date Activity version total active count - ', self.activity_version_total_active_count)
        print('Date Activity version total inactive count - ', self.activity_version_total_inactive_count)
        print('Monthly active user list - ', self.monthly_active_user_list)

        # calculation for number of users/number of active activities days
        # User active activities on the day basis in the entire dataset
        for id in range(len(self.user_id_dist_arr)):
            c = 0
            for i in range(len(self.all_user_ids_list)):
                if self.user_id_dist_arr[id] == self.all_user_ids_list[i]:
                    c += self.user_activity_arr[i]
                    if i+1 < len(self.all_user_ids_list) and self.all_user_ids_list[i] != self.all_user_ids_list[i+1]:
                        break
            self.number_of_user_active.append(c)
        #print('Number of total activity days count of users - ', self.number_of_user_active)

    def process_dataset_for_general_summary_2(self):
        print('\nProcessing activity calculation for general summary information ...')
        v13ac = 0
        v14ac = 0
        v141ac = 0
        v15ac = 0
        v16ac = 0
        v13inac = 0
        v14inac = 0
        v141inac = 0
        v15inac = 0
        v16inac = 0

        self.no_of_user_registered_by_version = []
        reg_user = []
        v13reg_c = 0
        v14reg_c = 0
        v141reg_c = 0
        v15reg_c = 0
        v16reg_c = 0
        for index, row in self.dataset.iterrows():
            if int(row['USER_ID']) not in reg_user:
                reg_user.append(int(row['USER_ID']))
                if row['VERSION_DATE_JOINED'] == self.version_arr[0]:
                    v13reg_c += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[1]:
                    v14reg_c += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[2]:
                    v141reg_c += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[3]:
                    v15reg_c += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[4]:
                    v16reg_c += 1

            ## not using below code
            if row['USER_ACTIVITY'] == 1:
                if row['VERSION_DATE_JOINED'] == self.version_arr[0]:
                    v13ac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[1]:
                    v14ac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[2]:
                    v141ac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[3]:
                    v15ac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[4]:
                    v16ac += 1
            else:
                if row['VERSION_DATE_JOINED'] == self.version_arr[0]:
                    v13inac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[1]:
                    v14inac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[2]:
                    v141inac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[3]:
                    v15inac += 1
                if row['VERSION_DATE_JOINED'] == self.version_arr[4]:
                    v16inac += 1
            ## end of not using code.

        self.no_of_user_registered_by_version =[v13reg_c, v14reg_c, v141reg_c, v15reg_c, v16reg_c]
        print('No of user registered by app versions - ', self.no_of_user_registered_by_version)

        sum_v13_reg = v13ac + v13inac
        sum_v14_reg = v14ac + v14inac
        sum_v141_reg = v141ac + v141inac
        sum_v15_reg = v15ac + v15inac
        sum_v16_reg = v16ac + v16inac
        total_version_register_usage_count = [sum_v13_reg, sum_v14_reg, sum_v141_reg, sum_v15_reg, sum_v16_reg]
        active_version_register_usage_count = [v13ac, v14ac, v141ac, v15ac, v16ac]
        inactive_version_register_usage_count = [v13inac, v14inac, v141inac, v15inac, v16inac]
        percentage_active_usage_count_on_reg_ver = []
        precentage_retention_on_reg_ver = [] # count inactive usage on version register/total version register

        for v in range(len(total_version_register_usage_count)):
            percentage_active_usage_count_on_reg_ver.append((active_version_register_usage_count[v]/total_version_register_usage_count[v])*100)
            precentage_retention_on_reg_ver.append((inactive_version_register_usage_count[v]/total_version_register_usage_count[v])*100)

        # activity analysis using VERSION_DATE_ACTIVITY column.
        v13dac = 0
        v14dac = 0
        v141dac = 0
        v15dac = 0
        v16dac = 0
        v13indac = 0
        v14indac = 0
        v141indac = 0
        v15indac = 0
        v16indac = 0
        for index, row in self.dataset.iterrows():
            if row['USER_ACTIVITY'] == 1:
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[0]:
                    v13dac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[1]:
                    v14dac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[2]:
                    v141dac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[3]:
                    v15dac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[4]:
                    v16dac += 1
            else:
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[0]:
                    v13indac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[1]:
                    v14indac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[2]:
                    v141indac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[3]:
                    v15indac += 1
                if row['VERSION_DATE_ACTIVITY'] == self.version_arr[4]:
                    v16indac += 1

        sum_v13_act_date = v13dac + v13indac
        sum_v14_act_date = v14dac + v14indac
        sum_v141_act_date = v141dac + v141indac
        sum_v15_act_date = v15dac + v15indac
        sum_v16_act_date = v16dac + v16indac
        self.activity_version_total_entries_count = [sum_v13_act_date, sum_v14_act_date, sum_v141_act_date, sum_v15_act_date, sum_v16_act_date]
        self.activity_version_user_active_count = [v13dac, v14dac, v141dac, v15dac, v16dac]
        self.activity_version_user_not_active_count = [v13indac, v14indac, v141indac, v15indac, v16indac]

        #print('activity_version_total_entries_count> ', self.activity_version_total_entries_count)
        #print('activity_version_user_active_count> ', self.activity_version_user_active_count)
        #print('activity_version_user_not_active_count> ', self.activity_version_user_not_active_count)

        for v in range(len(self.activity_version_total_entries_count)):
            self.activity_version_user_active_percentage.append(round((self.activity_version_user_active_count[v]/self.activity_version_total_entries_count[v])*100, 2))
            self.activity_version_user_not_active_percentage.append(round((self.activity_version_user_not_active_count[v]/self.activity_version_total_entries_count[v])*100, 2))

        print('Percentage of user active based on version date ativity - ', self.activity_version_user_active_percentage)
        print('Percentage of user not active based on version date ativity -  ', self.activity_version_user_not_active_percentage)

    def process_dataset_for_weekly_retention_visualization(self):
        print('\nProcessing 7 days retention calculation based on user registration ...')
        # user retention calculation for 7 days
        start_w = date(2017, 1, 13)
        week = timedelta(days=7)
        user_weekly_retention_dict = {}
        for wk in range(self.number_of_weeks):
            ulist_w = []
            range_date_w = start_w + week
            print('Week: ' + str(wk) + ' Range Date: ' + str(start_w) + ' ~ ' + str(range_date_w))
            if wk == 0:
                for index, row in self.dataset.iterrows():
                    if row['DATE_JOINED'] >= start_w and row['DATE_JOINED'] < range_date_w:
                        if row['USER_ID'] not in ulist_w:
                            ulist_w.append(int(row['USER_ID']))
            else:
                for index, row in self.dataset.iterrows():
                    if row['DATE_ACTIVITY'] >= start_w and row['DATE_ACTIVITY'] < range_date_w:
                        if row['USER_ACTIVITY'] == 1:
                            if row['USER_ID'] not in ulist_w:
                                ulist_w.append(int(row['USER_ID']))
            #list_w = list(set(ulist_w))
            #print(len(ulist_w))
            user_weekly_retention_dict[wk] = ulist_w
            #print(user_weekly_retention_dict[wk])
            start_w = range_date_w # for next iteration
        #print('user_weekly_retention_dict>', user_weekly_retention_dict)
        for key, value in user_weekly_retention_dict.items():
            retain_user = []
            user_arr = value
            #print('user_arr values>', user_arr)
            retain_user.append(len(user_arr))
            #print('user_arr> ', len(user_arr))
            for i in range(key + 1, len(user_weekly_retention_dict)):
                c = 0
                next_user_arr = user_weekly_retention_dict[i]
                for x in range(len(user_arr)):
                    if user_arr[x] in next_user_arr:
                        c += 1
                retain_user.append(round((c/retain_user[0])*100, 2))
            retain_user[0] = (retain_user[0]/retain_user[0]) * 100
            if len(retain_user) < len(user_weekly_retention_dict):
                c = len(retain_user)
                for i in range(c, len(user_weekly_retention_dict)):
                    retain_user.append(0)
            #print(len(retain_user))
            self.app_retention_cohort_by_7_day_analysis_dict[key] = retain_user

    def process_dataset_for_30days_retention_visualization(self):
        print('\nProcessing 30 days retention calculation based on user registration ...')
        # user retention calculation for 30 days
        start_m = date(2017, 1, 13)
        add_30 = timedelta(days=30)
        user_monthly_retention_dict = {}
        for mn in range(self.number_of_months):
            ulist_m = []
            range_date_m = start_m + add_30
            print('30 days Interval: ' + str(mn) + ' Range Date: ' + str(start_m) + ' ~ ' + str(range_date_m))
            if mn == 0:
                for index, row in self.dataset.iterrows():
                    if row['DATE_JOINED'] >= start_m and row['DATE_JOINED'] < range_date_m:
                        if row['USER_ID'] not in ulist_m:
                            ulist_m.append(int(row['USER_ID']))
            else:
                for index, row in self.dataset.iterrows():
                    if row['DATE_ACTIVITY'] >= start_m and row['DATE_ACTIVITY'] < range_date_m:
                        if row['USER_ACTIVITY'] == 1:
                            if row['USER_ID'] not in ulist_m:
                                ulist_m.append(int(row['USER_ID']))
            #print(len(ulist_m))
            user_monthly_retention_dict[mn] = ulist_m
            start_m = range_date_m # for next iteration
        #print('user_monthly_retention_dict>', user_monthly_retention_dict)
        for key, value in user_monthly_retention_dict.items():
            retain_user = []
            user_arr = value
            #print('user_arr values>', user_arr)
            retain_user.append(len(user_arr))
            #print('user_arr> ', len(user_arr))
            for i in range(key + 1, len(user_monthly_retention_dict)):
                c = 0
                next_user_arr = user_monthly_retention_dict[i]
                for x in range(len(user_arr)):
                    if user_arr[x] in next_user_arr:
                        c += 1
                retain_user.append(round((c/retain_user[0]) * 100, 2))
            retain_user[0] = (retain_user[0]/retain_user[0]) * 100
            if len(retain_user) < len(user_monthly_retention_dict):
                c = len(retain_user)
                for i in range(c, len(user_monthly_retention_dict)):
                    retain_user.append(0)
            #print(retain_user)
            self.app_retention_cohort_by_30_day_analysis_dict[key] = retain_user

    # Daily Active User(DAU) calculation for retention
    def process_dataset_for_n_day_retention(self):
        print('\nProcessing N day rentention calculation based on Daily Active User(DAU)...')
        #print(len(self.user_active_days_list))
        for index, row in self.dataset.iterrows():
            c = int(row['USER_LTD'])
            self.user_ltd_entries_list[c] += 1
            if row['USER_ACTIVITY'] == 1:
                #c = int(row['USER_LTD'])
                self.user_active_days_list[c] += 1
            else:
                self.user_not_active_days_list[c] += 1
        #print('ActiveUserNumOnDaybasis> ' , self.user_active_days_list)
        #print('InactiveUserNumOnDaybasis> ', self.user_not_active_days_list)
        #print('user_ltd_entries_list> ', self.user_ltd_entries_list)

        # No. of days retention measures how many of the users come back to the app on a particular day.
        self.user_retention_list = self.user_active_days_list.copy()
        # Day 0 - user installed/register to the app (so active+inactive values are added to retention list)
        self.user_retention_list[0] = self.user_active_days_list[0] + self.user_not_active_days_list[0]
        #print('user_retention_list>', self.user_retention_list)

        self.user_churn_list = self.user_not_active_days_list.copy()
        # Day 0 - user installed/register to the app (so active+inactive values are added to retention/churn list)
        self.user_churn_list[0] = self.user_active_days_list[0] + self.user_not_active_days_list[0]
        #print('user_churn_list>', self.user_churn_list)

        for r in range(len(self.user_active_days_list)):
            if r%7 == 0:
                self.weekly_active_users.append(self.user_active_days_list[r])
            if r%30 == 0:
                self.monthly_active_users.append(self.user_active_days_list[r])
        print('Weekly active users - ', self.weekly_active_users)
        #print(len(self.weekly_active_users))
        print('Monthly active users - ', self.monthly_active_users)
        #print(len(self.monthly_active_users))

        # users are still active on day 1, 7, 30, 90 (respectively)
        for a in range(len(self.user_active_days_list)):
            self.user_active_days_list_percentage.append((self.user_retention_list[a]/len(self.user_id_dist_arr)) * 100)
        #print('self.user_active_days_list_percentage> ',self.user_active_days_list_percentage)

    # dataset summary diagram - 1
    # how many users are registered, what version's are used when a user is active?
    # Total active/inactive count on the entire dataset
    def dataset_summary_diagram_1(self):
        print('\nPlotting MyTherapy App summary info 1: Monthwise Bar Chart ...')
        fig, ax = plt.subplots()
        fig.canvas.set_window_title('MyTherapy App - Monthwise Bar Chart')
        ind = np.arange(len([1, 2, 3, 4, 5, 6]))
        width = 0.11
        bar1 = ax.bar(ind, self.number_of_users_register_per_month, width, color='green')
        bar2 = ax.bar(ind + 1 * width, self.monthly_activity_app_version_1_3, width, color='cyan')
        bar3 = ax.bar(ind + 2 * width, self.monthly_activity_app_version_1_4, width, color='gray')
        bar4 = ax.bar(ind + 3 * width, self.monthly_activity_app_version_1_4_1, width, color='olive')
        bar5 = ax.bar(ind + 4 * width, self.monthly_activity_app_version_1_5, width, color='silver')
        bar6 = ax.bar(ind + 5 * width, self.monthly_activity_app_version_1_6, width, color='magenta')
        bar7 = ax.bar(ind + 6 * width, self.number_of_active_action_per_month, width, color='blue')
        bar8 = ax.bar(ind + 7 * width, self.number_of_inactive_action_per_month, width, color='red')

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Numbers/Counts')
        ax.set_title('MyTherapy App - Monthly summary of users activities and app version usage from Jan~Jun, Y2017\n T = Total')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(('Jan, 2017', 'Feb, 2017', 'Mar, 2017', 'Apr, 2017', 'May, 2017', 'Jun, 2017'))
        ax.legend((bar1[0], bar2[0], bar3[0], bar4[0], bar5[0], bar6[0], bar7[0], bar8[0]),
                  ('Registered User, T-' + str(len(self.user_id_dist_arr)),
                   'App V1.3 Activity, T-' + str(self.app_version_1_3_date_activity_total),
                   'App V1.4 Activity, T-' + str(self.app_version_1_4_date_activity_total),
                   'App V1.4.1 Activity, T-' + str(self.app_version_1_4_1_date_activity_total),
                   'App V1.5 Activity, T-' + str(self.app_version_1_5_date_activity_total),
                   'App V1.6 Activity, T-' + str(self.app_version_1_6_date_activity_total),
                   'User Active Action, T-' + str(self.activity_version_total_active_count),
                   'User Inactive Action, T-' + str(self.activity_version_total_inactive_count)))

        rects = [bar1, bar2, bar3, bar4, bar5, bar6, bar7, bar8]
        for r in range(len(rects)):
            for rect in rects[r]:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.01*height, '%d' % int(height), fontsize=7, ha='center', va='bottom')
        plt.savefig('summary-bar-1.png')
        plt.show()

    # dataset summary diagram - 2
    # App versions plotting
    def dataset_summary_diagram_2(self):
        print('\nPlotting MyTherapy App summary info 2: App Versions Usage Pie Chart ...')
        labels_arr1 = []
        labels_arr2 = []
        labels_arr3 = []
        labels_arr4 = []
        for i in range(len(self.version_arr)):
            labels_arr1.append(str(self.version_arr[i])+'('+ str(self.no_of_user_registered_by_version[i]) + ')')
            labels_arr2.append(str(self.version_arr[i])+'('+ str(self.activity_version_total_entries_count[i]) + ')')
            labels_arr3.append(str(self.version_arr[i])+'('+ str(self.activity_version_user_active_count[i]) + ')')
            labels_arr4.append(str(self.version_arr[i])+'('+ str(self.activity_version_user_not_active_count[i]) + ')')

        # Make square figures and axes
        explode1 = (0, 0, 0, 0.1, 0)
        explode2 = (0, 0, 0, 0, 0.1)
        explode3 = (0, 0, 0, 0, 0.1)

        the_grid = GridSpec(2, 2)
        plt.subplot(the_grid[0, 0], aspect=1)
        plt.pie(self.no_of_user_registered_by_version, explode=explode1, labels=labels_arr1, autopct='%1.1f%%', shadow=True)
        plt.title('% of users ('+str(len(self.user_id_dist_arr)) + ') registered - MyTherapy App versions')

        plt.subplot(the_grid[0, 1], aspect=1)
        plt.pie(self.activity_version_total_entries_count, explode=explode2, labels=labels_arr2, autopct='%.0f%%', shadow=True, radius=0.5)
        plt.title('% of total entries ('+ str(self.activity_version_total_entries) + ') - MyTherapy App versions')

        plt.subplot(the_grid[1, 0], aspect=1)
        plt.pie(self.activity_version_user_active_count, explode=explode2, labels=labels_arr3, autopct='%.0f%%', shadow=True)
        plt.title('% of active entries ('+ str(self.activity_version_total_active_count)  + ') - MyTherapy App versions')

        plt.subplot(the_grid[1, 1], aspect=1)
        plt.pie(self.activity_version_user_not_active_count, explode=explode3, labels=labels_arr4, autopct='%.0f%%', shadow=True, radius=0.5)
        plt.title('% of inactive entries ('+ str(self.activity_version_total_inactive_count)  + ') - MyTherapy App versions')
        plt.savefig('summary-pie-2.png')
        plt.show()

    # dataset summary diagram - 3
    # User active activities on the day basis in the entire dataset / user activity pattern.
    def dataset_summary_diagram_3(self):
        print('\nPlotting MyTherapy App summary info 3: Users active activities on the daily basis ...')
        dist_activities_list = np.asarray(self.number_of_user_active)
        act_unq, act_unq_cnt = np.unique(dist_activities_list, return_counts=True)
        # histogram 1
        fig, ax = plt.subplots()
        fig.canvas.set_window_title('No. of total activity days of users')
        indices = np.arange(len(act_unq))
        width = 0.65
        rects = plt.bar(indices, act_unq_cnt, width, color='green')
        plt.xlabel("No. of active days (Active = 1)", fontsize=12)
        plt.ylabel("No. of total users", fontsize=12)
        plt.xticks(indices, act_unq, rotation='vertical')
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2., 1.05*height, '%d' % int(height), fontsize=10, ha='center', va='bottom')
        plt.savefig('summary-bar-3.png')
        plt.show()

    # dataset summary diagram - 4
    # App version plotting
    def dataset_summary_diagram_4(self):
        fig, ax = plt.subplots()
        fig.canvas.set_window_title('MyTherapy App - Versions Activity Bar Chart')
        ind = np.arange(len([1, 2, 3, 4, 5]))
        width = 0.25
        bar1 = ax.bar(ind, self.activity_version_user_active_percentage, width, color='green')
        bar2 = ax.bar(ind + width, self.activity_version_user_not_active_percentage, width, color='red')

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Percentage (%)')
        ax.set_title('MyTherapy App Versions Activity Bar Chart for the Y2017\n T = Total')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(('Version 1.3', 'Version 1.4', 'Version 1.4.1', 'Version 1.5', 'Version 1.6'))
        ax.legend((bar1[0], bar2[0]),
                  ('User Active % ' + str(len(self.activity_version_user_active_count)),
                   'User Not Active % ' + str(self.activity_version_user_not_active_count)))
        rects = [bar1, bar2]
        for r in range(len(rects)):
            for rect in rects[r]:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.01*height, '%d' % int(height), fontsize=12, ha='center', va='bottom')
        plt.show()

    # Retention diagram - 0 > retention
    def dataset_weekly_retention_visualization(self):
        print('\nPlotting MyTherapy App 7 days period retention visualization ...')
        cols = list(self.app_retention_cohort_by_7_day_analysis_dict.keys())
        ind = ['W_0', 'W_1', 'W_2', 'W_3', 'W_4', 'W_5', 'W_6', 'W_7', 'W_8', 'W_9', 'W_10', 'W_11',
               'W_12', 'W_13', 'W_14', 'W_15', 'W_16', 'W_17', 'W_18', 'W_19', 'W_20', 'W_21']
        columns = ['2017-01-20', '2017-01-27', '2017-02-03', '2017-02-10', '2017-02-17', '2017-02-24', '2017-03-03', '2017-03-10', '2017-03-17', '2017-03-24', '2017-03-31', '2017-04-07',
                   '2017-04-14', '2017-04-21', '2017-04-28', '2017-05-05', '2017-05-12', '2017-05-19', '2017-05-26', '2017-06-02', '2017-06-09', '2017-06-16']
        df = pd.DataFrame(self.app_retention_cohort_by_7_day_analysis_dict, index=ind)
        df.columns = columns
        #print(df.shape)
        df = df.transpose()
        sns.set(font_scale=1.1)
        plt.title('Cohorts: Weekly User Retention from Jan 13, 2017 ~ Jun 16, 2017')
        sns.heatmap(df, cmap="Blues", annot=True, fmt='.1f', annot_kws={"size": 8})
        plt.savefig('weekly-retention.png' , dpi=600)
        plt.show()

    # Retention diagram - 0 > retention
    def dataset_30days_retention_visualization(self):
        print('\nPlotting MyTherapy App 30 days period retention visualization ...')
        cols = list(self.app_retention_cohort_by_30_day_analysis_dict.keys())
        ind = ['Day_30', 'Day_60', 'Day_90', 'Day_120', 'Day_150']
        columns = ['30 Days', '60 Days', '90 Days', '120 Days', '150 Days']
        df = pd.DataFrame(self.app_retention_cohort_by_30_day_analysis_dict, index=ind)
        df.columns = columns
        df = df.transpose()
        sns.set(font_scale=1.2)
        plt.title('Cohorts: 30 Days User Retention from Jan 13, 2017 ~ Jun 16, 2017')
        sns.heatmap(df, cmap="Blues", annot=True, fmt='.1f', annot_kws={"size": 10})
        plt.savefig('30days-retention.png' , dpi=600)
        plt.show()

    # Retention diagram - 1 > N day retention
    def dataset_retention_diagram_1(self):
        print('\nPlotting N-Day Retention - percentange of daily active users retention visualization ...')
        days = []
        xticks = []
        yticks = []
        for i in range(155):
            days.append(i)
            if i%5 == 0:
                xticks.append(i)
        for y in range(100):
            if i%5 == 0:
                yticks.append(y)
        plt.plot(days, self.user_active_days_list_percentage, marker='o', markerfacecolor='blue', markersize=3, color='maroon')
        plt.xlabel('No. of Days')
        plt.ylabel('% of Users Retention')
        plt.xticks(xticks)
        plt.yticks(yticks)
        plt.title('MyTherapy App - ' + str(self.number_of_days) + ' Days of Retention')
        plt.savefig('retention-n-day-line-1.png')
        plt.show()

    # Retention diagram - 2 > Daily/7 days, 30 days active Users (DAU/WAU/MAU)
    def dataset_retention_diagram_2(self):
        print('\nPlotting 1/7/30 days Retention - number of 1/7/30 days activity of users retention visualization ...')
        weekly_x = []
        monthly_x = []
        xticks = []
        for a in range(len(self.weekly_active_users)):
            weekly_x.append(a*7)
        for b in range(len(self.monthly_active_users)):
            monthly_x.append(b*30)

        for i in range(155):
            if i%5 == 0:
                xticks.append(i)
        plt.plot(self.user_ltd_dist_arr, self.user_active_days_list, label='daily active users', marker='o', markerfacecolor='blue', markersize=2, color='black')
        plt.plot(weekly_x, self.weekly_active_users, label='weekly active users', marker='x', markerfacecolor='olive', markersize=2, color='red')
        plt.plot(monthly_x, self.monthly_active_users, label='monthly active users', linewidth=2, linestyle='dashed', color='green')
        plt.xlabel('No. Of Days')
        plt.ylabel('No. of Active User')
        plt.xticks(xticks)
        plt.legend(framealpha=1, frameon=True)
        plt.savefig('retention-dau-wau-mau-lines-2.png')
        plt.show()

    # Retention diagram - 3 > What percentage of users are still active on day 1, 7, 30, 90 (respectively)?
    def dataset_retention_diagram_3(self):
        print('\nPlotting percentage of users are still active on day 1, 7, 30, 90 visualization ...')
        fig, ax = plt.subplots()
        fig.canvas.set_window_title('User Activity (Active=1) Percentage')
        input_days = [1, 7, 30, 90]
        output = []
        ind = np.arange(len([1, 2, 3, 4]))
        width = 0.35
        for p in range(len(input_days)):
            output.append(self.user_active_days_list_percentage[input_days[p]])

        rects = ax.bar(ind, output, width, color='green', align='edge')
        ax.set_xlabel('No. of Days')
        ax.set_ylabel('Percentage (%)')
        ax.set_title('% of users active on day 1, 7, 30, 90 (Jan~Jun, Y2017)')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(('1 Day', '7 Days' , '30 Days', '90 Days'))
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height, '%d' % int(height), fontsize=10, ha='center', va='bottom')
        plt.savefig('retention-percentage-user-active-bar-3.png')
        plt.show()

    def dataset_user_activity_trend_diagram_1(self):
        print('\nPlotting number of users activity pattern visualization ...')
        xticks = []
        for i in range(155):
            if i%5 == 0:
                xticks.append(i)
        plt.plot(self.user_ltd_dist_arr, self.user_active_days_list, label='daily active users', marker='o', markerfacecolor='blue', markersize=2, color='black')
        plt.xlabel('No. Of Days')
        plt.ylabel('No. of Active User')
        plt.xticks(xticks)
        plt.title('MyTherapy App - Active days pattern with regards to users count.')
        plt.savefig('activity-pattern-line-1.png')
        plt.show()

    # Monthly Active Users(MAU)
    def dataset_user_activity_trend_diagram_2(self):
        print('\nPlotting monthly active users visualization ...')
        months_id = [1,2,3,4,5,6]
        plt.plot(months_id, self.monthly_active_user_list, marker='o', markerfacecolor='blue', markersize=8, color='black')
        plt.xlabel('Month Number')
        plt.ylabel('Monthly Active User Count')
        plt.title('MyTherapy App - Monthly Active User')
        plt.savefig('activity-pattern-mau-line-2.png')
        plt.show()
