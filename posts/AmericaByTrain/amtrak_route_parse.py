def main():
    import json

    direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/projects/AmericaByTrain'
    with open('amtrak.geojson') as f:
        data = json.load(f)

    for feature in data['features']:
        print(feature['geometry']['type'])
        
