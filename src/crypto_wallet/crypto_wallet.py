"""
This is a script that takes a calculates the value of a cryptocurrency portfolio
It uses JSON in the with quantities of different cryptocurrencies in the form

{
    "ticker" : volume,
    "ticker" : volume
}

gets the live price from an API endpoint and returns the price of each item in the portfolio and the total
It also writes these into a sqlite3 database for future reference with a timestamp

"""


import os, logging, argparse, json
import sqlite3
import requests
import datetime
import time

"""
TODO: Error handling & logging
"""

#  Need API from https://min-api.cryptocompare.com/
API_KEY = os.getenv("CRYPTO_API_KEY")
HEADER = {"authorization": f"Apikey {API_KEY}"}

# Taken from https://docs.python.org/3/library/sqlite3.html#registering-an-adapter-callable
def adapt_datetime(ts):
    return time.mktime(ts.timetuple())


sqlite3.register_adapter(datetime.datetime, adapt_datetime)


def setup_db(db_path):
    """
    Initialises a local sqlite3 database and create the table required to hold data.

    Parameters
    -------------
    db_path
        string : A filepath to  a target sqlite database

    Returns
    -------------
    con:
        Connection : Returns a connection to that database
    """
    con = sqlite3.connect(db_path)

    # Create table
    with con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS CRYPTO_PRICE
                (DATE timestamp, TICKER text, QTY real, PRICE real, VALUE real )"""
        )

    logging.info("Database and table created")
    return con


def insert_into_db(connection, ticker, price, dict):
    """
    Writes crypto price data to specified sqlite3 database

    Parameters
    -------------
    connection
        string : Connection to sqlite3 database output of setup_db() fn
    ticker
        string : String of the Ticker for a cryptocurrency e.g. BTC
    price
        float : Price of a cryptocurrency
    dict
        Dictionary : Dictionary loaded from portfolio JSON. output of parse_json() fn

    """

    now = datetime.datetime.now()
    with connection as con:
        if ticker != "SUM":
            con.execute(
                """insert into CRYPTO_PRICE
                        values (?,?,?,?,?)""",
                (now, ticker, dict[ticker], price, price * dict[ticker]),
            )

        else:
            con.execute(
                """insert into CRYPTO_PRICE
                        values (?,?,?,?,?)""",
                (now, ticker, 0, price, price),
            )

    logging.info(f"Inserted {ticker} values into database")


def parse_json(json_path):
    """
    Loads portfolio in JSON into a python dictionary.

    Parameters
    -------------
    json_path
        string : Path to portfolio JSON described in header documentation

    Returns
    -------------
    crypto_dict
        Dictionary : Dictionary loaded from portfolio json. output of parse_json() fn

    """

    with open(json_path) as j:
        crypto_dict = json.load(j)
    return crypto_dict


def get_price(ticker):
    """
    Returns the live price of a unit a cryptocurrency in GBP.

    Parameters
    -------------
    ticker
        string : String of the Ticker for a cryptocurrency e.g. BTC


    Returns
    -------------
    price
        float : Price of a cryptocurrency

    """

    API_ENDPOINT = f"https://min-api.cryptocompare.com/data/price?fsym={ticker}&tsyms=GBP"
    response = requests.get(API_ENDPOINT, headers=HEADER)
    price = response.json()["GBP"]
    return price


def main(json_path, connection):

    crypto_dict = parse_json(json_path)
    wallet_dict = dict()
    for key_ in crypto_dict.keys():
        price = get_price(key_)
        print(f"{key_}: £{round(price*crypto_dict[key_],2)}")
        wallet_dict[key_] = price * crypto_dict[key_]
        insert_into_db(connection, key_, price, crypto_dict)
    insert_into_db(connection, "SUM", sum(wallet_dict.values()), crypto_dict)
    print(f"Total: £{sum(wallet_dict.values())}")
    return sum(wallet_dict.values())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s: %(asctime)s] %(filename)s, %(funcName)s, line %(lineno)d : %(message)s"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filepath_in", required=False, type=str, default=os.getcwd(), help="Filepath to json holding volumes of crypto"
    )

    parser.add_argument(
        "--db_path", required=False, type=str, default=f"{os.getcwd()}/crypto.db", help="Filepath to sqlite database"
    )

    args = parser.parse_args()
    FILEPATH_IN = args.filepath_in
    con = setup_db(args.db_path)
    main(FILEPATH_IN, con)
    con.close()
