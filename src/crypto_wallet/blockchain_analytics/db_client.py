import os, sqlite3, logging
import datetime
import boto3
from sqlite3 import Connection
from boto3 import Session

def adapt_datetime(ts):
    return time.mktime(ts.timetuple())


sqlite3.register_adapter(datetime.datetime, adapt_datetime)
today_ = datetime.datetime.today().strftime("%d-%m-%Y_%H:%m")


class DatabaseClient:
    def __init__(self, connection, table=None):
        self.connection = connection
        self.table = table

        if isinstance(self.connection, Connection):
            self.db = SQLLiteClient()

        elif isinstance(self.connection, Session):
            self.db = AWSDynamoDBClient(self.connection, table)

    def get_all(self):
        return self.db.get_all()

    def insert_rows(self, *args, **kwargs):
        return self.db.insert_rows(*args, **kwargs)


class SQLLiteClient:
    def __init__(self, db_path="{os.getcwd}/data/crpyto.db"):
        self.db_path = db_path
        self.con = self.setup_db()
        self.table = table

    def setup_db(self):
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
        if os.path.exists("data"):
            os.mkdir("data")
        con = sqlite3.connect(db_path)
        with con:
            con.execute(
                """CREATE TABLE IF NOT EXISTS CRYPTO_PRICE
                    (DATE timestamp, TICKER text, QTY real, PRICE real, VALUE real )"""
            )

        logging.info("Database and table created")
        return con

    def get_all(self):
        return pd.read_sql_query(f"SELECT * FROM {self.table}", self.con)

    def insert_rows(self, ticker, price, dict):
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
            Dictionary : Dictionary loaded from portfolio JSON.

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


class AWSDynamoDBClient:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.numeric_attr = ["Price", "Value", "Quantity"]
        self.dynamodb_resource = boto3.resource("dynamodb")
        self.table = self.dynamodb_resource.Table(self.table_name)
        self.client = self.client.client("dynamodb")

    def get_all(self):
        logging.info("Querying DynamoDB")
        response = self.table.scan()
        logging.info("Scan successful!")
        items = response["Items"]
        while "LastEvaluatedKey" in response:
            response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response["Items"])

        processed_items = [
            {key: (float(value) if key in self.numeric_attr else value) for (key, value) in row.items()} for row in items
        ]
        return processed_items

    def insert_rows(self, value_dict, price_dict):

        request = [
            {
                "PutRequest": {
                    "Item": {
                        "Key": {"S": f"{ticker}_{today_}"},
                        "Date": {"S": f"{today_}"},
                        "Ticker": {"S": ticker},
                        "Quantity": {"N": f"{value_dict[ticker]/price_dict[ticker]}"},
                        "Value": {"N": f"{value_dict[ticker]}"},
                        "Price": {"N": f"{price_dict[ticker]}"},
                    }
                }
            }
            for ticker in value_dict
        ]

        response = self.client.batch_write_item(RequestItems={f"{self.table_name}": request})
        return response
