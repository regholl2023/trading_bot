# How to run

> python3 bot.py
NOTE: I've purposely included my API keys in this repo within constants.py so that anyone wanted to test this bot out can do so without creating an Alpaca account. However, if possible, please do create your own Alpaca account use your own Paper Trading API keys. 
# What it does

This is a Python trading bot which does the following for stock TSLA:
    1. Opens a long/short position for TSLA once a point at time occurs at which all of below filters pass:
        A. Long order filters
            i. General Trend Analysis: EMA9 > EMA26 > EMA 50 using 30 minute candlesticks
            ii. Instant Trend Analysis: EMA9 > EMA26 > EMA 50 using 5 minute candlesticks
            iii. RSI Analysis: 50 < RSI < 80
            iv. Stochastic Indicator Analysis
                A. Long filters
        B. Short order filters
            i. General Trend Analysis: EMA9 < EMA26 < EMA 50 using 30 minute candlesticks
            ii. Instant Trend Analysis: EMA9 < EMA26 < EMA 50 using 5 minute candlesticks
            iii. RSI Analysis: 20 < RSI < 50
            iv. Stochastic Indicator Analysis
    2. After the long/short TSLA order is placed, the position is held until at point in time at which one of the below criteria is met, at which point the position is closed:
        A. Comparison of Current Price to Stop Loss / Take Profit
            i. Long Order: Stop Loss <= Current TSLA Price <= Take Profit 
            ii. Short Order: Stop Loss >= Current TSLA Price or Current TSLA Price >= Take Profit 
        B. Stochastic Curve Crossing
    3. Repeat Steps 1-2 above
# Services Used/API's Consumed

1. Alpaca API: This API is used to broker opening and closing positions. I picked this because it's free, provides a Paper Trading account which enables users to test applications without using real money, and has a good interface for displaying positions opened/closed.
2. Yahoo Finance API: This API is used for fetching market data, namely the stock price of TSLA.
# Credits

I created this using the following trading bot tutorial at https://www.udemy.com/course/trading-bot-bootcamp/. For people new to financial markets and trading, I'd highly recommend following this tutorial because it:
    1. It does a great job at explaining the statistical analysis tools used for deciding when to buy/sell stocks, and 
    2. Points out exceptions and the way to handle them in order for the trading bot to be able to handle real money as safely as possible


        
