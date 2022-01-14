import datetime
import logging
import math
import os
import tkinter as tk
from collections import OrderedDict
from tkinter import *
from tkinter import ttk

import numpy as np
import pandas as pd
import stravalib.exc
from stravalib import unithelper
from stravalib.client import Client


class BillExcept(Exception):
	def __init__(self, message=None):
		self.message = message


def get_client(code):
	client_id = 34049
	client_secret = '2265a983040000b3b865a0fc333f41cd701dcb5f'
	
	client = Client()
	client.authorization_url(34049, 'http://localhost:8080', scope='activity:read_all')
	token_response = client.exchange_code_for_token(client_id, client_secret, code)
	client.access_token = token_response['access_token']
	client.refresh_token = token_response['refresh_token']
	return client


def get_activities(client, after=datetime.date.today() - datetime.timedelta(days=7), before=datetime.date.today()):
	activities = client.get_activities(after=after, before=before)
	try:
		activities = list(activities)
		activities = activities[::-1]  # reverse order so they're chronological
		return activities
	except stravalib.exc.Fault:
		return None


def data_input_popup(date, shoes, mileage):
	# Creating tkinter window
	window = tk.Tk()
	window.geometry('350x350')
	
	ttk.Label(window,
	          text=f'Enter data for {mileage:.2f} mile run on\n{date.strftime("%A, %b %d %Y")}',
	          font=("Times New Roman", 10)).grid(
		column=0, row=10, padx=10, pady=25)
	sho = tk.StringVar(window, 'catchall')
	ttk.Label(window, text="Shoes Worn :", font=("Times New Roman", 10)).grid(column=0, row=15, padx=10, pady=5)
	shoe_menu = ttk.OptionMenu(window, sho, '', *shoes)
	shoe_menu.grid(column=1, row=15)
	
	ttk.Label(window, text='Liters Consumed :', font=("Times New Roman", 10)).grid(column=0, row=16, padx=10, pady=5)
	liter_num = tk.DoubleVar(value=0.)
	liter_entry = ttk.Entry(window, textvariable=liter_num)
	liter_entry.grid(column=1, row=16)
	
	ttk.Label(window, text='Calories Consumed :', font=("Times New Roman", 10)).grid(column=0, row=17, padx=10, pady=5)
	cal_num = tk.DoubleVar(value=0.)
	calnum_entry = ttk.Entry(window, textvariable=cal_num)
	calnum_entry.grid(column=1, row=17)
	
	ttk.Label(window, text='Calorie Description :', font=("Times New Roman", 10)).grid(column=0, row=18, padx=10,
	                                                                                   pady=5)
	cal_desc = tk.StringVar()
	caldesc_entry = ttk.Entry(window, textvariable=cal_desc)
	caldesc_entry.grid(column=1, row=18)
	
	ttk.Label(window, text='Start Weight (lb) :', font=("Times New Roman", 10)).grid(column=0, row=19, padx=10, pady=5)
	# strtw_num = tk.DoubleVar(value=math.nan)
	strtw_entry = ttk.Entry(window)
	strtw_entry.grid(column=1, row=19)
	
	ttk.Label(window, text='End Weight (lb) :', font=("Times New Roman", 10)).grid(column=0, row=20, padx=10, pady=5)
	# endw_num = tk.DoubleVar(value=math.nan)
	endw_entry = ttk.Entry(window)
	endw_entry.grid(column=1, row=20)
	
	def close_window():
		global shoes_worn
		global liters_consumed
		global start_weight_lb
		global end_weight_lb
		global calories_consumed
		global calorie_description
		shoes_worn = sho.get()
		if liter_entry.get() == '':
			liters_consumed = np.nan
		else:
			liters_consumed = float(liter_entry.get())
		if calnum_entry.get() == '':
			calories_consumed = np.nan
		else:
			calories_consumed = float(calnum_entry.get())
		if caldesc_entry.get() == '':
			calorie_description = np.nan
		else:
			calorie_description = caldesc_entry.get()
		if strtw_entry.get() == '':
			start_weight_lb = np.nan
		else:
			start_weight_lb = float(strtw_entry.get())
		if endw_entry.get() == '':
			end_weight_lb = np.nan
		else:
			end_weight_lb = float(endw_entry.get())
		
		window.destroy()
	
	button = Button(window, text='Ok', command=close_window)
	button.grid(row=25, column=1)
	
	window.mainloop()
	
	return shoes_worn, liters_consumed, start_weight_lb, end_weight_lb, calories_consumed, calorie_description


