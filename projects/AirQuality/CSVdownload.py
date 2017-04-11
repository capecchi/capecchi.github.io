# >>> import CSVdownload as scrape
# >>> scrape.main(save=True,merge=True)

def main(all_after_date=0,
         all_before_date=100000000,
         save=False,
         merge=False,
         test=False):

    import urllib
    from bs4 import BeautifulSoup
    import requests
    import os
    import pandas as pd

    def find_csvs(url):

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        #print(r.text)

        csv_names = []

        for f in soup.find_all('key'):
            string = str(f)
            name = string[5:len(f)-7] #remove <key> and </key>
            if name[len(name)-3:] == "csv":
                csv_names.append(name)
        
        return csv_names

    #START OF PROGRAM
    url = "https://openaq-data.s3.amazonaws.com/"
    csv_names = find_csvs(url)
    if 0:     ## show what you've found:
        print("Listing CSVs")
        for csv in csv_names:
            print(csv)

    yr = []
    mo = []
    day = []

    for f in csv_names:
        yr.append(f[:4])
        mo.append(f[5:7])
        day.append(f[8:10])

    good_csvs = []
    for i in range(len(csv_names)): #all_after_date, all_before_date keywords
        if int(yr[i]+mo[i]+day[i]) >= all_after_date and \
        int(yr[i]+mo[i]+day[i]) <= all_before_date:
            good_csvs.append(csv_names[i])

    if 0: #check to see which csvs are being kept
        for csv in good_csvs:
            print(csv)

    direc = "C:/Python34/Air_Quality/"
    if save: #download csvs (as needed)
        for f in good_csvs:
            file_url = url+f
            fsav = direc + "csv/"+f
            if not os.path.isfile(fsav):
                print("downloading ",file_url)
                file = urllib.request.urlretrieve(file_url,fsav)
            else:
                print(f," already exists")
        
    if merge:
        col_names = ['location','city','country','utc','local','parameter','value','latitude','longitude']
        if test: good_csvs = ["test1.csv","test2.csv"] #test case

        merged = pd.DataFrame()
        for f in good_csvs:
            print(f)
            df = pd.read_csv(direc + "csv/"+f, chunksize=1000,usecols=col_names)
            for chunk in df:
                chunk.dropna(axis=0, inplace=True) # Dropping all rows with any NaN value
                merged = merged.append(chunk)
            del df, chunk

        if test: print(merged)
        merged.to_csv(direc+"data_merged.csv",index=False)

main()
