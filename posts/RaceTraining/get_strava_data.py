import datetime
import math
from collections import OrderedDict

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
import stravalib.exc
from plotly.subplots import make_subplots
from scipy.optimize import minimize
from stravalib import unithelper
from stravalib.client import Client

from .playground import data_input_popup


def get_client(code):
    client_id = 34049
    client_secret = '2265a983040000b3b865a0fc333f41cd701dcb5f'

    client = Client()
    client.authorization_url(34049, 'http://localhost:8080', scope='activity:read_all')
    token_response = client.exchange_code_for_token(client_id, client_secret, code)
    client.access_token = token_response['access_token']
    client.refresh_token = token_response['refresh_token']
    return client


def get_training_data(client, after=datetime.date.today() - datetime.timedelta(days=7), before=datetime.date.today(),
                      get_cals=True):
    # race_day = before - datetime.timedelta(days=1)
    race_day = before.replace(hour=0, minute=0, second=0, microsecond=0)

    activities = client.get_activities(after=after, before=before)
    try:
        activities = list(activities)
        activities = activities[::-1]  # reverse order so they're chronological
        if get_cals:
            all_days_before = [(a.start_date_local.date() - race_day.date()).days for a in activities]
            all_cals = [client.get_activity(id).calories for id in [a.id for a in activities]]
            cum_cals = np.cumsum(all_cals)
        else:
            all_days_before, cum_cals = None, None
        runs = [act for act in activities if act.type == 'Run']
        runs = [r for r in runs if
                unithelper.miles(r.distance).num > 2 and unithelper.miles_per_hour(r.average_speed).num > 4]
        days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
        dist = [unithelper.miles(r.distance).num for r in runs]
        cum = np.cumsum(dist)
        pace = [60. / unithelper.miles_per_hour(r.average_speed).num for r in runs]  # min/mile
        speed = [60 / p for p in pace]  # mph
        # igood = [i for i in np.arange(len(dist)) if (speed[i] > 4 or dist[i] > 5)]
        # days_before, dist, cum, pace, speed = days_before[igood], dist[igood], cum[igood], pace[igood], speed[igood]
        return days_before, dist, cum, pace, speed, all_days_before, cum_cals
    except stravalib.exc.Fault:
        return None, None, None, None, None, None, None


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


def manual_tracking_plots(client):
    analysis_startdate = datetime.datetime(2020, 9, 12, 0, 0, 0, 0)  # hard coded start date
    fp = 'C:/Users/Owner/Dropbox/'
    fn = fp + 'training_data.xlsx'
    sho = pd.read_excel(fn, sheet_name='shoes')
    shoe_options = sho['shoe_options'].values
    df = pd.read_excel(fn, sheet_name='data')
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

    activ_since_strt_date = list(client.get_activities(after=analysis_startdate, before=datetime.datetime.utcnow()))
    runs_since_strt_date = [act for act in activ_since_strt_date if act.type == 'Run']

    for run in runs_since_strt_date:
        if run.id not in df['runid'].values:
            shoes_available = []
            for i in sho.index:
                if math.isnan(sho['retired_date'][i]):
                    if run.start_date_local > sho['start_date'][i]:
                        shoes_available.append(sho['shoe_options'][i])
                else:
                    if sho['start_date'][i] < run.start_date_local < sho['retired_date'][i]:
                        shoes_available.append(sho['shoe_options'][i])
            runid_arr.append(run.id)
            date_arr.append(run.start_date_local)
            dist_arr.append(unithelper.miles(run.distance).num)
            temp_arr.append(run.average_temp * 9. / 5 + 32.)

            # initialize vars (need these next 4 lines)
            shoes_worn = 'catchall'
            liters_consumed = 0.
            start_weight_lb = np.nan
            end_weight_lb = np.nan
            sh, lc, sw, ew, cc, cd = data_input_popup(run.start_date_local, shoes_available,
                                                      unithelper.miles(run.distance).num)
            strw_arr.append(sw)
            endw_arr.append(ew)
            swtrt_arr.append((sw - ew) / 2.20462 / (run.moving_time.seconds / 60. / 60.))
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
    man_fig.add_trace(go.Bar(x=sho_dist, y=shoe_options, orientation='h', marker_color=colors[4]),
                      row=1, col=1)  # shoe mileage
    man_fig.add_trace(go.Histogram(x=swtrt_arr, xbins=dict(start=0, end=3.0, size=0.1), marker_color=colors[1]),
                      row=2, col=1)  # sweatrate histogram
    man_fig.add_trace(go.Scatter(x=dist_arr, y=lit_cons_arr, mode='markers', marker_color=colors[2]),
                      row=3, col=1)  # fluid consumption
    man_fig.add_trace(go.Scatter(x=dist_arr, y=cal_cons_arr, mode='markers', yaxis='y4', xaxis='x3',
                                 marker_color=colors[3]))  # calorie consumption
    yr = np.ceil(max([max(lit_cons_arr), max(cal_cons_arr) / 500.]))
    man_fig.layout.update(height=750,
                          xaxis1=dict(title='Cumulative Mileage'),
                          xaxis2=dict(title='Sweat Loss Rate (L/h)', range=[0, 3]),
                          xaxis3=dict(title='Distance (miles)'),
                          yaxis2=dict(title='Count'),
                          yaxis3=dict(title='Liters Consumed', color=colors[2], range=[-.5, yr]),
                          yaxis4=dict(title='Calories Consumed', color=colors[3], side='right',
                                      overlaying='y3', range=[-250, yr * 500]),
                          showlegend=False)
    man_fig.update_yaxes(automargin=True)

    return man_fig


