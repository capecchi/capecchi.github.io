---
layout: post
title: 4D Visualization of Time Series Analysis
date: 2017-04-25
excerpt: MACD time series analysis with comments on 4D data visualization
image: /images/posts/small_3d_scan.png
project: true
tags: time-series optimization 4D-visualization
---

I recently completed a project for an Upwork client optimizing parameters in a time-series analysis. I thought both the project itself the subsequent task of communicating the results through visuals presented some interesting material, and so I wanted to briefly mention a few things here.

**The Project**

My client's goal in hiring me was to increase the success of his stock trading by using the moving average convergence/divergence ([MACD](https://en.wikipedia.org/wiki/MACD)) technique. This technique computes three exponential moving averages ([EMA](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average)) based on three time windows (a,b,c), which is supposed to reveal changes in the strength, direction, momentum, and duration of a trend in a stock's prices.

Developed in the 1970s, this technique is typically computed with time windows of 12, 26, and 9 days. This represented two weeks, one month, and a week and a half of the old 6-day trading cycle. As today's stock prices are updated in near real-time there is much more flexibility in the choice of time window parameters.

Steps to the analysis are as follows:
1. Compute two EMA(a) and EMA(b) of the closing price
2. Calculate MACD = EMA(a) - EMA(b)
3. Compute EMA(c) of the MACD time series
4. Calculate a 'Histogram' = MACD - Signal

Below is an excerpt from the data representing this analysis, done with (a,b,c) = (12,26,9)

Time | Open | High | Low | Close | Volume | EMA(a) | EMA(b) | MACD | EMA(c) | Histogram
-----|------|------|-----|-------|--------|--------|--------|------|--------|----------
1040 | 112.869 | 112.898 | 112.350 | 112.350 | 103.979 | 109.486				

1050	113.533	113.937	113.388	113.388	277.277	110.0861667				
1055	112.927	112.927	112.927	112.927	34.6596	110.5232179				
1100	113.129	113.533	113.129	113.533	69.3193	110.9862613				
1105	113.417	113.417	113.417	113.417	34.6596	111.3602211				
1110	113.244	113.616	113.244	113.616	207.958	111.707264				
1115	113.388	113.388	113.244	113.244	69.3192	111.943685				
1120	113.042	113.443	111.542	111.542	277.277	111.8818873				
1125	110.793	110.793	110.244	110.590	277.277	111.6831354				
1140	111.513	111.744	111.513	111.744	103.979	111.6924992				
1145	111.859	111.859	111.859	111.859	34.6596	111.7181147				
1150	112.321	112.321	112.321	112.321	34.6596	111.8108663				
1155	112.580	112.580	112.552	112.552	77.9842	111.9248868				
1205	112.494	112.494	112.465	112.465	69.3192	112.0079812				
1210	112.754	112.754	112.754	112.754	34.6596	112.1227533	111.145	0.977291763		
1215	112.465	112.465	112.465	112.465	34.6596	112.1754066	111.2432051	0.932201512		
1220	112.321	112.321	111.109	111.109	138.638	112.0113441	111.233264	0.778080072		
1225	111.196	111.224	111.196	111.224	69.3192	111.8902142	111.2325778	0.657636437		
1230	111.773	111.773	111.773	111.773	34.6596	111.8721813	111.2726091	0.599572204		
1235	112.811	112.811	112.811	112.811	34.6596	112.0166149	111.3865639	0.630050972		
1240	112.725	112.725	112.725	112.725	34.6596	112.1255972	111.4857074	0.639889881		
1245	112.379	112.379	112.379	112.379	34.6596	112.1645823	111.5518772	0.612705096		
1300	113.273	113.533	112.984	112.984	242.617	112.2906465	111.6579604	0.632686189	0.717790458	-0.085104269
1305	113.244	113.273	113.244	113.273	69.3192	112.4417778	111.7775929	0.664184924	0.707069351	-0.042884428
1315	113.763	114.340	113.763	114.340	1005.13	112.733812	111.9674009	0.76641117	0.718937715	0.047473455



The client provided me with roughly three years of stock price data for two stocks. This included an 'open', 'close', 'high', and 'low' price and 'volume' for each entry, with entries at 5 minute intervals between 9:30 am and 4:00 pm.


![image](/images/posts/small_3d_scan.png)
*Small scan of (a,b,c) parameters*
