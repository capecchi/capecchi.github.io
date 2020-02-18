"""
Create a class object for a park.
- runs that have been analyzed are tracked so it doesn't re-analyze all runs when a new one is added to directory
- breaks runs down into segments based on identified junctions. Identified junctions are tracked. Segments are tracked
- Every time a new junction is identified every segment present is re-analyzed and segmented further if necessary
"""
from typing import List
from bs4 import BeautifulSoup
import glob
import matplotlib.pyplot as plt
import numpy as np
import geopy.distance as dist
import uuid


class SomethingHappened(Exception):
	def __init__(self, message):
		self.message = message


class Junction:
	def __init__(self, coord, is_trailhead=False):
		self.coord = coord
		self.weight = 1  # should end up with multiple intersections identified to average out to get junction location
		self.id = uuid.uuid1().__str__()
		self.trailhead = is_trailhead
	
	def plot(self, color='r'):
		plt.plot(self.coord[0], self.coord[1], '{}s'.format(color))


class Segment:
	def __init__(self, coords, junction1: Junction, junction2: Junction, weight=1):
		self.coords = coords  # lon, lat, alt
		self.weight = weight  # multiple runs of a segment will average together
		self.end1 = junction1
		self.end2 = junction2
		self.id = uuid.uuid1().__str__()
		self.length = None
		self.check()
		self.update_length()
	
	def check(self):
		if dist.vincenty(self.end1.coord[::-1][1:], self.coords[0, ::-1][1:]).m > 10:
			print('OOPS! UNEXPECTED LARGE DISTANCE, something is broken but carrying on...')
		# raise SomethingHappened('Oops, unexpected large distance. Plot segment and endpoints and figure it out...')
		if dist.vincenty(self.end2.coord[::-1][1:], self.coords[-1, ::-1][1:]).m > 10:
			print('OOPS! UNEXPECTED LARGE DISTANCE, something is broken but carrying on...')
		# raise SomethingHappened('Oops, unexpected large distance. Plot segment and endpoints and figure it out...')
		print('Segment seems to be in good condition')
	
	def update_length(self):
		length = 0
		length += dist.vincenty(self.end1.coord[::-1][1:], self.coords[0, ::-1][1:]).m
		for i in range(len(self.coords) - 1):
			length += dist.vincenty(self.coords[i, ::-1][1:], self.coords[i + 1, ::-1][1:]).m
		length += dist.vincenty(self.end2.coord[::-1][1:], self.coords[-1, ::-1][1:]).m
		self.length = length
		print('segment length updated to {:.2f}m'.format(self.length))
	
	def plot(self):
		plt.plot(self.coords[:, 0], self.coords[:, 1], '-')


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


def plot_runs(runs: dict, ax):
	for run in runs.keys():
		ax.plot(runs[run][:, 0], runs[run][:, 1], 'o-', markevery=100)


def point_to_point_dist(pt1, pt2):
	return dist.vincenty(pt1[::-1][1:], pt2[::-1][1:]).m


def identify_junction_indices(junction_candidate_indices, seg_from, seg_onto):
	"""
	:param junction_candidate_indices: passed in tuple array of indices where they are >50m from seg_onto, but adjacent to index <50m
	:param seg_from: segment in which we are looking for junction indices
	:param seg_onto: segment we are using to compare closest approach distance from seg_from candidate junction indices
	:return: new_j, array of new junction indices
	"""
	print('identifying junction indices')
	new_j = []
	for (i_abv, i_bel) in junction_candidate_indices:
		initial_approach_dist, _ = point_to_route_min_dist(seg_from.coords[i_abv], seg_onto.coords)
		if i_abv > i_bel:
			incr = -1
		else:
			incr = 1
		while True:
			# todo: investigate possible speedup, we don't need to analyze entire seg2 here if we extract the part of seg2 that's close to our seg1 index
			approach_dist, _ = point_to_route_min_dist(seg_from.coords[i_abv], seg_onto.coords)
			# print('approach at: {}m, index {}'.format(approach_dist, i_abv))
			if point_to_point_dist(seg_from.coords[i_abv], seg_from.end1.coord) < 50 or \
					point_to_point_dist(seg_from.coords[i_abv], seg_from.end2.coord) < 50:  # near start/end, exit while
				break
			if approach_dist > 5 * initial_approach_dist:
				# todo: interesting to investigate- did we really come close but not close enough?
				break
			if approach_dist < 20:  # todo: validate choice of 20m here
				new_j.append(i_abv)
				break
			# todo: possible speedup- instead of stepping by one, use approach_dist. ie if we know we're 50m away and trying to get within 10, why not move the number of indices that gets us 40m down the segment?
			i_abv += incr  # step towards start of segment
	return new_j


