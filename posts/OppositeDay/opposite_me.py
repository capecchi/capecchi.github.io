def main():
    import gpxpy
    import gpxpy.gpx
    import coords2geojson
    
    fp = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/OppositeDay/TCmarathon'
    file = fp + '.gpx'
        
    gpx_file = open(file,'r')
    gpx = gpxpy.parse(gpx_file)
    for t in gpx.tracks:
        for s in t.segments:
            coords = [[p.longitude,p.latitude] for p in s.points]
            ocoords = [[p.longitude+180.,-p.latitude] for p in s.points]
            ncoords = [[p.longitude+180.,p.latitude] for p in s.points]
            
    coords2geojson.main(coords,fp)
    coords2geojson.main(ocoords,fp+'_opposite')
    coords2geojson.main(ncoords,fp+'_north_opposite')
    
