import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize
from helpful_stuff import get_my_direc, grn_ylw_red_colorscale

from posts.RaceTraining.app_tools import *

wks_18 = datetime.timedelta(weeks=18)
wks_1 = datetime.timedelta(weeks=1)
day_1 = datetime.timedelta(days=1)
ttext = [str(int(i)) for i in abs(-7 * np.arange(19) / 7)]
tvals = -7 * np.arange(19)


def fig_architect(df, sho, races, plots=None):
    df = df.sort_values(by=['Date'])  # put in chronological order
    graphs = []
    if 'weighthistory' in plots:
        [graphs.append(g) for g in create_weighthist_fig(df, races)]
    if 'rdist' in plots:
        graphs.append(create_rdist_fig(df, races))
    if 'rcumdist' in plots:
        # graphs.append(cumdist_v_weeks2race(df, races))
        graphs.append(cumulative_v_weeks2race(df, races))
    if 'rwk' in plots:
        # deprecated
        pass
    if 'rpace' in plots:
        graphs.append(create_rpace_fig(df, races))
    if 'rcumcal' in plots:
        graphs.append(cumcal_v_weeks2race(df, races))
    if 'rpvd' in plots:
        [graphs.append(g) for g in pace_v_dist_and_duration_splits_wklyavg(df, races)]
    if 'rswt' in plots:
        [graphs.append(g) for g in create_rman_fig(df, sho)]
    if 'rcalbytype' in plots:
        graphs.append(create_calbytype_fig(df))
    message = 'Analysis Complete'
    return graphs, message


img_path = get_my_direc(append='PycharmProjects/capecchi.github.io/images/posts/', err='cannot locate image path')


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
        runs = runs[(runs['Dist (mi)'] > 2)]  # & (runs['Pace (min/mi)'] < 15)]
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


def cumulative_v_weeks2race(df, races):
    print('Creating CUMDIST figure')
    traces = []
    ydist, ycals, ytime = [], [], []
    for i, (k, v) in enumerate(races.items()):
        # read: if race day is after today, ie in the future, then thicker line plot
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items()) * .75 + .25
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[
            (runs['Dist (mi)'] > 2)]  # & (runs['Pace (min/mi)'] < 15)]  # why'd I put this in? I run slo as hell
        race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
        days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
        cumdist = np.nancumsum(runs['Dist (mi)'].values)
        cumcals = np.nancumsum(runs['Calories'].values)
        cumtime = np.nancumsum(runs['Elapsed Time (sec)'].values) / 60. / 60.  # convert to hrs
        ydist.append(cumdist)
        ycals.append(cumcals)
        ytime.append(cumtime)
        hovertext = [f'days to race: {abs(x)}<br>total miles: {y:.2f}' for (x, y) in
                     zip(days_before, cumdist)]
        hovertemp = '%{text}'
        traces.append(
            go.Scatter(x=days_before, y=cumdist, opacity=op, name=k, hovertemplate=hovertemp, text=hovertext,
                       mode='lines+markers', line=dict(width=width)))
    # traces.append(
    #     go.Scatter(x=[t.x[-1] for t in traces if len(t.x) > 0], y=[t.y[-1] for t in traces if len(t.y) > 0],
    #                text=[f'{round(t.y[-1], 1)}' for t in traces if len(t.y) > 0], mode='text',
    #                textposition='middle left', showlegend=False, hoverinfo='none'))
    butt_dist = dict(method="update", args=[{'y': ydist}, {'yaxis.title': 'Distance (cumulative miles)'}],
                     label='Distance')
    butt_cals = dict(method="update", args=[{'y': ycals}, {'yaxis.title': 'Calories (cumulative)'}], label='Calories')
    butt_time = dict(method="update", args=[{'y': ytime}, {'yaxis.title': 'Elapsed Time (cumulative hours)'}],
                     label='Elapsed Time')
    # lgnd = dict(x=0, y=1, bgcolor='rgba(0,0,0,0)')
    lgnd = dict(bgcolor='rgba(0,0,0,0)')
    clayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
                        yaxis=dict(title='Distance (cumulative miles)'), legend=lgnd,
                        updatemenus=[dict(active=0, buttons=[butt_dist, butt_cals, butt_time])])
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
        runs = runs[(runs['Dist (mi)'] > 2)]  # & (runs['Pace (min/mi)'] < 15)]
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


