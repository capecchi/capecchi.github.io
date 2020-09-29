import json
import pandas as pd


def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type': 'FeatureCollection', 'features': []}
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


if __name__ == '__main__':
    df = pd.DataFrame(data={'latitude': [1, 2, 3], 'longitude': [4, 5, 6], 'city': ['cheeseburger', 'and', 'fries']})
    cols = ['city']
    geojson = df_to_geojson(df, cols)
    save_geojson(geojson, 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/test.geojson')
