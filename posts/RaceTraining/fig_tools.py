import matplotlib.pyplot as plt
import numpy as np
import datetime
from posts.RaceTraining.app_tools import *
import plotly.graph_objs as go

wks_18 = datetime.timedelta(weeks=18)
wks_1 = datetime.timedelta(weeks=1)
day_1 = datetime.timedelta(days=1)
ttext = [str(int(i)) for i in abs(-7 * np.arange(19) / 7)]
tvals = -7 * np.arange(19)


def fig_architect(df, sho, races2analyze=None, plots=None):
	# ('rdist', 'Distance vs. Weeks Before'), ('rcum', 'Cumulative Distance vs. Weeks Before'),
	# ('rwk', 'Current Week'), ('rpace', 'Pace vs. Weeks Before'),
	# ('rcal', 'Calories (cumulative) vs. Weeks Before'), ('rpvd', 'Speed vs. Distance'),
	# ('rswt', 'Manual Data Analysis (sweatrate, shoe mileage, fluid/calorie intake vs mileage)'),
	# ('calbytype', 'Calories (cumulative) by Activity Type over past 18 weeks')]
	races = get_past_races(races2analyze)
	graphs = []
	if 'rdist' in plots:
		graphs.append(create_rdist_fig(df, races))
	if 'rcum' in plots:
		graphs.append(create_rcum_fig(df, races))
	if 'rwk' in plots:
		a = 1
	if 'rpace' in plots:
		a = 1
	if 'rcal' in plots:
		a = 1
	if 'rpvd' in plots:
		a = 1
	if 'rswt' in plots:
		a = 1
	if 'rcalbytype' in plots:
		a = 1
	message = 'you smell'
	return graphs, message


