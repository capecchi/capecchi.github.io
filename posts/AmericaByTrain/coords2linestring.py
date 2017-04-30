#need module to convert coordinate array to LineString
#fn = full directory path + .geojson
#coords in form [[long,lat],[long,lat]...]

def main(coords,fn):

    f = open(fn,'w')
    f.write('{"type":"LineString",\n')
    f.write('"coordinates":[\n')
    tally = 0
    for pair in coords:
        if tally == 0:
            f.write(str(pair))
            tally = 1
        else:
            f.write(',\n'+str(pair))
    f.write(']\n}')
    f.close()
