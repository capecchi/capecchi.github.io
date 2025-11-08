import datetime
import os
import pickle

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pace_predictor_method_development import extract_coords_gpx, smooth_run_coords_distwindow, compute_grade_pace

# todo: compute total elevation vs distance to compare different races difficulty
# todo move all plots to plotly

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

basedirec = 'C:/Users/willi/PyCharmProjects/capecchi.github.io/posts/PacePredictor/data/'
rundirec = f'{basedirec}create_model_data/'
fpkl = f'{basedirec}pace_model.p'
gpx_model_files = os.listdir(f'{rundirec}')
gpx_model_files = [f for f in gpx_model_files if f.endswith('.gpx')]
gpx_predict = f'{basedirec}/Teanaway_100_planned.gpx'
fs = 15
plt.rcParams.update({'font.size': fs})
fgsz1 = (15, 7)
fgsz2 = (20, 7)
fgsz3 = (25, 5)
gr_binwidth = 2
pct_thresh = 75  # ignore slowest paces above pct_thresh
grade_bin_cntrs = np.arange(-100, 102, 2)
spm_minpmile = 26.8224
m_per_mile = 1609.34


def aggregate_new_gradepace_data(pace_model, pace_weight, gp_data):  # gp_data = [grade, pace, weight]
    for ib in range(len(grade_bin_cntrs)):
        if not np.isnan(gp_data[ib, 1]):  # data exists for this bin
            pace_model[ib] = (pace_model[ib] * pace_weight[ib] + gp_data[ib, 1] * gp_data[ib, 2]) / (
                    pace_weight[ib] + gp_data[ib, 2])
            pace_weight[ib] = pace_weight[ib] + gp_data[ib, 2]
    return pace_model, pace_weight


def create_predictor():
    model_data = {}
    for i, gpxf in enumerate(gpx_model_files):
        print(f'analyzing {gpxf}')
        run_coords = extract_coords_gpx(f'{rundirec}{gpxf}')  # # [lon, lat, elev, dcum, dstep, tcum, tstep]
        # NEED to smooth since elev only records rounded to the meter
        coords = smooth_run_coords_distwindow(run_coords, 10)  # dist window halfwidth in [m]
        gp, gp_pred = compute_grade_pace(coords)

        ax0.plot(gp_pred[:, 0], gp_pred[:, 1], 's-', label=f'{gpxf}')
        model_data[gpxf] = gp_pred
        if i == 0:
            agg_data = gp
        else:
            agg_data = np.append(agg_data, gp, axis=0)

    pace_model = np.zeros(len(grade_bin_cntrs))
    for ib, b in enumerate(grade_bin_cntrs):
        ii = np.where((agg_data[:, 0] - b < gr_binwidth / 2.) & (agg_data[:, 0] - b >= -gr_binwidth / 2.) & (
            ~np.isnan(agg_data[:, 1])))[0]
        if len(ii) > 0:
            if len(ii) > 20:  # apply pct_thresh only if there are enough points in bin
                imax_bin_pace = int(pct_thresh / 100 * (len(ii) + 1))
                max_bin_pace = np.sort(agg_data[ii, 1])[imax_bin_pace]
                ii = np.where((agg_data[:, 0] - b < gr_binwidth / 2.) & (agg_data[:, 0] - b >= -gr_binwidth / 2.) & (
                        agg_data[:, 1] <= max_bin_pace))[0]
            pace_model[ib] = np.nanmean(agg_data[ii, 1])
        else:
            pace_model[ib] = np.nan  # put nan in place of bins missing data
    with open(fpkl, 'wb') as fn:
        pickle.dump([grade_bin_cntrs, pace_model, model_data], fn)
    print(f'saved pace model to: {fpkl}')

    return grade_bin_cntrs, pace_model, model_data


