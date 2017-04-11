def main(test=False):
    import pandas as pd
    import numpy as np
    import os

    def csv_list(direc):
        csvs = []
        for file in os.listdir(direc):
            if file.endswith(".csv") and 'test' not in file:
                csvs.append(file)        
        return csvs

    direc = "C:/Python34/Air_Quality/csv/"
    col_names = ['location','city','country','utc','local','parameter','value','latitude','longitude']
    csvs = csv_list(direc)

    month_csvs = []
    for f in csvs:
        y=f[:4]
        m=f[5:7]
        if y+'-'+m not in month_csvs:
            month_csvs.append(y+'-'+m)

    if test:
        month_csvs = month_csvs[0:1]

    if reverse:
        month_csvs = month_csvs.reverse()

    for ym in month_csvs: #for each month
        fsav = direc+'monthly/'+ym+'.csv'
        if os.path.isfile(fsav):
                print(fsav," already exhists")
        else:
            relevant = []
            for file in csvs: #find daily csv files from that month
                if ym in file:
                    relevant.append(file)
            all_month_data = pd.concat(pd.read_csv(direc+r,usecols=col_names) for r in relevant)#create one month dataframe  
            #drop duplicates
            sub =['parameter','latitude','longitude']
            subv =['parameter','latitude','longitude','value']
            month_data = all_month_data.drop_duplicates(subset=sub)
            unique_rows = np.arange(len(month_data['location']))
    
            #update each unique entry with average of monthly measurements from that location
            for r in unique_rows:
                print(r,'/',len(unique_rows))
                multiple_records = all_month_data[ all_month_data[sub[0]] == month_data[sub[0]].iloc[r] ]
                multiple_records = multiple_records[ multiple_records[sub[1]] == month_data[sub[1]].iloc[r] ]
                multiple_records = multiple_records[ multiple_records[sub[2]] == month_data[sub[2]].iloc[r] ]
                av_val = np.mean(multiple_records['value'])
                month_data['value'].set_value(r,av_val,takeable=True)
            month_data.to_csv(fsav,index=False)
            print('Saved:: /monthly/'+ym+'.csv') #end of if file not present

        month_data = pd.read_csv(fsav) #add this on to clean it up
        month_data.rename(columns{"utc":"year","local":"month"})  
        print(month_data.shape)





main()
