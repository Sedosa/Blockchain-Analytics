import argparse
import os,json,logging,argparse
import requests
from http import HTTPStatus

def main():
    raise NotImplementedError

if __name__ == "__main__":
    # TODO optional argument to define crypto of interest
    # TODO verbosity argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath_out",
                        required=False,
                        type=str,
                        default=os.getcwd(),
                        help="directory to hold file")
    args = parser.parse_args()
    FILEPATH_OUT = args.filepath_out
    API_KEY = os.getenv("CRYPTO_API_KEY")
    NUM_RECORDS= os.getenv("NUM_RECORDS","1000")
    API_ENDPOINT = "https://min-api.cryptocompare.com/data/v2/"
    API_OPTIONS = f"histohour?fsym=ADA&tsym=GBP&limit={NUM_RECORDS}"
    HEADER = {"authorization": f"Apikey {API_KEY}"}
    response = requests.get(f"{API_ENDPOINT}{API_OPTIONS}",headers=HEADER)
    if response.status_code >= HTTPStatus.BAD_REQUEST:
        raise RuntimeError(f'Request failed: {response.text}')

    with open(f"{FILEPATH_OUT}/ADA_hourly.json","w") as j:
        json.dump(response.json(),j)