def cumcal_v_weeks2race(df, races):
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
        runs = runs[(runs['Dist (mi)'] > 2)]  # & (runs['Pace (min/mi)'] < 15)]
        race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
        days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
        cumcals = np.nancumsum(runs['Calories'].values)
        hovertext = [f'days to race: {abs(x)}<br>total cals: {y}' for (x, y) in
                     zip(days_before, cumcals)]
        hovertemp = '%{text}'
        traces.append(go.Scatter(x=days_before, y=cumcals, opacity=op, name=k, hovertemplate=hovertemp, text=hovertext,
                                 mode='lines+markers', line=dict(width=width)))
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


def pace_v_dist_and_duration_splits_wklyavg(df, races):
    print('Creating PACE V DIST, PACE V DURATION, SPLITS, and WEEKLY AVERAGE figures')
    pvd_traces, split_traces, pvt_traces = [], [], []
    yrsago = [(datetime.datetime.utcnow() - rd).days / 365. for rd in [races[k] for k in races.keys()]]
    yrsago = [ya + 18 / 52. for ya in yrsago]  # add 18 weeks onto each race
    nyr = np.ceil(max(yrsago))
    nyr = max([nyr, 3])
    nyrs = datetime.timedelta(weeks=52 * nyr)
    aft = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - nyrs
    runs = df[(df['Type'] == 'Run') & (aft < df['Date'])]
    runs = runs[(runs['Dist (mi)'] > 2)]  # & (runs['Pace (min/mi)'] < 15)]
    race_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + day_1
    days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
    dist, pace, dates = runs['Dist (mi)'].values, runs['Pace (min/mi)'].values, runs['Date'].values
    timevals = pace * dist / 60.  # hr
    prettydates = [pd.to_datetime(str(dates[i])) for i in range(len(pace))]
    prettydates = [ts.strftime('%d %b %Y %I:%M:%S %p') for ts in prettydates]
    hovertext = [f'pace: {int(s)}:{str(int((s - int(s)) * 60)).zfill(2)} (min/mile)<br>date: {prettydates[i]}' for i, s
                 in
                 enumerate(pace)]
    hovertemp = 'mileage: %{x:.2f}<br>%{text}'
    pvd_traces.append(go.Scatter(x=dist, y=pace, mode='markers', name=f'past {nyr} years', text=hovertext,
                                 hovertemplate=hovertemp, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
    pvt_traces.append(go.Scatter(x=timevals, y=pace, mode='markers', name=f'past {nyr} years', text=hovertext,
                                 hovertemplate=hovertemp, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
    sort_splits = sorted(zip(runs['Split Shift (min/mile)'].values, dist))  # tuple list of [(split, dist), ...]
    sorted_split, sorted_dist = [s[0] for s in sort_splits], [s[1] for s in sort_splits]
    split_traces.append(go.Scatter(x=sorted_dist, y=sorted_split, mode='markers', text=hovertext,
                                   hovertemplate=hovertemp, showlegend=False,
                                   marker=dict(line=dict(width=.5, color='black'), color=sorted_split, cmin=-5, cmax=5,
                                               colorscale='rdylgn_r')))
    split_traces.append(go.Scatter(x=[dist[-1]], y=[runs['Split Shift (min/mile)'].values[-1]], mode='markers',
                                   marker=dict(line=dict(width=1), color='rgba(0,0,0,0)', symbol='star-diamond-dot',
                                               size=10), showlegend=False))
    pvd_traces, pvt_traces = add_max_effort_curve(pvd_traces, pvt_traces,
                                                  max_dist=max(dist))  # add here so data only counted once
    recent, htemp = (dist[-1], pace[-1]), hovertemp
    htxt = f'pace: {int(pace[-1])}:{str(int((pace[-1] - int(pace[-1])) * 60)).zfill(2)} (min/mile)<br>date: {prettydates[-1]}'

    i, wktot, wktot_db, npdist, nppredays, wktot_dates = 0, [], [], np.array(dist), np.array(days_before), []
    nday_av = 14
    while -i - 7 > min(days_before):
        wktot.append(np.sum(npdist[(nppredays > -i - 7) & (nppredays <= -i)]))
        wktot_db.append(-i)
        wktot_dates.append(datetime.date.today() - datetime.timedelta(days=i))  # no min, sec, usec
        i += 1
    runav = [np.mean(wktot[i:i + nday_av]) for i in np.arange(len(wktot) - nday_av + 1)]
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
    wklyav_data.append(go.Scatter(x=dates, y=dist, name='runs', mode='markers'))

    for i, (k, v) in enumerate(races.items()):  # add race specific data
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[(runs['Dist (mi)'] > 2)]  # & (runs['Pace (min/mi)'] < 15)]
        rs_dist, rs_pace, rs_dates = runs['Dist (mi)'].values, runs['Pace (min/mi)'].values, runs['Date'].values
        rs_timevals = rs_pace * rs_dist / 60.  # hr
        rs_prettydates = [pd.to_datetime(str(rs_dates[i])) for i in range(len(rs_dates))]
        rs_prettydates = [ts.strftime('%d %b %Y %I:%M:%S %p') for ts in rs_prettydates]
        rs_hovertext = [f'pace: {int(s)}:{str(int((s - int(s)) * 60)).zfill(2)} (min/mile)<br>date: {rs_prettydates[i]}'
                        for i, s in enumerate(rs_pace)]
        pvd_traces.append(
            go.Scatter(x=rs_dist, y=rs_pace, mode='markers', name=k, text=rs_hovertext, hovertemplate=hovertemp))
        pvt_traces.append(
            go.Scatter(x=rs_timevals, y=rs_pace, mode='markers', name=k, text=rs_hovertext, hovertemplate=hovertemp))
    pvd_traces.append(go.Scatter(x=[recent[0]], y=[recent[1]], mode='markers', name='most recent',
                                 marker=dict(line=dict(width=1), color='rgba(0,0,0,0)', symbol='star-diamond-dot',
                                             size=10), text=[htxt], hovertemplate=htemp))
    pvt_traces.append(go.Scatter(x=[timevals[-1]], y=[pace[-1]], mode='markers', name='most recent',
                                 marker=dict(line=dict(width=1), color='rgba(0,0,0,0)', symbol='star-diamond-dot',
                                             size=10), text=[htxt], hovertemplate=htemp))
    pvd_layout = go.Layout(xaxis=dict(title='Distance (miles)'),
                           yaxis=dict(title='Pace (min/mile)', hoverformat='.2f'),
                           legend=dict(bgcolor='rgba(0,0,0,0)'))
    pc_v_dist_fig = go.Figure(data=pvd_traces, layout=pvd_layout)
    pc_v_dist_fig.write_html(f'{img_path}rta_pvd.html')
    print('saved pace-vs-dist image')

    pvt_layout = go.Layout(xaxis=dict(title='Duration (hr)'),
                           yaxis=dict(title='Pace (min/mile)', hoverformat='.2f'),
                           legend=dict(bgcolor='rgba(0,0,0,0)'))
    pc_v_time_fig = go.Figure(data=pvt_traces, layout=pvt_layout)
    pc_v_time_fig.write_html(f'{img_path}rta_pvt.html')
    print('saved pace-vs-duration image')

    split_layout = go.Layout(xaxis=dict(title='Distance (miles)'),
                             yaxis=dict(title='change to av. splits (2nd-1st half) (min/mile)', range=[-5, 5]))
    splits_fig = go.Figure(data=split_traces, layout=split_layout)
    splits_fig.write_html(f'{img_path}rta_splitsvsdist.html')
    print('saved splits-vs-dist image')

    wklyav_layout = go.Layout(yaxis=dict(title='Mileage', hoverformat='.2f'),
                              legend=dict(x=1, y=1, bgcolor='rgba(0,0,0,0)', xanchor='right', orientation='h'))
    wklyav_fig = go.Figure(data=wklyav_data, layout=wklyav_layout)
    wklyav_fig.write_html(f'{img_path}rta_wklyav.html')
    print('saved weekly average image')

    return pc_v_dist_fig, pc_v_time_fig, splits_fig, wklyav_fig


def add_max_effort_curve(pvd_traces, pvt_traces, max_dist=100):
    max_dist_km = max_dist * 1.60934  # convert miles to km
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
        return spd * time / 60. / 60. - max_dist_km

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
    bdist, bpace = [], []  # miles, min/mile
    not_important = [bdist.extend(s.x) for s in pvd_traces]
    not_important = [bpace.extend(s.y) for s in pvd_traces]
    bdist, bpace = np.array(bdist), np.array(bpace)

    # bin and keep only highest in range
    xbin, dist_max, pace_max = 2, [], []  # size [miles] of bin
    for xb in np.arange(0, max_dist, xbin):
        if len(bpace[(bdist >= xb) & (bdist < xb + xbin)]) > 0:  # check to ensure data exists in this range
            imax = \
                np.where(bpace[(bdist >= xb) & (bdist < xb + xbin)] == min(bpace[(bdist >= xb) & (bdist < xb + xbin)]))[
                    0][
                    0]  # (note fastest pace means min(pace))
            dist_max.append(bdist[(bdist >= xb) & (bdist < xb + xbin)][imax])
            pace_max.append(bpace[(bdist >= xb) & (bdist < xb + xbin)][imax])
    bdist, bpace = np.array(dist_max), np.array(pace_max)

    bspeed = 60. / bpace  # if inputting pace, convert to speed for fitting

    if 1:  # 1/x fit
        def minfunc(fit):  # fit = [a, b, c] = a/(x-b) + c
            ydiff = bspeed - (fit[0] / (bdist - fit[1]) + fit[2])
            return np.sum((ydiff - max(ydiff)) ** 2)

        fitin = [223., -30., 2.]  # close guess based off previous fits
        res = minimize(minfunc, fitin, method='Nelder-Mead')
        fit = res.x
        fit[2] += max(bspeed - (fit[0] / (bdist - fit[1]) + fit[2]))
        print(res.message)
        print(f'asymptotic pace is {60. / fit[2]:.2f} min/mile')
        bill_dist = np.linspace(min(bdist), max(bdist) + 5)
        bill_speed = fit[0] / (bill_dist - fit[1]) + fit[2]
        bill_pace = 60. / bill_speed  # [min/mile]

    hovertext = [f'{int(bp)}:{str(int((bp - int(bp)) * 60)).zfill(2)}' for bp in bill_pace]

    plotdist = np.arange(int(min(bdist)), int(max(bdist)) + 2)
    plotpacevdist = np.interp(plotdist, bill_dist, bill_pace)
    plotdura = np.arange(0, int(max(bdist / bspeed)) + 1, .5)
    plotpacevdura = np.interp(plotdura, bill_dist / bill_speed, bill_pace)

    pvd_traces.append(
        go.Scatter(x=plotdist, y=plotpacevdist, mode='lines', line=dict(width=2), name='Max Effort (Bill)',
                   hovertemplate='mileage: %{x}<br>pace: %{text} (min/mile)',
                   text=hovertext))
    pvt_traces.append(
        go.Scatter(x=plotdura, y=plotpacevdura, mode='lines', line=dict(width=2),
                   name='Max Effort (Bill)',
                   hovertemplate='Duration: %{x} (hr)<br>pace: %{text} (min/mile)',
                   text=hovertext))
    minetti_pace = 60. / minetti_spd  # min/mile
    pvd_traces.append(
        go.Scatter(x=minetti_dst, y=minetti_pace, mode='lines', line=dict(width=2),
                   name='Max Effort (Human) [Minetti]', visible='legendonly'))
    pvt_traces.append(go.Scatter(x=minetti_dst * minetti_pace / 60., y=minetti_pace, mode='lines', line=dict(width=2),
                                 name='Max Effort (Human) [Minetti]', visible='legendonly'))
    return pvd_traces, pvt_traces


def create_rman_fig(df, sho, consumption=False):
    '''creates sweat rate, shoe mileage, comsumption plots'''
    # deprecating consumption plots May 2024
    analysis_startdate = datetime.datetime(2020, 9, 12, 0, 0, 0, 0)  # hard coded start date
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS

    # SWEAT RATE PLOT
    # restrict to runs between 4-10miles
    swt_fig = go.Figure()
    runs = df[
        (df['Type'] == 'Run') & (df['Dist (mi)'] >= 4) & (df['Dist (mi)'] <= 10) & (df['Date'] > analysis_startdate)]
    nptemp, npswt = runs['Temp (F)'].values, runs['Sweat Loss Rate (L/h)'].values
    # drop nan values
    bool_notnan = ~np.isnan(nptemp) & ~np.isnan(npswt)
    nptemp, npswt = nptemp[bool_notnan], npswt[bool_notnan]
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
        swt_fig.add_trace(
            go.Histogram(x=npswt[np.where((rangelist[i] <= nptemp) & (nptemp < rangelist[i + 1]))],
                         xbins=dict(start=0, end=3.0, size=0.1), marker=dict(color=rb[i], line=dict(width=0.5)),
                         name=lbl))
        if rangelist[i] <= nptemp[-1] < rangelist[i + 1]:
            lastrunbin = (np.floor(npswt[-1] * 10.) / 10., np.ceil(npswt[-1] * 10.) / 10.)
            # count number where sweatrate is in bin, and temp is below current rangelist bin max so we overlay properly
            numinlastbin = len(
                np.where((npswt < lastrunbin[1]) & (npswt >= lastrunbin[0]) & (nptemp < rangelist[i + 1]))[0])
    swt_fig.add_shape(type='rect', x0=lastrunbin[0], y0=numinlastbin - 1, x1=lastrunbin[1], y1=numinlastbin,
                      line=dict(width=2, color='black'))
    swt_fig.layout.update(barmode='stack', xaxis=dict(title='Sweat Loss Rate (L/h)', range=[0, 2.5]),
                          yaxis1=dict(title='Count'), showlegend=True, legend_title_text='Temp (F)')

    if consumption:
        # LITERS/CALORIES CONSUMED
        cons_fig = make_subplots(rows=2, cols=1, vertical_spacing=.12)
        runs = df.dropna(axis=0, how='any', subset=['Liters Consumed', 'Calories Consumed'])
        runs = runs[(runs['Date'] > analysis_startdate) & (runs['Type'] == 'Run')]
        lit_cons, cal_cons = runs['Liters Consumed'].values, runs['Calories Consumed'].values
        carbs, pace = runs['Carbs Consumed (g)'].values, runs['Pace (min/mi)'].values  # carbs will have nans
        runids, dates, dist = runs['runid'].values, runs['Date'].values, runs['Dist (mi)'].values
        duration_h = pace * dist / 60.  # convert to hours
        prettydates = [pd.to_datetime(str(dates[i])) for i in range(len(pace))]
        prettydates = [ts.strftime('%d %b %Y %I:%M:%S %p') for ts in prettydates]

        hovertext = [f'runid: {r}<br>date: {d}<br>dist: {dd:.1f}' for (r, d, dd) in zip(runids, prettydates, dist)]
        hovertemp1 = '%{text}<br>liters: %{y}<extra></extra>'
        hovertemp2 = '%{text}<br>cals: %{y}<extra></extra>'
        dur = np.sort(duration_h)

        # zone of good hydration
        cons_fig.add_trace(
            go.Scatter(x=dur, y=.8 * dur, line_color=colors[2], showlegend=False), row=1, col=1)
        cons_fig.add_trace(
            go.Scatter(x=dur, y=1. * dur, line_color=colors[2], fill='tonexty', showlegend=False), row=1, col=1)
        cons_fig.add_trace(
            go.Scatter(x=duration_h, y=lit_cons, mode='markers', marker_color=colors[2],
                       showlegend=False, text=hovertext, hovertemplate=hovertemp1), row=1, col=1)  # fluid consumption
        cons_fig.add_trace(go.Scatter(x=[duration_h[-1]], y=[lit_cons[-1]], mode='markers', name='most recent',
                                      marker=dict(line=dict(width=1), color=colors[2], symbol='star-diamond-dot',
                                                  size=10), showlegend=False), row=1, col=1)

        # zone of good fueling
        cons_fig.add_trace(
            go.Scatter(x=dur, y=150. * dur, line_color=colors[3], showlegend=False), row=2, col=1)
        cons_fig.add_trace(
            go.Scatter(x=dur, y=200. * dur, line_color=colors[3], fill='tonexty', showlegend=False, ), row=2, col=1)
        cons_fig.add_trace(
            go.Scatter(x=duration_h, y=cal_cons, mode='markers',
                       marker_color=colors[3], showlegend=False, text=hovertext,
                       hovertemplate=hovertemp2), row=2, col=1)  # calorie consumption
        cons_fig.add_trace(go.Scatter(x=[duration_h[-1]], y=[cal_cons[-1]], mode='markers', name='most recent',
                                      marker=dict(line=dict(width=1), color=colors[3], symbol='star-diamond-dot',
                                                  size=10), showlegend=False), row=2, col=1)
        yr = np.ceil(np.nanmax([np.nanmax(lit_cons), np.nanmax(cal_cons) / 500.]))
        cons_fig.layout.update(height=750,
                               xaxis1=dict(title='Duration (hr)'),
                               xaxis2=dict(title='Duration (hr)'),
                               yaxis1=dict(title='Liters Consumed', color=colors[2]),
                               yaxis2=dict(title='Calories Consumed', color=colors[3]))
        cons_fig.update_yaxes(automargin=True)
        cons_fig.write_html(f'{img_path}rta_consumption.html')

    # SHOE MILEAGE
    sho_dist, shoe_options = sho['cum_dist (mi)'].values, sho['shoe_options'].values
    hovertemp = '%{y:.0f} miles on %{x}<extra></extra>'  # <extra></extra> removes trace name from hover
    sho_trace = [go.Bar(x=shoe_options, y=sho_dist, orientation='v', showlegend=False, hovertemplate=hovertemp,
                        marker=dict(color=sho_dist, colorscale=grn_ylw_red_colorscale(max=500 / max(sho_dist)),
                                    showscale=True, colorbar=dict(title='Mileage')))]  # shoe mileage
    sho_fig = go.Figure(data=sho_trace, layout=go.Layout(yaxis=dict(title='Mileage', hoverformat='.2f')))
    # add rect for most recent activity
    runs = df[(df['Type'] == 'Run') & (df['Date'] > analysis_startdate)]  # don't restrict milage to >4, <10
    last_shoes, last_dist = runs['Shoes Worn'].values[-1], runs['Dist (mi)'].values[-1]
    try:
        y1rect = sho_dist[shoe_options == last_shoes][0]
        y0rect = y1rect - last_dist
        xrect = np.where(shoe_options == last_shoes)[0][0]

        sho_fig.add_shape(type='rect', x0=xrect - .5, y0=y0rect, x1=xrect + .5, y1=y1rect,
                          line=dict(width=2, color='black'))
    except IndexError:  # most likely last activity wasn't a run
        pass

    swt_fig.write_html(f'{img_path}rta_sweatrate.html')
    sho_fig.write_html(f'{img_path}sho_mileage.html')
    print('saved manual analysis images')

    if consumption:
        return swt_fig, cons_fig, sho_fig
    else:
        return swt_fig, sho_fig


def create_calbytype_fig(df):
    race_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    runs = df[(race_day - wks_18 < df['Date']) & (df['Date'] < race_day + day_1)]
    days_before = np.array([(pd.Timestamp(val) - race_day).days for val in runs['Date'].values])
    cals, types = runs['Calories'].values, runs['Type'].values

    calbytype_fig = make_subplots(rows=2, cols=1, vertical_spacing=.05, shared_xaxes=True)
    current_day_of_week = race_day.weekday()  # 0=Monday=Start of training week

    cols = plotly.colors.DEFAULT_PLOTLY_COLORS
    for i, typ in enumerate(np.unique(types)):
        typecals = np.zeros_like(cals)
        typecals[types == typ] = cals[types == typ]
        calbytype_fig.add_trace(
            go.Scatter(x=days_before, y=np.cumsum(typecals), mode='lines', line=dict(color=cols[i]),
                       showlegend=False, ), row=1, col=1)
        calbytype_fig.add_trace(
            go.Scatter(x=days_before[types == typ], y=np.cumsum(typecals)[types == typ], mode='markers',
                       marker=dict(color=cols[i]), showlegend=False), row=1, col=1)
        calbytype_fig.add_trace(
            go.Histogram(x=days_before[types == typ], name=typ,
                         xbins=dict(start=-7 * 18 - current_day_of_week, end=7 - current_day_of_week, size=7),
                         marker_color=cols[i]), row=2, col=1)
    calbytype_fig.layout.update(height=750, barmode='stack',  # 0.5 in tickvals to place grid between bins
                                xaxis1=dict(tickmode='array', tickvals=-7 * np.arange(19) - current_day_of_week - .5),
                                xaxis2=dict(title='Weeks Ago', tickmode='array', tickvals=-7 * np.arange(19),
                                            ticktext=[str(int(i)) for i in abs(-7 * np.arange(19) / 7)]),
                                yaxis1=dict(title='Calories\n(cumulative)'),
                                yaxis2=dict(title='Activities per Week'))
    calbytype_fig.update_yaxes(automargin=True)

    calbytype_fig.write_html(f'{img_path}rta_calbytype.html')
    print('saved calbytype image')
    return calbytype_fig


def create_weighthist_fig(df, races):
    weightdf = df.dropna(axis=0, how='any', subset=['Date', 'End Weight (lb)'])
    date_arr = list(weightdf['Date'].values)
    endw_arr = list(weightdf['End Weight (lb)'].values)

    rr = races.copy()  # make a copy here so other plots aren't affected
    rr2 = races.copy()
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + day_1
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # use of today vs now:
    # by adding a day to today, (raceday-today).days returns 1 for yesterday instead of 0 since timedelta < 1 day
    days_before = [(pd.Timestamp(val) - today).days for val in date_arr]
    # remove races before we have weight history data
    [rr.pop(k) for k in list(rr.keys()) if rr[k] < pd.Timestamp(min(date_arr))]
    # remove races in the future
    [rr.pop(k) for k in list(rr.keys()) if rr[k] > now]
    # remove races > 18wks in future
    [rr2.pop(k) for k in list(rr2.keys()) if rr2[k] > now + datetime.timedelta(weeks=18)]

    xann = [rd for rd in [rr[k] for k in rr.keys()]]
    intx2 = [(rd - today).days for rd in [rr[k] for k in rr.keys()]]  # days before today for each race
    yann = np.interp(intx2, days_before, endw_arr)  # interpolated weights on race days

    dns = float(date_arr[-1] - date_arr[0])  # ns between first/last weight value
    ns_vals = [d - min(date_arr) for d in date_arr]
    ndays = int(dns / 1.e9 / 60 / 60 / 24)  # convert elapsed ns to elapsed num of days
    xx = np.linspace(0, dns, num=ndays)
    xd = [pd.Timestamp(min(date_arr) + np.timedelta64(int(x), 'ns')) for x in xx]
    yy = np.interp(xx, ns_vals, endw_arr)
    nday_avg = 21
    avg_x = xd[nday_avg - 1:]
    avg_y = np.zeros_like(avg_x)
    for i in np.arange(len(avg_x)):
        avg_y[i] = np.average(yy[i:i + nday_avg], weights=np.arange(1, nday_avg + 1))
    traces = [go.Scatter(x=avg_x, y=avg_y, mode='lines', name=f'{nday_avg} day WME'),
              go.Scatter(x=weightdf['Date'], y=weightdf['End Weight (lb)'], mode='markers', showlegend=False)]
    traces.append(go.Scatter(
        x=xann, y=yann, text=[k for k in rr.keys()], mode='text+markers',
        textposition='middle left', showlegend=False, marker=dict(color='red', line=dict(width=1))))
    playout = go.Layout(xaxis=dict(title='Date'), yaxis=dict(title='Weight (lb)'),
                        legend=dict(x=1, y=1, bgcolor='rgba(0,0,0,0)', xanchor='right', orientation='h'))
    weight_fig = go.Figure(data=traces, layout=playout)
    weight_fig.write_html(f'{img_path}rta_weighthist.html')
    print('saved weight history image')

    print('Creating weight2race figure')
    traces = []
    for i, (k, v) in enumerate(rr2.items()):
        # read: if race day is after today, ie in the future, then thicker line plot
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(rr2.items()) * .75 + .25
        runs = weightdf[(weightdf['Type'] == 'Run') & (v - wks_18 < weightdf['Date']) & (weightdf['Date'] < v + day_1)]
        race_day = (v + day_1).replace(hour=0, minute=0, second=0, microsecond=0)
        days_before = [(pd.Timestamp(val) - race_day).days for val in runs['Date'].values]
        weight2race = runs['End Weight (lb)'].values
        hovertext = [f'days to race: {abs(x)}<br>weight: {y} (lb)' for (x, y) in
                     zip(days_before, weight2race)]
        hovertemp = '%{text}'
        traces.append(
            go.Scatter(x=days_before, y=weight2race, opacity=op, name=k, hovertemplate=hovertemp, text=hovertext,
                       mode='lines+markers', line=dict(width=width)))
    weight2racelay = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
                               yaxis=dict(title='Weight (lb)'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
    weight2racefig = go.Figure(data=traces, layout=weight2racelay)
    weight2racefig.write_html(f'{img_path}rta_weight2race.html')
    print('saved weight2race image')

    return weight_fig, weight2racefig
