def main(test=False,
        reverse=False):
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
    webdirec = "C:/Users/Owner/Documents/GitHub/capecchi.github.io/projects/AirQuality/"
    col_names = ['location','city','country','utc','local','parameter','value','latitude','longitude']
    csvs = csv_list(direc)

    month_csvs = []
    for f in csvs:
        y=f[:4]
        m=f[5:7]
        if y+'-'+m not in month_csvs:
            month_csvs.append(y+'-'+m+'.csv')

    if test: month_csvs = os.listdir(webdirec+'monthly_csvs/')
    if reverse: month_csvs = month_csvs[::-1]
    for ym in month_csvs: #for each month
        fsav = webdirec+'monthly_csvs/'+ym
        if os.path.isfile(fsav):
                print(fsav," already exists")
        else: #compile daily data for this month
            relevant = []
            for file in csvs: #find daily csv files from that month
                if ym in file:
                    relevant.append(file)
            all_month_data = pd.concat(pd.read_csv(direc+r,usecols=col_names) for r in relevant)#create one month dataframe
            all_month_data.dropna(axis=0,inplace=True) #drop any rows with NaN values
            all_month_data = all_month_data[all_month_data.value >= 0] #keep only positive values
            #drop duplicates
            sub =['parameter','latitude','longitude']
            subv =['parameter','latitude','longitude','value']
            month_data = all_month_data.drop_duplicates(subset=sub)
            month_data = month_data.rename(columns={"utc":"year","local":"month"})
            unique_rows = np.arange(len(month_data['location']))

            #update each unique entry with average of monthly measurements from that location
            for r in unique_rows:
                print(r+1,'/',len(unique_rows))
                multiple_records = all_month_data[ all_month_data[sub[0]] == month_data[sub[0]].iloc[r] ]
                multiple_records = multiple_records[ multiple_records[sub[1]] == month_data[sub[1]].iloc[r] ]
                multiple_records = multiple_records[ multiple_records[sub[2]] == month_data[sub[2]].iloc[r] ]
                av_val = np.mean(multiple_records['value'])
                month_data['value'].set_value(r,av_val,takeable=True)
                month_data['year'].set_value(r,ym[:4],takeable=True)
                month_data['month'].set_value(r,ym[5:7],takeable=True)

            month_data.to_csv(fsav,index=False)
            print('Saved:: /monthly/'+ym) #end of if file not present

    month_master = pd.concat(pd.read_csv(webdirec+'monthly_csvs/'+f,\
                                         encoding='latin-1') for f in month_csvs)
    temp = month_master.drop('month',axis=1)
    print(temp[0:1])
    temp = temp.rename(columns={"year":"year-month"})
    print(temp[0:1])
    for r in np.arange(len(temp)): #change month values to year-month values
        ym = month_master['year'].iloc[r]*100+month_master['month'].iloc[r]
        temp['year-month'].set_value(r,ym,takeable=True)
    print(temp[0:1])
    month_master = temp
    month_master.to_csv(webdirec+'month_master.csv',index=False)
    print('Saved:: month_master.csv')
#main()
