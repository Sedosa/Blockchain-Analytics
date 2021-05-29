import argparse
import os,json,logging,argparse
from typing import Dict
import requests
from http import HTTPStatus

#################################
# GLOBAL VARIABLES
#################################
API_ENDPOINT = "https://min-api.cryptocompare.com/data/v2/"
API_KEY = os.getenv("CRYPTO_API_KEY")
HEADER = {"authorization": f"Apikey {API_KEY}"}

def main(filepath_out) -> Dict:
    '''
    Parameters
    ---------------
    filepath_out
        str : Where the output file should be written

    Return
    ---------------
    json_
        Dict : A Dictionary holding the data retreived from the API request
    '''
    NUM_RECORDS= os.getenv("NUM_RECORDS","1000")
    API_OPTIONS = f"histohour?fsym=ADA&tsym=GBP&limit={NUM_RECORDS}"
    logging.info("Parameters gathered. Sending request to endpoint.")
    response = requests.get(f"{API_ENDPOINT}{API_OPTIONS}",headers=HEADER)
    if response.status_code >= HTTPStatus.BAD_REQUEST:
        raise RuntimeError(f'Request failed: {response.text}')

    json_ = response.json()
    return json_

if __name__ == "__main__":
    # TODO optional argument to define crypto of interest

    logging.basicConfig(level=logging.INFO,
                        format="[%(levelname)s: %(asctime)s] %(filename)s, %(funcName)s, line %(lineno)d : %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath_out",
                        required=False,
                        type=str,
                        default=os.getcwd(),
                        help="directory to hold file")

    args = parser.parse_args()
    FILEPATH_OUT = args.filepath_out   
    json_ = main(FILEPATH_OUT)

    with open(f"{FILEPATH_OUT}/ADA_hourly.json","w") as j:
        json.dump(json_,j)

    logging.info(f"Data written successfully to {FILEPATH_OUT}/ADA_hourly.json")
    logging.info("Executed successfully.")