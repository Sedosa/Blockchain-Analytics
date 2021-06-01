import os,logging,argparse,json
import requests

API_KEY = os.getenv("CRYPTO_API_KEY")
HEADER = {"authorization": f"Apikey {API_KEY}"}

def parse_json(json_path):
    with open(json_path) as j:
        crypto_dict = json.load(j)
    return crypto_dict
    
def get_price(crypto):
    API_ENDPOINT = f"https://min-api.cryptocompare.com/data/price?fsym={crypto}&tsyms=GBP"
    response = requests.get(API_ENDPOINT,headers=HEADER)
    price = response.json()['GBP']
    return price

def main(json_path):
    crypto_dict = parse_json(json_path)
    wallet_dict = dict()
    for key_ in crypto_dict.keys():
        price = get_price(key_)
        print(f"{key_}: £{round(price*crypto_dict[key_],2)}")
        wallet_dict[key_] = price*crypto_dict[key_]

    print(f"Total: £{sum(wallet_dict.values())}")
    return sum(wallet_dict.values())

if __name__ =="__main__":
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s: %(asctime)s] %(filename)s, %(funcName)s, line %(lineno)d : %(message)s"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filepath_in", required=False, type=str, default=os.getcwd(), help="Filepath to json holding volumes of crypto"
    )

    args = parser.parse_args()
    FILEPATH_IN = args.filepath_in
    main(FILEPATH_IN)