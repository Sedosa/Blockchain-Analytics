import argparse
import os,json,logging,argparse
import requests

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
    API_OPTIONS = F"histohour?fsym=ADA&tsym=GBP&limit={LIMIT}"
    HEADER = {"authorization": f"Apikey {API_KEY}"}
    data = requests.get(f"{API_ENDPOINT}{API_OPTIONS}",headers=HEADER)

    with open(f"{FILEPATH_OUT}/ADA_hourly.json","w") as j:
        json.dump(data.json(),j)

