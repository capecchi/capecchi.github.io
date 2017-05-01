#need module to convert coordinate array to LineString
#fn = full directory path + .geojson
#coords in form [[long,lat],[long,lat]...]
#will append _1, _2, ... so as to not overwrite existing files

def main(coords,fn,ptB=False):
    import os

    ftype = '.geojson'
    append = ''
    i = 1
    ftest = fn+ftype
    while os.path.isfile(ftest):
        append = '_'+str(i)
        ftest = fn + append + ftype    
        i += 1
    fn = ftest
        
    f = open(fn,'w')
    f.write('{"type":"Feature",\n"properties":{\n')
    if ptB: f.write('"ptB":"True"')
    else: f.write('"ptB":"False"')
    f.write('\n},\n"geometry":{\n')
    f.write('"type":"LineString",\n')
    f.write('"coordinates":[\n')
    tally = 0
    for pair in coords:
        if tally == 0:
            last = pair
            f.write('['+str(pair[0])+','+str(pair[1])+']')
            tally = 1
        else:
            if not (last[0] == pair[0] and last[1] == pair[1]):
                last = pair #new coordinate
                f.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    f.write(']\n}\n}')
    f.close()

    print('saved ',fn)
