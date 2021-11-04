#separates month_master.csv into parameter files
#to more easily be handeld as geojson files

def main():
    import pandas as pd
    import os
    import numpy as np

    def csv_list(direc):
        csvs = []
        for file in os.listdir(direc):
            if file.endswith(".csv") and 'test' not in file:
                csvs.append(file)
        return csvs

    direc = "C:/Python34/Air_Quality/csv/"
    csvs = csv_list(direc)

    units = []
    i = 1
    for f in csvs:
#        print(i,len(csvs))
        i += 1
        df = pd.read_csv(direc+f)
        for r in np.arange(len(df)):
            if df['unit'].iloc[r] not in units:
                units.append(df['unit'].iloc[r])
                print(df['unit'].iloc[r])
    np.save(direc+'units',units)    
    print(units)        
