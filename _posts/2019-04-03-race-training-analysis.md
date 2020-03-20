---
layout: post
title: Race Training
date: 2019-04-03
excerpt: Analyzing my historical training efforts
#image: /images/posts/abt_bar.png
tags: StravaAPI
---

This too is a post in progress. There are a couple difficulties I'll discuss below.

GPS watches are amazing, but I have years of activity data and have never really used it. My watch basically serves to give me my current heartrate and distance, but little else.
So I'm going to leverage my data by using the Strava API to compare how my current training effort compares to races I've done in the past.

The issue with the Strava API is that it is built to be integrated into a website, and so responds to web requests. "Great!" you may think, as we currently sit on a website. Unfortunately, GitHub, on which this site is hosted, is a static host, meaning it does not allow me to make calls dynamically to the Strava API. Instead, I write up this post, add some images or links or whatever, and then it just sits there. So while it's possible (and preferable) to have the data update whenever you visit this post, I have to update the data by running a `localhost` session, get the data, save some figures, and update the git repo so that the next time you visit this post, the images will be updated.

That said, maybe some day I'll move to a different hosting setup. Then my plots could be *interactive*!

Using the Strava API I can grab activities (and filter by type='Run') between certain dates. I've created a list of races and their corresponding race date, then go through and gather the runs I did in the 18 weeks prior to and including race day.

![image](/images/posts/rta_dist.html)
**Training Runs**

I think it is more interesting to look at the cumulative distance. I think time (or total miles) is a stronger indicator of success than say max distance.

![image](/images/posts/rta_cum.png)
**Cumulative distance run during training**

And just for some added motivation to keep up my weekly runs, compare my totals for the past week between all races. So if, for example, we're currently 20 days prior to my next race, it'll compare what I've done in the past week to what I did 28-20 days before previous races.

![image](/images/posts/rta_week.png)
**Runs and cumulative distance for prior week**
