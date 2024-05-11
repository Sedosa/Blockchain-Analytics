import streamlit as st
import boto3
import pandas as pd
from decimal import Decimal

TABLE_NAME="Crypto_Portfolio_Tracker"

client = boto3.client('dynamodb')

st.set_page_config(
    page_title="Crypto Dashboard V2",
    page_icon="💵",
)


@st.cache_data
def get_data():
    data = client.scan(TableName=TABLE_NAME)
    last_eval_key =  data.get('LastEvaluatedKey')
    while last_eval_key is not None:
        more_data = client.scan(TableName=TABLE_NAME,ExclusiveStartKey=last_eval_key)
        last_eval_key = more_data.get('LastEvaluatedKey')
        data['Items'].extend(more_data['Items'])
    def dynamodb_to_records(items: dict) -> list[dict]:
        def get_key_values(item):
            record = {
                "Date": item["Date"]["S"],
                "Ticker": item["Ticker"]["S"],
                "Price": round(Decimal(item["Price"]["N"]),4),
                "Quantity": round(Decimal(item["Quantity"]["N"]),5),
                "Value": round(Decimal(item["Value"]["N"]),2),
                "Key": item["Key"]["S"],
            }
            return record
        records = [get_key_values(item) for item in items]
        return records

    records = dynamodb_to_records(data['Items'])

    df = pd.DataFrame.from_records(records)
    df["Date"] = pd.to_datetime(df["Date"],format='%d-%m-%Y_%H:%M')
    return df


def wallet_snapshot():
    """
    
    """

    data = get_data()
    
    col1, col2 = st.columns(2)
    col1.header("Total Snapshot")
    col2.header("Relative Snapshot")
    
    current_values = data[data['Date']==max(data['Date'])].reset_index(drop=True).drop(columns = ["Key"])
    current_values = current_values.set_index(current_values['Ticker'])
    starting_values = data[data['Date']==min(data['Date'])].reset_index(drop=True)
    current_wallet_value = current_values[current_values.index=='SUM']['Value'].iloc[0]
    starting_wallet_value = starting_values[starting_values['Ticker']=='SUM']['Value'].iloc[0]
    total_delta_pct = round(((current_wallet_value/starting_wallet_value)-1) * 100,2)

    comparison_date = col2.date_input("Date For comparison",
                                      value=min(data["Date"]),
                                      min_value=min(data['Date'].dt.date),
                                      max_value=max(data['Date'].dt.date,))
    reference_values = data[data['Date'].dt.date==comparison_date].reset_index(drop=True).drop(columns=['Key'])
    reference_values = reference_values.set_index(reference_values['Ticker'])
    reference_wallet_value = reference_values[reference_values.index=='SUM']['Value'].iloc[0]
    relative_delta_pct = round(((current_wallet_value/reference_wallet_value)-1) * 100,2)

    view_frame = current_values[current_values.index!='SUM'].drop(columns = ['Date']).sort_index()
    
    col1.metric("Current Value", f"£{current_wallet_value}",delta=f"{total_delta_pct}%")
    col1.metric("Current Net Profit",f"£{current_wallet_value-starting_wallet_value}")

    col2.metric(f"Value on {comparison_date}", f"£{reference_wallet_value}",delta=f"{relative_delta_pct}%")
    col2.metric("Net Profit Relative to Date",f"£{current_wallet_value-reference_wallet_value}")

    col1.divider()
    col1.subheader("Current Breakdown")
    st.dataframe(view_frame)

def wallet_over_time():
    all_data = get_data().sort_values(by=['Date','Ticker'])
    all_data['Value'] = all_data["Value"].astype('float')
    if 'options' not in st.session_state:
        st.session_state['options'] = ['ETH', 'BTC', 'SUM']

    items = st.multiselect('Tickers',all_data['Ticker'].unique(),key="options")

    filtered_data = all_data[all_data["Ticker"].isin(items)]
    st.line_chart(filtered_data,x='Date',y='Value',color='Ticker',use_container_width=True)


views = {
    "Wallet Snapshot": wallet_snapshot,
    "Wallet Value over Time": wallet_over_time

}

view_name = st.sidebar.selectbox("Select view",views.keys(),)
# scan, query, get item
if view_name is None:
    view_name = "Wallet Snapshot"
views[view_name]()