---
layout: post
title: 4D Visualization of Time Series Analysis
date: 2017-04-25
excerpt: MACD time series analysis with comments on 4D data visualization
image: /images/posts/macd_thumb.png
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

As each EMA value depends upon the one preceding it, the first EMA value is computed as an average of the closing price over a period matching the time window parameter. An example of the results of this analysis is shown below.
![image](/images/posts/macd_time_series.png)
These time series are then used as trading indicators, with 'buy' and 'sell' signals triggered by some event in the data (a zero-crossing, for example, or a certain drop in price or volume).

The client provided me with roughly three years of stock price data for two stocks. This included an 'open', 'close', 'high', and 'low' price and 'volume' for each entry, with entries at 5 minute intervals between 9:30 am and 4:00 pm. The goal of hiring me for this project was to optimize the time window parameters (a,b,c) to maximize an investor's return on investment (ROI). To assess the 'goodness' of a set of parameters, I model how an initial investment would change given the client's buy/sell criteria applied to the signals generated for those parameters.

For this work the three year dataset was broken up into a 2-year 'in-sample' and 1-year 'out-sample' set. This allowed us to perform the optimization on the in-sample and see how it would perform on data for which it was not optimized. The following two plots show examples of the results on a small (and hopefully digestible) scale.

![image](/images/posts/macd_a_scan.png)
*Scan of a parameter on in/out-sample data*

After scanning over a single parameter we apply investment model to calculate the ROI for each value of *a* on both the in- and out-sample data. The optimization on the in-sample data (green marker) gives an ROI of 1.5, falling to 1.36 when applied to the out-sample data. While not a bad return, it is noticeably not the best we could have done with the out-sample data.

![image](/images/posts/macd_small_3d_scan.png)
*Small scan of (a,b,c) parameters*

We now scan over all three parameters, given the constraint that *c <= a < b*. By allowing variation in all three parameters, we are able to increase the ROI on in-sample data up to 3.08 with optimized parameters of (a,b,c) = (5,9,4). Applied to the out-sample data however, the ROI falls to 0.93.

The actual analysis was conducted over a much larger parameter array. Although stock volatility makes this analysis far from guaranteed to increase profit, the optimization here did result in a 32.3 and 51.9% increase in ROI on the out-sample data when compared to the "standard" analysis parameters of (12,26,9) conducted on the two stocks. While smaller sample sizes can be fairly effectively visualized as shown above, the much larger datasets created through the full 3D parameter scan are more difficult to portray in easily understandable formats. This is the motivation for the second portion of this post.

**The Visualization of 4-dimensional Data**
(coming soon)
