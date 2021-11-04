'''
Intent here is to grab a bunch of runs (kml file?) and aggregate the coordinates into a map of the park while identifying
all intersections and segments connecting intersections with their lengths
'''

import glob

import geopy.distance as dist
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup


def process_coordinate_string(str):
    """
    Take the coordinate string from the KML file, and break it up into [[Lat,Lon,Alt],[Lat,Lon,Alt],...]
    """
    long_lat_alt_arr = []
    for point in str.split('\n'):
        if len(point) > 0:
            long_lat_alt_arr.append(
                [float(point.split(',')[0]), float(point.split(',')[1]), float(point.split(',')[2])])
    return long_lat_alt_arr


def smooth_run_coords(run_coords, thresh):
    # [[lon, lat, alt], ...]
    smooth = np.zeros_like(run_coords)
    for j, pt in enumerate(run_coords):
        print(str(j / len(run_coords) * 100.) + '%')
        '''compute distance (input is [lat, long])'''
        dis = np.array([dist.distance(pt[::-1][1:], run_coords[i, ::-1][1:]).m for i in np.arange(len(run_coords))])
        inearby = np.where(dis < thresh)[0]
        smooth[j] = np.mean(run_coords[inearby], axis=0)
        a = 1
    return smooth


def extract_park_runs_coords(park):
    run_dict = {}
    for run in glob.glob(park + '*.kml'):
        with open(run, 'r') as f:
            s = BeautifulSoup(f, 'xml')
            run_coords = []
            for coords in s.find_all('coordinates'):
                if len(run_coords) == 0:
                    run_coords = np.array(process_coordinate_string(coords.string))
                else:
                    run_coords = np.append(run_coords, process_coordinate_string(coords.string))
        run_dict[run] = run_coords

    return run_dict


def smooth_park_runs_coords(run_dict: dict):
    smooth_run_dict = {}
    for run in run_dict.keys():
        smooth_coords = smooth_run_coords(run_dict[run], 3.0)
        smooth_run_dict[run] = smooth_coords
    return smooth_run_dict


def another_run_nearby(coord, current_run_key, run_dict, nearby_radius_m):
    nearby_run_icoord = {}
    for key, rc in run_dict.items():
        if key != current_run_key:
            dis = np.array([dist.distance(coord[::-1][1:], rc[i, ::-1][1:]).m for i in np.arange(len(rc))])
            if min(dis) <= nearby_radius_m:  # another run is sufficiently nearby
                nearby_run_icoord[key] = np.where(dis == min(dis))[0][0]
    return nearby_run_icoord


def identify_junctions(run_dict: dict, bubble_radius_m=500, nearby_radius_m=10):
    junctions = None
    for key, run_coords in run_dict.items():
        for coord in run_coords:
            nearby_runs_icoord = another_run_nearby(coord, key, run_dict, nearby_radius_m)
            if len(nearby_runs_icoord) > 0:  # nearby run found
                # given runs nearby A, B, C.
                # create a, a subset of A where a starts from coord and extends until it is no longer near B, C
                # create b, s.t. b is close to a
                # create c, s.t. c is close to b
                # recreate a, b s.t. a, b are close to c
                # except for the first step these should all be very fast since arrays become much shorter right away
                a = 1
    return junctions


def plot_runs(runs: dict, ax):
    for run in runs.keys():
        ax.plot(runs[run][:, 0], runs[run][:, 1], '-')


