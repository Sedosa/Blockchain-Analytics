import json
import boto3
from blockchain_analytics import db_client,analytics

def parse_json(json_path):
    """
    Loads portfolio in JSON into a python dictionary.

    Parameters
    -------------
    json_path
        string : Path to portfolio JSON

    Returns
    -------------
    portfolio_dict
        Dictionary : Dictionary loaded from portfolio json. output of parse_json() fn

    """

    with open(json_path) as j:
        portfolio_dict = json.load(j)
    return portfolio_dict


def init_data(DYNAMO_TABLE):
  session = boto3.Session()
  dynamo_client = db_client.DatabaseClient(session,DYNAMO_TABLE)
  rows = dynamo_client.get_all()

  data_cleaner = analytics.DataPrep()
  df = data_cleaner.dynamo_to_dataframe(rows)
  return df