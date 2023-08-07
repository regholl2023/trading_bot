# encoding: utf-8
# import alpaca_trade_api as tradeapi
import sys, os, time, pytz
import tulipy as ti
import pandas as pd
import logging as lg
import constants
import pdb
from alpaca_trade_api import TimeFrame, TimeFrameUnit
import yfinance as yf

from datetime import datetime, date, timedelta
from math import ceil


class Trader:
    def __init__(self, ticker, api):
        lg.info("Trader initialized with ticker %s", ticker)
        self.ticker = ticker
        self.api = api

    def is_tradable(self, ticker):
        # check if tradable: ask the broker/API if "asset" is tradable
        # IN: asset (string)
        # OUT: True/Fals (bool) if tradable ot not
        try:
            asset = None  # get asset from alpaca API TODO
            if not asset.tradable:
                lg.info("the asset %s is not tradable", ticker)
                return False
            else:
                lg.info("the asset %s is tradable!", ticker)
                return True
        except:
            lg.error("The asset %s is not answering well from Alpaca API", ticker)
            return False

    def set_stoploss(
        self, entryPrice, direction, stopLossMargin=constants.stopLossMargin
    ):
        # set stop loss: determines stop loss based on entryPrice and direction
        # IN: entry price, direction (long/short)
        # OUT: stop loss (num)

        try:
            if direction == "long":
                stopLoss = entryPrice * (1 - stopLossMargin)
                lg.info("Stop loss set for long at %.2f", stopLoss)
                return stopLoss
            elif direction == "short":
                stopLoss = entryPrice * (1 + stopLossMargin)
                lg.info("Stop loss set for short at %.2f", stopLoss)
                return stopLoss
            else:
                raise ValueError
        except Exception as e:
            lg.error(
                "Invalid direction value used for determining stop loss: % s", direction
            )
            sys.exit()

    def set_takeprofit(
        self, entryPrice, direction, takeProfitMargin=constants.takeProfitMargin
    ):
        # set take profit: determines take profit based on entryPrice and direction
        # IN: entry price, direction (long/short)
        # OUT: stop loss (num)

        try:
            if direction == "long":
                takeProfit = entryPrice * (1 + takeProfitMargin)
                lg.info("Take profit set for long at %.2f", takeProfit)
                return takeProfit
            elif direction == "short":
                takeProfit = entryPrice * (1 - takeProfitMargin)
                lg.info("Take profit set for long at %.2f", takeProfit)
                return takeProfit
            else:
                raise ValueError
        except Exception as e:
            lg.error(
                "Invalid direction value used for determining take margin: % s",
                direction,
            )
            sys.exit()

    # Loads 'limit' 'timeframe' candlesticks by making call to alpaca data api
    # Returns result as a pandas DataFrame
    def load_historical_data_alpaca(
        self, timeframe=TimeFrame(15, TimeFrameUnit.Minute), limit=3 * 24 * 4
    ):
        currentTime = datetime.now(pytz.timezone("US/Eastern"))
        endTime = (currentTime - timedelta(hours=1)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ) + "-00:00"
        startTime = (currentTime - timedelta(days=2)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ) + "-00:00"
        data = self.api.get_bars(
            symbol=self.ticker,
            timeframe=timeframe,
            start=startTime,
            end=endTime,
            limit=limit,
        )
        df = data.df
        return df

    def load_historical_data_yahoo(self, interval="30m", period="5d"):
        try:
            ticker = yf.Ticker(self.ticker)
            data = ticker.history(interval=interval, period=period)
        except Exception as e:
            lg.error("somethign happened while loading historical data")
            lg.error(str(e))
            sys.exit()
        return data

    def get_open_positions(self, assetId):
        # get open positions
        # IN: assetId, a unique identifier for stock, (ticker not unique)
        # OUT: True/False if open (bool)
        positions = None  # get open positions from alpaca API TODO
        for position in positions:
            if position.symbol == assetId:
                return True
            else:  # TODO -> is this correct?
                return False

    def check_position(self, fastFalse=False):
        # check whether position exists or not
        # IN: ticker, fastFalse (don't retry if not found)
        # OUT: boolean (True if order is there, False otws)
        for attempt in range(constants.maxAttemptsCheckPosition):
            try:
                position = self.api.get_position(self.ticker)
                currentPrice = position.current_price
                lg.info(
                    "The position was checked with current price: %.2f", currentPrice
                )
                return True
            except:
                if fastFalse:
                    lg.info("Position not found (good!)")
                    return False
                lg.info("Position not found, waiting for it ...")
                time.sleep(constants.sleepTimeCheckPosition)  # 5 seconds
        lg.info("Position not found for %s, not any more", self.ticker)
        return False

    def get_shares_amount(self, assetPrice):
        # works out number of shares I want to buy/sell (default $1000)
        # IN: assetPrice
        # OUT: number of shares
        try:
            # get equity available from alpaca api TODO
            equity = float(self.api.get_account().equity)
            shares = min(equity, constants.maxSpendEquity) // assetPrice
            if equity - shares * assetPrice > 0:
                lg.info("Total shares to operate with: %d", shares)
                return shares
            else:
                lg.info("Cannot spend that amount, remaining equity is %.2f", equity)
                sys.exit()
        except Exception as e:
            lg.error("Unable to get equity avilable")
            lg.info(str(e))

        # calc number of shares

    def get_current_price(self):
        # get current price of asset with a position open
        # IN: ticker/asset
        # OUT: current price
        asset = self.ticker
        for attempt in range(constants.maxAttemptsCurrentPrice):
            try:
                position = None  # get open positions from alpaca API TODO
                currentPrice = position.current_price
                lg.info(
                    "The position was checked with current price: %.2f", currentPrice
                )
                return currentPrice
            except:
                lg.info("Position not found,cannot check price ...")
                time.sleep(constants.sleepTimeCurrentPrice)  # 5 seconds
        lg.error("Position not found for %s, not any more", asset)
        sys.exit()

    def get_general_trend(self):
        # get general trend: detect interesting trend (UP/DOWN/NONE)
        # IN: asset
        # OUT: 'long'/'short'/'none' (strings)
        lg.info("General trend analysis ...")
        asset = self.ticker
        for attempt in range(constants.maxAttemptsGeneralTrend):
            # get 30 min candles from yahoo API (aim to get ~50 samples of 30m candlesticks)
            data = self.load_historical_data_yahoo(interval="30m", period="5d")
            # check EMA's relative positions to identify trend
            close = data.Close.values
            ema9, ema26, ema50 = (
                ti.ema(close, 9)[-1],
                ti.ema(close, 26)[-1],
                ti.ema(close, 50)[-1],
            )
            lg.info(
                "General trend EMAs = [EMA9: %.2f, EMA26: %.2f, EMA50: %.2f]",
                ema9,
                ema26,
                ema50,
            )

            if ema9 > ema26 and ema26 > ema50:
                lg.info("Trend detected for %s: long", asset)
                return "long"
            elif ema9 < ema26 and ema26 < ema50:
                lg.info("Trend detected for %s: short", asset)
                return "short"
            if attempt != constants.maxAttemptsGeneralTrend - 1:
                lg.info("Trend not clear, waiting to try again")
                time.sleep(
                    constants.sleepTimeGeneralTrend * constants.maxAttemptsGeneralTrend
                )
        lg.info("Trend not detected and max attempts reached")
        return "none"

    def get_instant_trend(
        self,
        trend,
        maxAttempts=constants.maxAttemptsInstantTrend,
        retryInterval=constants.sleepTimeInstantTrend,
    ):
        # get instant trend: detect interesting trend (UP/DOWN/NONE)
        # IN: asset, trend
        # OUT: boolean, True iff confirms trend
        lg.info("Instant trend analysis ...")
        asset = self.ticker
        for attempt in range(maxAttempts):
            # get 5 min candles from yahoo API (~50 samples)
            data = self.load_historical_data_yahoo(interval="5m", period="1d")
            # check EMA's relative positions to identify trend
            close = data.Close.values
            ema9, ema26, ema50 = (
                ti.ema(close, 9)[-1],
                ti.ema(close, 26)[-1],
                ti.ema(close, 50)[-1],
            )
            lg.info(
                "Instant trend EMAs = [EMA9: %.2f, EMA26: %.2f, EMA50: %.2f]",
                ema9,
                ema26,
                ema50,
            )
            if trend == "long" and ema9 > ema26 and ema26 > ema50:
                lg.info("Trend confirmed for %s: long", asset)
                return True
            elif trend == "short" and ema9 > ema26 and ema26 > ema50:
                lg.info("Trend confirmed for %s: short", asset)
                return True
            if attempt != maxAttempts - 1:
                lg.info("Trend %s not clear, waiting to try again", trend)
                time.sleep(retryInterval)
        lg.info("Trend %s not confirmed and max attempts reached", trend)
        return False

    def get_rsi(
        self,
        trend,
        maxAttempts=constants.maxAttemptsRSI,
        retryInterval=constants.sleepTimeRSI,
    ):
        # get rsi: perform rsi analysis to confirm trend
        # IN: asset, trend
        # OUT: boolean, True iff confirms trend

        lg.info("RSI analysis ...")
        asset = self.ticker
        for attempt in range(maxAttempts):
            # get 5 min candles from yahoo (~50 samples)
            data = self.load_historical_data_yahoo(interval="5m", period="1d")
            rsi = ti.rsi(data.Close.values, 14)[-1]  # using 14 sample window
            pdb.set_trace()
            lg.info("RSI = %.2f", rsi)
            if trend == "long" and 50 < rsi and rsi < 80:
                lg.info("Trend confirmed for %s: long", asset)
                return True
            elif trend == "short" and 20 < rsi and rsi < 50:
                lg.info("Trend confirmed for %s: short", asset)
                return True
            if attempt != maxAttempts - 1:
                lg.info("Trend not clear, waiting to try again")
                time.sleep(retryInterval)
        lg.info("Trend not confirmed and max attempts reached")
        return False

    def get_stochastic(
        self,
        trend,
        maxAttempts=constants.maxAttemptsStochastic,
        retryInterval=constants.sleepTimeStochastic,
    ):
        # get stochastic: perform stochastic analysis to confirm trend
        # IN: asset, trend
        # OUT: boolean, True iff confirms trend

        lg.info("Stochastic analysis ...")
        asset = self.ticker
        for attempt in range(maxAttempts):
            # get 5 min candles from alpaca API TODO
            data = self.load_historical_data_yahoo(interval="5m", period="1d")
            stoch_k, stoch_d = ti.stoch(
                data.High.values,
                data.Low.values,
                data.Close.values,
                9,
                6,
                9,
            )  # 14-sample window
            stoch_k, stoch_d = stoch_k[-1], stoch_d[-1]
            lg.info("Stochastic values [%.2f, %.2f]", stoch_k, stoch_d)

            if trend == "long" and stoch_d < stoch_k and stoch_k < 80:
                lg.info("Trend confirmed for %s: long", asset)
                return True
            elif trend == "short" and 20 < stoch_k and stoch_k < stoch_d:
                lg.info("Trend confirmed for %s: short", asset)
                return True
            lg.info("Trend not clear, waiting to try again")
            time.sleep(retryInterval)
        lg.info("Trend not confirmed and max attempts reached")
        return False

    def check_stochastic_crossing(self, trend):
        # check whetherf the stochastic curves have crossed or not dep on trend
        # IN: trend
        # OUt: True if crossed, False otws
        lg.info("Checking stochastic crossing...")
        data = None  # ask yahoo API for 5 min candles
        data = self.load_historical_data_yahoo(interval="5m", period="1d")
        stoch_k, stoch_d = ti.stoch(
            data.High.values,
            data.Low.values,
            data.Close.values,
            9,
            6,
            9,
        )  # 14-sample window
        stoch_k, stoch_d = stoch_k[-1], stoch_d[-1]
        lg.info("Stochastic values (checking crossing) [%.2f, %.2f]", stoch_k, stoch_d)
        if trend == "long" and stoch_k <= stoch_d:
            lg.info("Stochastic curves crossed: long, k=%.2f, d=%.2f", stoch_k, stoch_d)
            return True
        elif trend == "short" and stoch_k >= stoch_d:
            lg.info(
                "Stochastic curves crossed: short, k=%.2f, d=%.2f", stoch_k, stoch_d
            )
            return True
        else:
            lg.info("Stochastic curves have not crossed")
            return False

    def enter_position_mode(self, trend, retryInterval=20, maxAttempts=1440):
        # default params will stay in position for at most 8 hours (since 20 * 1440 seconds is 8 hrs)
        # check the conditions in parallel once inside the position, if any are true -> close
        asset = self.ticker
        entryPrice = None  #  ask alpaca API for entry price TODO

        takeProfit = self.set_takeprofit(entryPrice, trend)
        stopLoss = self.set_stoploss(entryPrice, trend)

        for attempt in range(maxAttempts):
            currentPrice = self.get_current_price()
            # check take profit
            if trend == "long" and currentPrice >= takeProfit:
                lg.info(
                    "Take profit met at %.2f (long). Current price is %.2f",
                    takeProfit,
                    currentPrice,
                )
                return True
            # check stop loss
            elif trend == "long" and currentPrice <= stopLoss:
                lg.info(
                    "Stop loss met at %.2f (long). Current price is %.2f",
                    stopLoss,
                    currentPrice,
                )
                return False
            elif trend == "short" and currentPrice <= takeProfit:
                lg.info(
                    "Take profit met at %.2f (short). Current price is %.2f",
                    takeProfit,
                    currentPrice,
                )
                return True
            # check stop loss
            elif trend == "short" and currentPrice >= stopLoss:
                lg.info(
                    "Stop loss met at %.2f (short). Current price is %.2f",
                    stopLoss,
                    currentPrice,
                )
                return False
            elif self.check_stochastic_crossing(asset, trend):
                lg.info(
                    "Stochastic curves crossed. Current price is %.2f", currentPrice
                )
                return True
            else:
                lg.info("Waiting inside position, attempt#%d", attempt)
                lg.info(
                    "stop loss: %.2f|  $.2f  |%.2f :take profit",
                    stopLoss,
                    currentPrice,
                    takeProfit,
                )
                time.sleep(retryInterval)

        lg.info("Timeout reached, time to exit position")
        return False

        # check stochastic crossing

    def submit_order(
        self, type, trend, ticker, sharesQuantity, currentPrice, exit=False
    ):
        lg.info("Submitting %s order for %s" % (trend, ticker))

        if trend == "long" and not exit:
            side = "buy"
            limitPrice = round(currentPrice + currentPrice * constants.maxVar, 2)
        elif trend == "short" and not exit:
            side = "sell"
            limitPrice = round(currentPrice - currentPrice * constants.maxVar, 2)
        elif trend == "long" and exit:
            side = "buy"
        else:
            lg.error("Trend was not understood")
            sys.exit()
        try:
            if type == "limit":
                lg.info(
                    "Current price: %.2f // Limit price %.2f", currentPrice, limitPrice
                )
                order = self.api.submit_order(
                    symbol=self.ticker,
                    qty=sharesQuantity,
                    side=side,
                    type=type,
                    time_in_force="gtc",
                    limitPrice="limitPrice",
                )
            elif type == "market":
                lg.info("Current price: %.2f", currentPrice)
                order = self.api.submit_order(
                    symbol=self.ticker,
                    qty=sharesQuantity,
                    side=side,
                    type=type,
                    time_in_force="gtc",
                )
            else:
                lg.error("Type of order was not understood")
                sys.exit()

            self.orderId = order.id
            lg.info("%s order submitted correctly!", trend)
            lg.info("%d shares %s", sharesQuantity, side)
            lg.info("Client order ID: %s", self.orderId)
            return True

        except Exception as e:
            lg.error("Order submission error")
            lg.error(str(e))
            sys.exit()

    def run(self):
        # LOOP until timeout reached (ex. 2 hr)
        while True:
            # ask broker/api if we have an open position with asset
            if self.check_position(fastFalse=True):
                lg.info(
                    "There is already and open position with that asset! Aborting..."
                )
                return False  # aborting execution

            # get general trend
            while True:
                # find general trend
                trend = self.get_general_trend()
                if trend == "none":
                    lg.info("No general trend found for %s", self.ticker)
                    return False
                # confirm instant trend matches general trend
                if not self.get_instant_trend(trend):
                    lg.info("Instant analysis is not confirming trend, going back")
                    continue

                # perform rsi analysis
                if not self.get_rsi(trend):
                    lg.info("RSI is not confirming trend, going back")
                    continue

                # perform stichastic analysis
                if not self.get_stochastic(trend):
                    lg.info("Stochastic analysis is not confirming trend, going back")
                    continue

                # all of filters passed
                lg.info("All filtering passed, make an order")
                break

            # get current price
            self.currentPrice = round(
                float(
                    self.load_historical_data_yahoo(
                        interval="1min", period="1d"
                    ).Close.values[-1]
                ),
                2,
            )
            # decide amount to invest
            sharesQuantity = self.get_shares_amount(self.currentPrice)
            # submit order TODO

            # check position
            if not self.check_position():
                # cancel order if it didn't go through TODO

                continue
            # enter position mode
            successfulSell = self.enter_position_mode(trend)
            while True:
                # submit order TODO

                if not self.check_position(True):
                    break
                time.sleep(10)
            return successfulSell
