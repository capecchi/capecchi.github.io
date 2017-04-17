#separates month_master.csv into parameter files
#to more easily be handeld as geojson files

def main():
    import pandas as pd
    import os
    
    webdirec = "C:/Users/Owner/Documents/GitHub/capecchi.github.io/projects/AirQuality/"
    df = pd.read_csv(webdirec+'month_master.csv',encoding='latin-1')
    params = ['pm10','pm25','no2','so2','co','o3','bc']

    for p in params:
        param_df = df[ df['parameter'] == p ]
        param_df.to_csv(webdirec+p+'_master.csv',index=False)
        