"""
		pace_traces = []
		cal_traces = []
		wk_traces = []
		wks_18 = datetime.timedelta(weeks=18)
		wks_1 = datetime.timedelta(weeks=1)
		if len(races.keys()) > 0:
			ref_day = min(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
			              races[list(races.keys())[-1]])
			days_to_race = datetime.timedelta(days=(races[list(races.keys())[-1]] - ref_day).days)
		else:
			days_to_race = 0
		for i, (k, v) in enumerate(races.items()):
			print(k)
			# read: if race day is after today, ie in the future, then solid line plot
			if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
				width = 3
			else:
				width = 2
			op = (i + 1.) / len(races.items()) * .75 + .25
			activities = get_activities(client, v - wks_18, v + day_1)
			if k == 'Past 18 weeks' and 'calbytype' in plots:
				calbytype_figs = create_calbytype_fig(client, activities, v + day_1, img_path)
			days_before, dist, cum, pace, speed, adb, cals, dates = get_training_data(client, activities,
			                                                                          before=v + day_1)
			max_dist = max([max(dist), max_dist])
			if 'rsvd' in plots:
				bill_pace = 60. / np.array(speed)  # min/mile
				hovertext = [f'pace: {int(s)}:{str(int((s - int(s)) * 60)).zfill(2)} (min/mile)<br>date: {dates[i]}' for
				             i, s in enumerate(bill_pace)]
				hovertemp = 'mileage: %{x:.2f}<br>%{text}'
				# svd_traces.append(
				#     go.Scatter(x=dist, y=speed, mode='markers', name=k, text=hovertext, hovertemplate=hovertemp))
				svd_traces.append(
					go.Scatter(x=dist, y=pace, mode='markers', name=k, text=hovertext, hovertemplate=hovertemp))
			if 'rcal' in plots:
				cal_traces.append(
					go.Scatter(x=adb, y=cals, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
			if 'rwk' in plots:
				activities = get_activities(client, v - days_to_race - wks_1, v - days_to_race)
				wdb, wd, wc, wp, ws, _, _, _ = get_training_data(client, activities, before=v - days_to_race)
				wk_traces.append(
					go.Scatter(x=wdb, y=wd, yaxis='y2', opacity=op, name=k, mode='lines+markers',
					           marker=dict(color=colors[i]),
					           line=dict(width=width)))
				wk_traces.append(
					go.Scatter(x=wdb, y=wc, opacity=op, name=k, mode='lines+markers', marker=dict(color=colors[i]),
					           line=dict(width=width), showlegend=False))
				wk_traces.append(
					go.Scatter(x=wdb, y=wp, yaxis='y3', opacity=op, name=k, mode='lines+markers',
					           marker=dict(color=colors[i]),
					           line=dict(width=width), showlegend=False, hovertemplate='pace: %{y:.2f}<br>dist:%{text}',
					           text=['{:.2f}'.format(d) for d in wd]))
		
		if 'rsvd' in plots:
			svd_traces.append(go.Scatter(x=[recent[0]], y=[recent[1]], mode='markers', name='most recent',
			                             marker=dict(line=dict(width=3), color='rgba(0,0,0,0)',
			                                         symbol='star-diamond-dot',
			                                         size=10), text=[htxt], hovertemplate=htemp))
		
		# append annotation traces
		if 'rwk' in plots:
			wk_annotations = {'dx': [t.x[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y2')],
			                  'dy': [t.y[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y2')],
			                  'dt': [f'{round(t.y[-1], 1)}' for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y2')],
			                  'cx': [t.x[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis is None)],
			                  'cy': [t.y[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis is None)],
			                  'ct': [f'{round(t.y[-1], 1)}' for t in wk_traces if (len(t.x) > 0 and t.yaxis is None)],
			                  'px': [t.x[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y3')],
			                  'py': [t.y[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y3')],
			                  'pt': [f'{round(t.y[-1], 1)}' for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y3')]
			                  }
			wk_traces.append(
				go.Scatter(x=wk_annotations['dx'], y=wk_annotations['dy'], text=wk_annotations['dt'], mode='text',
				           textposition='middle left', showlegend=False, hoverinfo='none', ))
			wk_traces.append(
				go.Scatter(x=wk_annotations['px'], y=wk_annotations['py'], text=wk_annotations['pt'], yaxis='y3',
				           mode='text', textposition='middle left', showlegend=False, ))
			wk_traces.append(
				go.Scatter(x=wk_annotations['cx'], y=wk_annotations['cy'], text=wk_annotations['ct'], mode='text',
				           textposition='middle left', showlegend=False, hoverinfo='none', ))
	
	figs = []
	ttext = [str(int(i)) for i in abs(-7 * np.arange(19) / 7)]
	tvals = -7 * np.arange(19)
	if calbytype_figs is not None:
		for cf in calbytype_figs:
			figs.append(cf)
	if 'rsvd' in plots:
		svd_layout = go.Layout(xaxis=dict(title='Distance (miles)'),
		                       # yaxis=dict(title='Speed (miles/hr)', hoverformat='.2f'),
		                       yaxis=dict(title='Pace (min/mile)', hoverformat='.2f'),
		                       legend=dict(bgcolor='rgba(0,0,0,0)'))
		# legend=dict(x=1, y=1.02, bgcolor='rgba(0,0,0,0)', xanchor='right', orientation='h'))
		pc_v_dist_fig = go.Figure(data=svd_traces, layout=svd_layout)
		pc_v_dist_fig.write_html(f'{img_path}rta_svd.html')
		print('saved speed-vs-dist image')
		figs.append(pc_v_dist_fig)
		split_layout = go.Layout(xaxis=dict(title='Distance (miles)'),
		                         yaxis=dict(title='change to av. splits (2nd-1st half) (min/mile)'))
		splits_fig = go.Figure(data=split_traces, layout=split_layout)
		splits_fig.write_html(f'{img_path}rta_splitsvsdist.html')
		print('saved splits-vs-dist image')
		figs.append(splits_fig)
		
		wktot_layout = go.Layout(yaxis=dict(title='Mileage', hoverformat='.2f'),
		                         legend=dict(x=1, y=1, bgcolor='rgba(0,0,0,0)', xanchor='right', orientation='h'))
		wktot_fig = go.Figure(data=wktot_data, layout=wktot_layout)
		wktot_fig.write_html(f'{img_path}rta_wktot.html')
		print('saved weekly total image')
		figs.append(wktot_fig)
	if 'rcal' in plots:
		calayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
		                     yaxis=dict(title='Calories'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
		cal_fig = go.Figure(data=cal_traces, layout=calayout)
		cal_fig.write_html(f'{img_path}rta_cal.html')
		print('saved cal image')
		figs.append(cal_fig)
	if 'rwk' in plots:
		wlayout = go.Layout(legend=dict(orientation='h', y=1.1), xaxis=dict(title='Prior week training', ),
		                    yaxis=dict(title='Distance', domain=[0., .3], ),
		                    yaxis2=dict(title='Cumulative', domain=[0.35, 0.65]),
		                    yaxis3=dict(title='Pace', domain=[0.7, 1.], ), )
		wk_fig = go.Figure(data=wk_traces, layout=wlayout)
		wk_fig.write_html(f'{img_path}rta_week.html')
		print('saved week image')
		figs.append(wk_fig)
	if 'rswt' in plots:
		man_fig.write_html(f'{img_path}rta_man.html')
		print('saved manual analysis image')
		figs.append(man_fig)
	message = 'Analysis Complete'
	
	return figs, message
"""

