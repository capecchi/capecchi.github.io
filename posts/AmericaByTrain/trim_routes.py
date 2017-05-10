#compare two geojson files and eliminate doubles of GPS coords

def coords2geojson(coords,fn,rtnum):
    ftype = '.geojson'
    fn = fn+ftype
    f = open(fn,'w')
    f.write('{"type":"Feature",\n"properties":{\n')
    f.write('"route":"route'+str(rtnum)+'"')
    f.write('\n},\n"geometry":{\n')
    f.write('"type":"LineString",\n')
    f.write('"coordinates":[\n')
    tally = 0
    for pair in coords:
        if tally == 0:
            f.write('['+str(pair[0])+','+str(pair[1])+']')
            tally = 1
        else:
                f.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    f.write(']\n}\n}')
    f.close()
    print('saved',fn[-16:],len(coords))
    

def main():
    import json
    import glob
    import numpy as np

    local = 'C:/Python34/America_By_Train/empire_builder_all/'
    trimmed = local + 'trimmed/'
    geos = glob.glob(local+'*.geojson')
    index = np.arange(len(geos))
    rtnum = 0

    for i in index:
        fn = geos[i]
        with open(fn) as file:
            data = json.load(file)
        coords = data['geometry']['coordinates']
        if i == 0:
            coords2geojson(coords,trimmed+'trim'+str(i),i)
        else:
            for j in index[0:i]: # numbers 0 to i-1
                fn = geos[j]
                with open(fn) as file:
                    data = json.load(file)
                coords_old = data['geometry']['coordinates']
                coords_new = [elem for elem in coords if elem not in coords_old]
                coords = coords_new
            coords2geojson(coords,trimmed+'trim'+str(i),i)
