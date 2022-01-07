import math
import os
from collections import OrderedDict

import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize
from stravalib import unithelper

from posts.RaceTraining.app_tools import *


def get_training_data(client, activities, get_cals=True, before=datetime.date.today(), get_splits=False):
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


def create_calbytype_fig(client, activities, before, img_path):
    race_day = before.replace(hour=0, minute=0, second=0, microsecond=0)
    days_before = np.array([(a.start_date_local.date() - race_day.date()).days for a in activities])
    cals = np.array([client.get_activity(id).calories for id in [a.id for a in activities]])
    type = np.array([a.type for a in activities])
    calbytype_fig = make_subplots(rows=2, cols=1, vertical_spacing=.05, shared_xaxes=True)
    current_day_of_week = race_day.weekday()  # 0=Monday=Start of training week

    cols = plotly.colors.DEFAULT_PLOTLY_COLORS
    for i, typ in enumerate(np.unique(type)):
        typecals = np.zeros_like(cals)
        typecals[type == typ] = cals[type == typ]
        calbytype_fig.add_trace(
            go.Scatter(x=days_before, y=np.cumsum(typecals), mode='lines', line=dict(color=cols[i]),
                       showlegend=False, ), row=1, col=1)
        calbytype_fig.add_trace(
            go.Scatter(x=days_before[type == typ], y=np.cumsum(typecals)[type == typ], mode='markers',
                       marker=dict(color=cols[i]), showlegend=False), row=1, col=1)
        calbytype_fig.add_trace(
            go.Histogram(x=days_before[type == typ], name=typ,
                         xbins=dict(start=-7 * 18 - current_day_of_week, end=7 - current_day_of_week, size=7),
                         marker_color=cols[i]), row=2, col=1)
    calbytype_fig.layout.update(height=750, barmode='stack',  # 0.5 in tickvals to place grid between bins
                                xaxis1=dict(tickmode='array', tickvals=-7 * np.arange(19) - current_day_of_week - .5),
                                xaxis2=dict(title='Weeks Ago', tickmode='array', tickvals=-7 * np.arange(19),
                                            ticktext=[str(int(i)) for i in abs(-7 * np.arange(19) / 7)]),
                                yaxis1=dict(title='Calories\n(cumulative)'),
                                yaxis2=dict(title='Activity Type Count'))
    calbytype_fig.update_yaxes(automargin=True)

    calbytype_fig.write_html(f'{img_path}rta_calbytype.html')
    print('saved calbytype image')
    return [calbytype_fig]


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
	# remove races not in racekeys
	if racekeys is not None:
		[races.pop(k) for k in list(races.keys()) if k not in racekeys]
	# order chronologically
	races = {k: v for k, v in sorted(races.items(), key=lambda item: item[1])}
	return races


