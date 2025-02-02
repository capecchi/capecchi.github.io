import glob
import uuid

import geopy.distance as dist
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

# SENSITIVITY CONTROLS--------------------------------------------------
set_break_dist = 1000.  # [m] segments disjoint if > this dist apart
junc_merge_dist = 100.  # [m] merge junctions if they're within this distance of each other
rsearch = 50.  # [m] box size to look for disjoint segments
rcompare = 2. * rsearch  # [m] box size to compare 2 segments- rsearch sets potential split dist, so make bigger to include these when we compare later
# ----------------------------------------------------------

dtor = np.pi / 180
rearth = 6371009.  # [m]
dlat = rsearch / rearth / dtor  # [deg]
dlat_comp = rcompare / rearth / dtor  # [deg]


class SomethingHappened(Exception):
    def __init__(self, message):
        self.message = message


class BrokenSegment:
    def __init__(self, lon_arr, lat_arr, jstart, jend):
        self.uid = uuid.uuid4()  # create unique ID for this segment
        self.lon_arr = lon_arr
        self.lat_arr = lat_arr
        self.start_junc = jstart
        self.end_junc = jend
        # self.weight = weight  # no weight for these since they have yet to be processed as Segment

    def prepend_to(self, lon_arr, lat_arr, start_junc, end_junc):
        self.lon_arr = np.append(lon_arr, self.lon_arr)
        self.lat_arr = np.append(lat_arr, self.lat_arr)
        if start_junc is not None:
            self.start_junc = start_junc
        if end_junc is not None:
            self.end_junc = end_junc

    def plot(self):
        plt.plot(self.lon_arr, self.lat_arr)


def segment_on_junctions(coords, junctions):
    lon, lat = coords[:, 0], coords[:, 1]
    avlat = np.mean(lat)
    dlon = rsearch / (rearth * np.cos(avlat * dtor)) / dtor  # [deg]
    loop = dist.distance(coords[0][::-1][1:], coords[-1][::-1][1:]).m < rsearch
    icuts, juncs = [], []
    for junc in junctions:  # see if junction is close to coords
        ii = np.where((lat >= junc.lat - dlat) & (lat < junc.lat + dlat) & (lon >= junc.lon - dlon) & (
                lon < junc.lon + dlon))[0]
        # todo: work here- find way to pull route through junction (find nearest, look 200m in each direc, smooth through junc or something- normalize distance later?)
        ibreak = np.where((ii - np.roll(ii, 1) + len(lon)) % len(lon) != 1)[0]
        if 0 in ii[ibreak]:  # start included- check if coords are loop?
            if dist.distance([lat[0], lon[0]], [lat[-1], lon[-1]]).m < rsearch:
                ibreak = np.delete(ibreak, np.where(ii[ibreak] == 0))
        for iib, ib in enumerate(ibreak):  # go through each seg and find closest pt
            if ib == ibreak[-1]:  # if last index, take segment to end
                iseg = ii[ib:]
            else:
                iseg = ii[ibreak[iib]:ibreak[iib + 1]]
                # iseg = ii[ibreak[ib]:ibreak[ib + 1]]  this is bad- ib doesn't index ibreak
            jdist = [dist.distance([junc.lat, junc.lon], [lat[ic], lon[ic]]).m for ic in
                     iseg]  # compute dist to each pt
            iclosest = np.where(np.array(jdist) == min(jdist))[0][0]
            jdist[iclosest] = max(jdist)
            i2nd = np.where(np.array(jdist) == min(jdist))[0][0]
            icuts.append(min([iseg[iclosest], iseg[i2nd]]))  # take the first index and we'll cut after this index later
            juncs.append(junc)  # keep track of which junction we segmented on
    if len(icuts) > 0:
        icuts, juncs = zip(*sorted(zip(icuts, juncs)))  # sort cuts so we're taking chunks out of coords
    seg_arr = []
    if len(icuts) == 0:  # no cuts found, return whole array
        seg_arr.append(BrokenSegment(lon, lat, None, None))
    for ic in np.arange(len(icuts)):
        if ic == 0:  # +1 so we include ic in index array
            seg_arr.append(BrokenSegment(lon[:icuts[ic] + 1], lat[:icuts[ic] + 1], None, juncs[ic]))
        if ic == len(icuts) - 1:  # last index
            if loop:
                seg_arr[0].prepend_to(lon[icuts[ic]:], lat[icuts[ic]:], juncs[ic], None)
            else:
                seg_arr.append(BrokenSegment(lon[icuts[ic]:], lat[icuts[ic]:], juncs[ic], None))
        else:
            seg_arr.append(
                BrokenSegment(lon[icuts[ic]:icuts[ic + 1] + 1], lat[icuts[ic]:icuts[ic + 1] + 1], juncs[ic],
                              juncs[ic + 1]))
    return seg_arr


