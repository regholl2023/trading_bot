# encoding: utf-8

# import libraries
import sys
from traderlib import *
from logger import *

# check trading account
def check_account_ok():
    try:
        account_info = None  # get account info TODO
    except Exception as e:
        lg.error("Could not get account info")
        lg.info(str(e))
        sys.exit()


# close current orders
def clean_open_orders():
    open_orders = []  # get list of open orders TODO
    lg.info("List of open orders")
    lg.info(str(clean_open_orders))

    for order in open_orders:
        # close order TODO
        lg.info("Order %s closed", str(order.id))

    lg.info("Closing orders complete")


# execute trading bot
def main():

    # init logger
    init_logger()

    # check our trading account
    check_account_ok()

    # close current orders
    clean_open_orders()

    # get ticker
    ticker = input("Which ticker would you like to use?")

    # run trading bot
    trader = Trader()
    trader.run()


if __name__ == "__main__":
    main()
