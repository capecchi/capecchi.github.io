import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import gpxpy
import geopy.distance as dist  # takes (lat, lon) as input coords
from helpful_stuff import BillExcept

# todo move all plots to plotly

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']
spm_minpmile = 26.8224
m_per_mile = 1609.34
gr_binwidth = 2
pct_thresh = 75  # ignore slowest paces above pct_thresh
grade_bin_cntrs = np.arange(-100, 102, 2)


def extract_coords_gpx(runfile, plot=False):
    # returns [lon, lat, elev, dcum, dstep, tcum, tstep]
    lat, lon = 100., 0.  # impossible set of coords to start with
    with open(runfile, 'r') as f:
        gpx = gpxpy.parse(f)
        run_coords = []
        for track in gpx.tracks:
            for segment in track.segments:
                for i, point in enumerate(segment.points):
                    lat, lon, elev = point.latitude, point.longitude, point.elevation
                    tcum = point.time_difference(segment.points[0])  # time since first point
                    if i == 0:
                        dx, dt = 0, 0
                    else:
                        if segment.points[i - 1].time_difference(segment.points[i]) != 1:
                            a = 1
                        prev = segment.points[i - 1]
                        dx = dist.distance((lat, lon), (prev.latitude, prev.longitude)).m
                        dt = point.time_difference(segment.points[i - 1])  # time since last point
                    run_coords.append([lon, lat, elev, dx, dx, tcum, dt])
    coords = np.array(run_coords)
    coords[:, 3] = np.cumsum(coords[:, 3])  # convert dx to cumulative distance [m]

    # Here we remove all consecutive duplicate points (not moving) and will adjust our pace predictions later to keep
    # total time consistent with initial gpx, so av pace will be slower than computed to account for stoppage time
    idup = []
    for ic in range(1, len(coords[:, 0])):
        if coords[ic, 0] == coords[ic - 1, 0] and coords[ic, 1] == coords[ic - 1, 1]:
            idup.append(ic)
    if plot:
        ax11.plot(coords[:, 0], coords[:, 1], label='raw data')
        ax11.plot(coords[idup, 0], coords[idup, 1], 'o', label='stationary')
    coords = np.delete(coords, idup, axis=0)
    if np.where(coords[:, 4] == 0)[0] != [0]:
        raise BillExcept('too many dx=0 found, expected 1 at first position')
    return coords


def smooth_run_coords_timewindow(coords, twin: 10):  # smooth based on time window +/-twin [s]
    print('smoothing coordinates')
    smooth = np.zeros_like(coords)
    smooth[:, 3] = coords[:, 3]  # keep same time array
    for i in range(len(coords[:, 0])):  # for each pt, average pts within twin
        itimewin = np.where(abs(coords[:, 3] - coords[i, 3]) <= twin)[0]
        smooth[i, 0] = np.nanmean(coords[itimewin, 0])  # average long
        smooth[i, 1] = np.nanmean(coords[itimewin, 1])  # average lat
        smooth[i, 2] = np.nanmean(coords[itimewin, 2])  # average elev
    return smooth


def smooth_run_coords_distwindow(coords, dwin: 10):  # smooth based on distance window +/- dwin [m]
    # Averages over all pts in range
    print('smoothing coordinates using distance')
    smooth = np.copy(coords)  # [lon, lat, elev, dcum, dstep, tcum, tstep]
    smooth[:, 2] = np.zeros(len(coords[:, 2]))  # zero out to recompute elev array
    for i in range(len(coords[:, 0])):  # for each pt, average pts within dwin
        idistwin = np.where(abs(coords[:, 5] - coords[i, 5]) <= dwin)[0]
        smooth[i, 2] = np.nanmean(coords[idistwin, 2])  # average elev
    return smooth


def smooth_run_coords_distwindow2(coords, dwin: 20):  # smooth based on distance window +/- dwin [m]
    # Averages using weights from points in range
    print('smoothing coordinates using weighted distance')
    w_smooth = np.copy(coords)  # [lon, lat, elev, dcum, dstep, tcum, tstep]
    w_smooth[:, 2] = np.zeros(len(coords[:, 2]))  # zero out to recompute elev array
    for i in range(len(coords[:, 0])):  # for each pt, average pts within dwin
        idistwin = np.where(abs(coords[:, 3] - coords[i, 3]) <= dwin)[0]
        w = -abs(idistwin - i) - min(-abs(idistwin - i)) + 1
        w_smooth[i, 2] = np.average(coords[idistwin, 2], weights=w)  # average weighted elev
    return w_smooth


