import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize
from helpful_stuff import get_my_direc

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
        graphs.append(create_rman_fig(df, sho))
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
    clayout = go.Layout(xaxis=dict(title='Weeks before race', tickmode='array', tickvals=tvals, ticktext=ttext),
                        yaxis=dict(title='Distance (cumulative miles)'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'),
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
    split_traces.append(go.Scatter(x=dist, y=runs['Split Shift (min/mile)'].values, mode='markers', text=hovertext,
                                   hovertemplate=hovertemp))
    split_traces.append(go.Scatter(x=[dist[-1]], y=[runs['Split Shift (min/mile)'].values[-1]], mode='markers',
                                   marker=dict(line=dict(width=1), color='rgba(0,0,0,0)', symbol='star-diamond-dot',
                                               size=10)))
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

    for i, (k, v) in enumerate(races.items()):
        runs = df[(df['Type'] == 'Run') & (v - wks_18 < df['Date']) & (df['Date'] < v + day_1)]
        runs = runs[(runs['Dist (mi)'] > 2)]  # & (runs['Pace (min/mi)'] < 15)]
        dist, pace, dates = runs['Dist (mi)'].values, runs['Pace (min/mi)'].values, runs['Date'].values
        timevals = pace * dist / 60.  # hr
        prettydates = [pd.to_datetime(str(dates[i])) for i in range(len(dates))]
        prettydates = [ts.strftime('%d %b %Y %I:%M:%S %p') for ts in prettydates]
        hovertext = [f'pace: {int(s)}:{str(int((s - int(s)) * 60)).zfill(2)} (min/mile)<br>date: {prettydates[i]}' for
                     i, s in enumerate(pace)]
        pvd_traces.append(
            go.Scatter(x=dist, y=pace, mode='markers', name=k, text=hovertext, hovertemplate=hovertemp))
        pvt_traces.append(
            go.Scatter(x=timevals, y=pace, mode='markers', name=k, text=hovertext, hovertemplate=hovertemp))
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
                             yaxis=dict(title='change to av. splits (2nd-1st half) (min/mile)'))
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
    not_important = [bdist.extend(s.x) for s in pvd_traces]
    not_important = [bspeed.extend(s.y) for s in pvd_traces]
    bdist, bspeed = np.array(bdist), np.array(bspeed)

    bspeed = 60. / bspeed  # if inputting pace, convert to speed for fitting

    if 1:  # bent linear
        def minfunc1(fit):  #
            ydiff = bspeed - (fit[0] * bdist + fit[1])
            fit[1] += max(ydiff)  # push up above all pts
            return np.sum((ydiff - max(ydiff)) ** 2)

        fit1 = [-.06, 8.5]
        res = minimize(minfunc1, fit1, method='Nelder-Mead')
        fit1 = res.x
        ydiff = abs(bspeed - (fit1[0] * bdist + fit1[1]))
        ipt1 = np.where(ydiff == min(ydiff))[0][0]
        ipt2 = np.where(ydiff == min(np.delete(ydiff, ipt1)))[0][0]

        rpts, thpts = np.sqrt(bdist ** 2 + bspeed ** 2), np.arctan2(bspeed, bdist)
        throt = -np.arctan2(bspeed[ipt2] - bspeed[ipt1], bdist[ipt2] - bdist[ipt1])
        x2, y2 = rpts * np.cos(thpts + throt), rpts * np.sin(thpts + throt)
        xshift = np.mean([x2[ipt1], x2[ipt2]])  # center rotated pts about x=0
        x2 -= xshift

        def minfunc2(fit):
            ydiff = y2 - (fit[0] * x2 ** 2 + fit[1])
            fit[1] += max(ydiff)
            return np.sum((ydiff - max(ydiff)) ** 2)

        fit2 = [1.e-4, 0]
        res = minimize(minfunc2, fit2, method='Nelder-Mead')
        fit2 = res.x

        print(res.message)
        xx = 1.5 * np.linspace(min(x2), max(x2), endpoint=True)
        yy = fit2[0] * xx ** 2 + fit2[1]
        xx += xshift  # shift back in place
        rr, thth = np.sqrt(xx ** 2 + yy ** 2), np.arctan2(yy, xx)
        bill_dist, bill_speed = rr * np.cos(thth - throt), rr * np.sin(thth - throt)  # rotate back in place
        bill_pace = 60. / bill_speed  # [min/mile]

    # debugging:::
    # x = np.linspace(0, max(bdist))
    # plt.plot(bdist, bspeed, 'o')
    # plt.plot(x, fit1[0] * x + fit1[1])
    # for ip in [ipt1, ipt2]:
    # 	plt.plot(bdist[ip], bspeed[ip], 'x')
    # plt.plot(x2, y2, 'o')
    # plt.plot(x2, fit2[0] * x2 ** 2 + fit2[1])
    # plt.plot(bill_dist, bill_speed, 'x')

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


def create_rman_fig(df, sho):
    '''creates sweat rate, shoe mileage, comsumption plots'''
    analysis_startdate = datetime.datetime(2020, 9, 12, 0, 0, 0, 0)  # hard coded start date
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    man_fig = make_subplots(rows=4, cols=1, vertical_spacing=.12)

    # SWEAT RATE PLOT
    # restrict to runs between 4-10miles
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

    # LITERS/CALORIES CONSUMED
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
    man_fig.add_trace(
        go.Scatter(x=dur, y=.8 * dur, line_color=colors[2], showlegend=False), row=2, col=1)
    man_fig.add_trace(
        go.Scatter(x=dur, y=1. * dur, line_color=colors[2], fill='tonexty', showlegend=False), row=2, col=1)
    man_fig.add_trace(
        go.Scatter(x=duration_h, y=lit_cons, mode='markers', marker_color=colors[2],
                   showlegend=False, text=hovertext, hovertemplate=hovertemp1), row=2, col=1)  # fluid consumption
    man_fig.add_trace(go.Scatter(x=[duration_h[-1]], y=[lit_cons[-1]], mode='markers', name='most recent',
                                 marker=dict(line=dict(width=1), color=colors[2], symbol='star-diamond-dot',
                                             size=10), showlegend=False), row=2, col=1)

    # zone of good fueling
    man_fig.add_trace(
        go.Scatter(x=dur, y=150. * dur, line_color=colors[3], showlegend=False), row=3, col=1)
    man_fig.add_trace(
        go.Scatter(x=dur, y=200. * dur, line_color=colors[3], fill='tonexty', showlegend=False, ), row=3, col=1)
    man_fig.add_trace(
        go.Scatter(x=duration_h, y=cal_cons, mode='markers',
                   marker_color=colors[3], showlegend=False, text=hovertext,
                   hovertemplate=hovertemp2), row=3, col=1)  # calorie consumption
    man_fig.add_trace(go.Scatter(x=[duration_h[-1]], y=[cal_cons[-1]], mode='markers', name='most recent',
                                 marker=dict(line=dict(width=1), color=colors[3], symbol='star-diamond-dot',
                                             size=10), showlegend=False), row=3, col=1)

    # SHOE MILEAGE
    sho_dist, shoe_options = sho['cum_dist (mi)'].values, sho['shoe_options'].values
    hovertemp = '%{x:.0f} miles on %{y}<extra></extra>'  # <extra></extra> removes trace name from hover
    man_fig.add_trace(go.Bar(x=shoe_options, y=sho_dist, orientation='v', showlegend=False,
                             hovertemplate=hovertemp), row=4, col=1)  # shoe mileage
    # man_fig.add_trace(go.Bar(x=sho_dist, y=shoe_options, orientation='h', showlegend=False,
    #                          hovertemplate=hovertemp), row=2, col=1)  # shoe mileage
    # add rect for most recent activity
    # runs = df[(df['Type'] == 'Run') & (df['Date'] > analysis_startdate)]  # don't restrict milage to >4, <10
    # last_shoes, last_dist = runs['Shoes Worn'].values[-1], runs['Dist (mi)'].values[-1]
    # try:
    #     x1rect = sho_dist[shoe_options == last_shoes][0]
    #     x0rect = x1rect - last_dist
    #     yrect = np.where(shoe_options == last_shoes)[0][0]
    #     man_fig.add_shape(type='rect', x0=x0rect, y0=yrect - .5, x1=x1rect, y1=yrect + .5,
    #                       line=dict(width=2, color='black'), row=2, col=1)
    # except IndexError:  # most likely last activity wasn't a run
    #     pass

    yr = np.ceil(np.nanmax([np.nanmax(lit_cons), np.nanmax(cal_cons) / 500.]))
    man_fig.layout.update(height=1000, barmode='stack',
                          xaxis1=dict(title='Sweat Loss Rate (L/h)', range=[0, 3]),
                          xaxis2=dict(title='Duration (hr)'),
                          xaxis3=dict(title='Duration (hr)'),
                          yaxis1=dict(title='Count'),
                          yaxis2=dict(title='Liters Consumed', color=colors[2]),
                          yaxis3=dict(title='Calories Consumed', color=colors[3]),
                          yaxis4=dict(title='Miles on Shoes'),
                          showlegend=True, legend_title_text='Temp (F)')
    man_fig.update_yaxes(automargin=True)
    man_fig.write_html(f'{img_path}rta_man.html')
    print('saved manual analysis image')

    return man_fig


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
    # todo: add weighted running average (14-day? 7-day?)

    weightdf = df.dropna(axis=0, how='any', subset=['Date', 'End Weight (lb)'])
    date_arr = list(weightdf['Date'].values)
    endw_arr = list(weightdf['End Weight (lb)'].values)

    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + day_1
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # use of today vs now:
    # by adding a day to today, (raceday-today).days returns 1 for yesterday instead of 0 since timedelta < 1 day
    days_before = [(pd.Timestamp(val) - today).days for val in date_arr]
    # remove races before we have weight history data
    [races.pop(k) for k in list(races.keys()) if races[k] < pd.Timestamp(min(date_arr))]
    # remove races in the future
    [races.pop(k) for k in list(races.keys()) if races[k] > datetime.datetime.today()]

    traces = [go.Scatter(x=weightdf['Date'], y=weightdf['End Weight (lb)'], mode='lines', line=dict(dash='dash'),
                         showlegend=False),
              go.Scatter(x=weightdf['Date'], y=weightdf['End Weight (lb)'], mode='markers', showlegend=False)]
    xann = [rd for rd in [races[k] for k in races.keys()]]
    intx2 = [(rd - today).days for rd in [races[k] for k in races.keys()]]  # days before today for each race
    yann = np.interp(intx2, days_before, endw_arr)  # interpolated weights on race days
    traces.append(go.Scatter(
        x=xann, y=yann, text=[k for k in races.keys()], mode='text+markers',
        textposition='middle left', showlegend=False, marker=dict(color='red', line=dict(width=1))))

    playout = go.Layout(xaxis=dict(title='Date'), yaxis=dict(title='Weight (lb)'))
    weight_fig = go.Figure(data=traces, layout=playout)
    weight_fig.write_html(f'{img_path}rta_weighthist.html')
    print('saved weight history image')

    print('Creating weight2race figure')
    traces = []
    for i, (k, v) in enumerate(races.items()):
        # read: if race day is after today, ie in the future, then thicker line plot
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items()) * .75 + .25
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
