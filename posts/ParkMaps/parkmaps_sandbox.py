import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import geopy.distance as dist

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']


# just some testing grounds for new algorithms

def subdivide_arc(lon, lat):
    # my version of split-average method
    # add pt between adjacent pts based on midpoint of perp bisector between segment and the point defined by joining of two adjacent segments
    # ambitious? maybe. but might have cool implications for rounding corners without losing them
    nsmooth = 2  # do this many iterations of smoothing algorithm
    slon, slat = np.copy(lon), np.copy(lat)
    delta = np.array([dist.distance([lat[i], lon[i]], [lat[i + 1], lon[i + 1]]).m for i in np.arange(len(lat) - 1)])
    for i in np.arange(nsmooth):
        # "smart" bisect phase
        dlon = slon[1:] - slon[:-1]
        dlon[dlon == 0] = 1.e-10  # small but nonzero
        dlatdlon = (slat[1:] - slat[:-1]) / dlon  # slopes of all segments
        b = slat[:-1] - dlatdlon * slon[:-1]  # intercept of each segment
        mplon = (b[2:] - b[:-2]) / (dlatdlon[:-2] - dlatdlon[2:])
        mplat = dlatdlon[:-2] * mplon + b[:-2]

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

        plt.plot(slon, slat, 'o--')
        a = 1
    # desample
    plt.plot(slon, slat, 'kd-')
    x1, x2 = np.linspace(0, 1, num=len(lon)), np.linspace(0, 1, num=len(slon))
    slon, slat = np.interp(x1, x2, slon), np.interp(x1, x2, slat)
    plt.plot(slon, slat, 'rd-')
    a = 1
    return slon, slat


def clean_subdivide(lon, lat, delta, num):
    slon, slat, sdel = np.copy(lon), np.copy(lat), np.copy(delta)
    for i in np.arange(num):  # iterate N times
        splon, splat = (slon[:-1] + slon[1:]) / 2., (slat[:-1] + slat[1:]) / 2.  # midpoints
        slon = np.append([x for p in zip(slon[:-1], splon) for x in p], slon[-1])
        slat = np.append([x for p in zip(slat[:-1], splat) for x in p], slat[-1])
        sdel = np.array([x for p in zip(delta, delta) for x in p]) / 2.
        a = 1
    return slon, slat, sdel


def seg_intersect(s1, s2):
    x11, y11, x12, y12 = s1[0][0], s1[0][1], s1[1][0], s1[1][1]
    x21, y21, x22, y22 = s2[0][0], s2[0][1], s2[1][0], s2[1][1]
    m1, m2 = (y12 - y11) / (x12 - x11), (y22 - y21) / (x22 - x21)
    b1, b2 = y11 - m1 * x11, y22 - m2 * x22
    xint = (b2 - b1) / (m1 - m2)
    yint = m1 * xint + b1
    if (xint >= x11) & (xint < x12) & (yint >= y11) & (yint < y12):
        return [xint, yint]
    else:
        return None