def compute_grade_pace(coords):  # [lon, lat, elev, dcum, dstep, tcum, tstep]
    print('computing grade & pace')
    gp = np.zeros((len(coords[:, 0]) - 1, 3))  # [grade, pace, dstep]
    gp[:, 2] = coords[1:, 4]  # attach segment distance

    nwings = 1  # look nwings to each side of segment to compute
    for i in range(len(gp[:, 0])):
        nw = min([nwings, i + 1, len(gp[:, 0]) - i]) - 1  # if near the edge, reduce num wings to look at
        dx = coords[i + nw + 1, 3] - coords[i - nw, 3]  # m
        if dx < 0:
            a = 1
        dy = coords[i + 1 + nw, 2] - coords[i - nw, 2]  # [m]
        dt = coords[i + 1 + nw, 5] - coords[i - nw, 5]  # [s]
        if dt < 0:
            a = 1
        grade = dy / dx * 100.
        pace = dt / dx * spm_minpmile  # convert s/m to [min/mile]
        if pace < 0:
            a = 1
        if pace < 120:  # set upper limit. I mean come on... 2 hr mile pace? ditch those outliers
            gp[i, 0], gp[i, 1] = grade, pace
        else:
            gp[i, 0], gp[i, 1] = grade, np.nan

    gp_pred = []
    for ib, b in enumerate(grade_bin_cntrs):
        ii = np.where((gp[:, 0] - b < gr_binwidth / 2.) & (gp[:, 0] - b >= -gr_binwidth / 2.) & (~np.isnan(gp[:, 1])))[
            0]
        if len(ii) > 0:
            if len(ii) > 20:  # apply pct_thresh only if there are enough points in bin
                imax_bin_pace = int(pct_thresh / 100 * (len(ii) + 1))
                max_bin_pace = np.sort(gp[ii, 1])[imax_bin_pace]
                ii = np.where((gp[:, 0] - b < gr_binwidth / 2.) & (gp[:, 0] - b >= -gr_binwidth / 2.) & (
                        gp[:, 1] <= max_bin_pace))[0]
            gp_pred.append([b, np.nanmean(gp[ii, 1]), len(ii)])  # [bin, avg_pace, weight]
        else:
            gp_pred.append([b, np.nan, 0.])  # put nan in place of bins missing data
    gp_out = np.array(gp_pred)

    # normalize to total time
    segment_time = []  # array of times computed for each segment
    for grade, dst in gp[:, [0, 2]]:  # don't need pace from data array, computing from predictions
        ig = np.where((gp_out[:, 0] - grade < gr_binwidth / 2) & (gp_out[:, 0] - grade >= -gr_binwidth / 2.))[0]
        if len(ig) != 1:
            raise BillExcept(f'Expected 1 element array, got {len(ig)}')
        seg_pace = gp_out[ig[0], 1]  # [min/mile]
        seg_pace_spm = seg_pace / spm_minpmile  # convert min/mile to [s/m]
        segment_time.append(seg_pace_spm * dst)
    ttot = np.nancumsum(segment_time)  # total time [s]
    # scale by time ratio
    gp_out[:, 1] *= coords[-1, 5] / ttot[-1]
    gp[:, 1] *= coords[-1, 5] / ttot[-1]  # scale raw data by same
    return gp, gp_out


def predict_run_performance(gp_pred, gp):  # grade/pace data gp=[grade, pace, dist] compute arrival times and ttot
    # create new time array using computed grade/pace and compare to original total time
    binsize = gp_pred[1, 0] - gp_pred[0, 0]  # grade bin size
    segment_time = []  # array of times computed for each segment
    for grade, dist in gp[:, [0, 2]]:  # don't need pace from data array, computing from predictions
        ig = np.where((gp_pred[:, 0] - grade < binsize / 2) & (gp_pred[:, 0] - grade >= -binsize / 2.))[0]
        if len(ig) != 1:
            raise BillExcept(f'Expected 1 element array, got {len(ig)}')
        seg_pace = gp_pred[ig[0], 1]  # [min/mile]
        seg_pace_spm = seg_pace / spm_minpmile  # convert min/mile to [s/m]
        segment_time.append(seg_pace_spm * dist)
    ttot = np.cumsum(segment_time)  # total time [s]
    ttot = np.insert(ttot, 0, 0)  # prepend with t=0 to match size of pt array
    return ttot


if __name__ == '__main__':
    gpx = 'data/Lunch_Trail_Run.gpx'

    fs = 15
    fgsz = (20, 7)
    plt.rcParams.update({'font.size': fs})
    fig1, (ax11, ax12, ax13) = plt.subplots(ncols=3, figsize=fgsz)

    run_coords = extract_coords_gpx(gpx, plot=True)  # # [lon, lat, elev, dcum, dstep, tcum, tstep]
    # NEED to smooth since elev only records rounded to the meter
    coords = smooth_run_coords_distwindow(run_coords, 10)  # dist window halfwidth in [m]
    gp_notsmooth, _ = compute_grade_pace(run_coords)
    gp, gp_pred = compute_grade_pace(coords)
    ttot = predict_run_performance(gp_pred, gp)

    ax11.set_xlabel('lon (deg)')
    ax11.set_ylabel('lat (deg)')
    ax11.legend()
    ax12.plot(run_coords[:, 5] / 3600, run_coords[:, 2], 'o-', c=clrs[2], label='raw data')
    ax12.plot(coords[:, 5] / 3600, coords[:, 2], 'o-', c=clrs[3], label='smoothed')
    ax12.set_xlabel('time (hr)')
    ax12.set_ylabel('elevation (m)')
    ax12.set_xlim((.25, .26))
    ax12.set_ylim((235, 245))
    ax12.legend()
    ax13.plot(gp_notsmooth[:, 0], gp_notsmooth[:, 1], '.')
    ax13.set_xlim((-40, 40))
    ax13.set_ylim((0, 40))
    ax13.set_ylabel('pace (min/mile)')
    ax13.set_xlabel('grade (%)')

    # grade vs pace
    fig2, (ax21, ax22) = plt.subplots(ncols=2, figsize=fgsz)
    ax21.plot(gp[:, 0], gp[:, 1], '.', label='data')
    ax21.plot(gp_pred[:, 0], gp_pred[:, 1], 'kd-', label='predicted pace')
    ax21.set_xlim((-40, 40))
    ax21.set_ylim((0, 40))
    ax21.set_ylabel('pace (min/mile)')
    ax21.set_xlabel('grade (%)')
    ax21.legend()

    # elev vs time
    ax22.plot(coords[:, 5] / 3600, coords[:, 2], label='data')
    ax22.plot(ttot / 3600, coords[:, 2], label='predicted')
    ax22.set_xlabel('time (hr)')
    ax22.set_ylabel('elevation (m)')
    ax22.legend()
    plt.show()
