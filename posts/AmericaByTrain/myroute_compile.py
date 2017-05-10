def main():
    import json
    import glob

    local = 'C:/Python34/America_By_Train/'
    fn = 'my_routes.geojson'
    f = open(local+fn,'w')
    f.write('{"type":"FeatureCollection",\n"features": [\n')
    rts = glob.glob(local+'finished_routes/*.geojson')
    rtnum = 1
    allcoords = []
    for r in rts:
        print(r)
        with open(r) as file:
            data = json.load(file)
        if rtnum == 1:
            f.write('{"type":"Feature",\n"properties":{\n')
        else:
            f.write(',\n{"type":"Feature",\n"properties":{\n')
        f.write('"route":"route'+str(rtnum)+'"')
        rtnum += 1
        f.write('\n},\n"geometry":{\n')
        f.write('"type":"LineString",\n')
        f.write('"coordinates":[\n')
        tally = 0
        coords = data['geometry']['coordinates']
        for pair in coords:
            if tally == 0:
                f.write('['+str(pair[0])+','+str(pair[1])+']')
                tally = 1
            else:
                f.write(',\n['+str(pair[0])+','+str(pair[1])+']')
        #end of coords, geometry, feature
        f.write(']\n}\n}') 
    f.write('\n]\n}')#end of features, FeatureCollection
    f.close()
    print('saved',fn)
