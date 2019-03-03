'''
Intent here is to grab a bunch of runs (kml file?) and aggregate the coordinates into a map of the park while identifying
all intersections and segments connecting intersections with their lengths
'''

from bs4 import BeautifulSoup
import glob
import matplotlib.pyplot as plt
import numpy as np
import geopy.distance as dist


def process_coordinate_string(str):
    """
    Take the coordinate string from the KML file, and break it up into [[Lat,Lon,Alt],[Lat,Lon,Alt],...]
    """
    long_lat_alt_arr = []
    for point in str.split('\n'):
        if len(point) > 0:
            long_lat_alt_arr.append([float(point.split(',')[0]), float(point.split(',')[1]), float(point.split(',')[2])])
    return long_lat_alt_arr


def smooth_run_coords(run_coords, thresh):
    # [[lon, lat, alt], ...]
    smooth = np.zeros_like(run_coords)
    for j, pt in enumerate(run_coords):
        print(str(j/len(run_coords)*100.)+'%')
        '''compute vincenty distance (input is [lat, long])'''
        dis = np.array([dist.vincenty(pt[::-1][1:], run_coords[i, ::-1][1:]).m for i in np.arange(len(run_coords))])
        inearby = np.where(dis < thresh)[0]
        smooth[j] = np.mean(run_coords[inearby], axis=0)
        a=1
    return smooth


def extract_park_runs_coords(park):
    run_dict = {}
    for run in glob.glob(park+'*.kml'):
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
            dis = np.array([dist.vincenty(coord[::-1][1:], rc[i, ::-1][1:]).m for i in np.arange(len(rc))])
            if min(dis) <= nearby_radius_m:  # another run is sufficiently nearby
                nearby_run_icoord[key] = np.where(dis == min(dis))[0][0]
    return nearby_run_icoord


def identify_junctions(run_dict: dict, bubble_radius_m=500, nearby_radius_m=10):
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
            a=1


def plot_runs(runs: dict, ax):
    for run in runs.keys():
        ax.plot(runs[run][:, 0], runs[run][:, 1], 'o-')


if __name__ == "__main__":
    park = 'ElmCreekRuns/'
    rd = extract_park_runs_coords(park)
    juncs = identify_junctions(rd)
    # srd = smooth_park_runs_coords(rd)
    fig = plt.figure('Park Runs')
    ax = fig.add_subplot(111)
    ax.set_xlabel('Longitude (deg)')
    ax.set_ylabel('Latitude (deg)')
    plot_runs(rd, ax)
    plt.show()
