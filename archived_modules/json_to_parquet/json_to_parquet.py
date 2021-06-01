import os, logging, argparse, json
import pandas as pd


def convert_json_to_parquet(filepath_in, filepath_out):
    """
    Parameters
    ---------------
    filepath_in
        str : Filepath to the raw JSON file

    filepath_out
        str : Where the output file should be written

    Return
    ---------------
    FILENAME_OUT
        str : Filepath of output parquet
    """

    FILENAME_OUT = "ADA_GBP_hourly.parquet"

    logging.info(f"Reading data from {filepath_in}")
    with open(filepath_in, "r") as j:
        json_ = json.load(j)

    df = pd.DataFrame.from_records(json_["Data"]["Data"])
    df["time"] = pd.to_datetime(df["time"], unit="s")

    if filepath_out is not None:
        FILENAME_OUT = f"{filepath_out}/{FILENAME_OUT}"

    logging.info(f"Writing data to {FILENAME_OUT}")
    df.to_parquet(FILENAME_OUT, engine="pyarrow", compression="snappy", index=False)

    return FILENAME_OUT


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s: %(asctime)s] %(filename)s, %(funcName)s, line %(lineno)d : %(message)s"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filepath_out", required=False, type=str, default=os.getcwd(), help="Directory to hold output parquetfile"
    )

    parser.add_argument(
        "--filepath_in",
        required=True,
        type=str,
        default=f"{os.getcwd()}/ADA_GBP_hourly.json",
        help="Path to json file with crypto data",
    )
    args = parser.parse_args()

    FILEPATH_OUT = args.filepath_out
    FILEPATH_IN = args.filepath_in

    FILENAME_OUT = convert_json_to_parquet(FILEPATH_IN, FILEPATH_OUT)

    logging.info(f"Output file written to {FILENAME_OUT}")
    logging.info("Executed successfully")