def box_smooth_coords(lon, lat, dlon):
    slat, slon = np.copy(lat), np.copy(lon)
    for i in np.arange(len(lon)):
        ii = np.where((lon >= lon[i] - dlon / 2.) & (lon < lon[i] + dlon / 2.) & (
                lat >= lat[i] - dlat / 2.) & (lat < lat[i] + dlat / 2.))[0]
        slat[i], slon[i] = np.mean(lat[ii]), np.mean(lon[ii])
    plt.plot(slon, slat)
    return slon, slat


def subdivide_coords(lon, lat):
    nsub = 10  # number of times to subdivide
    slon, slat = np.copy(lon), np.copy(lat)
    for i in np.arange(nsub):
        splon, splat = (slon[:-1] + slon[1:]) / 2., (slat[:-1] + slat[1:]) / 2.  # midpoints
        slon = [x for p in zip((slon[:-1] + splon) / 2., (splon + slon[1:]) / 2.) for x in p]  # averaging
        slat = [x for p in zip((slat[:-1] + splat) / 2., (splat + slat[1:]) / 2.) for x in p]
        slon = np.append(lon[0], np.append(slon, lon[-1]))  # reattach endpoints
        slat = np.append(lat[0], np.append(slat, lat[-1]))
        slon = np.interp(np.linspace(0, 1, len(lon)), np.linspace(0, 1, len(slon)), slon)  # downsample to keep N pts
        slat = np.interp(np.linspace(0, 1, len(lat)), np.linspace(0, 1, len(slat)), slat)
    plt.plot(slon, slat)
    return slon, slat


def clean_subdivide(lon, lat, delta, num):
    slon, slat, sdel = np.copy(lon), np.copy(lat), np.copy(delta)
    for i in np.arange(num):  # iterate N times
        splon, splat = (slon[:-1] + slon[1:]) / 2., (slat[:-1] + slat[1:]) / 2.  # midpoints
        slon = np.append([x for p in zip(slon[:-1], splon) for x in p], slon[-1])
        slat = np.append([x for p in zip(slat[:-1], splat) for x in p], slat[-1])
        sdel = np.array([x for p in zip(sdel, sdel) for x in p]) / 2.
    return slon, slat, sdel


