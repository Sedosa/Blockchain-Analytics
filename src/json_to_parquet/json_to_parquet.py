import os,logging,argparse
import pandas as pd

def convert_json_to_parquet(filepath_in,filepath_out=None):
    data = pd.read_json(filepath_in)
    if filepath_out is not None:
        data.to_parquet(filepath_out,engine="pyarrow",compression="snappy")
    else:
        data.to_parquet("ADA_GBP_hourly.parquet")

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO,
                        format="[%(levelname)s: %(asctime)s] %(filename)s, %(funcName)s, line %(lineno)d : %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath_out",
                        required=False,
                        type=str,
                        default=os.getcwd(),
                        help="Directory to hold output parquetfile")


    parser.add_argument("--filepath_in",
                    required=False,
                    type=str,
                    default=f"{os.getcwd()}/ADA_hourly.json",
                    help="Path to json file with crypto data")
    args = parser.parse_args()
    FILEPATH_OUT = args.filepath_out   