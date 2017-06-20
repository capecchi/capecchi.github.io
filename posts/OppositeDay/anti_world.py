def main():
    import json
    import glob
    import coords2geojson
    import numpy as np

    webdir = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/OppositeDay/'
    fn = 'worldmap.json'
    anti_f = webdir+'anti_worldmap.geojson'
    f = open(anti_f,'w')
    f.write('{"type":"FeatureCollection",\n"features": [\n')
    fnum = 1
    
    with open(webdir+fn) as file:
        data = json.load(file)

    for feats in data['features']:

        if feats['geometry']['type'] == "Polygon":
            coords = feats['geometry']['coordinates']
            coords = np.array(coords[0])
            coords[:,0] += 180.
            coords2 = np.array(coords)
            coords = np.where(coords > 180.,coords-360.,coords)
            coords[:,1] = coords[:,1]*(-1)
            if fnum == 1: f.write('{')
            else: f.write(',\n{')
            fnum = 2
            f.write('"type":"Feature",\n"properties":{},\n')
            f.write('"geometry":{\n')
            f.write('"type":"LineString",\n"coordinates":[')
            tally = 0
            for i in np.arange(len(coords)):
                pair = coords[i]
                if i > 0:#check for 180deg crossing
                    if (coords2[i-1][0] < 180. and coords2[i][0] > 180.) \
                       or (coords2[i-1][0] > 180. and coords2[i][0] < 180.):
                        f.write(']\n}\n}')
                        f.write(',\n{"type":"Feature",\n"properties":{},\n')
                        f.write('"geometry":{\n')
                        f.write('"type":"LineString",\n"coordinates":[')
                        tally = 0
                    
                if tally == 0:
                    f.write('['+str(pair[0])+','+str(pair[1])+']')
                    tally = 1
                else:
                    f.write(',\n['+str(pair[0])+','+str(pair[1])+']')
            #end of coords, geometry, feature
            f.write(']\n}\n}')

        if feats['geometry']['type'] == "MultiPolygon":
            multicoords = feats['geometry']['coordinates']
            for coords in multicoords:
                coords = np.array(coords[0])
                coords[:,0] += 180.
                coords2 = np.array(coords)
                coords = np.where(coords > 180.,coords-360.,coords)
                coords[:,1] = coords[:,1]*(-1)
                if fnum == 1: f.write('{')
                else: f.write(',\n{')
                fnum = 2
                f.write('"type":"Feature",\n"properties":{},\n')
                f.write('"geometry":{\n')
                f.write('"type":"LineString",\n"coordinates":[')
                tally = 0
                for i in np.arange(len(coords)):
                    pair = coords[i]
                    if i > 0:#check for 180deg crossing
                        if (coords2[i-1][0] < 180. and coords2[i][0] > 180.) \
                           or (coords2[i-1][0] > 180. and coords2[i][0] < 180.):
                            f.write(']\n}\n}')
                            f.write(',\n{"type":"Feature",\n"properties":{},\n')
                            f.write('"geometry":{\n')
                            f.write('"type":"LineString",\n"coordinates":[')
                            tally = 0
                        
                    if tally == 0:
                        f.write('['+str(pair[0])+','+str(pair[1])+']')
                        tally = 1
                    else:
                        f.write(',\n['+str(pair[0])+','+str(pair[1])+']')

                #end of coords, geometry, feature
                f.write(']\n}\n}')

        
    f.write('\n]\n}')#end of features, FeatureCollection
    f.close()
    print('saved',anti_f)