def subdivide_arc(lon, lat, delta):
    # my version of split-average method
    # add pt between adjacent pts based on adjacent segment intersect
    # ambitious? maybe. but might have cool implications for rounding corners without losing them
    nsmooth = 2  # do this many iterations of smoothing algorithm
    slon, slat = np.copy(lon), np.copy(lat)
    for i in np.arange(nsmooth):
        # "smart" bisect phase
        dlon = slon[1:] - slon[:-1]
        dlon[dlon == 0] = 1.e-10  # small but nonzero
        dlatdlon = (slat[1:] - slat[:-1]) / dlon  # slopes of all segments
        b = slat[:-1] - dlatdlon * slon[:-1]  # intercept of each segment
        th = np.arctan2(slat[1:] - slat[:-1], dlon)  # angle of each segment
        mplon = (slon[1:-2] + slon[2:-1]) / 2.  # initialize with midpoint
        mplat = (slat[1:-2] + slat[2:-1]) / 2.
        ii = np.where((abs(th[2:] - th[:-2]) < np.pi) & (abs(th[2:] - th[:-2]) > 0))  # ensure segs < 90 deg change
        mplon[ii] = (b[2:][ii] - b[:-2][ii]) / (dlatdlon[:-2][ii] - dlatdlon[2:][ii])
        mplat[ii] = dlatdlon[:-2][ii] * mplon[ii] + b[:-2][ii]

        # COULD try different weighting here to see what feels good
        mplon, mplat = (3 * (slon[1:-2] + slon[2:-1]) / 2. + mplon) / 4., (
                3 * (slat[1:-2] + slat[2:-1]) / 2. + mplat) / 4.
        mplon = np.append((lon[0] + lon[1]) / 2., np.append(mplon, (lon[-2] + lon[-1]) / 2.))  # add on first/last mids
        mplat = np.append((lat[0] + lat[1]) / 2., np.append(mplat, (lat[-2] + lat[-1]) / 2.))
        slon = np.append(np.array([x for p in zip(slon[:-1], mplon) for x in p]), slon[-1])
        slat = np.append(np.array([x for p in zip(slat[:-1], mplat) for x in p]), slat[-1])

        # smooth phase
        slon, slat = (slon[1:] + slon[:-1]) / 2., (slat[1:] + slat[:-1]) / 2.
        slon = np.append(lon[0], np.append(slon, lon[-1]))  # add back endpoints
        slat = np.append(lat[0], np.append(slat, lat[-1]))

    # desample
    plt.plot(slon, slat, 'kd-')
    # x1, x2 = np.linspace(0, 1, num=len(lon)), np.linspace(0, 1, num=len(slon))
    # slon, slat = np.interp(x1, x2, slon), np.interp(x1, x2, slat)
    # plt.plot(slon, slat, 'rd-')
    # a = 1
    return slon, slat


def find_array_intersect(x1, y1, x2, y2):
    interc = None
    for iy1 in np.arange(len(y1) - 1):
        x11, y11, x12, y12 = x1[iy1], y1[iy1], x1[iy1 + 1], y1[iy1 + 1]
        for iy2 in np.arange(len(y2) - 1):
            x21, y21, x22, y22 = x2[iy2], y2[iy2], x2[iy2 + 1], y2[iy2 + 1]
            m1, m2 = (y12 - y11) / (x12 - x11), (y22 - y21) / (x22 - x21)
            b1, b2 = y11 - m1 * x11, y22 - m2 * x22
            xint = (b2 - b1) / (m1 - m2)
            yint = m1 * xint + b1
            if (xint >= min([x11, x12])) & (xint < max([x11, x12])) & (yint >= min([y11, y12])) & (
                    yint < max([y11, y12])):
                interc = [xint, yint]
                break
        if interc is not None:
            break
    return interc


