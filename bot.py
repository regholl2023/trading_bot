# encoding: utf-8

# import libraries
import sys
from traderlib import *
from logger import *
import alpaca_trade_api as trade_api

# check trading account
def check_account_ok(api):
    try:
        account = api.get_account()
        if account.status != "ACTIVE":
            raise ValueError("Account is not active")
    except Exception as e:
        lg.error("Could not get account info")
        lg.info(str(e))
        sys.exit()


# close current orders
def clean_open_orders(api):
    try:
        api.cancel_all_orders()
    except Exception as e:
        lg.error("Could not cancel all orders")
        lg.error(str(e))
        sys.exit()
    lg.info("Closing orders complete")


# outputs true if asset is OK for trading
def check_asset_ok(api, ticker):
    try:
        asset = api.get_asset(ticker)
        if asset.tradable:
            lg.info("Asset exists and tradable")
            return True
        else:
            lg.info("Asset exists but not tradable")
            return False
    except Exception as e:
        lg.error("Asset does not exist or irretrievable from Alpaca")
        lg.error(str(e))
        sys.exit()


# execute trading bot
def main():
    # authenticate for using alpaci api
    api = trade_api.REST(
        key_id=constants.API_KEY,
        secret_key=constants.API_SECRET_KEY,
        base_url=constants.API_URL,
    )

    # init logger
    init_logger()

    # check our trading account can be accessed and is active
    check_account_ok(api)

    # close current orders
    clean_open_orders(api)

    # get ticker
    # ticker = input("Which ticker would you like to use?")
    ticker = "TSLA"
    check_asset_ok(api=api, ticker=ticker)
    # run trading bot
    trader = Trader(ticker, api)
    trader.run()


if __name__ == "__main__":
    main()
