import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

Actual_order_list = ['Within_PC_test/Actual_Orders_lists_A.csv','Within_PC_test/Actual_Orders_lists_B.csv']
Limit_order_list = ['Within_PC_test/Limit_order_A.csv','Within_PC_test/Limit_order_B.csv']

for i in range(2):
    LIMIT_ORDER_FILE = Limit_order_list[i]
    BUY_SELL_FILE = Actual_order_list[i]
    CHANGELOG = 'Within_PC_test/Changelog.csv'

    #today = datetime.now().date()
    #today_str = today.strftime('%Y-%m-%d')

    today_str = "2025-12-18"
    yesterday_str = '2025-12-17'

    if os.path.exists(LIMIT_ORDER_FILE):
        df_orders = pd.read_csv(LIMIT_ORDER_FILE)
    else:
        print("No stop/limit file found. Exiting.")
        exit(0)

    if os.path.exists(BUY_SELL_FILE):
        df_buy_sell = pd.read_csv(BUY_SELL_FILE)
    else:
        df_buy_sell = pd.DataFrame(columns=['Date', 'Action', 'Number of units', 'Ticker'])

    if os.path.exists(CHANGELOG):
        changelog = pd.read_csv(CHANGELOG)
    else:
        changelog = pd.DataFrame(columns=['Date','Action'])
    print(changelog)


    for index, row in df_orders.iterrows():
        #Check if the order is already complete
        if df_orders.loc[index,'Status'] == 'Complete':
            continue
        
        # Fetch yesterday's high and low
        try:
            stock_data = yf.download(row['Ticker'], start=yesterday_str, end=today_str)
            if stock_data.empty:
                print(f"No data for {row['Ticker']}. Skipping.")
                continue
            high_price = stock_data['High'].iloc[0].values[0]
            low_price = stock_data['Low'].iloc[0].values[0]
        except Exception as e:
            print(f"Error fetching {row['Ticker']}: {e}. Skipping.")
            continue
        
        # Determine if triggered
        triggered = False
        if row['Action(buy/sell)'] == 'Buy' and low_price <= row['TriggerPrice']:
            triggered = True
        elif row['Action(buy/sell)'] == 'Sell' and high_price >= row['TriggerPrice']:
            triggered = True
            
        if triggered:
        # Complete the order
            df_orders.loc[index,'Status'] = 'Complete'
        
        # Append to buy/sell
            new_row_limit_order = {
                'Date(YYYY-MM-DD)': today_str,
                'Action(buy/sell)': row['Action(buy/sell)'],
                'Number of units': int(row['Number of units']),
                'Ticker': row['Ticker']
            }
            df_buy_sell = pd.concat([df_buy_sell, pd.DataFrame([new_row_limit_order])], ignore_index=True)
            print(f"Triggered and added: {new_row_limit_order}")

            new_row_changelog = {
                'Date':today_str,
                'Action': f'Triggered and added {new_row_limit_order}'
            }
            changelog = pd.concat([changelog, pd.DataFrame([new_row_changelog])], ignore_index=True)

    #Save updated into to CSVs        
    df_orders.to_csv(LIMIT_ORDER_FILE, index = False)
    df_buy_sell.to_csv(BUY_SELL_FILE, index=False)
    changelog.to_csv(CHANGELOG, index = False)