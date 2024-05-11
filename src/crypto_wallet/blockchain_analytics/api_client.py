import logging
import requests


class CryptoPriceClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_price(self, ticker):
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
        HEADER = {"authorization": f"Apikey {self.api_key}"}
        response = requests.get(API_ENDPOINT, headers=HEADER)
        price = response.json()
        return price

    def calculate_portfolio(self, portfolio):
        price_dict = {ticker: self.get_price(ticker)["GBP"] for (ticker, quantity) in portfolio.items()}
        value_dict = {ticker: self.get_price(ticker)["GBP"] * portfolio[ticker] for (ticker, quantity) in portfolio.items()}
        value_dict["SUM"] = sum(value_dict.values())
        price_dict["SUM"] = 1
        return (value_dict, price_dict)
