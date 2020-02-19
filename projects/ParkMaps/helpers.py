from bs4 import BeautifulSoup
import geopy.distance as dist
import glob
import numpy as np
import gpxpy


def point_to_point_dist(pt1, pt2):
	return dist.vincenty(pt1[::-1][1:], pt2[::-1][1:]).m


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


def point_to_route_min_dist(pt, route):
	# find index of closest approach
	dis = [dist.vincenty(pt[::-1][1:], route[i, ::-1][1:]).m for i in np.arange(len(route))]
	i_close_approach = dis.index(min(dis))
	min_dist = min(dis)
	return min_dist, i_close_approach


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
	m_per_deg = dist.vincenty([0, 0], [0, 1]).m
	lon = np.linspace(-2500 / m_per_deg, 2500 / m_per_deg, num=500)  # 5k
	alt = np.zeros_like(lon)
	lat = np.array([np.sqrt(1000 ** 2 - dist.vincenty([0, 0], [0, lon[i]]).m ** 2) / m_per_deg if dist.vincenty(
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
		elif file.split('.')[-1] == 'tcx':
			rc = extract_coords_tcx(file)
		print('{} : {}'.format(file, len(rc)))
