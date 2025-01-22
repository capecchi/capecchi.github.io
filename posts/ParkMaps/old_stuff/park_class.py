"""
Create a class object for a park.
- runs that have been analyzed are tracked so it doesn't re-analyze all runs when a new one is added to directory
- breaks runs down into segments based on identified junctions. Identified junctions are tracked. Segments are tracked
- Every time a new junction is identified every segment present is re-analyzed and segmented further if necessary
"""
from typing import List
import matplotlib.pyplot as plt
import uuid
from posts.ParkMaps.old_stuff.helpers import *


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
	def __init__(self, coords, junction1: Junction = None, junction2: Junction = None, weight=1):
		if junction1 is None:
			junction1 = Junction(coords[0, :])
		if junction2 is None:
			junction2 = Junction(coords[-1, :])
		self.coords = coords  # lon, lat, alt
		self.weight = weight  # multiple runs of a segment will average together
		self.end1 = junction1
		self.end2 = junction2
		self.id = uuid.uuid1().__str__()
		self.length = None
		# self.check()
		self.update_length()
	
	def check(self):
		if dist.distance(self.end1.coord[::-1][1:], self.coords[0, ::-1][1:]).m > 10:
			print('OOPS! UNEXPECTED LARGE DISTANCE, something is broken but carrying on...')
		# raise SomethingHappened('Oops, unexpected large distance. Plot segment and endpoints and figure it out...')
		if dist.distance(self.end2.coord[::-1][1:], self.coords[-1, ::-1][1:]).m > 10:
			print('OOPS! UNEXPECTED LARGE DISTANCE, something is broken but carrying on...')
	
	# raise SomethingHappened('Oops, unexpected large distance. Plot segment and endpoints and figure it out...')
	# print('Segment seems to be in good condition')
	
	def update_length(self):
		length = 0
		length += dist.distance(self.end1.coord[::-1][1:], self.coords[0, ::-1][1:]).m
		for i in range(len(self.coords) - 1):
			length += dist.distance(self.coords[i, ::-1][1:], self.coords[i + 1, ::-1][1:]).m
		length += dist.distance(self.end2.coord[::-1][1:], self.coords[-1, ::-1][1:]).m
		self.length = length
	
	# print('segment length updated to {:.2f}m'.format(self.length))
	
	def plot(self):
		c = np.append(np.append([self.end1.coord], self.coords, axis=0), [self.end2.coord], axis=0)  # stick on ends
		plt.plot(c[:, 0], c[:, 1], '-')
		plt.plot([self.end1.coord[0], self.end2.coord[0]], [self.end1.coord[1], self.end2.coord[1]], 's')


def plot_runs(runs: dict, ax):
	for run in runs.keys():
		ax.plot(runs[run][:, 0], runs[run][:, 1], 'o-', markevery=100)