def fold_test():
    known_dist = 306.7  # this will be a known quantity of the segment (eventually)
    jlon1, jlat1 = -93.24447793750001, 45.02520596875
    jlon2, jlat2 = -93.2477414375, 45.02601475

    lon1 = np.array(
        [-93.24464, -93.244637, -93.244642, -93.244648, -93.244658, -93.244679, -93.244812, -93.244861, -93.244905,
         -93.245044, -93.245203, -93.245339, -93.245414, -93.245401, -93.245372, -93.245355, -93.245368, -93.245404,
         -93.245445, -93.245604, -93.245736, -93.245842, -93.245972, -93.246134, -93.246171, -93.24622, -93.246262,
         -93.246303, -93.246338, -93.246365, -93.246395, -93.246424, -93.246453, -93.246475, -93.246527, -93.246564,
         -93.246604, -93.246644, -93.246681, -93.24672, -93.246759, -93.246796, -93.246835, -93.246875, -93.246918,
         -93.246961, -93.247005, -93.247049, -93.247092, -93.247135, -93.24718, -93.247228, -93.247277, -93.247323,
         -93.24737, -93.247415, -93.247458, -93.247493, -93.247526, -93.24752, -93.247519, -93.247519, -93.247518,
         -93.247516, -93.24752, -93.247534, -93.24756, -93.247596, -93.247635, -93.247677, -93.24772])
    lat1 = np.array(
        [45.025207, 45.025233, 45.02526, 45.025289, 45.025317, 45.025339, 45.025407, 45.025447, 45.025478, 45.025511,
         45.025524, 45.025533, 45.025559, 45.025586, 45.025629, 45.025663, 45.025689, 45.025705, 45.025719, 45.025737,
         45.025741, 45.025739, 45.025744, 45.025752, 45.025757, 45.025764, 45.02577, 45.025768, 45.025771, 45.025769,
         45.025783, 45.025791, 45.025761, 45.025729, 45.025717, 45.025717, 45.025715, 45.025718, 45.025721, 45.025726,
         45.025729, 45.02573, 45.025733, 45.025738, 45.025738, 45.025734, 45.025736, 45.025737, 45.025736, 45.025735,
         45.025736, 45.025733, 45.025728, 45.025723, 45.025719, 45.025712, 45.025706, 45.025702, 45.025698, 45.025718,
         45.025739, 45.025764, 45.025788, 45.025813, 45.025837, 45.025858, 45.025871, 45.025881, 45.025893, 45.025901,
         45.025905])
    lon2 = np.array(
        [-93.247554, -93.247552, -93.24755, -93.247548, -93.247548, -93.24755, -93.247551, -93.247554, -93.247557,
         -93.247567, -93.247577, -93.247582, -93.247593, -93.247601, -93.247601, -93.247603, -93.247605, -93.2476,
         -93.247593, -93.247588, -93.247565, -93.247521, -93.24748, -93.247448, -93.247411, -93.247376, -93.24734,
         -93.247302, -93.247266, -93.247227, -93.247189, -93.247153, -93.247114, -93.247079, -93.247041, -93.247,
         -93.246962, -93.246924, -93.246886, -93.246849, -93.246811, -93.246771, -93.246728, -93.246689, -93.246651,
         -93.246614, -93.246577, -93.246539, -93.246499, -93.246463, -93.24643, -93.246395, -93.246358, -93.246323,
         -93.246282, -93.246241, -93.246201, -93.246163, -93.246127, -93.246082, -93.246046, -93.246014, -93.245979,
         -93.245955, -93.245943, -93.245932, -93.245914, -93.245886, -93.245854, -93.245817, -93.245783, -93.245745,
         -93.24571, -93.245675, -93.245638, -93.245602, -93.245568, -93.245535, -93.245501, -93.245461, -93.245415,
         -93.245372, -93.245329, -93.245284, -93.245237, -93.245192, -93.245147, -93.245111, -93.245069, -93.245034,
         -93.245, -93.244963, -93.244929, -93.244892, -93.244855, -93.244823, -93.244792, -93.244761, -93.244728,
         -93.244694, -93.244663, -93.244631, -93.244602, -93.244576, -93.244549, -93.244523, -93.244494, -93.244466,
         -93.244443, -93.24442, -93.244398, -93.244375, -93.244353, -93.244334, -93.244313])
    lat2 = np.array(
        [45.026028, 45.026002, 45.025973, 45.025944, 45.025919, 45.025894, 45.025871, 45.02585, 45.025832, 45.025804,
         45.025786, 45.025767, 45.025748, 45.025728, 45.025707, 45.025681, 45.025655, 45.025629, 45.025607, 45.025587,
         45.025577, 45.02558, 45.025586, 45.025586, 45.025587, 45.02559, 45.025593, 45.025598, 45.025604, 45.025609,
         45.025613, 45.025616, 45.025619, 45.025618, 45.025615, 45.025612, 45.02561, 45.025608, 45.025606, 45.025604,
         45.025605, 45.025605, 45.025605, 45.025601, 45.025599, 45.025597, 45.025598, 45.0256, 45.0256, 45.0256,
         45.0256, 45.025596, 45.025592, 45.025591, 45.025592, 45.025593, 45.025591, 45.025588, 45.025585, 45.025591,
         45.0256, 45.025604, 45.025607, 45.025625, 45.025641, 45.025659, 45.025679, 45.025695, 45.025704, 45.025706,
         45.025709, 45.025713, 45.025717, 45.02572, 45.025724, 45.025725, 45.025725, 45.025727, 45.025728, 45.025728,
         45.025725, 45.025726, 45.025728, 45.025727, 45.025725, 45.025722, 45.02572, 45.025717, 45.025712, 45.025701,
         45.025692, 45.025683, 45.025678, 45.02567, 45.025661, 45.025651, 45.025637, 45.025622, 45.025605, 45.025589,
         45.025572, 45.025555, 45.025539, 45.025521, 45.0255, 45.02548, 45.025462, 45.025446, 45.025427, 45.02541,
         45.025391, 45.025373, 45.025354, 45.025333, 45.025312])
    lon2 = lon2[::-1]
    lat2 = lat2[::-1]

    d1 = [dist.distance([lat1[0], lon1[0]], [lat1[i], lon1[i]]).m for i in np.arange(len(lon1))]
    d2 = [dist.distance([lat2[0], lon2[0]], [lat2[i], lon2[i]]).m for i in np.arange(len(lon2))]
    x1, x2 = np.linspace(0, 1, num=len(d1)), np.linspace(0, 1, num=len(d2))

    xint = np.linspace(0, 1, num=int(known_dist * 2))  # set for roughly 1/2 m interval
    ilon1, ilat1 = np.interp(xint, x1, lon1), np.interp(xint, x1, lat1)
    ilon2, ilat2 = np.interp(xint, x2, lon2), np.interp(xint, x2, lat2)
    ilon, ilat = (ilon1 + ilon2) / 2., (ilat1 + ilat2) / 2.

    plt.plot(lon1, lat1)
    plt.plot(lon2, lat2)
    plt.plot(ilon, ilat, '--')
    a = 1


if __name__ == '__main__':
    # lon, lat = np.array([0, 0, .1, .5, 2, 5]), np.array([0, 2, 2.5, 2.9, 3.0, 3.0])
    # delta = np.array([dist.distance([lat[i], lon[i]], [lat[i + 1], lon[i + 1]]).m for i in np.arange(len(lat) - 1)])
    # plt.plot(lon, lat, 'o-')
    # # slon, slat = subdivide_arc(lon, lat)
    # slon, slat, sdel = clean_subdivide(lon, lat, delta, 4)
    # xx = np.linspace(0, 10)
    # yy1, yy2 = xx, 10 - xx
    # inters = find_array_intersect(xx, yy1, xx, yy2)
    # plt.plot(xx, yy1, 'o-')
    # plt.plot(xx, yy2, 'o-')
    # plt.plot(inters[0], inters[1], 'kd')
    fold_test()
    a = 1
