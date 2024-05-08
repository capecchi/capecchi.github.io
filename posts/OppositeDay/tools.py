import json

import gpxpy
import numpy as np
import pandas as pd


def coords2geojson(coords, fn):
	ftype = '.geojson'
	fn = fn + ftype
	f = open(fn, 'w')
	f.write('{"type":"Feature",\n"properties":{},\n')
	f.write('"geometry":{\n')
	f.write('"type":"LineString",\n')
	f.write('"coordinates":[\n')
	tally = 0
	for pair in coords:
		if tally == 0:
			f.write('[' + str(pair[0]) + ',' + str(pair[1]) + ']')
			tally = 1
		else:
			f.write(',\n[' + str(pair[0]) + ',' + str(pair[1]) + ']')
	f.write(']\n}\n}')
	f.close()
	print('saved', fn[-16:], len(coords))


def manipulate_gpx(gpx_fn, fsav, fliplat=True, rotlon=True):
	gpx_file = open(gpx_fn, 'r')
	gpx = gpxpy.parse(gpx_file)
	lat, lon = [], []
	for t in gpx.tracks:
		for s in t.segments:
			lon = [p.longitude for p in s.points]
			lat = [p.latitude for p in s.points]
	if fliplat:
		lat = [-la for la in lat]
	if rotlon:
		lon = [lo + 180. if lo + 180. <= 180 else lo - 180. for lo in lon]
	
	geo = df_to_geojson(pd.DataFrame(data={'latitude': lat, 'longitude': lon}), connected=True)
	save_geojson(geo, fsav)


def manipulate_worldmap(fload, fsav, fliplat=True, rotlon=True):
	f = open(fsav, 'w')
	f.write('{"type":"FeatureCollection",\n"features": [\n')
	fnum = 1
	
	with open(fload) as file:
		data = json.load(file)
	
	for feats in data['features']:
		
		if feats['geometry']['type'] == "Polygon":
			coords = feats['geometry']['coordinates']
			coords = np.array(coords[0])
			if rotlon:
				coords[:, 0] += 180.
			coords2 = np.array(coords)
			coords = np.where(coords > 180., coords - 360., coords)
			if fliplat:
				coords[:, 1] = coords[:, 1] * (-1)
			if fnum == 1:
				f.write('{')
			else:
				f.write(',\n{')
			fnum = 2
			f.write('"type":"Feature",\n"properties":{},\n')
			f.write('"geometry":{\n')
			f.write('"type":"LineString",\n"coordinates":[')
			tally = 0
			for i in np.arange(len(coords)):
				pair = coords[i]
				if i > 0:  # check for 180deg crossing
					if (coords2[i - 1][0] < 180. and coords2[i][0] > 180.) \
							or (coords2[i - 1][0] > 180. and coords2[i][0] < 180.):
						frac = (180. - coords2[i - 1][0]) / (coords2[i][0] - coords2[i - 1][0])
						interp_lat = frac * (coords[i][1] - coords[i - 1][1]) + coords[i - 1][1]
						if tally != 0:  # write a value at +/-180deg
							f.write(',\n')
						f.write('[' + str(np.sign(coords[i - 1][0]) * 180.) + ',' + str(interp_lat) + ']')
						f.write(']\n}\n}')  # close out feature and start new one
						f.write(',\n{"type":"Feature",\n"properties":{},\n')
						f.write('"geometry":{\n')
						f.write('"type":"LineString",\n"coordinates":[')
						f.write('[' + str(np.sign(coords[i][0]) * 180.) + ',' + str(interp_lat) + ']')
						tally = 1
				
				if tally == 0:
					f.write('[' + str(pair[0]) + ',' + str(pair[1]) + ']')
					tally = 1
				else:
					f.write(',\n[' + str(pair[0]) + ',' + str(pair[1]) + ']')
			# end of coords, geometry, feature
			f.write(']\n}\n}')
		
		if feats['geometry']['type'] == "MultiPolygon":
			multicoords = feats['geometry']['coordinates']
			for coords in multicoords:
				coords = np.array(coords[0])
				if rotlon:
					coords[:, 0] += 180.
				coords2 = np.array(coords)
				coords = np.where(coords > 180., coords - 360., coords)
				if fliplat:
					coords[:, 1] = coords[:, 1] * (-1)
				if fnum == 1:
					f.write('{')
				else:
					f.write(',\n{')
				fnum = 2
				f.write('"type":"Feature",\n"properties":{},\n')
				f.write('"geometry":{\n')
				f.write('"type":"LineString",\n"coordinates":[')
				tally = 0
				for i in np.arange(len(coords)):
					pair = coords[i]
					if i > 0:  # check for 180deg crossing
						if (coords2[i - 1][0] < 180. and coords2[i][0] > 180.) \
								or (coords2[i - 1][0] > 180. and coords2[i][0] < 180.):
							frac = (180. - coords2[i - 1][0]) / (coords2[i][0] - coords2[i - 1][0])
							interp_lat = frac * (coords[i][1] - coords[i - 1][1]) + coords[i - 1][1]
							if tally != 0:  # write a value at +/-180deg
								f.write(',\n')
							f.write('[' + str(np.sign(coords[i - 1][0]) * 180.) + ',' + str(interp_lat) + ']')
							f.write(']\n}\n}')  # close out feature and start new one
							f.write(',\n{"type":"Feature",\n"properties":{},\n')
							f.write('"geometry":{\n')
							f.write('"type":"LineString",\n"coordinates":[')
							f.write('[' + str(np.sign(coords[i][0]) * 180.) + ',' + str(interp_lat) + ']')
							tally = 1
					
					if tally == 0:
						f.write('[' + str(pair[0]) + ',' + str(pair[1]) + ']')
						tally = 1
					else:
						f.write(',\n[' + str(pair[0]) + ',' + str(pair[1]) + ']')
				
				# end of coords, geometry, feature
				f.write(']\n}\n}')
	
	f.write('\n]\n}')  # end of features, FeatureCollection
	f.close()
	print('saved', fsav)