def identify_junction_indices(junction_candidate_indices, seg_from, seg_onto):
	"""
	:param junction_candidate_indices: passed in tuple array of indices where they are >50m from seg_onto, but adjacent to index <50m
	:param seg_from: segment in which we are looking for junction indices
	:param seg_onto: segment we are using to compare closest approach distance from seg_from candidate junction indices
	:return: new_j, array of new junction indices
	"""
	# print('identifying junction indices')
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
		self.scan_park_directory()
	
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
	
	def scan_park_directory(self):
		print('scanning park directory')
		for file in glob.glob(self.park_run_directory + '*.*'):
			if file not in self.files_analyzed:
				self.process_new_run(file)
	
	def process_new_run(self, runfile):
		print('processing new run: {}'.format(runfile))
		self.files_analyzed.append(runfile)
		if 1:
			if runfile.split('.')[-1] == 'kml': run_coords = extract_coords_kml(runfile)
			if runfile.split('.')[-1] == 'gpx': run_coords = extract_coords_gpx(runfile)
		else:  # make simplified fake coords for testing
			run_coords = get_dummy_coordinates()
		j1 = Junction(run_coords[0], True)  # start and end are trailheads
		j2 = Junction(run_coords[-1], True)
		seg = Segment(run_coords, j1, j2)
		self.add_segment(seg)
		self.look_for_junctions(seg)
		self.scan_for_consistency()  # check for consistency between existing segments and junctions
	
	def scan_for_consistency(self):
		consistent = False
		while not consistent:
			njuncs = len(self.junctions)
			for j in self.junctions:
				self.chop_segment(self.segments, j)  # chop up segments based on existing junctions
			n_current_segs = len(self.segments)
			i = 0
			while i < n_current_segs - 1:
				j = n_current_segs - 1  # start at last index and work backwards
				while j > i:
					self.compare_segments(self.segments[i], self.segments[j])  # average segs, add new junctions
					n_current_segs = len(self.segments)  # if we averaged we reduced len(self.segments)
					j -= 1
				i += 1
			if len(self.junctions) == njuncs:
				consistent = True  # shouldn't have to check # segs here
	
	def compare_junctions(self, j1, j2):
		jdist = dist.distance(j1.coord[::-1][1:], j2.coord[::-1][1:]).m
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
				a = 1
			self.changeout_junction(j_from=j2, j_to=j1)
			return True
		else:
			return False
	
	def changeout_junction(self, j_from=None, j_to=None):
		seg: Segment
		for seg in self.segments:  # go through and replace j_from with j_to
			if seg.end1.id == j_from.id:
				seg.end1 = j_to
			if seg.end2.id == j_from.id:
				seg.end2 = j_to
	
	def add_junction(self, junction: Junction):
		# print('adding junction')
		# compare junction to existing junctions
		# two junctions deemed the same if they're within XXm of each other
		j: Junction
		is_new = True
		for j in self.junctions:
			jdist = dist.distance(junction.coord[::-1][1:], j.coord[::-1][1:]).m
			if jdist < 50:  # todo: validate choice of 50m radius here
				is_new = False
				if junction.id != j.id:
					j.coord = (j.weight * j.coord + junction.coord) / (j.weight + 1)  # avg points together
					j.weight += 1  # increase weight factor
					if j.weight > 2:
						a = 1
					self.changeout_junction(j_from=junction, j_to=j)
		if is_new:
			if not junction.trailhead:
				print('---> NEW JUNCTION ({})'.format(len(self.junctions)))
			# self.plot()
			# junction.plot(color='g')
			# plt.show()
			self.junctions.append(junction)
	
	def add_segment(self, seg: Segment):
		# print('adding segment')
		self.segments.append(seg)
		junc_ids = [j.id for j in self.junctions]
		if seg.end1.id not in junc_ids:
			self.add_junction(seg.end1)
		if seg.end2.id not in junc_ids:
			self.add_junction(seg.end2)
	
	def analyze_close_approach(self, s1: Segment, s2: Segment):
		# when analyzing close approaches, we chop off area around endpoints so that sequential segments don't look like they overlap
		s1coords = chop_off_ends(s1.coords)
		s2coords = chop_off_ends(s2.coords)
		Npts = 50
		speedup1 = int(np.ceil(len(s2coords) / Npts))  # want N points to analyze a run  # todo: justify this speedup
		speedup2 = int(np.ceil(len(s2coords) / Npts))
		
		if speedup1 == 0:
			a=1
		# seg1 onto seg2
		seg1on2_close_approach = []
		for ii, pt in enumerate(s1coords[::speedup1]):  # start with every nth pt just for speed
			# print('{}% done'.format(ii * 100. / len(seg1.coords[::speedup1])))
			min_dist, _ = point_to_route_min_dist(pt, s2coords)
			seg1on2_close_approach.append(min_dist)
		# plt.plot(seg1on2_close_approach)  # let's see what this looks like
		
		# seg2 onto seg1
		seg2on1_close_approach = []
		for ii, pt in enumerate(s2coords[::speedup2]):  # start with every 50th pt just for speed
			# print('{}% done'.format(ii * 100. / len(seg2.coords[::speedup2])))
			min_dist, _ = point_to_route_min_dist(pt, s1coords)
			seg2on1_close_approach.append(min_dist)
		# plt.plot(seg2on1_close_approach)  # let's see what this looks like
		
		i1on2gt50 = [ca > 50 for ca in seg1on2_close_approach]
		i2on1gt50 = [ca > 50 for ca in seg2on1_close_approach]
		
		return i1on2gt50, i2on1gt50, speedup1, speedup2
	
	def look_for_junctions(self, seg1: Segment, seg2: Segment = None):
		# break up into ~1000m segments to compare
		if seg2 is None:
			seg2 = Segment(seg1.coords, seg1.end1, seg1.end2)
		junctions = []
		ni1 = int(len(seg1.coords[:, 0]) / np.floor(seg1.length / 1000.))  # num indices for sub-segment >= 1km
		ni2 = int(len(seg2.coords[:, 0]) / np.floor(seg2.length / 1000.))
		seg1_shorts, seg2_shorts = [], []
		i1, i2 = 0, 0
		while i1 < len(seg1.coords[:, 0]) - ni1:
			seg1_shorts.append(Segment(seg1.coords[i1:i1 + ni1, :]))
			i1 += int(ni1 / 2.)  # shift by half
		while i2 < len(seg2.coords[:, 0]) - ni2:
			seg2_shorts.append(Segment(seg2.coords[i2:i2 + ni2, :]))
			i2 += int(ni2 / 2.)
		
		junction_found = False
		for short1 in seg1_shorts:
			for short2 in seg2_shorts:
				if point_to_point_dist(short1.end1.coord,
				                       short2.end1.coord) < 2000:  # if endpoints are > 2km apart they'll never intersect and we can skip for SPEED
					i1on2gt50, i2on1gt50, speedup1, speedup2 = self.analyze_close_approach(short1, short2)
					
					if any(i1on2gt50) and not all(i1on2gt50) and any(i2on1gt50):
						# suffices to find only a single junction since we'll then chop up existing segments and re-analyze
						
						for i, pt in enumerate(short1.coords):
							min_dis, _ = point_to_route_min_dist(pt, short2.coords)
							if i == 0:
								together = (min_dis < 50)
							together_now = (min_dis < 50)
							if together_now != together:  # routes just diverged or converged
								together = together_now
								_, i2 = point_to_route_min_dist(short1.coords[i, :],
								                                short2.coords)  # get closest point on short2
								_, i1 = point_to_route_min_dist(short2.coords[i2, :],
								                                short1.coords)  # get closest point on short1 from point on short2 close to original index
								possible_coords = (short1.coords[i1, :] + short2.coords[i2, :]) / 2.
								if point_to_point_dist(possible_coords, short1.end1.coord) > 50 and \
										point_to_point_dist(possible_coords, short1.end2.coord) > 50 and \
										point_to_point_dist(possible_coords, short2.end1.coord) > 50 and \
										point_to_point_dist(possible_coords, short2.end2.coord) > 50:
									junc = Junction(possible_coords)
									self.add_junction(junc)
									junction_found = True
									break  # break out of enumerating short1.coords
				if junction_found:
					break  # break out of seg2_shorts loop
			if junction_found:
				break  # break out of seg1_shorts loop
	
	def compare_segments(self, seg1: Segment, seg2: Segment):
		# print('comparing segments')
		# this is the heart of things
		# we've already segmented on known junctions, so should either be same, totally  different, or find new junction
		# If the same we average them together- remove seg2 and update seg1 as the average of the two
		# If disjoint we do nothing
		# If both close and far away we identify and add new junctions to self.junctions or average existing junctions together
		
		i1on2gt50, i2on1gt50, _, _ = self.analyze_close_approach(seg1, seg2)
		
		if not any(i1on2gt50) and not any(i2on1gt50):  # seg1/2 never >50m from each other, consider same  and average
			# todo: validate choice of 50m here
			try:
				self.segments.pop([seg.id for seg in self.segments].index(seg2.id))  # remove seg2 from Park Class
			except ValueError:
				raise SomethingHappened('segment id missing')
			self.average_segments(seg1, seg2)
		elif all(i1on2gt50):  # seg1 never within 50m of seg2, consider disjoint, no action needed (?)
			a = 1
			pass
		elif (not any(i1on2gt50) and any(i2on1gt50)) or (not any(i2on1gt50) and any(i1on2gt50)):
			# one segment is just a sub-segment of the other, do nothing for now, larger segment will be chopped later
			a = 1
			pass
		else:
			raise SomethingHappened("Here there be dragons")
			a = 1  # THIS SHOULDN"T HAPPEN- we looked for junctions already
	
	def average_segments(self, seg1: Segment, seg2: Segment):
		print('averaging segments together')
		# average seg2 onto seg1
		end1s_same = self.compare_junctions(seg1.end1, seg2.end1)
		_ = self.compare_junctions(seg1.end1, seg2.end2)
		_ = self.compare_junctions(seg1.end2, seg2.end1)
		_ = self.compare_junctions(seg1.end2, seg2.end2)
		
		if not end1s_same:  # reverse seg2 so directions match up
			seg2.coords = seg2.coords[::-1]
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
		averaged_seg = Segment(averaged_coords, seg1.end1, seg1.end2, weight=seg2.weight + seg1.weight)
		if averaged_seg.weight > 2:
			a = 1
		self.segments[[seg.id for seg in self.segments].index(seg1.id)] = averaged_seg
	
	def chop_segment(self, segs: List[Segment], junc: Junction):
		segmentation = []
		for seg in segs:
			# this is the slow bit
			# identify indices to chop, could be multiple in single segment (think running past the start)
			dist = point_to_route_min_dist(junc.coord, seg.coords, return_dist=True)
			# todo: verify min length of 100 in next line
			inear = np.where(np.array(dist) < 100)[0]
			inear_arrays = consecutive_arrays(inear)
			ichop = []
			for iarr in inear_arrays:
				min_dist, iarr_index = point_to_route_min_dist(junc.coord, seg.coords[iarr, :])
				close_approach_index = iarr[iarr_index]
				# todo: verify min length of 100 in next line
				if index_path_dist_to_ends(close_approach_index, seg.coords) > 100.:
					ichop.append(close_approach_index)
				
			if len(ichop) > 0:  # found indices to chop
				for n, ic in enumerate(ichop):
					if n == 0:
						chopped_coords = np.append(seg.coords[:ic], [junc.coord], axis=0)
						chopped_seg = Segment(chopped_coords, seg.end1, junc, weight=seg.weight)  # pass on weight
					else:
						chopped_coords = np.append([junc.coord], seg.coords[ichop[n-1]:ic], axis=0)
						chopped_coords = np.append(chopped_coords, [junc.coord], axis=0)
						chopped_seg = Segment(chopped_coords, junc, junc, weight=seg.weight)
					segmentation.append(chopped_seg)
					if n == len(ichop)-1:
						chopped_coords = np.append([junc.coord], seg.coords[ic:], axis=0)
						chopped_seg = Segment(chopped_coords, junc, seg.end2, weight=seg.weight)
						segmentation.append(chopped_seg)
			else:
				segmentation.append(seg)
		self.segments = segmentation


if __name__ == "__main__":
	park_dir = 'ElmCreekRuns/'
	park = Park('Elm_Creek', park_dir)
	park.plot()
	plt.show()
	a = 1