def self_compare_old(seg: BrokenSegment):  # compares a segment with itself to look for junctions
    lon, lat = seg.lon_arr, seg.lat_arr
    avlat = np.mean(lat)
    dlon = rsearch / (rearth * np.cos(avlat * dtor)) / dtor  # [deg]
    # plt.plot(lon, lat)
    # dist.distance takes [lat, lon] as input
    delta = np.array([dist.distance([lat[i], lon[i]], [lat[i + 1], lon[i + 1]]).m for i in np.arange(len(lon) - 1)])
    nsmooth = np.ceil(np.log2(max(delta)))  # subdivide so steps are < 1 m
    lon, lat, delta = clean_subdivide(lon, lat, delta, nsmooth)  # just adds in midpoints, no smoothing
    delta = np.append(0., delta)  # throw 0 out front so delta lines up with lat/lon array
    cumdist = np.nancumsum(delta)  # cumulative route distance

    loop = dist.distance([lat[0], lon[0]], [lat[-1], lon[-1]]).m < rsearch

    segs, isibs = [], []
    i2scan = np.arange(len(lon))
    while len(i2scan) > 0:
        ptstat, _ = determine_pt_status(lon, lat, dlon, dlat, i2scan[0], cumdist, loop, verbose=True)
        posptstat, negptstat, ipos, ineg = ptstat, ptstat, i2scan[0], i2scan[0]

        # big moves
        ijump = 500  # jump some pts and check again
        while posptstat == ptstat:
            ipos += ijump
            if ipos not in i2scan:
                break
            posptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ipos, cumdist, loop)
        while negptstat == ptstat:
            ineg -= ijump
            if (ineg + len(lon)) % len(lon) not in i2scan:
                break
            negptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ineg, cumdist, loop)

        # small moves
        posptstat, negptstat, ipos, ineg = ptstat, ptstat, ipos - ijump, ineg + ijump  # reset and check again
        ijump = 1  # jump some pts and check again
        while posptstat == ptstat:
            ipos += ijump
            if ipos not in i2scan:
                ipos -= ijump  # reset to last index
                break
            posptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ipos, cumdist, loop)
        while negptstat == ptstat:
            ineg -= ijump
            if (ineg + len(lon)) % len(lon) not in i2scan:
                ineg += ijump  # reset to last index
                break
            negptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ineg, cumdist, loop)

        # if ineg < 0:  # spanning start pt
        #     plt.plot(np.roll(lon, -ineg)[:ipos - ineg], np.roll(lat, -ineg)[:ipos - ineg])
        # else:
        #     plt.plot(lon[ineg:ipos], lat[ineg:ipos])
        iseg = np.arange(ineg, ipos + 1)
        if ptstat == 2:
            if len(iseg) % 2 == 0:  # even
                imid = int(np.median(iseg))
            else:
                imid = int(np.median(iseg[:-1]))
            _, isib = determine_pt_status(lon, lat, dlon, dlat, imid, cumdist, loop)  # , verbose=True)
            isibs.append(isib)
        else:
            isibs.append([None])
        segs.append(iseg)
        i2scan = np.setdiff1d(i2scan, (iseg + len(lon)) % len(lon))  # mod here so that if < 0 returns pos index for pts
        print('looping')

    juncs = []
    if len(segs) > 1:  # only look for junctions if more than one segment identifies
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
    # for j in juncs:
    #     plt.plot(j[0], j[1], 'o')
    # merge adjacent juncs
    juncs_merged, weights = [], []
    ijunc2scan = np.arange(len(juncs))
    while len(ijunc2scan) > 0:
        jdist = [dist.distance(juncs[ijunc2scan[0]][::-1], juncs[iij][::-1]).m for iij in ijunc2scan]
        iav = np.where(np.array(jdist) < junc_merge_dist)  # merge juncs within junc_merge_dist
        avgd_junc = np.mean(np.array(juncs)[ijunc2scan[iav]], axis=0)
        # attempt at improving junc location----------------------------
        ii = np.where((lon >= avgd_junc[0] - dlon) & (lon < avgd_junc[0] + dlon) & (
                lat >= avgd_junc[1] - dlat) & (lat < avgd_junc[1] + dlat))[0]

        # --------------------------------------------------------------
        juncs_merged.append(avgd_junc)
        weights.append(len(iav[0]))
        ijunc2scan = np.setdiff1d(ijunc2scan, ijunc2scan[iav])
    # for j in juncs_merged:
    #     plt.plot(j[0], j[1], 's')
    return juncs_merged, weights