def predict_run(pace_model, grade_bin_cntrs, gpx):
    coords = extract_coords_gpx(gpx)  # [lon, lat, elev, dcum, dstep, Nones, Nones]
    coords = coords.astype(float)  # convert to floats

    print('computing grade & interpolating pace from model')
    gp = np.zeros((len(coords[:, 0]) - 1, 3))  # [grade, pace, dstep]
    gp[:, 2] = coords[1:, 4]  # attach segment distance

    nwings = 3  # look nwings to each side of segment to compute
    for i in range(len(gp[:, 0])):
        nw = min([nwings, i + 1, len(gp[:, 0]) - i]) - 1  # if near the edge, reduce num wings to look at
        dx = coords[i + 1 + nw, 3] - coords[i - nw, 3]  # [m]
        dy = coords[i + 1 + nw, 2] - coords[i - nw, 2]  # [m]
        grade = np.arctan2(dy, dx) * 180 / np.pi / .9  # divide by 0.9 to convert angle to grade
        pace = np.interp(grade, grade_bin_cntrs, pace_model)
        gp[i, 0], gp[i, 1] = grade, pace

    segment_time = [0]  # array of times computed for each segment
    for seg_pace, seg_dst in gp[:, [1, 2]]:
        seg_pace_spm = seg_pace / spm_minpmile  # convert min/mile to [s/m]
        segment_time.append(seg_pace_spm * seg_dst)
    ttot = np.nancumsum(segment_time)  # total time [s]
    print(
        f'predicted finish in: {int(ttot[-1] / 3600):02.0f}:{int((ttot[-1] - int(ttot[-1] / 3600) * 3600) / 60):02.0f}')

    # compute new segment times assuming constant pace
    avg_speed_mps = coords[-1, 3] / ttot[-1]  # avg speed [m/s] computed from total time and dist
    ap = spm_minpmile / avg_speed_mps  # average pace [min/mile]
    avg_segtime = [0]
    for seg_dst in gp[:, 2]:
        avg_segtime.append(seg_dst / avg_speed_mps)
    ttot_avg = np.nancumsum(avg_segtime)
    t_pred, t_avgpace = np.array(ttot) / 3600., np.array(ttot_avg) / 3600.  # [hr], [hr]

    aids = {'Sasse Ridge': 6.5, 'Gallagher Head': 15.8, 'Van Epps': 21., 'Iron Peak': 27.5, 'Beverly Turnpike': 35.,
            'Miller Peak': 45.5, 'Miller Peak 2': 54.5, 'Beverly Turnpike 2': 65., 'Iron Peak 2': 72.5,
            'Van Epps 2': 79., 'Gallagher Head 2': 84.2, 'Sasse Ridge 2': 93.5, 'Finish': 100.}
    ya = [np.interp(aids[k], list(coords[:, 3] / m_per_mile), list(coords[:, 2])) for k in aids.keys()]
    xa = [np.interp(aids[k], list(coords[:, 3] / m_per_mile), list(t_pred)) for k in aids.keys()]

    ax11r.fill_between(coords[:, 3] / m_per_mile, coords[:, 2], facecolor='k', alpha=0.2)
    ax11.plot(coords[:, 3] / m_per_mile, (t_pred - t_avgpace) * 60)  # ahead/behind pace plot

    xa_cp = [np.interp(aids[k], list(coords[:, 3] / m_per_mile), list(t_avgpace)) for k in aids.keys()]
    # xa_diff = [xa[i] - xa_cp[i] for i in range(len(xa))]  # time diff between model and avg pace
    ax21.plot(t_pred, coords[:, 2], label='predicted')
    ax21.plot(t_avgpace, coords[:, 2], label='constant pace')
    rows = [k for k in aids.keys()]
    strt = datetime.datetime(2024, 9, 21, 5)
    eta = [(strt + datetime.timedelta(hours=xa[i])).strftime('%a %I:%M %p') for i in range(len(xa))]
    eta_avpace = [(strt + datetime.timedelta(hours=xa_cp[i])).strftime('%a %I:%M %p') for i in range(len(xa))]
    diff = [xa_cp[i] - xa[i] for i in range(len(xa))]
    sign = ['+' if ed >= 0 else '-' for ed in diff]
    diff = [f'{sign[i]}{abs(int(diff[i] * 60)):02}:{abs(int((diff[i] - int(diff[i] * 60) / 60) * 3600)):02}' for i in
            range(len(xa))]
    rowv2 = [[eta[i], eta_avpace[i], diff[i]] for i in range(len(xa))]
    ax21.plot(xa, ya, 'ko')
    for i, k in enumerate(aids.keys()):
        ax21.annotate(k, (xa[i], ya[i]), rotation=60)
    ax22.set_axis_off()
    tb2 = ax22.table(rowv2, rowLabels=rows,
                     colLabels=['ETA', f'{int(ap):02}:{(ap - int(ap)) * 60:02.0f} pace', 'diff (m:s)'], loc='center',
                     colWidths=[.25, .25, .25])
    tb2.scale(1, 2)
    # tb2.set_fontsize = 136
    imaxdiff = np.where(abs(t_pred - t_avgpace) == max(abs(t_pred - t_avgpace)))[0][0]