class Park:
	def __init__(self, name, directory):
		self.park_name = name
		self.park_run_directory = directory
		self.files_analyzed = []
		self.segments = []
		self.junctions = []
		self.scan_park_directory(level=0)
	
	def plot(self):
		fig = plt.figure(self.park_name)
		plt.clf()
		seg: Segment
		for seg in self.segments:
			plt.plot(seg.coords[:, 0], seg.coords[:, 1])
			imid = int(len(seg.coords[:, 0]) / 2)
			plt.annotate(seg.weight, (seg.coords[imid, 0], seg.coords[imid, 1]))
		junc: Junction
		for junc in self.junctions:
			plt.plot(junc.coord[0], junc.coord[1], 'rs')
			plt.annotate(junc.weight, junc.coord[:-1])
	
	def scan_park_directory(self, level=0):
		print('scanning park directory  L-{}'.format(level))
		for file in glob.glob(self.park_run_directory + '*.kml'):
			if file not in self.files_analyzed:
				self.process_new_run(file, level=level + 1)
	
	def process_new_run(self, runfile, level=0):
		print('processing new run  L-{}'.format(level))
		self.files_analyzed.append(runfile)
		if 0:
			with open(runfile, 'r') as f:
				s = BeautifulSoup(f, 'xml')
				run_coords = []
				for coords in s.find_all('coordinates'):
					if len(run_coords) == 0:
						run_coords = np.array(process_coordinate_string(coords.string))
					else:
						run_coords = np.append(run_coords, process_coordinate_string(coords.string))
		else:  # make simplified fake coords for testing
			m_per_deg = dist.vincenty([0, 0], [0, 1]).m
			lon = np.linspace(-2500 / m_per_deg, 2500 / m_per_deg, num=500)  # 5k
			alt = np.zeros_like(lon)
			lat = np.array([np.sqrt(1000 ** 2 - dist.vincenty([0, 0], [0, lon[i]]).m ** 2) / m_per_deg if dist.vincenty([0, 0], [0, lon[i]]).m <= 1000. else 0. for i in np.arange(len(lon))])
			if runfile == 'ElmCreekRuns\\Move_2018_08_28_13_27_03_Running.kml':
				lat *= -1.
			run_coords = np.zeros((500, 3))
			run_coords[:, 0] = lon
			run_coords[:, 1] = lat
			run_coords[:, 2] = alt
		j1 = Junction(run_coords[0], True)  # start and end are trailheads
		j2 = Junction(run_coords[-1], True)
		# self.add_junction(j1, level=level + 1)
		# self.add_junction(j2, level=level + 1)
		seg = Segment(run_coords, j1, j2)
		self.analyze_segment(seg, level=level + 1)
	
	def compare_junctions(self, j1, j2):
		jdist = dist.vincenty(j1.coord[::-1][1:], j2.coord[::-1][1:]).m
		if jdist < 50 and j1.id != j2.id:  # todo: validate choice, see add_junction for other use
			junction_ids = [j.id for j in self.junctions]
			try:
				self.junctions.pop(junction_ids.index(j2.id))  # remove j2 from Park junction list
			except ValueError:
				print('tried to pop a missing junction')
				pass
			j1.coord = (j1.weight * j1.coord + j2.coord) / (j1.weight + 1)
			j1.weight += 1
			if j1.weight > 2:
				a=1
			self.changeout_junction(j_from=j2, j_to=j1)
	
	def changeout_junction(self, j_from=None, j_to=None):
		seg: Segment
		for seg in self.segments:  # go through and replace j_from with j_to
			if seg.end1.id == j_from.id:
				seg.end1 = j_to
			if seg.end2.id == j_from.id:
				seg.end2 = j_to
	
	def add_junction(self, junction: Junction, level=0):
		print('adding junction  L-{}'.format(level))
		# compare junction to existing junctions
		# two junctions deemed the same if they're within XXm of each other
		j: Junction
		is_new = True
		for j in self.junctions:
			jdist = dist.vincenty(junction.coord[::-1][1:], j.coord[::-1][1:]).m
			if jdist < 50:  # todo: validate choice of 50m radius here
				is_new = False
				if junction.id != j.id:
					j.coord = (j.weight * j.coord + junction.coord) / (j.weight + 1)  # avg points together
					j.weight += 1  # increase weight factor
					if j.weight > 2:
						a=1
					self.changeout_junction(j_from=junction, j_to=j)
		if is_new:
			if not junction.trailhead:
				print('---> NEW JUNCTION ({})'.format(len(self.junctions)))
				self.plot()
				junction.plot(color='g')
			self.junctions.append(junction)
			self.analyze_new_junction(junction, level=level + 1)
	
	def analyze_new_junction(self, junction: Junction, level=0):
		print('analyzing new junction  L-{}'.format(level))
		# when we add new junction, re-analyze all segments against that new junction
		s: Segment
		old_segs = list(self.segments)
		new_segs = []
		for s in old_segs:
			segmentation = self.chop_segment([s], junction, level=level + 1)
			if len(segmentation) > 1:  # we split this segment, remove old from list and add new ones
				seg_ids = [seg.id for seg in self.segments]
				# try:
				# 	seg_index = seg_ids.index(s.id)
				# 	self.segments.pop(seg_index)
				# except ValueError:
				# 	pass
				new_segs.extend(segmentation)
			a=1
		if len(new_segs) > 0:
			for new_seg in new_segs:
				self.analyze_segment(new_seg, level=level + 1)
	
	def add_segment(self, seg: Segment):
		print('adding segment')
		self.segments.append(seg)
		junc_ids = [j.id for j in self.junctions]
		if seg.end1.id not in junc_ids:
			self.add_junction(seg.end1)
		if seg.end2.id not in junc_ids:
			self.add_junction(seg.end2)
	
	def analyze_segment(self, segment: Segment, level=0):
		print('analyzing segment  L-{}'.format(level))
		# scan for existing junctions in segment
		# if junction(s) found amid run, chop up and analyze each sub-segment, otherwise add
		segmentation = [segment]
		j: Junction
		for j in self.junctions:
			segmentation = self.chop_segment(segmentation, j, level=level + 1)
		# if adding a new segment, compare to existing segments to find new junctions
		for seg in segmentation:
			self.add_segment(seg)  # add segment and junctions to Park class
			print('---> {} segments present'.format(len(self.segments)))
			s: Segment
			for s in self.segments:
				if s.id != seg.id:  # don't need to compare it to itself
					self.compare_segments(seg, s, level=level + 1)
	
	def compare_segments(self, seg1: Segment, seg2: Segment, level=0):
		print('comparing segments  L-{}'.format(level))
		# this is the heart of things
		# we've already segmented on known junctions, so should either be same, totally  different, or find new junction
		# need to find junctions between these two segments, then add each found if new, chop if needed
		
		Npts = 50
		speedup1 = int(np.ceil(len(seg1.coords) / Npts))  # want N points to analyze a run  # todo: justify this speedup
		speedup2 = int(np.ceil(len(seg2.coords) / Npts))
		
		# seg1 onto seg2
		seg1on2_close_approach = []
		for ii, pt in enumerate(seg1.coords[::speedup1]):  # start with every nth pt just for speed
			# print('{}% done'.format(ii * 100. / len(seg1.coords[::speedup1])))
			min_dist, _ = point_to_route_min_dist(pt, seg2.coords)
			seg1on2_close_approach.append(min_dist)
		# plt.plot(seg1on2_close_approach)  # let's see what this looks like
		
		# seg2 onto seg1
		seg2on1_close_approach = []
		for ii, pt in enumerate(seg2.coords[::speedup2]):  # start with every 50th pt just for speed
			# print('{}% done'.format(ii * 100. / len(seg2.coords[::speedup2])))
			min_dist, _ = point_to_route_min_dist(pt, seg1.coords)
			seg2on1_close_approach.append(min_dist)
		# plt.plot(seg2on1_close_approach)  # let's see what this looks like
		
		i1on2gt50 = [ca > 50 for ca in seg1on2_close_approach]
		i2on1gt50 = [ca > 50 for ca in seg2on1_close_approach]
		
		if not any(i1on2gt50) and not any(i2on1gt50):  # seg1/2 never >50m from each other, consider same  and average
			# todo: validate choice of 50m here
			# we just added seg1, so verify weight=1 then we'll pop that out and average seg1 with seg2
			if seg1.weight != 1:
				raise SomethingHappened('Expected weight=1 but got weight={}'.format(seg1.weight))
			else:
				seg_ids = [seg.id for seg in self.segments]
				try:
					self.segments.pop(seg_ids.index(seg1.id))  # remove seg1 from Park Class
				except ValueError:
					pass
				self.average_segments(seg1, seg2, level=level + 1)
		elif all(i1on2gt50):  # seg1 never within 50m of seg2, consider disjoint, no action needed (?)
			pass
		elif (not any(i1on2gt50) and any(i2on1gt50)) or (not any(i2on1gt50) and any(i1on2gt50)):
			# one segment is just a subsegment of the other, do nothing for now, larger segment will be chopped later
			pass
		else:  # new junctions to be found! seg1/2 both within and further apart than 50m, so find out where
			# *50 below is to return the true indices of the seg1/2 coord arrays since we're using ::50 above
			# indices where dist > 50m but previous is not
			i1_junc_candidates = [(i * speedup1, (i - 1) * speedup1) for i in np.arange(len(i1on2gt50))[1:] if
			                      i1on2gt50[i] is True and i1on2gt50[i - 1] is False]
			i1_junc_candidates.extend(
				[(i * speedup1, (i + 1) * speedup1) for i in np.arange(len(i1on2gt50))[:-1] if
				 i1on2gt50[i] is True and i1on2gt50[i + 1] is False]
			)
			i2_junc_candidates = [(i * speedup2, (i - 1) * speedup2) for i in np.arange(len(i2on1gt50))[1:] if
			                      i2on1gt50[i] is True and i2on1gt50[i - 1] is False]
			i2_junc_candidates.extend(
				[(i * speedup2, (i + 1) * speedup2) for i in np.arange(len(i2on1gt50))[:-1] if
				 i2on1gt50[i] is True and i2on1gt50[i + 1] is False]
			)
			new_j1 = identify_junction_indices(i1_junc_candidates, seg1, seg2)
			new_j2 = identify_junction_indices(i2_junc_candidates, seg2, seg1)
			for j in new_j1:
				self.add_junction(Junction(seg1.coords[j]), level=level + 1)
			for j in new_j2:
				self.add_junction(Junction(seg2.coords[j]), level=level + 1)
	
	def average_segments(self, seg1: Segment, seg2: Segment, level=0):
		print('averaging segments together  L-{}'.format(level))
		# average seg1 onto seg2 (seg2 should be in self.segments, seg1 should not)
		seg_ids = [seg.id for seg in self.segments]
		if seg2.id not in seg_ids:
			raise SomethingHappened('Segment missing')
		if seg1.id in seg_ids:
			raise SomethingHappened('Found unexpected segment')
		self.compare_junctions(seg1.end1, seg2.end1)
		self.compare_junctions(seg1.end1, seg2.end2)
		self.compare_junctions(seg1.end2, seg2.end1)
		self.compare_junctions(seg1.end2, seg2.end2)
		
		d1 = [point_to_point_dist(seg1.coords[i], seg1.coords[i + 1]) for i in range(len(seg1.coords) - 1)]
		d1.insert(0, 0)
		d2 = [point_to_point_dist(seg2.coords[i], seg2.coords[i + 1]) for i in range(len(seg2.coords) - 1)]
		d2.insert(0, 0)
		cs1 = np.cumsum(d1)
		cs2 = np.cumsum(d2)
		avgdist = (cs1[-1] + cs2[-1]) / 2.
		Npts = np.ceil(avgdist / 5)  # have a point every 5m is the goal
		
		r_interp = np.linspace(0, avgdist, num=Npts)
		lon1_interp = np.interp(r_interp, cs1, seg1.coords[:, 0])
		lat1_interp = np.interp(r_interp, cs1, seg1.coords[:, 1])
		alt1_interp = np.interp(r_interp, cs1, seg1.coords[:, 2])
		lon2_interp = np.interp(r_interp, cs2, seg2.coords[:, 0])
		lat2_interp = np.interp(r_interp, cs2, seg2.coords[:, 1])
		alt2_interp = np.interp(r_interp, cs2, seg2.coords[:, 2])
		lon_avg = (lon1_interp + lon2_interp) / 2.  # todo: add weighting here from seg1.weight, seg2.weight
		lat_avg = (lat1_interp + lat2_interp) / 2.
		alt_avg = (alt1_interp + alt2_interp) / 2.
		
		averaged_coords = np.zeros((len(lon_avg), 3))
		averaged_coords[:, 0] = lon_avg
		averaged_coords[:, 1] = lat_avg
		averaged_coords[:, 2] = alt_avg
		if len(averaged_coords) < 1:
			a = 1
		averaged_seg = Segment(averaged_coords, seg2.end1, seg2.end2, weight=seg2.weight+seg1.weight)
		if averaged_seg.weight > 2:
			a=1
		seg2index = seg_ids.index(seg2.id)  # index of seg2 in self.segments array
		self.segments.pop(seg2index)  # remove original segment
		self.segments.append(averaged_seg)  # append new averaged segment
	
	def chop_segment(self, segs: List[Segment], junc: Junction, level=0):
		print('chopping segment at junction {} L-{}'.format(junc.id, level))
		segmentation = []
		for seg in segs:
			# this is the slow bit
			# todo: verify min length of 50 in next line
			if junc.id != seg.end1.id and junc.id != seg.end2.id and seg.length > 50:  # don't need to chop a segment using an end
				min_dist, close_approach_index = point_to_route_min_dist(junc.coord, seg.coords)
				near_point = seg.coords[close_approach_index]
				# todo: validate choice of 10m on next line
				junction_mid_segment = min_dist < 10 < point_to_point_dist(near_point, seg.end1.coord) and \
				                       point_to_point_dist(near_point, seg.end2.coord) > 10
				if junction_mid_segment:
					park_seg_ids = [s.id for s in self.segments]
					try:  # remove segment if present, add chopped segments below
						iid = park_seg_ids.index(seg.id)
						self.segments.pop(iid)
					except ValueError:
						pass
					chopped_coords1 = np.append(seg.coords[:close_approach_index], [junc.coord], axis=0)
					chopped_coords2 = np.append([junc.coord], seg.coords[close_approach_index:], axis=0)
					# j1first, j2last = Junction(chopped_coords1[0]), Junction(chopped_coords2[-1])
					# self.add_junction(j1first, level=level + 1)
					# self.add_junction(j2last, level=level + 1)
					chopped_seg1 = Segment(chopped_coords1, seg.end1, junc, weight=seg.weight)  # pass on weight when
					chopped_seg2 = Segment(chopped_coords2, junc, seg.end2, weight=seg.weight)  # we chop up segment
					chopped_seg1.id, chopped_seg2.id = seg.id+'_chop1', seg.id+'_chop2'  # pass on id of parent
					if chopped_seg1.length < 50 or chopped_seg2.length < 50:
						a = 1
					segmentation.append(chopped_seg1)
					segmentation.append(chopped_seg2)
				else:
					segmentation.append(seg)
			else:
				segmentation.append(seg)
		return segmentation


if __name__ == "__main__":
	park_dir = 'ElmCreekRuns/'
	park = Park('Elm_Creek', park_dir)
	park.plot()
	plt.show()
	a = 1
