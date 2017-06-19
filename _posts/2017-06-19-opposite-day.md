---
layout: post
title: Opposite Day
date: 2017-06-19
excerpt: What's really under your feet
tags:
---

Ever wonder what's on the other side of the world? Or hear the phrase "dig a hole straight through to China"? I just returned from my honeymoon in Thailand which, having a 12 hour time difference from US Central Time, got me thinking about this sort of thing. It's difficult to comprehend how big the world is, and it can be somewhat flabbergasting to think that if you could peer through the earth you could actually see people... upside down and almost 8,000 miles away.

So what is around the world? I decided to have some fun with this by imagining an inverse-me running the same routes that I run around here. By taking the data from my Suunto sport watch I can imagine a mirror image of myself running the same route I did but on the opposite side of the world. Easy enough...

Suunto lets you download your data in a number of formats, and in this case I used the GPX format which I manipulated using the Python module gpxpy. I read in the lat/long coordinates from the file and created three arrays of coordinates; one the unperturbed lat/long pairs, another the polar opposite, and the third the "northern" opposite where I did the reflection across the global axis instead of the global center thereby keeping the same latitude.

```Python
gpx_file = open(file,'r')
gpx = gpxpy.parse(gpx_file)
for t in gpx.tracks:
    for s in t.segments:
        coords = [[p.longitude,p.latitude] for p in s.points]
        opposite_coords = [[p.longitude+180.,-p.latitude] for p in s.points]
        north_opposite_coords = [[p.longitude+180.,p.latitude] for p in s.points]
```

I then saved these coordinate arrays as geojson LineStrings using the same modules I developed for my [Amtrak](/2017/america-by-train) post.

This method, applied to the Twin Cities Marathon I ran in 2015, shows that inverse-me would be getting pretty wet swimming his marathon somewhere between Australia and the Kerguelen Islands. Northern inverse-me would be running across the dunes in the western reaches of the Gobi desert in the northwestern part of China, pretty much equidistant from Kazakhstan and Mongolia.

[![image](/images/posts/oppositeday.png)](/posts/OppositeDay)
***(click the map for an interactive version)***
