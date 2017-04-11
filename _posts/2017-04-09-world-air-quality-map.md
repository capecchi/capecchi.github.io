---
layout: post
title: World Air Quality Map
date: 2017-04-09
excerpt: Mapping air quality data from around the world.
image: /images/posts/AirQuality_thumbnail.png
project: true
tags: scraper pollution Mapbox
---

![image](/images/posts/AirQuality_thumbnail.png)
**make this interactive**

Data does not tell its own story. My graduate thesis project, towards which I worked meticulously for over five years, essentially boils down to around 8 billion numbers in various arrays. The mere record of these numbers would surely not have persuaded my thesis committee to grant me my PhD. The point is, of course, not that I *have* the numbers, but what the numbers mean: These numbers, in this arrangement, arriving in this order means-- something. It's a human task to turn data into information.

A few weeks ago I found a database of air quality measurements from locations around the world. The data, available at [OpenAQ](https://openaq-data.s3.amazonaws.com/index.html), offers almost daily data beginning in June of 2015. I decided to create a map to visualize this data to get a sense of what the mountain of spreadsheets had to show. I had never built a web scraper before, nor done much coding in Python, so I took this as an opportunity to learn a few new skills in the process.

The key to writing a program to download the right files comes down to getting an array of the file names. Here we use the Python package BeautifulSoup to parse the page. In this case, the CSV files were given <key> tags in the site HTML, making them easy to pluck out.
```py
def find_csvs(url):

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        csv_names = []
        for f in soup.find_all('key'):
            string = str(f)
            name = string[5:len(f)-7] #remove <key> and </key>
            if name[len(name)-3:] == "csv":
                csv_names.append(name)

        return csv_names
```
After some slight string editing we're returned a string array of CSV names and can download them easily.
