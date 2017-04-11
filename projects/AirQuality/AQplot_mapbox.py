def main():
    #Display air quality data using CSV file from OpenAQ

    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib as mpl
    import plotly
    plotly.tools.set_credentials_file(username='william.capecchi',\
                                      api_key='PNxwH2xRk6vz7cQqlMX2')
    import plotly.plotly as py
    import mapbox

    direc = "C:/Python34/Air_Quality/"
    #csv = direc+"csv/2017-03-07.csv"
    csv = direc + "data_merged.csv"
    
    params = ["pm10","pm25","so2","co","no2","o3"]
    a = pd.read_csv(csv)
    a = a.dropna()
    minim = 100
    maxim = 10000
    a = a[a['value']>minim]
    a = a[a['value']<maxim] #optional threshold air concentration

   
    #scatter plot
    mapbox_access_token = 'pk.eyJ1IjoiY2FwZWNjaGkiLCJhIjoiY2owNzV0YzdzMHFiYzJxbHNnbTJuZ2h3diJ9.ArYGu-QKz3D8D0oZLyvgSA'
    data = []
    size = 50.
    for p in params:
        d = a[a['parameter']==p]
        if 0:
            val = d['value']*size/max(a['value'])
        else: #normalize to contaminant max value
            val = d['value']*size/max(d['value'])
        trace = dict(
            lat = d['latitude'],
            lon = d['longitude'],
            text = d['value'].astype(str)+'ug/m^3',
            name = p,
            marker = dict(size = val),
            type = 'scattermapbox'
        )
        data.append(trace)

    lon0 = 30 #np.mean(data['longitude'])
    lat0 = 35 #np.mean(data['latitude'])

    layout = dict(
        height = 800,
        margin = dict( t=0, b=0, l=0, r=0 ),
        font = dict( color='#FFFFFF', size=12 ),
        paper_bgcolor = '#000000',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat0,
                lon=lon0
            ),
            pitch=0,
            zoom=3,
            style='dark'
        ),
    )

    fig = dict(data=data, layout=layout)
    #plotly.offline.plot(fig)
    py.plot(fig,filename='AirQualityMap')

main()