def self_compare(seg: BrokenSegment):  # compares a segment with itself to look for junctions
    lon, lat = seg.lon_arr, seg.lat_arr
    avlat = np.mean(lat)
    dlon = rsearch / (rearth * np.cos(avlat * dtor)) / dtor  # [deg]
    # dist.distance takes [lat, lon] as input
    delta = np.array([dist.distance([lat[i], lon[i]], [lat[i + 1], lon[i + 1]]).m for i in np.arange(len(lon) - 1)])
    nsmooth = np.ceil(np.log2(max(delta)))  # subdivide so steps are < 1 m
    lon, lat, delta = clean_subdivide(lon, lat, delta, nsmooth)  # just adds in midpoints, no smoothing
    delta = np.append(0., delta)  # throw 0 out front so delta lines up with lat/lon array
    cumdist = np.nancumsum(delta)  # cumulative route distance

    loop = dist.distance([lat[0], lon[0]], [lat[-1], lon[-1]]).m < rsearch

    juncs = []
    scanning = True
    ipos = 0
    while scanning:
        ptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ipos, cumdist, loop)  # , verbose=True)
        posptstat = ptstat

        # big moves
        ijump = 100  # jump some pts and check again
        while posptstat == ptstat:
            ipos += ijump
            if ipos >= len(lon):
                scanning = False
                break
            posptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ipos, cumdist, loop)

        # small moves
        posptstat, ipos = ptstat, ipos - ijump  # reset and check again
        ijump = 1  # jump some pts and check again
        while posptstat == ptstat:
            ipos += ijump
            if ipos >= len(lon):
                scanning = False
                break
            posptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ipos, cumdist, loop)

        if ipos < len(lon):
            juncs.append([lon[ipos], lat[ipos]])  # [lon, lat]

    juncs_merged, weights = [], []
    ijunc2scan = np.arange(len(juncs))
    while len(ijunc2scan) > 0:
        jdist = [dist.distance(juncs[ijunc2scan[0]][::-1], juncs[iij][::-1]).m for iij in ijunc2scan]
        iav = np.where(np.array(jdist) < junc_merge_dist)  # merge juncs within junc_merge_dist
        avgd_junc = np.mean(np.array(juncs)[ijunc2scan[iav]], axis=0)
        juncs_merged.append(avgd_junc)
        weights.append(len(iav[0]))
        ijunc2scan = np.setdiff1d(ijunc2scan, ijunc2scan[iav])
    return juncs_merged, weights


def plot_box(lon, lat, ipt, dlon, dlat):
    ii = np.where((lon >= lon[ipt] - dlon / 2.) & (lon < lon[ipt] + dlon / 2.) & (
            lat >= lat[ipt] - dlat / 2.) & (lat < lat[ipt] + dlat / 2.))[0]
    plt.plot(lon[ii], lat[ii], 'o')
    plt.plot(
        [lon[ipt] - dlon / 2., lon[ipt] - dlon / 2., lon[ipt] + dlon / 2., lon[ipt] + dlon / 2., lon[ipt] - dlon / 2.],
        [lat[ipt] - dlat / 2., lat[ipt] + dlat / 2., lat[ipt] + dlat / 2., lat[ipt] - dlat / 2., lat[ipt] - dlat / 2.],
        'ko--')


def look_for_divergence(lon, lat, dlon, dlat, ipt, cumdist, loop):
    ii = np.where((lon >= lon[ipt] - dlon / 2.) & (lon < lon[ipt] + dlon / 2.) & (
            lat >= lat[ipt] - dlat / 2.) & (lat < lat[ipt] + dlat / 2.))[0]
    if 2 < len(ii):  # must identify at least 2 indices in dlon dlat box we're investigating
        # look for non-consecutive indices indicating different segments of route
        ibreak = np.where((ii - np.roll(ii, 1) + len(lon)) % len(lon) != 1)[0]
        if len(ibreak) > 0:  # multiple segments detected
            for ib in ibreak:  # determine if break exceeds gap threshold
                if loop:  # look forward and backward
                    break_dist = min([abs(cumdist[ii[ib]] - cumdist[ipt]),
                                      cumdist[-1] - abs(cumdist[ipt] - cumdist[ii[ib]])])  # cumulative dist from ref
                else:
                    break_dist = abs(cumdist[ii[ib]] - cumdist[ipt])
                if break_dist < set_break_dist:
                    ibreak = np.delete(ibreak, np.where(ibreak == ib))
            a = 1
    return None


def get_close_indices(lon, lat, dlon, dlat, ipt, cumdist, loop):
    if loop:
        reldist = np.min([abs(cumdist - cumdist[ipt]), cumdist[-1] - (cumdist - cumdist[ipt])], axis=0)
    else:
        reldist = abs(cumdist - cumdist[ipt])
    ii = np.where((lon >= lon[ipt] - dlon / 2.) & (lon < lon[ipt] + dlon / 2.) & (
            lat >= lat[ipt] - dlat / 2.) & (lat < lat[ipt] + dlat / 2.) & (
                          reldist > set_break_dist))[0]
    return ii


