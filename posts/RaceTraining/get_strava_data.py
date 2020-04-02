import plotly
from stravalib import unithelper
import numpy as np
from scipy.optimize import minimize
from stravalib.client import Client
import datetime
from collections import OrderedDict
import plotly.graph_objs as go
import stravalib.exc
import matplotlib.pyplot as plt


def get_client(code):
    client_id = 34049
    client_secret = '2265a983040000b3b865a0fc333f41cd701dcb5f'

    client = Client()
    client.authorization_url(34049, 'http://localhost:8080', scope='activity:read_all')
    token_response = client.exchange_code_for_token(client_id, client_secret, code)
    client.access_token = token_response['access_token']
    client.refresh_token = token_response['refresh_token']
    return client


def get_training_data(client, after=datetime.date.today() - datetime.timedelta(days=7), before=datetime.date.today()):
    race_day = before - datetime.timedelta(days=1)

    activities = client.get_activities(after=after, before=before)
    try:
        activities = list(activities)
        runs = [act for act in activities[::-1] if act.type == 'Run']  # reverse order so they're chronological
        days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
        dist = [unithelper.miles(r.distance).num for r in runs]
        cum = np.cumsum(dist)
        pace = [60. / unithelper.miles_per_hour(r.average_speed).num for r in runs]  # min/mile
        speed = [60 / p for p in pace]  # mph
        return days_before, dist, cum, pace, speed
    except stravalib.exc.Fault:
        return None, None, None, None


def get_past_races(trail=True, road=True):
    races = OrderedDict({})
    if trail:
        races.update({'Superior 50k 2018': datetime.datetime(2018, 5, 19),
                      'Driftless 50k 2018': datetime.datetime(2018, 9, 29),
                      'Superior 50k 2019': datetime.datetime(2019, 5, 18)})
    if road:
        races.update({'TC Marathon 2014': datetime.datetime(2014, 10, 5),
                      'Madison Marathon 2014': datetime.datetime(2014, 11, 9),
                      'TC Marathon 2015': datetime.datetime(2015, 10, 4)})
    return races