def self_segment(run):  # lon, lat, alt
    dtor = np.pi / 180
    lon, lat = run[:, 0], run[:, 1]
    avlong, avlat = np.mean(lon), np.mean(lat)
    plt.plot(lon, lat)
    # dist.distance takes [lat, lon] as input
    # dis_frm_strt = np.append([0], [dist.distance(run[0][::-1][1:], run[i][::-1][1:]).m for i in np.arange(1, len(run))])
    delta = np.append([0], [dist.distance(run[i][::-1][1:], run[i + 1][::-1][1:]).m for i in np.arange(len(run) - 1)])
    rearth = 6371009.  # [m]
    rsearch = 50.  # [m] look for pts this close to others
    dlat = rsearch / rearth / dtor  # [deg]
    dlon = rsearch / (rearth * np.cos(avlat * dtor)) / dtor  # [deg]
    i1, i2 = 300, 1410

    segs, isibs = [], []
    i2scan = np.arange(len(lon))
    while len(i2scan) > 0:
        ptstat, _ = determine_pt_status(lon, lat, dlon, dlat, i2scan[0], verbose=True)
        posptstat, negptstat, ipos, ineg = ptstat, ptstat, i2scan[0], i2scan[0]
        while posptstat == ptstat:
            ipos += 10  # jump 100 pts and check again
            posptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ipos)
        while negptstat == ptstat:
            ineg -= 10
            negptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ineg)
        if ineg < 0:  # spanning start pt
            plt.plot(np.roll(lon, -ineg)[:ipos - ineg], np.roll(lat, -ineg)[:ipos - ineg])
        else:
            plt.plot(lon[ineg:ipos], lat[ineg:ipos])
        iseg = np.arange(ineg, ipos + 1)
        if ptstat == 2:
            if len(iseg) % 2 == 0:  # even
                imid = int(np.median(iseg))
            else:
                imid = int(np.median(iseg[:-1]))
            _, isib = determine_pt_status(lon, lat, dlon, dlat, imid)
            isibs.append(isib)
        else:
            isibs.append([None])
        segs.append(iseg)
        i2scan = np.setdiff1d(i2scan, (iseg + len(lon)) % len(lon))
        print('looping')

    juncs = []
    for i1 in np.arange(len(segs)):
        seg1 = (segs[i1] + len(lon)) % len(lon)  # ensure all indices positive
        if i1 != len(segs) - 1:
            seg2 = segs[i1 + 1]  # start compare forward
        else:
            seg2 = segs[0]  # compare last to first
        seg2 = (seg2 + len(lon)) % len(lon)  # ensure all indices positive
        common = np.intersect1d(seg1, seg2)
        if len(common) > 0:
            juncs.append([np.mean(lon[common]), np.mean(lat[common])])  # [lon, lat]
    for j in juncs:
        plt.plot(j[0], j[1], 'o')
    # merge adjacent juncs
    juncs_merged = []
    ijunc2scan = np.arange(len(juncs))
    while len(ijunc2scan) > 0:
        jdist = [dist.distance(juncs[ijunc2scan[0]][::-1], juncs[iij][::-1]).m for iij in ijunc2scan]
        iav = np.where(np.array(jdist) < 100.)  # merge juncs within 100m
        juncs_merged.append(np.mean(np.array(juncs)[ijunc2scan[iav]], axis=0))
        ijunc2scan = np.setdiff1d(ijunc2scan, ijunc2scan[iav])
    for j in juncs_merged:
        plt.plot(j[0], j[1], 's')
    a = 1


def determine_pt_status(lon, lat, dlon, dlat, ipt, verbose=False):
    ii = np.where((lon >= lon[ipt] - dlon / 2.) & (lon < lon[ipt] + dlon / 2.) & (
            lat >= lat[ipt] - dlat / 2.) & (lat < lat[ipt] + dlat / 2.))[0]
    if 2 < len(ii):  # must identify at least 2 indices in dlon dlat box we're investigating
        ibreak = np.where(ii - np.roll(ii, 1) != 1)[0]
        if len(ibreak) > 1:  # multiple segments detected
            for ib in ibreak:  # determine if break exceeds gap threshold
                break_dist = dist.distance([lat[ii[ib]], lon[ib]], [lat[ib - 1], lon[ib - 1]]).m
                if break_dist < 100.:
                    ibreak = np.delete(ibreak, np.where(ibreak == ib))
        if len(ibreak) > 1:  # multiple segments persist
            if verbose:
                print('there is another')
            isibs = []  # array of one index from each segment (to tie them together later)
            for ib in np.arange(len(ibreak)):
                if ibreak[ib] != ibreak[-1]:
                    isibs.append(
                        int(np.median(ii[ibreak[ib]:ibreak[ib + 1]])))  # int works here since all consecutive nums
                else:
                    isibs.append(int(np.median(ii[ibreak[ib]:])))
            return 2, isibs
        else:
            if verbose:
                print('alone')
            return 1, None


if __name__ == "__main__":
    park = 'C:/Users/Owner/Dropbox/ParkMaps/ElmCreekRuns/'
    rd = extract_park_runs_coords(park)
    for run in rd.keys():
        self_segment(rd[run])

    fig = plt.figure('Park Runs')
    ax = fig.add_subplot(111)
    ax.set_xlabel('Longitude (deg)')
    ax.set_ylabel('Latitude (deg)')
    plot_runs(rd, ax)
    # plt.show()
    juncs = identify_junctions(rd)
    # srd = smooth_park_runs_coords(rd)
