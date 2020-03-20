---
layout: post
title: Race Training
date: 2019-04-03
excerpt: Analyzing my historical training efforts
#image: /images/posts/abt_bar.png
tags: StravaAPI
---

GPS watches are amazing, but I have years of underutilized activity data. Thanks to the Strava API though, I can compare how my current training effort compares to races I've done in the past.
Since GitHub (which hosts this site) is a static host, I can't dynamically make calls to the Strava API. Instead I run a `localhost` session to pull updated data, create the plots you see below and embed them as .html sources in an <iframe> element. So although they're not updated dynamically, they are still interactive.

Using the Strava API I can grab activities (and filter by type='Run') between certain dates. I've created a list of races and their corresponding race date, then go through and gather the runs I did in the 18 weeks prior to and including race day. By looking at run distance, cumulative distance, and pace, I can see how my current effort compares, helping me assess more realistically my readiness level for the upcoming race.

<iframe src="/images/posts/rta_dist.html" height="500" width="600"></iframe>
**Distance during training**

<iframe src="/images/posts/rta_cum.html" width="360"></iframe>
**Cumulative distance run during training**

<iframe src="/images/posts/rta_pace.html" width="360"></iframe>
**Pace during training**

I also run the same analysis for the prior week of training, isolating not just the past 7 days, but also that week of training for past races as well.

<iframe src="/images/posts/rta_week.html" height="500" width="600"></iframe>
**Runs and cumulative distance for prior week**
