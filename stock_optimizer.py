####### Funtion Requried For Optimizing Portfolio #################################################################

## --> For get_ret_vol_sr(weight) Function
# 1) log_return
# 2) weights
from scipy.optimize import minimize
import numpy as np
import streamlit as st


### Class Which Optimize Portfolio
class PortfolioOptimizer:
    def __init__(self, log_returns):
        self.log_returns = log_returns
    
    def get_ret_vol_sr(self, weights):
        weights = np.array(weights)
        ret = np.sum(np.mean(self.log_returns, axis=0) * weights) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(np.cov(self.log_returns, rowvar=False) * 252, weights)))
        sr = ret / vol
        return np.array([ret, vol, sr])
    
    def neg_sharpe(self, weights,log_returns):
        return self.get_ret_vol_sr(weights)[2] * -1
    
    def check_sum(self, weights):
        return np.sum(weights) - 1
    
    def optimize_portfolio(self, weights):
        cons = {'type': 'eq', 'fun': self.check_sum}
        bounds = [(0, 1) for _ in range(len(weights))]
        
        opt_results = minimize(self.neg_sharpe, weights, method='SLSQP', args=(self.log_returns,), bounds=bounds, constraints=cons)
        return opt_results
