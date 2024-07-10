import glob

import geopy.distance as dist
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

"""
the idea here is to aggregate all the runs at once, since junctions might depend on the combination of two distinct runs
with all the data on hand in large lat/lon arrays, we scan along the arrays looking for regions where we have > 2 exits
note if the bubble size is set too large we could have two paths near but not intersecting that cause a false positive
 junction identification
as we scan and don't find junctions we eliminate those indices
whenever we find a junction we eliminate those as well until we've scanned all the arrays
then we segment on junctions we've found and average segments together and weight them
in this method we analyze all the data each time, but it shouldn't be that heavy of a lift. we'll see 
"""


class Junction:
    def __init__(self, lat, lon, weight, found_in):
        self.lat = lat  # latitude of junction
        self.lon = lon  # longitude of junction
        self.weight = weight  # weight of junction
        self.found_in = found_in  # run in which junction was identified


class Segment:
    def __init__(self, lat_arr, lon_arr, weight):
        self.lat_arr = lat_arr
        self.lon_arr = lon_arr
        self.weight = weight
        self.dist = self.calculate_distance(lat_arr, lon_arr)

    def calculate_distance(self, lat_arr, lon_arr):
        delta = [dist.distance([lat_arr[i], lon_arr[i]], [lat_arr[i + 1], lon_arr[i + 1]]).m for i in
                 np.arange(len(lat_arr) - 1)]
        return np.sum(delta)  # [m]