def get_past_races(racekeys=None):
	races = OrderedDict({})
	# trail:
	races.update({'Superior 50k 2018': datetime.datetime(2018, 5, 19),
	              'Driftless 50k 2018': datetime.datetime(2018, 9, 29),
	              'Superior 50k 2019': datetime.datetime(2019, 5, 18),
	              'Batona (virtual) 33M 2020': datetime.datetime(2020, 10, 10),
	              'Dirty German (virtual) 50k 2020': datetime.datetime(2020, 10, 31),
	              'Stone Mill 50M 2020': datetime.datetime(2020, 11, 14)})
	# road:
	races.update({'TC Marathon 2014': datetime.datetime(2014, 10, 5),
	              'Madison Marathon 2014': datetime.datetime(2014, 11, 9),
	              'TC Marathon 2015': datetime.datetime(2015, 10, 4)})
	# past 18 weeks
	races.update({'Past 18 weeks': datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)})
	
	# remove races not in racekeys
	if racekeys is not None:
		[races.pop(k) for k in list(races.keys()) if k not in racekeys]
	# order chronologically
	races = {k: v for k, v in sorted(races.items(), key=lambda item: item[1])}
	return races


def update_data_file(code, races2analyze=None):
	client = get_client(code)
	
	races = get_past_races(racekeys=races2analyze)
	if 'Past 18 weeks' in races2analyze:
		races.update({'Past 18 weeks': datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)})
	aft = min(races.values()) - datetime.timedelta(weeks=18)  # 18 weeks before earliest race date
	bef = max(races.values()) + datetime.timedelta(days=1)
	activities = get_activities(client, aft, bef)
	
	if os.path.isdir('C:/Users/Owner/Dropbox/'):
		fn = 'C:/Users/Owner/Dropbox/training_data.xlsx'
	elif os.path.isdir('C:/Users/wcapecch/Dropbox/'):
		fn = 'C:/Users/wcapecch/Dropbox/training_data.xlsx'
	else:
		raise BillExcept('cannot locate training data file')
	
	sho = pd.read_excel(fn, sheet_name='shoes', engine='openpyxl')
	shoe_options = sho['shoe_options'].values
	df = pd.read_excel(fn, sheet_name='data', engine='openpyxl')
	runid_arr = list(df['runid'].values)
	date_arr = list(df['Date'].values)
	type_arr = list(df['Type'].values)
	cals_arr = list(df['Calories'].values)
	dist_arr = list(df['Dist (mi)'].values)
	pace_arr = list(df['Pace (min/mi)'].values)
	split_shift_arr = list(df['Split Shift (min/mile)'].values)  # 2nd half avg - 1st half avg splits
	strw_arr = list(df['Start Weight (lb)'].values)
	endw_arr = list(df['End Weight (lb)'].values)
	temp_arr = list(df['Temp (F)'].values)  # to see if sweatloss varies with temp
	swtrt_arr = list(df['Sweat Loss Rate (L/h)'].values)  # to determine my sweat loss rate
	sho_worn_arr = list(df['Shoes Worn'].values)  # to amass mileage on each pair of shoes
	lit_cons_arr = list(df['Liters Consumed'].values)  # to help me plan how much water to bring
	cal_cons_arr = list(df['Calories Consumed'].values)  # to help plan food
	cal_desc_arr = list(df['Calorie Description'].values)
	
	# runs_since_strt_date = [act for act in activities if act.type == 'Run']
	# runs_since_strt_date = runs_since_strt_date[::-1]  # put in chronological order
	activities = activities[::-1]  # put in chronological order
	
	# for run in runs_since_strt_date:
	for run in activities:
		# if run is missing, add it in
		if run.id not in df['runid'].values:
			runid_arr.append(run.id)
			date_arr.append(run.start_date_local)
			type_arr.append(run.type)
			cals_arr.append(run.calories)
			dist_arr.append(unithelper.miles(run.distance).num)
			try:
				pace_arr.append(60. / unithelper.miles_per_hour(run.average_speed).num)
			except ZeroDivisionError:
				pace_arr.append(np.nan)
			# add temp (note run.average_temp is temp of ALTITUDE SENSOR)
			# attached Klimat app to put weather into description
			# however run.description == None for some reason so we need to pull it specifically as below
			# THIS OFTEN GIVES "unable to set attribute..." ERRORS FOR SOME REASON!
			desc = client.get_activity(run.id).description
			if desc is None:
				temp_arr.append(np.nan)
			else:
				try:
					temp_arr.append(float(desc.split('°')[0].split(' ')[-1]))  # comes in in °F so don't need to convert
				except ValueError:
					temp_arr.append(np.nan)
					logging.info(
						f'problem converting {desc.split("°")[0].split(" ")[-1]} to float for runid: {run.id}- set to nan')
			
			# add splits
			splits = client.get_activity(run.id).splits_standard
			if splits is not None:
				minpmil = [60. / unithelper.miles_per_hour(s.average_speed).num for s in splits]  # min per mile pace
				firsthalf_av, secondhalf_av = np.nanmean(minpmil[0:int(len(minpmil) / 2)]), np.nanmean(
					minpmil[int(len(minpmil) / 2):])  # get av pace for first/second half of run
				split_shift_arr.append(secondhalf_av - firsthalf_av)
			else:
				split_shift_arr.append(np.nan)
			
			if run.type == 'Run':
				shoes_available = []
				for i in sho.index:
					if math.isnan(sho['retired_date'][i]):
						if run.start_date_local >= sho['start_date'][i]:
							shoes_available.append(sho['shoe_options'][i])
					else:
						if sho['start_date'][i] < run.start_date_local < sho['retired_date'][i]:
							shoes_available.append(sho['shoe_options'][i])
				# initialize vars (need next line)
				shoes_worn, liters_consumed, start_weight_lb, end_weight_lb = 'catchall', 0., np.nan, np.nan
				sh, lc, sw, ew, cc, cd = data_input_popup(run.start_date_local, shoes_available,
				                                          unithelper.miles(run.distance).num)
			else:
				sh, lc, sw, ew, cc, cd = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
			strw_arr.append(sw)
			endw_arr.append(ew)
			swtrt_arr.append(((sw - ew) / 2.20462 + lc) / (run.moving_time.seconds / 60. / 60.))
			sho_worn_arr.append(sh)
			lit_cons_arr.append(lc)
			cal_cons_arr.append(cc)
			cal_desc_arr.append(cd)
		else:  # run exists, can do other checks here
			pass
	
	df_updated = pd.DataFrame(
		{'runid': runid_arr, 'Date': date_arr, 'Type': type_arr, 'Calories': cals_arr, 'Dist (mi)': dist_arr,
		 'Pace (min/mi)': pace_arr, 'Split Shift (min/mile)': split_shift_arr,
		 'Start Weight (lb)': strw_arr, 'End Weight (lb)': endw_arr, 'Temp (F)': temp_arr,
		 'Sweat Loss Rate (L/h)': swtrt_arr, 'Shoes Worn': sho_worn_arr, 'Liters Consumed': lit_cons_arr,
		 'Calories Consumed': cal_cons_arr, 'Calorie Description': cal_desc_arr})
	df_updated = df_updated.sort_values(by=['Date'], ascending=False)  # put recent runs at the top
	
	sho_dist = np.zeros_like(shoe_options)
	for i in sho.index:
		sho_dist[i] = np.sum([dist_arr[j] for j in range(len(sho_worn_arr)) if sho_worn_arr[j] == shoe_options[i]])
		sho['cum_dist (mi)'] = sho_dist
	
	with pd.ExcelWriter(fn) as writer:
		df_updated.to_excel(writer, sheet_name='data', index=False)
		sho.to_excel(writer, sheet_name='shoes', index=False)
	
	logging.info('--> DATA FILE UPDATED <--')
	
	# return activities
	return df_updated[(aft < df_updated['Date']) & (df_updated['Date'] < bef)], sho
