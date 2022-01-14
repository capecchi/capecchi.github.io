from bottle import run, redirect, request, get
from posts.RaceTraining.app_tools import *

port = 8000
redirect_url = f'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:{port}&response_type=code&scope=activity:read_all'


def do_updates(code):
	# add type, calories, pace columns
	type_arr, cals_arr, pace_arr = [], [], []
	
	client = get_client(code)
	
	if os.path.isdir('C:/Users/Owner/Dropbox/'):
		fn = 'C:/Users/Owner/Dropbox/training_data.xlsx'
	elif os.path.isdir('C:/Users/wcapecch/Dropbox/'):
		fn = 'C:/Users/wcapecch/Dropbox/training_data.xlsx'
	else:
		raise BillExcept('cannot locate training data file')
	
	sho = pd.read_excel(fn, sheet_name='shoes', engine='openpyxl')
	df = pd.read_excel(fn, sheet_name='data', engine='openpyxl')
	runid_arr = list(df['runid'].values)
	date_arr = list(df['Date'].values)
	dist_arr = list(df['Dist (mi)'].values)
	strw_arr = list(df['Start Weight (lb)'].values)
	endw_arr = list(df['End Weight (lb)'].values)
	temp_arr = list(df['Temp (F)'].values)  # to see if sweatloss varies with temp
	swtrt_arr = list(df['Sweat Loss Rate (L/h)'].values)  # to determine my sweat loss rate
	sho_worn_arr = list(df['Shoes Worn'].values)  # to amass mileage on each pair of shoes
	lit_cons_arr = list(df['Liters Consumed'].values)  # to help me plan how much water to bring
	cal_cons_arr = list(df['Calories Consumed'].values)  # to help plan food
	cal_desc_arr = list(df['Calorie Description'].values)
	split_shift_arr = list(df['Split Shift (min/mile)'].values)  # 2nd half avg - 1st half avg splits
	
	for i, runid in enumerate(runid_arr):
		print(f'{i}/{len(runid_arr)}')
		act = client.get_activity(runid)
		type_arr.append(act.type)
		cals_arr.append(act.calories)
		try:
			pace_arr.append(60. / unithelper.miles_per_hour(act.average_speed).num)
		except ZeroDivisionError:
			pace_arr.append(np.nan)
	
	df_updated = pd.DataFrame(
		{'runid': runid_arr, 'Date': date_arr, 'Type': type_arr, 'Calories': cals_arr, 'Dist (mi)': dist_arr,
		 'Pace (min/mi)': pace_arr, 'Split Shift (min/mile)': split_shift_arr,
		 'Start Weight (lb)': strw_arr, 'End Weight (lb)': endw_arr, 'Temp (F)': temp_arr,
		 'Sweat Loss Rate (L/h)': swtrt_arr, 'Shoes Worn': sho_worn_arr, 'Liters Consumed': lit_cons_arr,
		 'Calories Consumed': cal_cons_arr, 'Calorie Description': cal_desc_arr})
	df_updated = df_updated.sort_values(by=['Date'], ascending=False)  # put recent runs at the top
	
	with pd.ExcelWriter(fn) as writer:
		df_updated.to_excel(writer, sheet_name='data', index=False)
		sho.to_excel(writer, sheet_name='shoes', index=False)
	
	logging.info('--> DATA FILE UPDATED <--')


@get('/')
def load_in():
	if 'code=' in request.url:
		for el in request.url.split('&'):
			if 'code=' in el:
				code = el.split('=')[-1]
				do_updates(code)
	else:
		return redirect(redirect_url)


run(host='localhost', port=port, debug=True, reloader=True)