def gather_training_seasons(code, rdist=False, rcum=True, rwk=False, rpace=False, rsvd=True, rcal=True, rswt=True):
    # rsvd, rcal, rcum = False, False, False  # for debugging just manual figs
    races = get_past_races(trail=True, road=False)
    races.update({'Dirty German (virtual) 50k 2020': datetime.datetime(2020, 10, 10),
                  'Stone Mill 50M 2020': datetime.datetime(2020, 11, 14),
                  'Past 18 weeks': datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)})

    wks_18 = datetime.timedelta(weeks=18)
    day_1 = datetime.timedelta(days=1)
    wks_1 = datetime.timedelta(weeks=1)

    ref_day = min(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                  races[list(races.keys())[-1]])
    days_to_race = datetime.timedelta(days=(races[list(races.keys())[-1]] - ref_day).days)
    client = get_client(code)

    dist_traces = []
    cum_traces = []
    pace_traces = []
    cal_traces = []
    wk_traces = []
    svd_traces = []  # speed vs dist
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    max_dist = 0
    if rswt:  # get activities for runs with sweat loss data
        man_fig = manual_tracking_plots(client)
    if rsvd:  # get large dataset
        nyr = 3
        nyrs = datetime.timedelta(weeks=52 * nyr)
        predays, dist, _, _, speed, _, _ = get_training_data(client,
                                                             datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                                                             microsecond=0) - nyrs,
                                                             datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                                                             microsecond=0) + day_1,
                                                             get_cals=False)
        bill_pace = 60. / np.array(speed)  # min/mile
        hovertext = [f'{int(s)}:{str(int((s - int(s)) * 60)).zfill(2)}' for s in bill_pace]
        hovertemp = 'mileage: %{x:.2f}<br>pace: %{text} (min/mile)'
        svd_traces.append(go.Scatter(x=dist, y=speed, mode='markers', name='past {} years'.format(nyr), text=hovertext,
                                     hovertemplate=hovertemp, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
        # make weekly average plot
        i, wktot, wktot_db, npdist, nppredays = 0, [], [], np.array(dist), np.array(predays)
        while -i - 7 > min(predays):
            wktot.append(np.sum(npdist[(nppredays > -i - 7) & (nppredays <= -i)]))
            wktot_db.append(-i)
            i += 1
        runav = [np.mean(wktot[i:i + 7]) for i in np.arange(len(wktot) - 7 + 1)]
        runav_db = wktot_db[:len(runav)]
        wktot_data = [go.Scatter(x=wktot_db, y=wktot, mode='lines', name='weekly total'),
                      go.Scatter(x=runav_db, y=runav, mode='lines', name='7 day running average',
                                 line=dict(dash='dash'))]
        now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        xann = [(rd - now).days for rd in [races[k] for k in races.keys()] if (rd - now).days < -10]
        yann = [wktot[i] for i in
                [-(rd - now).days for rd in [races[k] for k in races.keys()] if (rd - now).days < -10]]
        wktot_data.append(go.Scatter(
            x=xann, y=yann, text=[k for k in races.keys() if (races[k] - now).days < -10], mode='text+markers',
            textposition='middle right', showlegend=False, marker=dict(color='rgba(0,0,0,0)', line=dict(width=1))))
        wktot_data.append(go.Bar(x=predays, y=dist, width=1, name='runs'))

    for i, (k, v) in enumerate(races.items()):
        print(k)
        if v > datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                               microsecond=0):  # read: if race day is after today, ie in the future, then solid line plot
            width = 3
        else:
            width = 2
        op = (i + 1.) / len(races.items())
        days_before, dist, cum, pace, speed, adb, cals = get_training_data(client, v - wks_18, v + day_1)
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
        if rcal:
            cal_traces.append(
                go.Scatter(x=adb, y=cals, opacity=op, name=k, mode='lines+markers', line=dict(width=width)))
        if rwk:
            wdb, wd, wc, wp, ws, _, _ = get_training_data(client, v - days_to_race - wks_1, v - days_to_race)
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

    if rsvd:
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

        wktot_layout = go.Layout(xaxis=dict(title='Days ago'),
                                 yaxis=dict(title='Mileage', hoverformat='.2f'),
                                 legend=dict(x=1, y=1, bgcolor='rgba(0,0,0,0)', xanchor='right'))
        wktot_fit = go.Figure(data=wktot_data, layout=wktot_layout)
        wktot_fit.write_html(f'{img_path}wktot.html')
        print('saved weekly total image')
        figs.append(wktot_fit)
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
    if rcal:
        calayout = go.Layout(xaxis=dict(title='Days before race'), yaxis=dict(title='Calories'),
                             legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
        cal_fig = go.Figure(data=cal_traces, layout=calayout)
        cal_fig.write_html(f'{img_path}rta_cal.html')
        print('saved cal image')
        figs.append(cal_fig)
    if rwk:
        wlayout = go.Layout(legend=dict(orientation='h', y=1.1), xaxis=dict(title='Prior week training', ),
                            yaxis=dict(title='Distance', domain=[0., .3], ),
                            yaxis2=dict(title='Cumulative', domain=[0.35, 0.65]),
                            yaxis3=dict(title='Pace', domain=[0.7, 1.], ), )
        wk_fig = go.Figure(data=wk_traces, layout=wlayout)
        wk_fig.write_html(f'{img_path}rta_week.html')
        print('saved week image')
        figs.append(wk_fig)
    if rswt:
        man_fig.write_html(f'{img_path}rta_man.html')
        print('saved manual analysis image')
        figs.append(man_fig)
        # swt_fig.write_html(f'{img_path}rta_swt.html')
        # print('saved sweatloss image')
        # figs.append(swt_fig)
        # h20_fig.write_html(f'{img_path}rta_h20.html')
        # print('saved h20 consumption image')
        # figs.append(h20_fig)
        # sho_fig.write_html(f'{img_path}rta_sho.html')
        # print('saved shoe mileage image')
        # figs.append(sho_fig)

    return figs


def add_max_effort_curve(svd_traces, max_dist=100):
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
    bdist, bspeed = [], []  # miles, mph
    not_important = [bdist.extend(s.x) for s in svd_traces]
    not_important = [bspeed.extend(s.y) for s in svd_traces]
    bdist, bspeed = np.array(bdist), np.array(bspeed)

    # def minfunc(fit):  # 2-degree polyfit
    #     ydiff_0offset = bspeed - (fit[0] * bdist ** 2 + fit[1] * bdist + 0.)
    #     offset = max(ydiff_0offset)  # offset necessary so that curve is always >= data
    #     ydiff = bspeed - (fit[0] * bdist ** 2 + fit[1] * bdist + offset)
    #     return np.sum(ydiff ** 2)

    def minfunc2(fit):  # rotated parabola
        r = np.sqrt(bdist ** 2 + bspeed ** 2)
        th = np.arctan2(bspeed, bdist)
        x2, y2 = r * np.cos(th - fit[1]), r * np.sin(th - fit[1])  # rotate pts by -theta
        ydiff_0offset = y2 - fit[0] * x2 ** 2
        offset = max(ydiff_0offset)  # offset necessary so that curve is always >= data
        ydiff = y2 - (fit[0] * x2 ** 2 + offset)
        return np.sum(ydiff ** 2)

    fit0 = np.array([0, -4 / 30.])  # 2nd order, 1st order initial guesses for 2-degree polyfit
    fit0 = np.array([0., np.arctan2(-4, 30.)])  # 2nd order, theta initial guesses for rotated-parabola
    res = minimize(minfunc2, fit0, method='Nelder-Mead')
    fit = res.x
    print(res.message)
    # bill_dist = np.arange(int(min(bdist)), int(max(bdist)) + 1)
    # bill_spd = fit[0] * bill_dist ** 2 + fit[1] * bill_dist + max(bspeed - (fit[0] * bdist ** 2 + fit[1] * bdist + 0.))

    r = np.sqrt(bdist ** 2 + bspeed ** 2)
    th = np.arctan2(bspeed, bdist)
    dx2, dy2 = r * np.cos(th - fit[1]), r * np.sin(th - fit[1])  # rotate pts by -theta
    ydiff_0offset = dy2 - fit[0] * dx2 ** 2
    offset = max(ydiff_0offset)  # offset necessary so that curve is always >= data
    bill_dist_rot = np.linspace(0., max(bdist))
    bill_spd_rot = fit[0] * bill_dist_rot ** 2 + offset
    bill_r = np.sqrt(bill_dist_rot ** 2 + bill_spd_rot ** 2)
    bill_th = np.arctan2(bill_spd_rot, bill_dist_rot)
    bill_dist0, bill_spd0 = bill_r * np.cos(bill_th + fit[1]), bill_r * np.sin(bill_th + fit[1])  # rotate by +theta
    bill_dist = np.arange(int(min(bdist)), int(max(bdist)) + 1)
    bill_spd = np.interp(bill_dist, bill_dist0, bill_spd0)

    bill_pace = 60. / bill_spd  # min/mile
    hovertext = [f'{int(bp)}:{str(int((bp - int(bp)) * 60)).zfill(2)}' for bp in bill_pace]

    svd_traces.append(go.Scatter(x=bill_dist, y=bill_spd, mode='lines', line=dict(width=2), name='Max Effort (Bill)',
                                 hovertemplate='mileage: %{x}<br>pace: %{text} (min/mile)',
                                 text=hovertext))
    svd_traces.append(
        go.Scatter(x=minetti_dst, y=minetti_spd, mode='lines', line=dict(width=2),
                   name='Max Effort (Human) [Minetti]', visible='legendonly'))
    return svd_traces
