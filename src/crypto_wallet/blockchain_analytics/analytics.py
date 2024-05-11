
import logging
import pandas as pd

class DataPrep:

    def dynamo_to_dataframe(self,dynamo_records):
        try:
            return pd.DataFrame.from_records(dynamo_records)
        except Exception as e:
            logging.exception("Error raised when converting DynamoDB records to " + \
                                "pandas DataFrame: "+ e)  

