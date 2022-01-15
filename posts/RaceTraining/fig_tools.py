import plotly.graph_objs as go
from scipy.optimize import minimize

from posts.RaceTraining.app_tools import *

wks_18 = datetime.timedelta(weeks=18)
wks_1 = datetime.timedelta(weeks=1)
day_1 = datetime.timedelta(days=1)
ttext = [str(int(i)) for i in abs(-7 * np.arange(19) / 7)]
tvals = -7 * np.arange(19)


def fig_architect(df, sho, races, plots=None):
    df = df.sort_values(by=['Date'])  # put in chronological order
    graphs = []
    if 'rdist' in plots:
        graphs.append(create_rdist_fig(df, races))
    if 'rcumdist' in plots:
        graphs.append(create_rcumdist_fig(df, races))
    if 'rwk' in plots:
        a = 1
    if 'rpace' in plots:
        graphs.append(create_rpace_fig(df, races))
    if 'rcumcal' in plots:
        graphs.append(create_rcumcal_fig(df, races))
    if 'rpvd' in plots:
        [graphs.append(g) for g in create_rpvd_fig(df, races)]
    if 'rswt' in plots:
        a = 1
    if 'rcalbytype' in plots:
        a = 1
    message = 'you smell'
    return graphs, message


"""
		wk_traces = []
		for i, (k, v) in enumerate(races.items()):
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

if os.path.isdir('C:/Users/Owner/'):
    img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
elif os.path.isdir('C:/Users/wcapecch/'):
    img_path = 'C:/Users/wcapecch/PycharmProjects/capecchi.github.io/images/posts/'
else:
    raise BillExcept('cannot connect to image directory')


def create_rdist_fig(df, races):
    print('Creating DIST figure')
    traces = []
    for i, (k, v) in enumerate(races.items()):
        # read: if race day is after today, ie in the future, then thicker line plot
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items()) * .75 + .25
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[(runs['Dist (mi)'] > 2) & (runs['Pace (min/mi)'] < 15)]
        race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
        days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
        dist = runs['Dist (mi)'].values
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


def create_rcumdist_fig(df, races):
    print('Creating CUMDIST figure')
    traces = []
    for i, (k, v) in enumerate(races.items()):
        # read: if race day is after today, ie in the future, then thicker line plot
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items()) * .75 + .25
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[(runs['Dist (mi)'] > 2) & (runs['Pace (min/mi)'] < 15)]
        race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
        days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
        cumdist = np.nancumsum(runs['Dist (mi)'].values)
        traces.append(
            go.Scatter(x=days_before, y=cumdist, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
    traces.append(
        go.Scatter(x=[t.x[-1] for t in traces if len(t.x) > 0], y=[t.y[-1] for t in traces if len(t.y) > 0],
                   text=[f'{round(t.y[-1], 1)}' for t in traces if len(t.y) > 0], mode='text',
                   textposition='middle left', showlegend=False, hoverinfo='none'))
    clayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
                        yaxis=dict(title='Distance (cumulative miles)'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
    cumdist_fig = go.Figure(data=traces, layout=clayout)
    cumdist_fig.write_html(f'{img_path}rta_cumdist.html')
    print('saved cumdist image')
    return cumdist_fig


def create_rpace_fig(df, races):
    print('Creating PACE figure')
    traces = []
    for i, (k, v) in enumerate(races.items()):
        # read: if race day is after today, ie in the future, then thicker line plot
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items()) * .75 + .25
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[(runs['Dist (mi)'] > 2) & (runs['Pace (min/mi)'] < 15)]
        race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
        days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
        pace = runs['Pace (min/mi)'].values
        traces.append(
            go.Scatter(x=days_before, y=pace, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
    # pace_ = [t.y[-1] for t in traces if len(t.y) > 0]
    # traces.append(go.Scatter(x=[t.x[-1] for t in traces if len(t.x) > 0], y=dist_arr,
    # 						 text=[f'{round(t.y[-1], 1)}' for t in traces if len(t.y) > 0], mode='text',
    # 						 textposition='middle left', showlegend=False, hoverinfo='none'))
    playout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
                        yaxis=dict(title='Pace (min/mi)', hoverformat='.2f'),
                        legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
    pace_fig = go.Figure(data=traces, layout=playout)
    pace_fig.write_html(f'{img_path}rta_pace.html')
    print('saved pace image')
    return pace_fig


def create_rcumcal_fig(df, races):
    print('Creating CUMCAL figure')
    traces = []
    for i, (k, v) in enumerate(races.items()):
        # read: if race day is after today, ie in the future, then thicker line plot
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items()) * .75 + .25
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[(runs['Dist (mi)'] > 2) & (runs['Pace (min/mi)'] < 15)]
        race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
        days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
        cumcals = np.nancumsum(runs['Calories'].values)
        traces.append(
            go.Scatter(x=days_before, y=cumcals, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
    traces.append(
        go.Scatter(x=[t.x[-1] for t in traces if len(t.x) > 0], y=[t.y[-1] for t in traces if len(t.y) > 0],
                   text=[f'{round(t.y[-1], 1)}' for t in traces if len(t.y) > 0], mode='text',
                   textposition='middle left', showlegend=False, hoverinfo='none'))
    clayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
                        yaxis=dict(title='Calories (cumulative)'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
    cumcal_fig = go.Figure(data=traces, layout=clayout)
    cumcal_fig.write_html(f'{img_path}rta_cumcals.html')
    print('saved cumcal image')
    return cumcal_fig


def create_rpvd_fig(df, races):
    print('Creating PACE V DIST figure')
    svd_traces, split_traces = [], []
    yrsago = [(datetime.datetime.utcnow() - rd).days / 365. for rd in [races[k] for k in races.keys()]]
    yrsago = [ya + 18 / 52. for ya in yrsago]  # add 18 weeks onto each race
    nyr = np.ceil(max(yrsago))
    nyr = max([nyr, 3])
    nyrs = datetime.timedelta(weeks=52 * nyr)
    aft = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - nyrs
    runs = df[(df['Type'] == 'Run') & (aft < df['Date'])]
    runs = runs[(runs['Dist (mi)'] > 2) & (runs['Pace (min/mi)'] < 15)]
    race_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + day_1
    days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
    dist, pace, dates = runs['Dist (mi)'].values, runs['Pace (min/mi)'].values, runs['Date'].values
    hovertext = [f'pace: {int(s)}:{str(int((s - int(s)) * 60)).zfill(2)} (min/mile)<br>date: {dates[i]}' for i, s in
                 enumerate(pace)]
    hovertemp = 'mileage: %{x:.2f}<br>%{text}'
    svd_traces.append(go.Scatter(x=dist, y=pace, mode='markers', name=f'past {nyr} years', text=hovertext,
                                 hovertemplate=hovertemp, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
    split_traces.append(go.Scatter(x=dist, y=runs['Split Shift (min/mile)'].values, mode='markers', text=hovertext,
                                   hovertemplate=hovertemp))
    svd_traces = add_max_effort_curve(svd_traces, max_dist=max(dist))  # add here so data only counted once
    recent, htemp = (dist[-1], pace[-1]), hovertemp
    htxt = f'pace: {int(pace[-1])}:{str(int((pace[-1] - int(pace[-1])) * 60)).zfill(2)} (min/mile)<br>date: {dates[-1]}'

    i, wktot, wktot_db, npdist, nppredays, wktot_dates = 0, [], [], np.array(dist), np.array(days_before), []
    nday_av = 14
    while -i - 7 > min(days_before):
        wktot.append(np.sum(npdist[(nppredays > -i - 7) & (nppredays <= -i)]))
        wktot_db.append(-i)
        wktot_dates.append(datetime.date.today() - datetime.timedelta(days=i))  # no min, sec, usec
        i += 1
    runav = [np.mean(wktot[i:i + nday_av]) for i in np.arange(len(wktot) - nday_av + 1)]
    # runav_db = wktot_db[:len(runav)]
    runav_dates = wktot_dates[:len(runav)]
    wklyav_data = [go.Scatter(x=wktot_dates, y=wktot, mode='lines', name='weekly total'),
                   go.Scatter(x=runav_dates, y=runav, mode='lines', name=f'{nday_av} day avg of tot',
                              line=dict(dash='dash'))]
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    xann = [rd for rd in [races[k] for k in races.keys()] if (rd - now).days < 0]
    yann = [wktot[i] for i in [-(rd - now).days for rd in [races[k] for k in races.keys()] if (rd - now).days < 0]]
    wklyav_data.append(go.Scatter(
        x=xann, y=yann, text=[k for k in races.keys() if (races[k] - now).days < 0], mode='text+markers',
        textposition='middle right', showlegend=False, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
    # wklyav_data.append(go.Bar(x=dates, y=dist, name='runs', marker=dict(color='black', line=dict(width=100))))
    wklyav_data.append(go.Scatter(x=dates, y=dist, name='runs', mode='markers'))

    for i, (k, v) in enumerate(races.items()):
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[(runs['Dist (mi)'] > 2) & (runs['Pace (min/mi)'] < 15)]
        dist, pace, dates = runs['Dist (mi)'].values, runs['Pace (min/mi)'].values, runs['Date'].values
        hovertext = [f'pace: {int(s)}:{str(int((s - int(s)) * 60)).zfill(2)} (min/mile)<br>date: {dates[i]}' for i, s in
                     enumerate(pace)]
        svd_traces.append(
            go.Scatter(x=dist, y=pace, mode='markers', name=k, text=hovertext, hovertemplate=hovertemp))
    svd_traces.append(go.Scatter(x=[recent[0]], y=[recent[1]], mode='markers', name='most recent',
                                 marker=dict(line=dict(width=3), color='rgba(0,0,0,0)', symbol='star-diamond-dot',
                                             size=10), text=[htxt], hovertemplate=htemp))
    svd_layout = go.Layout(xaxis=dict(title='Distance (miles)'),
                           yaxis=dict(title='Pace (min/mile)', hoverformat='.2f'),
                           legend=dict(bgcolor='rgba(0,0,0,0)'))
    pc_v_dist_fig = go.Figure(data=svd_traces, layout=svd_layout)
    pc_v_dist_fig.write_html(f'{img_path}rta_pvd.html')
    print('saved pace-vs-dist image')

    split_layout = go.Layout(xaxis=dict(title='Distance (miles)'),
                             yaxis=dict(title='change to av. splits (2nd-1st half) (min/mile)'))
    splits_fig = go.Figure(data=split_traces, layout=split_layout)
    splits_fig.write_html(f'{img_path}rta_splitsvsdist.html')
    print('saved splits-vs-dist image')

    wklyav_layout = go.Layout(yaxis=dict(title='Mileage', hoverformat='.2f'),
                              legend=dict(x=1, y=1, bgcolor='rgba(0,0,0,0)', xanchor='right', orientation='h'))
    wklyav_fig = go.Figure(data=wklyav_data, layout=wklyav_layout)
    wklyav_fig.write_html(f'{img_path}rta_wklyav.html')
    print('saved weekly average image')

    return pc_v_dist_fig, splits_fig, wklyav_fig


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
