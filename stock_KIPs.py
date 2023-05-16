### Calculate important Kpi Analysis & Optimization
import numpy as np
import pandas as pd


##### Suggest Need For ortfolio Optimizer or not
# def suggest_portfolio_optimization(kpi_values):
#     if kpi_values["Sharpe Ratio"] < 1 or kpi_values["Sortino Ratio"] < 1:
#         return "Portfolio Optimization Recommended: Consider rebalancing the portfolio, reallocating assets, or exploring alternative investment options to improve risk-adjusted returns."

#     else:
#         return "Portfolio Optimization Not Required: The portfolio is performing well based on the provided KPIs."

# # Example usage

# kpi_values = {"Sharpe Ratio": 1.8, "Sortino Ratio": 1.2}  # Placeholder values for illustration

# suggested_optimization = suggest_portfolio_optimization(kpi_values)

# print("Suggested Strategy:", suggested_strategy)
# print("Optimization Recommendation:", suggested_optimization)







class KPIs:
    def __init__(self, stock_data):
        self.stock_data = stock_data
    
    def calculate_log_return(self):
        close_prices = self.stock_data
        ### Calulate Logarithmic return of Stock historical Data 
        self.log_returns = np.log(close_prices / close_prices.shift(1)).reset_index()
        ### Drop First Row
        self.log_returns = self.log_returns.drop(index=0)
        return self.log_returns
    
    ### Function to Calculate Portfolio Return Volatile and Sharpe Ratio by giving the weights allocation
    def get_ret_vol_sr(self, weights):
        weights = np.array(weights)
        log_ret = self.log_returns.iloc[:,1:]
        ret = np.sum(np.mean(log_ret, axis=0) * weights) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(np.cov(log_ret, rowvar=False) * 252, weights)))
        sr = ret / vol
        return np.array([ret, vol, sr])

    def yearl_risk_return(self):
        data = self.stock_data.copy()
        ## Convert Data index = Date to -> Datetime Formate
        data.index = pd.to_datetime(data.index)
        ## Rearrange entire data by only Yeard
        stock_yearly_exp_return = data.resample('Y').last().pct_change().mean()
        ## Clculate Standar deviation of daily log return and multipy with sqrt(number of trading days) which qives us yearly stock volatile
        stock_yearly_volatile = np.std(self.log_returns.iloc[:,1:])  * np.sqrt(250 ) 
        ## Create a Data frame of assets returns and risk and entire portfolio return ans risk
        assets = pd.concat([stock_yearly_exp_return, stock_yearly_volatile], axis=1)
        assets.columns = ['Returns', 'Volatility']
        assets = assets*100
        return assets
    
    ### Function To Calculatee Historical Valus of Portfolio with respect to weight associated with it
    def calculate_portfolio_values(self,initial_portfolio,weight):
        hist_data = self.stock_data
        total_value = initial_portfolio.Value.sum()
        total_share = round((total_value * weight) / initial_portfolio.Price)
        portfolio_hist_value = (hist_data*total_share.values).sum(axis=1).reset_index().rename(columns={0:'Portfolio Value'})
        return portfolio_hist_value
        return assets