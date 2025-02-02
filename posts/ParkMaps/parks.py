import glob

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import geopy.distance as dist
from bs4 import BeautifulSoup
from parkmap_tools import self_compare2, extract_park_runs_coords, segment_on_junctions, dual_compare, fold_together
import uuid

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
        self.uid = uuid.uuid4()  # create unique identifier for each junction


class Segment:
    def __init__(self, lat_arr, lon_arr, weight, start_junc: Junction, end_junc: Junction, runname):
        self.lat_arr = lat_arr
        self.lon_arr = lon_arr
        self.weight = weight
        self.uid = uuid.uuid4()
        self.found_in = runname
        self.start_junc = start_junc
        self.end_junc = end_junc
        self.dist = self.calculate_distance(lon_arr, lat_arr)

    def calculate_distance(self, lon_arr, lat_arr):
        lona = np.append(self.start_junc.lon, np.append(lon_arr, self.end_junc.lon))
        lata = np.append(self.start_junc.lat, np.append(lat_arr, self.end_junc.lat))
        delta = [dist.distance([lata[i], lona[i]], [lata[i + 1], lona[i + 1]]).m for i in
                 np.arange(len(lata) - 1)]
        return np.sum(delta)  # [m]


class Park:

    def __init__(self, park_direc, name='blank'):
        self.name = name
        self.junctions = []
        self.segments = []
        self.runs_analyzed = []
        self.analyze_park_runs(park_direc)

    def analyze_park_runs(self, park_direc):
        park_runs = extract_park_runs_coords(park_direc)
        for run in park_runs:
            if run not in self.runs_analyzed:  # only go through runs we haven't looked at before
                self.analyze_run(park_runs[run], run)

    def analyze_run(self, coords, runname):
        print('analyzing run')
        # step 1- segment on known junctions
        broken_up_segs = self.segment_on_junctions(coords)

        # step 2- compare resulting segments with known segments, average into if same
        for seg in broken_up_segs:
            sameas = self.compare_to_known_segments(seg)
            # todo Need to add handling for when new segment diverges from known, creating new junction
            if sameas is None:  # new segment
                newjuncs, weights = self_compare2(seg)  # check for new juncs in new segment
                if len(newjuncs) == 0:  # no new juncs, add as new segment
                    # print(f'found new segment in {runname}!')
                    self.segments.append(Segment(seg.lat_arr, seg.lon_arr, 1, seg.start_junc, seg.end_junc, runname))
                else:
                    for (nj, wt) in zip(newjuncs, weights):
                        # print(f'found new junction in {runname}')
                        self.junctions.append(Junction(nj[1], nj[0], wt, runname))
                    self.analyze_run(coords, runname)  # send through again with new junctions known
            else:
                self.fold_into(sameas, seg)
        self.runs_analyzed.append(runname)

    def segment_on_junctions(self, coords):
        broken_up_segs = segment_on_junctions(coords, self.junctions)
        return broken_up_segs

    def compare_to_known_segments(self, segment):
        sameas = None
        for kseg in self.segments:
            sameas = dual_compare(kseg, segment)
            if sameas is not None:
                break  # found same segment, no need to search further
        return sameas

    def fold_into(self, segid, seg):
        foldinto = self.segments[np.where(np.array([s.uid for s in self.segments]) == segid)[0][0]]
        foldlon, foldlat = foldinto.lon_arr, foldinto.lat_arr
        if foldinto.start_junc != seg.start_junc:  # reverse order to align direction of segments
            seglon, seglat = seg.lon_arr[::-1], seg.lat_arr[::-1]
        else:
            seglon, seglat = seg.lon_arr, seg.lat_arr
        newlon, newlat = fold_together(foldlon, foldlat, seglon, seglat, foldinto.dist)
        foldinto.weight += 1
        foldinto.lon_arr = newlon
        foldinto.lat_arr = newlat
        foldinto.dist = foldinto.calculate_distance(foldinto.lon_arr, foldinto.lat_arr)

    def plot(self):
        for seg in self.segments:
            plt.plot(seg.lon_arr, seg.lat_arr)
            imid = int(len(seg.lon_arr) / 2.)
            plt.annotate(f'{seg.weight}', (seg.lon_arr[imid], seg.lat_arr[imid]))
        for junc in self.junctions:
            plt.plot(junc.lon, junc.lat, 'd')
            plt.annotate(f'{junc.weight}', (junc.lon, junc.lat))


if __name__ == "__main__":
    fig, ax = plt.subplots()
    park_dir = 'C:/Users/willi/PycharmProjects/capecchi.github.io/posts/ParkMaps/ElmCreekRuns/'
    park = Park(park_dir, name='Elm Creek')
    park.plot()
    plt.show()
    a = 1
