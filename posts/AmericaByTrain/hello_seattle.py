#DELETE all routes that don't arrive at destination
def main():
    import glob
    import json
    import os
    
    local = 'F:/Python34/America_By_Train/'
    rb = local+'route_builder/'

    geos = glob.glob(rb+'*.geojson')
    if 0: #deleted routes that don't go to seattle
        for g in geos:
            with open(g) as f:
                data = json.load(f)
            seattle = data['properties']['ptB']
            if seattle == 'False':
                os.remove(g)
                print('removed',g)

    rts = glob.glob(local+'empire_builder_all/*.geojson')
    print(len(rts))