# ----------------------------------------------------------------

fig0, ax0 = plt.subplots(figsize=fgsz1)
new_model = False  # will create new pace model using gpx files in create_model_data/ folder
if new_model:
    grade_bin_cntrs, pace_model, model_data = create_predictor()
else:
    with open(fpkl, 'rb') as fn:
        grade_bin_cntrs, pace_model, model_data = pickle.load(fn)
        for k in model_data.keys():
            gp_pred = model_data[k]
            ax0.plot(gp_pred[:, 0], gp_pred[:, 1], 's-', alpha=.5)  # label=f'{k}',

ax0.plot(grade_bin_cntrs, pace_model, 'kd-', label='aggregate model')
ax0.set_xlim((-40, 40))
ax0.set_ylim((0, 60))
ax0.set_ylabel('pace (min/mile)')
ax0.set_xlabel('grade (%)')
ax0.legend()
ax0.set_aspect('equal')

# fig1 = plt.figure(figsize=fgsz2)
# gs = fig1.add_gridspec(1, 2, width_ratios=(2, 1))
# ax11 = fig1.add_subplot(gs[0, 0])
# ax12 = fig1.add_subplot(gs[0, 1])
fig1, ax11 = plt.subplots(figsize=fgsz3)
ax11.set_xlabel('dist (miles)')
ax11.set_ylabel('pace predictor\n(minutes)', color=clrs[0])
ax11.annotate('<--ahead    behind-->', (2, -12), rotation=90, fontsize=15, color=clrs[0])
ax11.set_xlim((0, 100))
ax11.set_ylim((-15, 30))
ax11r = ax11.twinx()
ax11r.set_ylabel('elevation (meters)')
ax11.spines['bottom'].set_position(('data', 0))  # move x-axis to y=0
ax11.spines['top'].set_visible(False)
ax11r.spines['top'].set_visible(False)
ax11r.spines['bottom'].set_visible(False)
xlabels = ax11.get_xticklabels()
xlabels[0].set_visible(False)
xlabels[-1].set_visible(False)

yl0, yl1 = ax11.get_ylim()
zero_pos = (0 - yl0) / (yl1 - yl0)
rmin, rmax = 0, 4000
yr0 = rmin + zero_pos * (rmax - rmin)
ax11r.set_ylim(rmin - yr0, rmax - yr0)

# fig2, (ax21, ax22) = plt.subplots(ncols=2, figsize=fgsz2, sharey='row')
fig2 = plt.figure(figsize=fgsz2)
gs = fig2.add_gridspec(1, 2, width_ratios=(2, 1))
ax21 = fig2.add_subplot(gs[0, 0])
ax22 = fig2.add_subplot(gs[0, 1])

predict_run(pace_model, grade_bin_cntrs, gpx_predict)  # run_predict = [time, dist, elev, pace]

ax21.set_xlabel('time (hr)')
ax21.set_ylabel('elev (m)')
ax21.legend()

plt.show()

if __name__ == '__main__':
    pass