def solo_seg_scan(lon, lat, dlon, dlat, ipt, cumdist, loop):
    plt.plot(lon, lat)
    plt.gca().set_aspect('equal')
    ijuncs = []

    # look backwards
    iback, scanback, approachdist, newapproach = ipt, True, np.inf, np.inf
    while scanback:
        ii = get_close_indices(lon, lat, dlon, dlat, iback, cumdist, loop)
        if len(ii) > 0:  # we're near another disjoint segment
            newapproach = min([dist.distance([lat[i], lon[i]], [lat[iback], lon[iback]]).m for i in ii])
        if newapproach < approachdist:
            approachdist = newapproach
        elif newapproach > approachdist:
            iback += 1  # reset to closest approach index
            ijuncs.append(iback)
            break  # if it ever increases, stop search
        iback -= 1
        if iback < 0:
            if loop:
                iback = len(lon) - 1  # restart at end of loop and keep scanning
            else:
                break

    # look forwards
    iforw, scanforw, approachdist, newapproach, reachedend = ipt, True, np.inf, np.inf, False
    while scanforw:
        ii = get_close_indices(lon, lat, dlon, dlat, iforw, cumdist, loop)
        if len(ii) > 0:  # we're near another disjoint segment
            newapproach = min([dist.distance([lat[i], lon[i]], [lat[iforw], lon[iforw]]).m for i in ii])
            # print(newapproach)
        if newapproach < approachdist:
            approachdist = newapproach
        elif newapproach > approachdist:
            iforw -= 1  # reset to closest approach index
            ijuncs.append(iforw)
            break  # if it ever increases, stop search
        iforw += 1
        if iforw >= len(lon):
            reachedend = True
            if loop:
                iforw = 0  # restart at beginning of loop and keep scanning
            else:
                break

    return ijuncs, reachedend


def self_compare2(seg: BrokenSegment):  # compares a segment with itself to look for junctions
    lon, lat = seg.lon_arr, seg.lat_arr
    avlat = np.mean(lat)
    dlon = rsearch / (rearth * np.cos(avlat * dtor)) / dtor  # [deg]
    # dist.distance takes [lat, lon] as input
    delta = np.array([dist.distance([lat[i], lon[i]], [lat[i + 1], lon[i + 1]]).m for i in np.arange(len(lon) - 1)])
    nsmooth = np.ceil(np.log2(max(delta)))  # subdivide so steps are < 1 m
    lon, lat, delta = clean_subdivide(lon, lat, delta, nsmooth)  # just adds in midpoints, no smoothing
    delta = np.append(0., delta)  # throw 0 out front so delta lines up with lat/lon array
    cumdist = np.nancumsum(delta)  # cumulative route distance

    loop = dist.distance([lat[0], lon[0]], [lat[-1], lon[-1]]).m < rsearch

    juncs = []
    scanning = True
    ipos, ijump = 0, 100
    while scanning:
        ptstat, _ = determine_pt_status(lon, lat, dlon, dlat, ipos, cumdist, loop)  # , verbose=True)
        if ptstat == 1:  # found solo segment, identify end junctions
            ijuncs, reachedend = solo_seg_scan(lon, lat, dlon, dlat, ipos, cumdist, loop)
            for ij in ijuncs:
                juncs.append([lon[ij], lat[ij]])
            if reachedend:
                break
            else:
                ipos = max(ijuncs)  # position at end of solo segment
        else:
            ipos += ijump
        if ipos >= len(lon):
            break

    juncs_merged, weights = [], []
    ijunc2scan = np.arange(len(juncs))
    while len(ijunc2scan) > 0:
        jdist = [dist.distance(juncs[ijunc2scan[0]][::-1], juncs[iij][::-1]).m for iij in ijunc2scan]
        iav = np.where(np.array(jdist) < junc_merge_dist)  # merge juncs within junc_merge_dist
        avgd_junc = np.mean(np.array(juncs)[ijunc2scan[iav]], axis=0)
        juncs_merged.append(avgd_junc)
        weights.append(len(iav[0]))
        ijunc2scan = np.setdiff1d(ijunc2scan, ijunc2scan[iav])
    return juncs_merged, weights