def df_to_geojson(df, connected=False, properties=[], lat='latitude', lon='longitude'):
	geojson = {'type': 'FeatureCollection', 'features': []}
	if connected:
		feature = {'type': 'Feature',
		           'properties': {},
		           'geometry': {'type': 'LineString',
		                        'coordinates': []}}
		coords = []
		for _, row in df.iterrows():
			coords.append([row[lon], row[lat]])
		feature['geometry']['coordinates'] = coords
		geojson['features'].append(feature)
	else:
		for _, row in df.iterrows():
			feature = {'type': 'Feature',
			           'properties': {},
			           'geometry': {'type': 'Point',
			                        'coordinates': []}}
			feature['geometry']['coordinates'] = [row[lon], row[lat]]
			for prop in properties:
				feature['properties'][prop] = row[prop]
			geojson['features'].append(feature)
	return geojson


def save_geojson(geojson, out_fn):
	geo_str = json.dumps(geojson, indent=2)
	with open(out_fn, 'w') as output_file:
		output_file.write('{}'.format(geo_str))


# if __name__ == '__main__':
#     df = pd.DataFrame(data={'latitude': [1, 2, 3], 'longitude': [4, 5, 6], 'city': ['cheeseburger', 'and', 'fries']})
#     cols = ['city']
#     geojson = df_to_geojson(df, cols)
#     save_geojson(geojson, 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/test.geojson')

if __name__ == '__main__':
	
	generate_worldmaps = False
	generate_madridmarathons = True
	generate_tcmarathons = False
	
	if generate_worldmaps:  # create flipped/rotated versions of world map
		webdir = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/'
		world_fn = webdir + 'worldmap.json'
		anti_f = webdir + 'worldmap_anti.geojson'
		rot_f = webdir + 'worldmap_rot.geojson'
		manipulate_worldmap(world_fn, anti_f, rotlon=True, fliplat=True)
		manipulate_worldmap(world_fn, rot_f, rotlon=True, fliplat=False)
	
	if generate_tcmarathons:  # manipulate gpx files
		fp = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/TCmarathon'
		file = fp + '.gpx'
		manipulate_gpx(file, fp + '_north_opposite.geojson', fliplat=False, rotlon=True)
		manipulate_gpx(file, fp + '_opposite.geojson', fliplat=True, rotlon=True)
	
	if generate_madridmarathons:  # manipulate gpx files
		fp = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/madridmarathon'
		file = fp + '.gpx'
		manipulate_gpx(file, fp + '_north_opposite.geojson', fliplat=False, rotlon=True)
		manipulate_gpx(file, fp + '_opposite.geojson', fliplat=True, rotlon=True)