def gather_training_seasons(code, rdist=False, rcum=True, rwk=False, rpace=False, rsvd=True):
    races = get_past_races(trail=True, road=False)
    races.update({'Dirty German 50k': datetime.datetime(2020, 5, 9)})
    # 'Shawangunk Ridge 50M': datetime.datetime(2020, 9, 12)})

    wks_18 = datetime.timedelta(weeks=18)
    day_1 = datetime.timedelta(days=1)
    wks_1 = datetime.timedelta(weeks=1)

    ref_day = min(datetime.datetime.now(), races[list(races.keys())[-1]])
    days_to_race = datetime.timedelta(days=(races[list(races.keys())[-1]] - ref_day).days)
    client = get_client(code)

    dist_traces = []
    cum_traces = []
    pace_traces = []
    wk_traces = []
    svd_traces = []  # speed vs dist
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    max_dist = 0
    for i, (k, v) in enumerate(races.items()):
        print(k)
        if v > datetime.datetime.today():  # read: if race day is after today, ie in the future, then solid line plot
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items())
        days_before, dist, cum, pace, speed = get_training_data(client, v - wks_18, v + day_1)
        max_dist = max([max(dist), max_dist])
        if rsvd:
            bill_pace = 60. / np.array(speed)  # min/mile
            hovertext = [f'{int(s)}:{str(int((s - int(s)) * 60)).zfill(2)}' for s in bill_pace]
            hovertemp = 'mileage: %{x:.2f}<br>pace: %{text} (min/mile)'
            svd_traces.append(go.Scatter(x=dist, y=speed, mode='markers', name=k, text=hovertext,
                                         hovertemplate=hovertemp))
            if i == len(races.items()) - 1:
                svd_traces.append(go.Scatter(x=[dist[-1]], y=[speed[-1]], mode='markers', name='most recent',
                                             marker=dict(line=dict(width=2), color='rgba(0,0,0,0)'),
                                             text=[hovertext[-1]], hovertemplate=hovertemp))
        if rdist:
            dist_traces.append(
                go.Scatter(x=days_before, y=dist, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
        if rcum:
            cum_traces.append(
                go.Scatter(x=days_before, y=cum, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
        if rpace:
            pace_traces.append(
                go.Scatter(x=days_before, y=pace, opacity=op, name=k, mode='lines+markers', line=dict(width=width),
                           hovertemplate='pace: %{y:.2f}<br>dist:%{text}', text=['{:.2f}'.format(d) for d in dist]))
        if rwk:
            wdb, wd, wc, wp, ws = get_training_data(client, v - days_to_race - wks_1, v - days_to_race)
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

    svd_traces = add_max_effort_curve(svd_traces, max_dist=max_dist)

    # append annotation traces
    if rdist:
        dist_arr = [t.y[-1] for t in dist_traces if len(t.y) > 0]
        dist_traces.append(go.Scatter(x=[t.x[-1] for t in dist_traces if len(t.x) > 0], y=dist_arr,
                                      text=[f'{round(t.y[-1], 1)}' for t in dist_traces if len(t.y) > 0], mode='text',
                                      textposition='middle left', showlegend=False, hoverinfo='none'))
    if rcum:
        cum_traces.append(
            go.Scatter(x=[t.x[-1] for t in cum_traces if len(t.x) > 0], y=[t.y[-1] for t in cum_traces if len(t.y) > 0],
                       text=[f'{round(t.y[-1], 1)}' for t in cum_traces if len(t.y) > 0], mode='text',
                       textposition='middle left', showlegend=False, hoverinfo='none'))
    if rpace:
        pace_traces.append(
            go.Scatter(x=[t.x[-1] for t in pace_traces if len(t.x) > 0],
                       y=[t.y[-1] for t in pace_traces if len(t.y) > 0],
                       text=[f'{round(t.y[-1], 1)}' for t in pace_traces if len(t.y) > 0], mode='text',
                       textposition='middle left', showlegend=False, hoverinfo='none'))
    if rwk:
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
    img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
    if rsvd:
        svd_layout = go.Layout(xaxis=dict(title='Distance (miles)'),
                               yaxis=dict(title='Speed (miles/hr)', hoverformat='.2f'),
                               legend=dict(x=1, y=1, bgcolor='rgba(0,0,0,0)', xanchor='right'))
        pc_v_dist_fig = go.Figure(data=svd_traces, layout=svd_layout)
        pc_v_dist_fig.write_html(f'{img_path}rta_svd.html')
        print('saved speed-vs-dist image')
        figs.append(pc_v_dist_fig)
    if rdist:
        dlayout = go.Layout(xaxis=dict(title='Days before race'),
                            yaxis=dict(title='Distance (miles)', hoverformat='.2f'),
                            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
        dist_fig = go.Figure(data=dist_traces, layout=dlayout)
        dist_fig.write_html(f'{img_path}rta_dist.html')
        print('saved dist image')
        figs.append(dist_fig)
    if rcum:
        clayout = go.Layout(xaxis=dict(title='Days before race'), yaxis=dict(title='Cumulative (miles)'),
                            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
        cum_fig = go.Figure(data=cum_traces, layout=clayout)
        cum_fig.write_html(f'{img_path}rta_cum.html')
        print('saved cum image')
        figs.append(cum_fig)
    if rpace:
        playout = go.Layout(xaxis=dict(title='Days before race'), yaxis=dict(title='Pace (min/mile)'),
                            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
        pace_fig = go.Figure(data=pace_traces, layout=playout)
        pace_fig.write_html(f'{img_path}rta_pace.html')
        print('saved pace image')
        figs.append(pace_fig)
    if rwk:
        wlayout = go.Layout(legend=dict(orientation='h', y=1.1), xaxis=dict(title='Prior week training', ),
                            yaxis=dict(title='Distance', domain=[0., .3], ),
                            yaxis2=dict(title='Cumulative', domain=[0.35, 0.65]),
                            yaxis3=dict(title='Pace', domain=[0.7, 1.], ), )
        wk_fig = go.Figure(data=wk_traces, layout=wlayout)
        wk_fig.write_html(f'{img_path}rta_week.html')
        print('saved week image')
        figs.append(wk_fig)

    return figs


def add_max_effort_curve(svd_traces, max_dist=100, minetti=True):
    if minetti:
        max_dist *= 1.60934  # convert miles to km
        a = 450.  # W
        b = 21000.  # J
        tau = 10.  # s
        wbas = 80.  # W
        ef = 0.25
        c = 270.  # J/m

        # c = 3.6 * 84.  # [J/kg/m] * 84kg you fat bastard

        def speed(time):
            a2 = a * (.085 * (time / 3600) ** 2 - 3.908 / 3600 * time + 91.82) / 100.  # [Formenti/Davies]
            # a2 = a * (940 - time / 60) / 1000.  # [Wilke/Saltin]
            return 3.6 / c * ((a2 + b / time - a2 * tau / time * (1 - np.exp(-time / tau))) / ef - wbas)

        def dist(time):
            a2 = a * (.085 * (time / 3600) ** 2 - 3.908 / 3600 * time + 91.82) / 100.  # [Formenti/Davies]
            # a2 = a * (940 - time / 60) / 1000.  # [Wilke/Saltin]
            spd = 3.6 / c * ((a2 + b / time - a2 * tau / time * (1 - np.exp(-time / tau))) / ef - wbas)
            return spd * time / 60. / 60. - max_dist

        tmax = 5. * 60 * 60  # initial guess
        h = dist(tmax) / (dist(tmax + .5) - dist(tmax - .5))  # s
        while abs(h) > 1:
            h = dist(tmax) / (dist(tmax + .5) - dist(tmax - .5))  # s
            tmax -= h

        t = np.linspace(40, tmax, endpoint=True, num=1000)  # [s]
        th = t / 60 / 60
        s = speed(t)

        minetti_spd = s / 1.60934  # [mph]
        minetti_dst = minetti_spd * th  # miles
        minetti_spd[np.where(minetti_spd > 15.)] = np.nan

    # do fit to my data
    xx, yy = [], []
    a = [xx.extend(s.x) for s in svd_traces]
    a = [yy.extend(s.y) for s in svd_traces]
    xx, yy = np.array(xx), np.array(yy)

    def minfunc(fit):
        y_reduced = yy - (fit[0] * xx ** 2 + fit[1] * xx + fit[2])
        y_weighted = [1000. * y ** 2. if y > 0 else abs(y) for y in
                      y_reduced]  # penalized if we drift up, really penalized if we're below
        return np.sum(y_weighted)

    fit0 = np.array([0, -4 / 30., 9.])
    res = minimize(minfunc, fit0)
    fit = res.x
    # fit = np.polyfit(xx, yy, 2, w=[y * 10 for y in yy])

    bill_dist = np.arange(int(min(xx)), int(max(xx)) + 1)
    bill_spd = fit[0] * bill_dist ** 2 + fit[1] * bill_dist + fit[2]
    bill_pace = 60. / bill_spd  # min/mile
    hovertext = [f'{int(bp)}:{str(int((bp - int(bp)) * 60)).zfill(2)}' for bp in bill_pace]

    svd_traces.append(go.Scatter(x=bill_dist, y=bill_spd, mode='lines', line=dict(width=2), name='Max Effort (Bill)',
                                 hovertemplate='mileage: %{x}<br>pace: %{text} (min/mile)',
                                 text=hovertext))

    if minetti:
        svd_traces.append(
            go.Scatter(x=minetti_dst, y=minetti_spd, mode='lines', line=dict(width=2),
                       name='Max Effort (Human) [Minetti]',
                       visible='legendonly'))
    return svd_traces