def dual_compare(known_seg, seg2compare):
    if (seg2compare.start_junc in [known_seg.start_junc, known_seg.end_junc]) & (
            seg2compare.end_junc in [known_seg.start_junc, known_seg.end_junc]):  # same endpoints
        klon, klat = known_seg.lon_arr, known_seg.lat_arr
        clon, clat = seg2compare.lon_arr, seg2compare.lat_arr
        kavlat = np.mean(klat)
        dlon_comp = rcompare / (rearth * np.cos(kavlat * dtor)) / dtor  # [deg]
        # do quick check first
        if (abs(min(clat) - min(klat)) < dlat_comp) & (abs(max(clat) - max(klat)) < dlat_comp) & (
                abs(min(clon) - min(klon)) < dlon_comp) & (abs(max(clon) - max(klon)) < dlon_comp):
            for ipt in np.arange(len(clon)):  # check each index
                ii = np.where((klon >= clon[ipt] - dlon_comp / 2.) & (klon < clon[ipt] + dlon_comp / 2.) & (
                        klat >= clat[ipt] - dlat_comp / 2.) & (klat < clat[ipt] + dlat_comp / 2.))[0]
                if len(ii) == 0:  # if we ever find pt on seg2compare with no pts in known_seg, consider distinct
                    return None
            return known_seg.uid  # all pts in seg2compare had cooresponding pts in known_seg, consider as same seg
        else:
            return None
    else:  # distinct endpoints, can't be same segment
        return None


def fold_together(lon1, lat1, lon2, lat2, known_dist):
    d1 = [dist.distance([lat1[0], lon1[0]], [lat1[i], lon1[i]]).m for i in np.arange(len(lon1))]
    d2 = [dist.distance([lat2[0], lon2[0]], [lat2[i], lon2[i]]).m for i in np.arange(len(lon2))]
    x1, x2 = np.linspace(0, 1, num=len(d1)), np.linspace(0, 1, num=len(d2))

    xint = np.linspace(0, 1, num=int(known_dist * 2))  # set for roughly 1/2 m interval
    ilon1, ilat1 = np.interp(xint, x1, lon1), np.interp(xint, x1, lat1)
    ilon2, ilat2 = np.interp(xint, x2, lon2), np.interp(xint, x2, lat2)
    ilon, ilat = (ilon1 + ilon2) / 2., (ilat1 + ilat2) / 2.

    return ilon, ilat


def determine_pt_status(lon, lat, dlon, dlat, ipt, cumdist, loop, verbose=False):
    # create box around pt of size dlat x dlon
    # print(ipt)
    ii = np.where((lon >= lon[ipt] - dlon / 2.) & (lon < lon[ipt] + dlon / 2.) & (
            lat >= lat[ipt] - dlat / 2.) & (lat < lat[ipt] + dlat / 2.))[0]
    if 2 < len(ii):  # must identify at least 2 indices in dlon dlat box we're investigating
        # look for non-consecutive indices indicating different segments of route
        ibreak = np.where((ii - np.roll(ii, 1) + len(lon)) % len(lon) != 1)[0]
        if len(ibreak) > 0:  # multiple segments detected
            for ib in ibreak:  # determine if break exceeds gap threshold
                if loop:  # look forward and backward
                    break_dist = min([abs(cumdist[ii[ib]] - cumdist[ipt]),
                                      cumdist[-1] - abs(cumdist[ipt] - cumdist[ii[ib]])])  # cumulative dist from ref
                else:
                    break_dist = abs(cumdist[ii[ib]] - cumdist[ipt])
                if break_dist < set_break_dist:
                    ibreak = np.delete(ibreak, np.where(ibreak == ib))
        if len(ibreak) > 0:  # multiple segments persist
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
    else:
        raise SomethingHappened('found < 2 indices in search box')


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


if __name__ == '__main__':
    pass
