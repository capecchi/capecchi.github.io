def main():
    import os
    import pandas as pd
    import numpy as np

    mdirec = 'C:/Python34/Air_Quality/monthly_csvs/'
    webdirec = "C:/Users/Owner/Documents/GitHub/capecchi.github.io/projects/AirQuality/"
    col_names = ['location','city','country','num_records','parameter','value','latitude','longitude']
    sub =['parameter','latitude','longitude']

    month_csvs = os.listdir(mdirec)
    #month_csvs = month_csvs[:2] #for testing
    all_data = pd.concat(pd.read_csv(mdirec+f,usecols=col_names) for f in month_csvs)

    #drop duplicates
    data = all_data.drop_duplicates(subset=sub)
    unique_rows = np.arange(len(data))

    #update each unique entry with average of all_data measurements
    for r in unique_rows:
        print(r+1,'/',len(unique_rows))
        multiple_rec = all_data[ all_data[sub[0]] == data[sub[0]].iloc[r] ]
        multiple_rec = multiple_rec[ multiple_rec[sub[1]] == data[sub[1]].iloc[r] ]
        multiple_rec = multiple_rec[ multiple_rec[sub[2]] == data[sub[2]].iloc[r] ]
        total_rec = np.sum(multiple_rec['num_records'])
        av_val = np.average(multiple_rec['value'],weights=multiple_rec['num_records'])
        
        #weighted_arr = []
        #for each in np.arange(multiple_rec['value']):
        #    vv = multiple_rec['value'].iloc[each]*multiple_rec['num_records'].iloc[each]/total_rec
        #    weighted_arr.append(vv)
        #    print(weighted_arr)
        #av_val = np.sum(weighted_arr)

        data['value'].set_value(r,av_val,takeable=True)
        data['num_records'].set_value(r,total_rec,takeable=True)

    aggregate_master = data
    fsav = webdirec+'aggregate_master.csv'
    aggregate_master.to_csv(fsav,index=False)
    print('Saved:: aggregate_master.csv')