def manual_tracking_plots(client):
    analysis_startdate = datetime.datetime(2020, 9, 12, 0, 0, 0, 0)  # hard coded start date
    if os.path.isdir('C:/Users/Owner/Dropbox/'):
        fn = 'C:/Users/Owner/Dropbox/training_data.xlsx'
    elif os.path.isdir('C:/Users/wcapecch/Dropbox/'):
        fn = 'C:/Users/wcapecch/Dropbox/training_data.xlsx'
    else:
        print('cannot locate training data file')
    sho = pd.read_excel(fn, sheet_name='shoes', engine='openpyxl')
    shoe_options = sho['shoe_options'].values
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

    # debugging
    # wt = client.get_activities(after=datetime.datetime(2021,8,16,0,0),before=datetime.datetime(2021,8,16,13,40))
    # list(wt)

    activ_since_strt_date = list(client.get_activities(after=analysis_startdate, before=datetime.datetime.utcnow()))
    runs_since_strt_date = [act for act in activ_since_strt_date if act.type == 'Run']
    runs_since_strt_date = runs_since_strt_date[::-1]  # put in chronological order

    for run in runs_since_strt_date:
        if run.id not in df['runid'].values:
            shoes_available = []
            for i in sho.index:
                if math.isnan(sho['retired_date'][i]):
                    if run.start_date_local >= sho['start_date'][i]:
                        shoes_available.append(sho['shoe_options'][i])
                else:
                    if sho['start_date'][i] < run.start_date_local < sho['retired_date'][i]:
                        shoes_available.append(sho['shoe_options'][i])
            runid_arr.append(run.id)
            date_arr.append(run.start_date_local)
            dist_arr.append(unithelper.miles(run.distance).num)
            # run.average_temp IS TEMP OF ALTITUDE SENSOR
            # attached Klimat app to put weather into description
            # however run.description == None for some reason so we need to pull it specifically as below
            desc = client.get_activity(run.id).description
            if desc is None:
                temp_arr.append(np.nan)
            else:
                temp_arr.append(float(desc.split('°')[0].split(' ')[-1]))  # comes in in °F so don't need to convert
            # initialize vars (need these next 4 lines)
            shoes_worn = 'catchall'
            liters_consumed = 0.
            start_weight_lb = np.nan
            end_weight_lb = np.nan
            sh, lc, sw, ew, cc, cd = data_input_popup(run.start_date_local, shoes_available,
                                                      unithelper.miles(run.distance).num)
            strw_arr.append(sw)
            endw_arr.append(ew)
            swtrt_arr.append(((sw - ew) / 2.20462 + lc) / (run.moving_time.seconds / 60. / 60.))
            sho_worn_arr.append(sh)
            lit_cons_arr.append(lc)
            cal_cons_arr.append(cc)
            cal_desc_arr.append(cd)
    df_updated = pd.DataFrame(
        {'runid': runid_arr, 'Date': date_arr, 'Dist (mi)': dist_arr, 'Start Weight (lb)': strw_arr,
         'End Weight (lb)': endw_arr, 'Temp (F)': temp_arr, 'Sweat Loss Rate (L/h)': swtrt_arr,
         'Shoes Worn': sho_worn_arr, 'Liters Consumed': lit_cons_arr, 'Calories Consumed': cal_cons_arr,
         'Calorie Description': cal_desc_arr})

    sho_dist = np.zeros_like(shoe_options)
    for i in sho.index:
        sho_dist[i] = np.sum([dist_arr[j] for j in range(len(sho_worn_arr)) if sho_worn_arr[j] == shoe_options[i]])
        sho['cum_dist (mi)'] = sho_dist

    with pd.ExcelWriter(fn) as writer:
        df_updated.to_excel(writer, sheet_name='data', index=False)
        sho.to_excel(writer, sheet_name='shoes', index=False)

    # make some figs
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    man_fig = make_subplots(rows=3, cols=1, vertical_spacing=.12)
    # restrict to runs between 4-10miles
    nptemp = np.array([temp_arr[i] for i in np.arange(len(temp_arr)) if 10. >= dist_arr[i] >= 4.])
    npswt = np.array([swtrt_arr[i] for i in np.arange(len(temp_arr)) if 10. >= dist_arr[i] >= 4.])
    # drop nan values
    bool_notnan = ~np.isnan(nptemp) & ~np.isnan(npswt)
    nptemp, npswt = nptemp[bool_notnan], npswt[bool_notnan]

    # nptemp, npswt = np.array(temp_arr), np.array(swtrt_arr)
    rb = plotly.colors.sequential.RdBu_r
    tmin, tmax = 20., 80.
    rangelist = np.append(np.append([-np.inf], np.linspace(tmin, tmax, endpoint=True, num=len(rb) - 1)), np.inf)
    lastrunbin, numinlastbin = (np.nan, np.nan), np.nan
    for i, col in enumerate(rb):
        if rangelist[i] == -np.inf:
            lbl = f'<{rangelist[i + 1]:.0f}'
        elif rangelist[i + 1] == np.inf:
            lbl = f'>{rangelist[i]:.0f}'
        else:
            lbl = f'{rangelist[i]:.0f}-{rangelist[i + 1]:.0f}'
        man_fig.add_trace(
            go.Histogram(x=npswt[np.where((rangelist[i] <= nptemp) & (nptemp < rangelist[i + 1]))],
                         xbins=dict(start=0, end=3.0, size=0.1), marker=dict(color=rb[i], line=dict(width=0.5)),
                         name=lbl), row=1, col=1)
        if rangelist[i] <= nptemp[-1] < rangelist[i + 1]:
            lastrunbin = (np.floor(npswt[-1] * 10.) / 10., np.ceil(npswt[-1] * 10.) / 10.)
            # count number where sweatrate is in bin, and temp is below current rangelist bin max so we overlay properly
            numinlastbin = len(
                np.where((npswt < lastrunbin[1]) & (npswt >= lastrunbin[0]) & (nptemp < rangelist[i + 1]))[0])
    man_fig.add_shape(type='rect', x0=lastrunbin[0], y0=numinlastbin - 1, x1=lastrunbin[1], y1=numinlastbin,
                      line=dict(width=2, color='black'), row=1, col=1)

    man_fig.add_trace(go.Bar(x=sho_dist, y=shoe_options, orientation='h', marker_color=colors[4], showlegend=False),
                      row=2, col=1)  # shoe mileage
    # add rect for most recent activity
    x1rect = sho_dist[shoe_options == sho_worn_arr[-1]][0]
    x0rect = x1rect - dist_arr[-1]
    yrect = np.where(shoe_options == sho_worn_arr[-1])[0][0]
    man_fig.add_shape(type='rect', x0=x0rect, y0=yrect - .5, x1=x1rect, y1=yrect + .5,
                      line=dict(width=2, color='black'), row=2, col=1)

    man_fig.add_trace(go.Scatter(x=dist_arr, y=lit_cons_arr, mode='markers', marker_color=colors[2], showlegend=False),
                      row=3, col=1)  # fluid consumption
    man_fig.add_trace(go.Scatter(x=dist_arr, y=cal_cons_arr, mode='markers', yaxis='y4', xaxis='x3',
                                 marker_color=colors[3], showlegend=False))  # calorie consumption
    yr = np.ceil(max([max(lit_cons_arr), max(cal_cons_arr) / 500.]))

    man_fig.layout.update(height=750, barmode='stack',
                          xaxis1=dict(title='Sweat Loss Rate (L/h)', range=[0, 3]),
                          xaxis2=dict(title='Distance (miles)'),
                          xaxis3=dict(title='Cumulative Mileage'),
                          yaxis1=dict(title='Count'),
                          yaxis3=dict(title='Liters Consumed', color=colors[2], range=[-.5, yr]),
                          yaxis4=dict(title='Calories Consumed', color=colors[3], side='right',
                                      overlaying='y3', range=[-250, yr * 500]),
                          showlegend=True, legend_title_text='Temp (F)')
    man_fig.update_yaxes(automargin=True)

    return man_fig


