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

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
#ignore sundays and saturdays
    if yesterday.weekday() == 6 or yesterday.weekday() == 5:
        continue
    
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')

#dates for showcase
    #today_str = "2026-01-16"
    #yesterday_str = "2026-01-15"

    if os.path.exists(LIMIT_ORDER_FILE):
        df_orders = pd.read_csv(LIMIT_ORDER_FILE)
    else:
        print("No stop/limit file found.")
        continue

    if os.path.exists(BUY_SELL_FILE):
        df_buy_sell = pd.read_csv(BUY_SELL_FILE)
    else:
        df_buy_sell = pd.DataFrame(columns=['Date(YYYY-MM-DD)', 'Action(buy/sell)', 'Number of units', 'Ticker','Price'])

    if os.path.exists(CHANGELOG):
        changelog = pd.read_csv(CHANGELOG)
    else:
        changelog = pd.DataFrame(columns=['Date','Action'])
    print(changelog)

    #strip whitespace & change to str
    df_orders.columns = df_orders.columns.str.strip()

    #Actual Order handling
    for index, row in df_orders.iterrows():
        #Check if the order is already complete
        if df_orders.loc[index,'Status'] == 'Complete':
            continue

        #Check if order date is valid
        if df_orders.loc[index, 'Date(YYYY-MM-DD)'] >= yesterday_str:
            continue
        
        # Fetch yesterday's high and low
        try:
            stock_data = yf.download(row['Ticker'], start=yesterday_str, end=today_str)
            if stock_data.empty:
                print(f"No data for {row['Ticker']}. Skipping.")
                continue
            high_price = stock_data['High'].iloc[0].values[0]
            low_price = stock_data['Low'].iloc[0].values[0]
            open_price = stock_data['Open'].iloc[0].values[0]
        except Exception as e:
            print(f"Error fetching {row['Ticker']}: {e}. Skipping.")
            continue
        
        # Determine if triggered
        #LIMIT ORDERS
        triggered = False
        if row['Action(lb/ls/sl/sb)'].lower().strip() == 'limitbuy' and low_price <= row['TriggerPrice']:
            triggered = True
        elif row['Action(lb/ls/sl/sb)'].lower().strip() == 'limitsell' and high_price >= row['TriggerPrice']:
            triggered = True
        
        #STOP LOSS AND STOP BUY
        elif row['Action(lb/ls/sl/sb)'].lower().strip() == 'stoploss' and low_price <= row['TriggerPrice']:
            triggered = True
        elif row['Action(lb/ls/sl/sb)'].lower().strip() == 'stopbuy' and high_price >= row['TriggerPrice']:
            triggered = True

        if triggered:
        # Complete the order
            df_orders.loc[index,'Status'] = 'Complete'

        #Figure out correct price and action
            if row['Action(lb/ls/sl/sb)'].lower().strip() == 'limitbuy':
                Executed_action = 'buy'
                if row['TriggerPrice'] >= open_price:
                    Executed_price = open_price
                elif row['TriggerPrice'] <= open_price and row['TriggerPrice'] >= low_price:
                    Executed_price = float(row['TriggerPrice'])
            
            elif row['Action(lb/ls/sl/sb)'].lower().strip() == 'limitsell':
                Executed_action = 'sell'
                if row['TriggerPrice'] <= open_price:
                    Executed_price = open_price
                elif row['TriggerPrice'] >= open_price and row['TriggerPrice'] <= high_price:
                    Executed_price = float(row['TriggerPrice'])
                
            elif row['Action(lb/ls/sl/sb)'].lower().strip() == 'stoploss':
                Executed_action = 'sell'
                if row['TriggerPrice'] >= open_price:
                    Executed_price = open_price
                elif row['TriggerPrice'] <= open_price and row['TriggerPrice'] >= low_price:
                    Executed_price = float(row['TriggerPrice'])
            
            elif row['Action(lb/ls/sl/sb)'].lower().strip() == 'stopbuy':
                Executed_action = 'buy'
                if row['TriggerPrice'] <= open_price:
                    Executed_price = open_price
                elif row['TriggerPrice'] >= open_price and row['TriggerPrice'] <= high_price:
                    Executed_price = float(row['TriggerPrice'])

        # Append to buy/sell
            new_row_limit_order = {
                'Date(YYYY-MM-DD)': yesterday_str,
                'Action(buy/sell)': Executed_action,
                'Number of units': int(row['Number of units']),
                'Ticker': row['Ticker'],
                'Price': Executed_price
            }
            df_buy_sell = pd.concat([df_buy_sell, pd.DataFrame([new_row_limit_order])], ignore_index=True)
            print(f"Triggered and added: {new_row_limit_order}")

            new_row_changelog = {
                'Date':yesterday_str,
                'Action': f'Triggered and added {new_row_limit_order}'
            }
            changelog = pd.concat([changelog, pd.DataFrame([new_row_changelog])], ignore_index=True)

    #Save updated into to CSVs        
    df_orders.to_csv(LIMIT_ORDER_FILE, index = False)
    df_buy_sell.to_csv(BUY_SELL_FILE, index=False)
    changelog.to_csv(CHANGELOG, index = False)