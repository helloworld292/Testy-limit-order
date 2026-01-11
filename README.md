# Instructions on usage
People place limit orders by using a Limit order csv file such as "Limit_order_A" in the format of:

Date(YYYY-MM-DD),Action(buy/sell),TriggerPrice,Number of units,Ticker,Status

The program will check for whether the limit order is executed, and if it is, automatically place a market order in a similar format as hku-cim-trades. Which is something like this:

Date(YYYY-MM-DD),Action(buy/sell),Number of units,Ticker

This is to make it easier for my program to be merged with the main system as this basically mimics the current process of placing a market order

The "status" of the limit order will then be changed to completed and the history of such a automatic order will also be added into changelog. The chnagelog is there to help verify what orders are executed in case there are any situations where the program is buggy and placed some wrong orders.

To add CSV files to be processed, it must be added to the two lists at the very start of the program (make sure the index is matching). It also has to be added in the Github actions program under "Commit and push changes" to make sure any changes made by the limit order program is properly saved and updated.

The current available order types:

buy(l):

Is the limit buy order, if price drops below trigger price then the selected number of stocks will be bought automactically. Compare with prev day low

sell(l):

Is the limit sell order, if price reaches above the trigger price then the selected number of stocks will be sold automatically. Compare with prev day high

stoploss:

Is the stoploss order, is prices reach below the trigger price, then the number of stocks selected will be sold automatically. Compare with prev day low

stopbuy:

Is the stop buy order, if prices reach above the trigger price, then the number of stocks selected will be bought automatically. Compare with prev day high

Notes:
1. Currently, the program has yet to be tested properly so may have a low tolerenance for user input error and any formats that are non-standard will likely result in a order just being skipped. Please follow the proper expected formatting requirements
2. The program executes at 11am (hkt) everyday and checks for yesterday's prices. This is to ensure that yfinance has all the data for all the markets around the world. 

