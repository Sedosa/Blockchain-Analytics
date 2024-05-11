import os,sys, json
import boto3
import dotenv

dotenv.load_dotenv()

sys.path.append(os.getcwd())

from blockchain_analytics import utils,api_client,db_client

def main():
    # SQLITE_PATH = os.getenv("SQLITE_PATH","")
    # con = sqlite3.connect(SQLITE_PATH)
    
    JSON_PATH = os.getenv("JSON_PATH","")
    DYNAMO_TABLE = os.getenv("DYNAMO_TABLE","")
    API_KEY = os.getenv("CRYPTO_API_KEY","")

    session = boto3.Session()

    portfolio = utils.parse_json(JSON_PATH)
    price_client = api_client.CryptoPriceClient(API_KEY)
    portfolio_value, price_dict = price_client.calculate_portfolio(portfolio)
    
    dynamo_client = db_client.DatabaseClient(session,DYNAMO_TABLE)
    response = dynamo_client.insert_rows(portfolio_value,price_dict)
    print(f"Total: £{round(sum(portfolio_value.values())- portfolio_value['SUM'],2)}")
    return response


def lambda_handler(event, context):
    response = main()
    return {
        'statusCode': 200,
        'body': json.dumps(f'Successfully updated DynamoDB: {str(response)}')
    }