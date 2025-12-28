# Instructions on usage
People place limit orders by using a Limit order csv file such as "Limit_order_A" in the format of:

Date(YYYY-MM-DD),Action(buy/sell),TriggerPrice,Number of units,Ticker,Status

The program will check for whether the limit order is executed, and if it is, automatically place a market order in a similar format as hku-cim-trades. Which is something like this:

Date(YYYY-MM-DD),Action(buy/sell),Number of units,Ticker

This is to make it easier for my program to be merged with the main system as this basically mimics the current process of placing a market order

The "status" of the limit order will then be changed to completed and the history of such a automatic order will also be added into changelog. The chnagelog is there to help verify what orders are executed in case there are any situations where the program is buggy and placed some wrong orders.

To add CSV files to be processed, it must be added to the two lists at the very start of the program (make sure the index is matching). It also has to be added in the Github actions program under "Commit and push changes" to make sure any changes made by the limit order program is properly saved and updated.


Notes:
1. Currently, the program has a very low tolerenance for user input error and any formats that are non-standard will likely result in a order just being skipped. (e.g. using "buy" instead of "Buy") This can easily be fixed if this presents itself as a frequent problem.
2. yfinance is in local currency (some currency change may be necesary depending on how the main portfolio program handles currency)
3. The program executes at 9am (hkt) everyday and checks for yesterday's prices. This is to ensure that yfinance has all the data for all the markets around the world. So technically the program is a day late but as it executes at 9am, which is quite early in the morning, hopefully it will basically be the same as executing on the same day. Changing it to execute on the same day should be possible but requires further research and testing.
4. Sundays will output an error while Saturdays will automatically be checking for Friday prices. Currently, the program converts both Saturday and Sunday orders to Friday orders, so there might be situations where teams place time travelling orders (i.e. place limit order on sat/sun to execute on Friday prices). I personally do not think this will be that big of an issue as this is basically just like a market order but the program can be changed to skip executing on sat and sun entirely.