if os.path.isdir('C:/Users/Owner/Dropbox/'):
	img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
elif os.path.isdir('C:/Users/wcapecch/Dropbox/'):
	img_path = 'C:/Users/wcapecch/PycharmProjects/capecchi.github.io/images/posts/'
else:
	raise BillExcept('cannot connect to image directory')


def create_rdist_fig(df, races):
	traces, max_dist = [], 0
	for i, (k, v) in enumerate(races.items()):
		print(k)
		# read: if race day is after today, ie in the future, then thicker line plot
		if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
			width = 3
		else:
			width = 2
		op = (i + 1.) / len(races.items()) * .75 + .25
		runs = [act for act in activs if act.type == 'Run' and v - wks_18 < act.start_date_local < v + day_1]
		runs = [r for r in runs if
		        unithelper.miles(r.distance).num > 2 and unithelper.miles_per_hour(r.average_speed).num > 4]
		race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
		days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
		dist = [unithelper.miles(r.distance).num for r in runs]
		max_dist = max([max(dist), max_dist])
		traces.append(
			go.Scatter(x=days_before, y=dist, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
	dist_arr = [t.y[-1] for t in traces if len(t.y) > 0]
	traces.append(go.Scatter(x=[t.x[-1] for t in traces if len(t.x) > 0], y=dist_arr,
	                         text=[f'{round(t.y[-1], 1)}' for t in traces if len(t.y) > 0], mode='text',
	                         textposition='middle left', showlegend=False, hoverinfo='none'))
	dlayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
	                    yaxis=dict(title='Distance (miles)', hoverformat='.2f'),
	                    legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
	dist_fig = go.Figure(data=traces, layout=dlayout)
	dist_fig.write_html(f'{img_path}rta_dist.html')
	print('saved dist image')
	return dist_fig


def create_rcum_fig(activs, races):
	traces = []
	for i, (k, v) in enumerate(races.items()):
		print(k)
		# read: if race day is after today, ie in the future, then thicker line plot
		if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
			width = 3
		else:
			width = 2
		op = (i + 1.) / len(races.items()) * .75 + .25
		runs = [act for act in activs if act.type == 'Run' and v - wks_18 < act.start_date_local < v + day_1]
		runs = [r for r in runs if
		        unithelper.miles(r.distance).num > 2 and unithelper.miles_per_hour(r.average_speed).num > 4]
		race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
		days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
		cum = np.cumsum([unithelper.miles(r.distance).num for r in runs])
		traces.append(
			go.Scatter(x=days_before, y=cum, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
	traces.append(
		go.Scatter(x=[t.x[-1] for t in traces if len(t.x) > 0],
		           y=[t.y[-1] for t in traces if len(t.y) > 0],
		           text=[f'{round(t.y[-1], 1)}' for t in traces if len(t.y) > 0], mode='text',
		           textposition='middle left', showlegend=False, hoverinfo='none'))
	clayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
	                    yaxis=dict(title='Distance (cumulative miles)'),
	                    legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
	cum_fig = go.Figure(data=traces, layout=clayout)
	cum_fig.write_html(f'{img_path}rta_cum.html')
	print('saved cum image')
	return cum_fig

# def create_rpace_fig(activs, races):
# 	pace_traces = []
# 	for i, (k, v) in enumerate(races.items()):
# 		print(k)
# 		# read: if race day is after today, ie in the future, then thicker line plot
# 		if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
# 			width = 3
# 		else:
# 			width = 2
# 		op = (i + 1.) / len(races.items()) * .75 + .25
# 		runs = [act for act in activs if act.type == 'Run' and v - wks_18 < act.start_date_local < v + day_1]
# 		runs = [r for r in runs if
# 		        unithelper.miles(r.distance).num > 2 and unithelper.miles_per_hour(r.average_speed).num > 4]
# 		race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
# 		days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
# 		pace_traces.append(
# 			go.Scatter(x=days_before, y=pace, opacity=op, name=k, mode='lines+markers', line=dict(width=width),
# 			           hovertemplate='pace: %{y:.2f}<br>dist:%{text}', text=['{:.2f}'.format(d) for d in dist]))
# 	pace_traces.append(
# 		go.Scatter(x=[t.x[-1] for t in pace_traces if len(t.x) > 0],
# 		           y=[t.y[-1] for t in pace_traces if len(t.y) > 0],
# 		           text=[f'{round(t.y[-1], 1)}' for t in pace_traces if len(t.y) > 0], mode='text',
# 		           textposition='middle left', showlegend=False, hoverinfo='none'))
# 	playout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
# 	                    yaxis=dict(title='Pace (min/mile)'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
# 	pace_fig = go.Figure(data=pace_traces, layout=playout)
# 	pace_fig.write_html(f'{img_path}rta_pace.html')
# 	print('saved pace image')

"""
get_training_data(client, activities, get_cals=False, before=bef)
	race_day = before.replace(hour=0, minute=0, second=0, microsecond=0)
	if get_cals:
		all_days_before = [(a.start_date_local.date() - race_day.date()).days for a in activities]
		all_cals = [client.get_activity(id).calories for id in [a.id for a in activities]]
		cum_cals = np.cumsum(all_cals)
	else:
		all_days_before, cum_cals = None, None
	runs = [act for act in activities if act.type == 'Run']
	runs = [r for r in runs if
	        unithelper.miles(r.distance).num > 2 and unithelper.miles_per_hour(r.average_speed).num > 4]
	dates = [r.start_date_local.date() for r in runs]
	days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
	dist = [unithelper.miles(r.distance).num for r in runs]
	cum = np.cumsum(dist)
	pace = [60. / unithelper.miles_per_hour(r.average_speed).num for r in runs]  # min/mile
	speed = [60 / p for p in pace]  # mph
	if get_splits:
		split_shift = []
		for run in runs:
			splits = client.get_activity(run.id).splits_standard
			if splits is not None:
				minpmil = [60. / unithelper.miles_per_hour(s.average_speed).num for s in splits]  # min per mile pace
				firsthalf_av, secondhalf_av = np.nanmean(minpmil[0:int(len(minpmil) / 2)]), np.nanmean(
					minpmil[int(len(minpmil) / 2):])  # get av pace for first/second half of run
				split_shift.append(secondhalf_av - firsthalf_av)
			else:
				split_shift.append(np.nan)
		return days_before, dist, cum, pace, speed, all_days_before, cum_cals, dates, split_shift
	else:
		return days_before, dist, cum, pace, speed, all_days_before, cum_cals, dates
"""