def gather_training_seasons(code, races2analyze=None, plots=None):
	nope = ''
	if len(plots) == 0:  # need to select a plot to show
		nope = f'{nope} <Please select some plots to show> '
	if len(races2analyze) == 0 and 'rswt' not in plots and 'rsvd' not in plots:
		nope = f'{nope} <Select races to analyze> '
	if len(nope) > 0:
		return [], nope  # empty figs list
	
	races = get_past_races(racekeys=races2analyze)
	if 'Past 18 weeks' in races2analyze:
		races.update({'Past 18 weeks': datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)})
	
	day_1 = datetime.timedelta(days=1)
	client = get_client(code)
	
	colors = plotly.colors.DEFAULT_PLOTLY_COLORS
	if os.path.isdir('C:/Users/Owner/Dropbox/'):
		img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
	elif os.path.isdir('C:/Users/wcapecch/Dropbox/'):
		img_path = 'C:/Users/wcapecch/PycharmProjects/capecchi.github.io/images/posts/'
	else:
		print('cannot connect to image directory')
	max_dist = 0
	if 'rswt' in plots:  # get activities for runs with sweat loss data
		man_fig = manual_tracking_plots(client)
	if 'rsvd' in plots:  # get large dataset
		svd_traces = []  # speed vs dist
		split_traces = []  # split shift vs dist
		if len(races.keys()) > 0:
			yrsago = [(datetime.datetime.utcnow() - rd).days / 365. for rd in [races[k] for k in races.keys()]]
			yrsago = [ya + 18 / 52. for ya in yrsago]  # add 18 weeks onto each race
			nyr = np.ceil(max(yrsago))
			nyr = max([nyr, 3])
		else:
			nyr = 3
		nyrs = datetime.timedelta(weeks=52 * nyr)
		aft = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - nyrs
		bef = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + day_1
		activities = get_activities(client, aft, bef)
		predays, dist, _, pace, speed, _, _, dates, split_shift = get_training_data(client, activities, get_cals=False,
		                                                                            before=bef, get_splits=True)
		max_dist = max([max(dist), max_dist])
		bill_pace = 60. / np.array(speed)  # min/mile
		hovertext = [f'pace: {int(s)}:{str(int((s - int(s)) * 60)).zfill(2)} (min/mile)<br>date: {dates[i]}' for i, s in
		             enumerate(bill_pace)]
		hovertemp = 'mileage: %{x:.2f}<br>%{text}'
		svd_traces.append(go.Scatter(x=dist, y=pace, mode='markers', name='past {} years'.format(nyr), text=hovertext,
		                             hovertemplate=hovertemp, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
		svd_traces = add_max_effort_curve(svd_traces, max_dist=max_dist)  # add here so data only counted once
		split_traces.append(go.Scatter(x=dist, y=split_shift, mode='markers', text=hovertext, hovertemplate=hovertemp))
		recent, htxt, htemp = (dist[-1], pace[
			-1]), f'pace: {int(bill_pace[-1])}:{str(int((bill_pace[-1] - int(bill_pace[-1])) * 60)).zfill(2)} (min/mile)<br>date: {dates[-1]}', hovertemp
		
		# make weekly average plot
		i, wktot, wktot_db, npdist, nppredays, wktot_dates = 0, [], [], np.array(dist), np.array(predays), []
		nday_av = 14
		while -i - 7 > min(predays):
			wktot.append(np.sum(npdist[(nppredays > -i - 7) & (nppredays <= -i)]))
			wktot_db.append(-i)
			wktot_dates.append(datetime.date.today() - datetime.timedelta(days=i))  # no min, sec, usec
			i += 1
		runav = [np.mean(wktot[i:i + nday_av]) for i in np.arange(len(wktot) - nday_av + 1)]
		# runav_db = wktot_db[:len(runav)]
		runav_dates = wktot_dates[:len(runav)]
		wktot_data = [go.Scatter(x=wktot_dates, y=wktot, mode='lines', name='weekly total'),
		              go.Scatter(x=runav_dates, y=runav, mode='lines', name=f'{nday_av} day avg of tot',
		                         line=dict(dash='dash'))]
		now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
		xann = [rd for rd in [races[k] for k in races.keys()] if (rd - now).days < 0]
		yann = [wktot[i] for i in [-(rd - now).days for rd in [races[k] for k in races.keys()] if (rd - now).days < 0]]
		wktot_data.append(go.Scatter(
			x=xann, y=yann, text=[k for k in races.keys() if (races[k] - now).days < 0], mode='text+markers',
			textposition='middle right', showlegend=False, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
		wktot_data.append(go.Bar(x=dates, y=dist, name='runs'))  # width=1,
	
	# if we're not doing any of these plots, skip this
	calbytype_figs = None
	if any([p in plots for p in ['rdist', 'rcum', 'rwk', 'rpace', 'rsvd', 'rcal', 'calbytype']]):
		dist_traces = []
		cum_traces = []
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
			if 'rdist' in plots:
				dist_traces.append(
					go.Scatter(x=days_before, y=dist, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
			if 'rcum' in plots:
				cum_traces.append(
					go.Scatter(x=days_before, y=cum, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
			if 'rpace' in plots:
				pace_traces.append(
					go.Scatter(x=days_before, y=pace, opacity=op, name=k, mode='lines+markers', line=dict(width=width),
					           hovertemplate='pace: %{y:.2f}<br>dist:%{text}', text=['{:.2f}'.format(d) for d in dist]))
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
		if 'rdist' in plots:
			dist_arr = [t.y[-1] for t in dist_traces if len(t.y) > 0]
			dist_traces.append(go.Scatter(x=[t.x[-1] for t in dist_traces if len(t.x) > 0], y=dist_arr,
			                              text=[f'{round(t.y[-1], 1)}' for t in dist_traces if len(t.y) > 0],
			                              mode='text',
			                              textposition='middle left', showlegend=False, hoverinfo='none'))
		if 'rcum' in plots:
			cum_traces.append(
				go.Scatter(x=[t.x[-1] for t in cum_traces if len(t.x) > 0],
				           y=[t.y[-1] for t in cum_traces if len(t.y) > 0],
				           text=[f'{round(t.y[-1], 1)}' for t in cum_traces if len(t.y) > 0], mode='text',
				           textposition='middle left', showlegend=False, hoverinfo='none'))
		if 'rpace' in plots:
			pace_traces.append(
				go.Scatter(x=[t.x[-1] for t in pace_traces if len(t.x) > 0],
				           y=[t.y[-1] for t in pace_traces if len(t.y) > 0],
				           text=[f'{round(t.y[-1], 1)}' for t in pace_traces if len(t.y) > 0], mode='text',
				           textposition='middle left', showlegend=False, hoverinfo='none'))
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
	if 'rdist' in plots:
		dlayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
		                    yaxis=dict(title='Distance (miles)', hoverformat='.2f'),
		                    legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
		dist_fig = go.Figure(data=dist_traces, layout=dlayout)
		dist_fig.write_html(f'{img_path}rta_dist.html')
		print('saved dist image')
		figs.append(dist_fig)
	if 'rcum' in plots:
		clayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
		                    yaxis=dict(title='Distance (cumulative miles)'),
		                    legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
		cum_fig = go.Figure(data=cum_traces, layout=clayout)
		cum_fig.write_html(f'{img_path}rta_cum.html')
		print('saved cum image')
		figs.append(cum_fig)
	if 'rpace' in plots:
		playout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
		                    yaxis=dict(title='Pace (min/mile)'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
		pace_fig = go.Figure(data=pace_traces, layout=playout)
		pace_fig.write_html(f'{img_path}rta_pace.html')
		print('saved pace image')
		figs.append(pace_fig)
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


def add_max_effort_curve(svd_traces, max_dist=100):
	max_dist *= 1.60934  # convert miles to km
	a = 450.  # W
	b = 21000.  # J
	tau = 10.  # s
	wbas = 80.  # W
	ef = 0.25
	c = 270.  # J/m
	
	# c = 3.6 * 84.  # [J/kg/m] * 84kg you fat bastard
	
	def speed(time):  # [s]
		a2 = a * (.085 * (time / 3600) ** 2 - 3.908 / 3600 * time + 91.82) / 100.  # [Formenti/Davies]
		# a2 = a * (940 - time / 60) / 1000.  # [Wilke/Saltin]
		return 3.6 / c * ((a2 + b / time - a2 * tau / time * (1 - np.exp(-time / tau))) / ef - wbas)
	
	def dist(time):  # [s]
		a2 = a * (.085 * (time / 3600) ** 2 - 3.908 / 3600 * time + 91.82) / 100.  # [Formenti/Davies]
		# a2 = a * (940 - time / 60) / 1000.  # [Wilke/Saltin]
		spd = 3.6 / c * ((a2 + b / time - a2 * tau / time * (1 - np.exp(-time / tau))) / ef - wbas)
		return spd * time / 60. / 60. - max_dist
	
	tmax = 5. * 60 * 60  # initial guess [s]
	h = dist(tmax) / (dist(tmax + .5) - dist(tmax - .5))
	while abs(h) > 1:
		h = dist(tmax) / (dist(tmax + .5) - dist(tmax - .5))
		tmax -= h
	
	t = np.linspace(40, tmax, endpoint=True, num=1000)  # [s]
	th = t / 60 / 60
	s = speed(t)
	
	minetti_spd = s / 1.60934  # [mph]
	minetti_dst = minetti_spd * th  # miles
	minetti_spd[np.where((15. < minetti_spd) | (minetti_spd < 0.))] = np.nan
	
	# do fit to my data
	bdist, bspeed = [], []  # miles, mph
	not_important = [bdist.extend(s.x) for s in svd_traces]
	not_important = [bspeed.extend(s.y) for s in svd_traces]
	bdist, bspeed = np.array(bdist), np.array(bspeed)
	
	bspeed = 60. / bspeed  # if inputting pace, convert to speed for fitting
	
	# ROTATED PARABOLA FIT METHOD
	if 1:
		def minfunc(fit):  # rotated parabola
			r = np.sqrt(bdist ** 2 + bspeed ** 2)
			th = np.arctan2(bspeed, bdist)
			x2, y2 = r * np.cos(th - fit[1]) - fit[2], r * np.sin(
				th - fit[1])  # rotate pts by -theta, shift x2 by fit[2]
			ydiff_0offset = y2 - fit[0] * x2 ** 2
			offset = max(ydiff_0offset)  # offset necessary so that curve is always >= data
			ydiff = y2 - (fit[0] * x2 ** 2 + offset)
			return np.sum(ydiff ** 2 * bdist ** 4)  # weight pts strongly by bdist
		
		fit0 = np.array(
			[0., np.arctan2(-4, 30.), 0.])  # [2nd order, theta, x' offset] initial guesses for rotated-parabola
		res = minimize(minfunc, fit0, method='Nelder-Mead')
		fit = res.x
		print(res.message)
		
		r = np.sqrt(bdist ** 2 + bspeed ** 2)
		th = np.arctan2(bspeed, bdist)
		dx2, dy2 = r * np.cos(th - fit[1]) - fit[2], r * np.sin(th - fit[1])  # rotate pts by -theta and shift by fit[2]
		ydiff_0offset = dy2 - fit[0] * dx2 ** 2
		offset = max(ydiff_0offset)  # offset necessary so that curve is always >= data
		bill_dist_rot = np.linspace(0., max(bdist))
		bill_spd_rot = fit[0] * bill_dist_rot ** 2 + offset
		bill_r = np.sqrt(bill_dist_rot ** 2 + bill_spd_rot ** 2)
		bill_th = np.arctan2(bill_spd_rot, bill_dist_rot)
		bill_dist0, bill_spd0 = bill_r * np.cos(bill_th + fit[1]), bill_r * np.sin(bill_th + fit[1])  # rotate by +theta
		bill_dist = np.arange(int(min(bdist)), int(max(bdist)) + 2)
		bill_spd = np.interp(bill_dist, bill_dist0, bill_spd0)
	
	bill_pace = 60. / bill_spd  # min/mile
	hovertext = [f'{int(bp)}:{str(int((bp - int(bp)) * 60)).zfill(2)}' for bp in bill_pace]
	
	svd_traces.append(go.Scatter(x=bill_dist, y=bill_pace, mode='lines', line=dict(width=2), name='Max Effort (Bill)',
	                             hovertemplate='mileage: %{x}<br>pace: %{text} (min/mile)',
	                             text=hovertext))
	minetti_pace = 60. / minetti_spd  # min/mile
	svd_traces.append(
		go.Scatter(x=minetti_dst, y=minetti_pace, mode='lines', line=dict(width=2),
		           name='Max Effort (Human) [Minetti]', visible='legendonly'))
	return svd_traces
