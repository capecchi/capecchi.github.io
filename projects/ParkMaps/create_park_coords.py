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


def process_park_coords(park, plot=False):
    """
    """
    run_dict = {}
    smooth_run_dict = {}
    for run in glob.glob(park+'*.kml'):
        with open(run, 'r') as f:
            s = BeautifulSoup(f, 'xml')
            run_coords = []
            for coords in s.find_all('coordinates'):
                if len(run_coords) == 0:
                    run_coords = np.array(process_coordinate_string(coords.string))
                else:
                    run_coords = np.append(run_coords, process_coordinate_string(coords.string))
            smooth_coords = smooth_run_coords(run_coords, 3.0)


        run_dict[run] = run_coords
        smooth_run_dict[run] = smooth_coords

    if plot:
        for run in run_dict.keys():
            plt.plot(run_dict[run][:, 0], run_dict[run][:, 1], 'o-')
            plt.plot(smooth_run_dict[run][:, 0], smooth_run_dict[run][:, 1])
    plt.show()
    a=1


if __name__ == "__main__":
    park = 'ElmCreekRuns/'
    process_park_coords(park, plot=True)