class Park:

    def __init__(self, park_direc, name='blank'):
        self.name = name
        self.junctions = []
        self.segments = []
        self.analyze_park_runs(park_direc)

    def analyze_park_runs(self, park_direc):
        park_runs = self.extract_park_runs_coords(park_direc)
        for run in park_runs:
            self.analyze_run(park_runs[run], run)

    def analyze_run(self, coords, runname):
        showme = 1
        dtor = np.pi / 180
        rearth = 6371009.  # [m]
        rbubble = 200.  # [m] size of bubble to consider segment separation
        rsearch = 50.  # [m] pts within this range are not considered distinct exits from bubble
        lon, lat = coords[:, 0], coords[:, 1]
        same_start_end = 0
        if dist.distance([lat[0], lon[0]], [lat[-1], lon[-1]]).m < rsearch:
            same_start_end = 1

        def check_point(ipt):  # see how many exits from bubble around this point
            irun = np.where(((lon - lon[ipt]) / dlon) ** 2 + ((lat - lat[ipt]) / dlat) ** 2 < 1)[
                0]  # pts in ellipse dlon x dlat

            endpt_lats, endpt_lons = [], []  # get lat/lon of all segment endpoints
            if 2 < len(irun):  # must identify at least 2 indices in dlon dlat box we're investigating
                # look for non-consecutive indices indicating different segments of route
                ibreak_run = np.where(irun - np.roll(irun, 1) != 1)[0]  # indices of irun
                if 0 in ibreak_run and same_start_end:
                    ibreak_run = np.setdiff1d(ibreak_run, [0])  # remove index 0 since start/end are continuous
                for ib in ibreak_run:
                    endpt_lats.extend([lat[irun[ib - 1]], lat[irun[ib]]])
                    endpt_lons.extend([lon[irun[ib - 1]], lon[irun[ib]]])
            ipark = np.where(((parklon - lon[ipt]) / dlon) ** 2 + ((parklat - lat[ipt]) / dlat) ** 2 < 1)[0]  # park pts
            ibreak_park = np.where(ipark - np.roll(ipark, 1) != 1)[0]  # indices of ipark
            for ib in ibreak_park:
                endpt_lats.extend([parklat[ipark[ib - 1]], parklat[ipark[ib]]])
                endpt_lons.extend([parklon[ipark[ib - 1]], parklon[ipark[ib]]])
            if showme:
                plt.plot(lon, lat)
                plt.plot(lon[irun], lat[irun], '.')
                plt.plot(endpt_lons, endpt_lats, 'o')
                th = np.linspace(0, 2 * np.pi)
                plt.plot(dlon * np.cos(th) + lon[ipt], dlat * np.sin(th) + lat[ipt], 'k--')
                sc = rsearch / rbubble
                for i in np.arange(len(endpt_lons)):
                    plt.plot(sc * dlon * np.cos(th) + endpt_lons[i], sc * dlat * np.sin(th) + endpt_lats[i], 'k--')
            if len(endpt_lons) < 2:
                return len(endpt_lons)
            else:
                ipersist = []  # build array of endpoints that are distinct (outside search radius of each other)
                for i in np.arange(len(endpt_lons) - 1):
                    d = [dist.distance([endpt_lats[i], endpt_lons[i]], [endpt_lats[a], endpt_lons[a]]).m for a in
                         np.arange(i + 1, len(endpt_lons))]
                    if min(d) < rsearch:
                        pass  # another pt is close enough we don't have to count this one as an exit
                    else:
                        ipersist.append(i)
                return len(ipersist) + 1  # add +1 for last endpoint we never checked against the rest

        parklat, parklon = self.aggregate_park_coords()

        avlong, avlat = np.mean(lon), np.mean(lat)
        # # dist.distance takes [lat, lon] as input
        # delta = np.append([0], [dist.distance(coords[i][::-1][1:], coords[i + 1][::-1][1:]).m for i in
        #                         np.arange(len(coords) - 1)])
        dlat = rbubble / rearth / dtor  # [deg]
        dlon = rbubble / (rearth * np.cos(avlat * dtor)) / dtor  # [deg]

        # search through new lat/lon arrays for new junctions
        i2scan = np.arange(len(lon))
        while len(i2scan) > 0:
            ipt = i2scan[0]
            check = check_point(ipt)
            while check <= 2:
                ipt += 10  # jump ahead and check again
                if ipt > i2scan[-1]:
                    check = check_point(i2scan[-1])
                    break
                check = check_point(ipt)
                print(f'ipt: {ipt} check = {check}')
                plt.show()
            a = 1

        self.junctions.append(Junction(1, 2, 3, 'ur_butt'))
        self.segments.append(Segment([1, 2, 3, 4], [5, 6, 7, 8], 9))

    def aggregate_park_coords(self):
        lat, lon = [], []
        for seg in self.segments:
            lat.append(seg.lat_arr)
            lon.append(seg.lon_arr)
        return lat, lon

    def process_coordinate_string(self, strng):
        """
        Take the coordinate string from the KML file, and break it up into [[Lat,Lon,Alt],[Lat,Lon,Alt],...]
        """
        long_lat_alt_arr = []
        for point in strng.split('\n'):
            if len(point) > 0:
                long_lat_alt_arr.append(
                    [float(point.split(',')[0]), float(point.split(',')[1]), float(point.split(',')[2])])
        return long_lat_alt_arr

    def extract_park_runs_coords(self, park):
        run_dict = {}
        for run in glob.glob(park + '*.kml'):
            runname = run.strip(park).strip('\\')
            with open(run, 'r') as f:
                s = BeautifulSoup(f, 'xml')
                run_coords = []
                for coords in s.find_all('coordinates'):
                    if len(run_coords) == 0:
                        run_coords = np.array(self.process_coordinate_string(coords.string))
                    else:
                        run_coords = np.append(run_coords, self.process_coordinate_string(coords.string))
            run_dict[runname] = run_coords
        return run_dict


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

    # scan over all points looking for junctions
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
    # I don't like this- we create a box 50 m wide, the only consider different segments distinct if the distance between the points is > 100? seems arbitrary and weird
    # create box around pt of size dlat x dlon
    ii = np.where((lon >= lon[ipt] - dlon / 2.) & (lon < lon[ipt] + dlon / 2.) & (
            lat >= lat[ipt] - dlat / 2.) & (lat < lat[ipt] + dlat / 2.))[0]
    if 2 < len(ii):  # must identify at least 2 indices in dlon dlat box we're investigating
        # look for non-consecutive indices indicating different segments of route
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
    park_dir = 'C:/Users/willi/Dropbox/ParkMaps/ElmCreekRuns/'
    park = Park(park_dir, name='Elm Creek')
    a = 1
