import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data 
def download_nifty50_stock_list():
    ## Wikipedia Link to Extract Data for Nifty 50
    url = 'https://en.wikipedia.org/wiki/NIFTY_50#Constituent_stocks'
    ## Selecting Table from URL
    stock_table = pd.read_html(url)[2]
    ## Adding .NS TO Nifty 50['SymbolS']
    stock_symbols = stock_table['Symbol']+ '.NS'
    ## Converting and Assigning in list formate to stock_symbol 
    stock_symbols = stock_symbols.tolist()
    return stock_symbols


## Create Personal Portfolio With HandPicked Stock
def create_personal_portfolio(stocks, shares,start_date, end_date):
    # Download stock data for the selected stocks
    stock_data = yf.download(list(stocks), start=start_date, end=end_date)['Adj Close']

    # Remove stocks with any null values
    stock_data = stock_data.dropna(axis=1)
    stock_list = []
    share_list = []
    for i, stock in enumerate(stocks):
        if shares[i] > 0 and stock in stock_data.keys():
            stock_list.append(stock)
            share_list.append(shares[i])
            # portfolio[stock] = shares[i]

    portfolio = pd.DataFrame({'Symbol': stock_list,
                              'Shares': share_list}
                             )
    
    # portfolio = pd.DataFrame(portfolio)
    return stock_data,portfolio

#### Generate Random Portfolio
# @st.cache_data 
def create_random_portfolio(list_stocks, start_date, end_date, max_portfolio_value=20000):
    """
    Create a random portfolio of stocks if list of stock is given .
    The portfolio will not contain any null values in any column for the selected stocks.
    The allocation of shares to each asset will be random, with the total value of the portfolio not exceeding the specified maximum.

    Parameters:
    -----------
    sp500_stocks : list
        A list of stock tickers in the S&P 500 index.

    start_date : str
        The start date of the portfolio.

    end_date : str
        The end date of the portfolio.

    max_portfolio_value : float, optional (default=100000)
        The maximum value of the portfolio.

    Returns:
    --------
    portfolio : pandas.DataFrame
        A DataFrame containing the selected stocks and the allocated number of shares for each stock.
    """

    # Select a random number of stocks from the Stock List list
    num_stocks = np.random.randint(4,10)
    selected_stocks = np.random.choice(list_stocks, size=num_stocks, replace=False)

    # Download stock data for the selected stocks
    stock_data = yf.download(list(selected_stocks), start=start_date, end=end_date)['Adj Close']

    # Remove stocks with any null values
    stock_data = stock_data.dropna(axis=1)

    # Get the list of valid stock tickers
    valid_tickers = stock_data.columns.tolist()

    # Generate random allocations
    allocations = np.random.random(len(valid_tickers))
    allocations /= np.sum(allocations)

    # Calculate the maximum number of shares for each stock to limit the total portfolio value
    stock_prices = stock_data.iloc[0]  # Use the end date prices
    max_shares = (max_portfolio_value * allocations) // stock_prices
    max_shares = max_shares.astype(int)

    # Create the portfolio DataFrame
    portfolio = pd.DataFrame({'Symbol': valid_tickers,
                              'Shares': np.random.randint(10, max_shares + 20)}
    )

    return stock_data,portfolio

@st.cache_data
def download_benchmark(start_date,end_date,sym='^NSEI'):
        benchmark = yf.download(sym,start=start_date,end=end_date)['Adj Close']
        return benchmark

def calculate_asset_composition(portfolio,values):

    """
    Calculate the weight of each stock in the portfolio.

    Parameters:
    -----------
    portfolio : pandas.DataFrame
        DataFrame containing Symbol, Price, and Shares.
    value : 

    Returns:
    --------
    weights : pandas.DataFrame
        DataFrame containing stock symbols and their corresponding weights.
    """
    ## Add Price Coloum to portfolio 
    portfolio['Price'] = values
    # Calculate the value of each stock (price * shares)
    portfolio['Value'] = portfolio['Price'] * portfolio['Shares']

    # Calculate the total portfolio value
    total_value = portfolio['Value'].sum()

    # Calculate the weight of each stock
    portfolio['Weight'] = portfolio['Value'] / total_value



    return portfolio




def Add_new_weight_to_portfolio(portfolio,weight,total_investment):
         temp_port = portfolio.copy()
         temp_port['Weight'] = weight
         temp_port['Value'] = total_investment*temp_port['Weight']
         temp_port['Shares'] = round(temp_port['Value'] / temp_port['Price'])        
         return temp_port   
