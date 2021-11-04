from bs4 import BeautifulSoup
import geopy.distance as dist
import glob
import numpy as np
import gpxpy


def consecutive_arrays(arr):
	consec_arr = []
	consec = []
	for i, arr_val in enumerate(arr):
		if len(consec) == 0 or arr_val == consec[-1] + 1:
			consec.append(arr_val)
		else:
			consec_arr.append(consec)
			consec = [arr_val]
		if i == len(arr)-1:
			consec_arr.append(consec)
	
	return consec_arr


def point_to_point_dist(pt1, pt2):
	return dist.distance(pt1[::-1][1:], pt2[::-1][1:]).m


def point_to_route_min_dist(pt, route, return_dist=False):
	# find index of closest approach
	lat_m_per_deg = dist.distance([pt[1], pt[0]], [pt[1] + 1., pt[0]]).m
	lon_m_per_deg = dist.distance([pt[1], pt[0]], [pt[1], pt[0] + 1.]).m
	
	# slow
	# dis = [dist.distance(pt[::-1][1:], route[i, ::-1][1:]).m for i in np.arange(len(route))]
	
	# faster
	dis = list(
		np.sqrt(((pt[0] - route[:, 0]) * lon_m_per_deg) ** 2 + ((pt[1] - route[:, 1]) * lat_m_per_deg) ** 2))  # [m]
	
	if return_dist:
		return dis
	else:
		i_close_approach = dis.index(min(dis))
		min_dist = min(dis)
		return min_dist, i_close_approach


def index_path_dist_to_ends(index, route, return_both=False):
	# get the distance along the path between a route index and the route ends
	pt = route[index, :]
	lat_m_per_deg = dist.distance([pt[1], pt[0]], [pt[1] + 1., pt[0]]).m
	lon_m_per_deg = dist.distance([pt[1], pt[0]], [pt[1], pt[0] + 1.]).m
	lon = route[:, 0]
	lat = route[:, 1]
	dis = np.sqrt(((lon - np.roll(lon, -1)) * lon_m_per_deg) ** 2 + ((lat - np.roll(lat, -1)) * lat_m_per_deg) ** 2)  # [m]
	dis[0] = 0
	if return_both:
		return np.sum(dis[:index]), np.sum(dis[index:])
	else:
		return min([np.sum(dis[:index]), np.sum(dis[index:])])
	

def chop_off_ends(coords, thresh=75.):
	i1, i2 = 0, len(coords[:, 0])-1
	try:
		while point_to_point_dist(coords[i1, :], coords[0, :]) < thresh:
			i1 += 1
		while point_to_point_dist(coords[i2, :], coords[-1, :]) < thresh:
			i2 -= 1
		return coords[i1:i2+1, :]  # +1 to include i2 in returned array
	except IndexError:
		return []
	

def extract_coords_kml(runfile):
	with open(runfile, 'r') as f:
		s = BeautifulSoup(f, 'xml')
		run_coords = []
		for coords in s.find_all('coordinates'):
			if len(run_coords) == 0:
				run_coords = np.array(process_coordinate_string(coords.string))
			else:
				run_coords = np.append(run_coords, process_coordinate_string(coords.string))
	return run_coords


def extract_coords_gpx(runfile):
	with open(runfile, 'r') as f:
		gpx = gpxpy.parse(f)
		run_coords = []
		for track in gpx.tracks:
			for segment in track.segments:
				for point in segment.points:
					run_coords.append([point.longitude, point.latitude, point.elevation])
	return np.array(run_coords)


def process_coordinate_string(str):
	"""
	Take the coordinate string from the KML file, and break it up into [[Lon,Lat,Alt],[Lon,Lat,Alt],...]
	"""
	long_lat_alt_arr = []
	for point in str.split('\n'):
		if len(point) > 0:
			long_lat_alt_arr.append(
				[float(point.split(',')[0]), float(point.split(',')[1]), float(point.split(',')[2])])
	return long_lat_alt_arr


def get_dummy_coordinates(top=True):
	m_per_deg = dist.distance([0, 0], [0, 1]).m
	lon = np.linspace(-2500 / m_per_deg, 2500 / m_per_deg, num=500)  # 5k
	alt = np.zeros_like(lon)
	lat = np.array([np.sqrt(1000 ** 2 - dist.distance([0, 0], [0, lon[i]]).m ** 2) / m_per_deg if dist.distance(
		[0, 0], [0, lon[i]]).m <= 1000. else 0. for i in np.arange(len(lon))])
	if not top:
		lat *= -1.
	run_coords = np.zeros((500, 3))
	run_coords[:, 0] = lon
	run_coords[:, 1] = lat
	run_coords[:, 2] = alt
	return run_coords


if __name__ == '__main__':
	park_dir = 'ElmCreekRuns/'
	for file in glob.glob(park_dir + '*.tcx'):
		if file.split('.')[-1] == 'kml':
			rc = extract_coords_kml(file)
		elif file.split('.')[-1] == 'gpx':
			rc = extract_coords_gpx(file)
		# elif file.split('.')[-1] == 'tcx':
		# 	rc = extract_coords_tcx(file)
		print('{} : {}'.format(file, len(rc)))

if __name__ == '__main__':
	itest = [1, 2, 3, 4, 6, 7, 10, 11, 12, 13, 25, 26, 28]
	consec = consecutive_arrays(itest)
	aa=1
