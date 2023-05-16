import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
from streamlit_option_menu import option_menu
# import yfinance as yf
import plotly.graph_objects as go
 
from stock_data import (
    download_nifty50_stock_list,
    create_random_portfolio,
    download_benchmark,
    calculate_asset_composition,
    Add_new_weight_to_portfolio
)

from stock_KIPs import (
     KPIs
)

from stock_optimizer import (
    PortfolioOptimizer
)



### Initial Variables
# stock_list = []
# Initialization





# If no, then initialize count to 0
# If count is already initialized, don't do anything
if 'count' not in st.session_state:
	st.session_state.count = 0

if 'portfolio' not in st.session_state:
	st.session_state.portfolio = []

if 'stock_data' not in st.session_state:
	st.session_state.stock_data = pd.DataFrame({})

if 'stock_list' not in st.session_state:
	st.session_state.stock_list = pd.DataFrame({})


portfolio = st.session_state.portfolio
stock_data = st.session_state.stock_data


# st.write(st.session_state.count)

with st.sidebar:
## --------------------------------------------------------GENERATE PROTFOLIO --------------------------------------------------------------
     with st.expander("Generate Random Protfolio"):
        
        # Define the date range for which you want to display market open dates
        
        col1 ,col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
            "Selecte Start Date",
            datetime.date(2007, 10, 6),
            max_value=datetime.date.today() - datetime.timedelta(days=7*30) ,
            min_value=datetime.date(2007,10,6)
            )

        with col2:
            end_date = st.date_input(
            "Selecte End Date",
             datetime.date(2008, 10, 6),
            max_value=datetime.date.today() - datetime.timedelta(days=30),
            min_value=datetime.date(2008,10,6)
            )

        data = pd.DataFrame({})
        if st.button('Generate Protfolio'):
            
                stock_list = download_nifty50_stock_list()
                
                stock_data,portfolio = create_random_portfolio(stock_list, start_date, end_date, max_portfolio_value=100000)
                st.session_state.count += 1
                st.session_state.portfolio = portfolio
                st.session_state.stock_data = stock_data
                st.session_state.stock_list = stock_list

                

                 
        


if st.session_state.count != 0:
        tab1, tab2, tab3,tab4 = st.tabs(["🗃 Portfolio Overview","Optimized Portfolio","Performance Comparison","📈 Backtesting"])
        ### Class For Calculate Imp Kpis 
        calculate_kpis = KPIs(stock_data=stock_data)
        ### Daily Log Calculation's
        daily_log_return = calculate_kpis.calculate_log_return()

        with tab1:
            col1,col2 = st.columns(2)
            ## Calculate initital & final Compossition of Assets 
            initial_portfolio = calculate_asset_composition(portfolio.copy(),values=stock_data.iloc[0].values)
            final_portfolio = calculate_asset_composition(portfolio.copy(),values=stock_data.iloc[-1].values)
            with col1:
                st.text('Initial Protfolio : ' + str(start_date))
                st.dataframe(initial_portfolio)
                ## Total Valuation of Portfolio At Beggining
                init_portfolio_inivestment = int(initial_portfolio['Value'].sum())
                col1.metric(label="Initial Investment Valuation", value=str(init_portfolio_inivestment))
                

            with col2:
                
                st.text('Current Protfolio : ' + str(end_date))
                st.dataframe(final_portfolio)
                ## Currently Total Valuation of Portfolio 
                final_portfolio_inivestment = int(final_portfolio['Value'].sum())

                total_return =  round((final_portfolio_inivestment - init_portfolio_inivestment) / init_portfolio_inivestment *100 ,2)      
        
                col2.metric("Current Investment Valuation",str(final_portfolio_inivestment) , str(total_return)+' %')

            st.write('The analysis of the risk and return between the '+ str(start_date)+' and ' + str(end_date) + ' reveals a significant imbalance, with a notably high level of risk and a comparatively low return. This observation underscores the inherent instability and volatility of our investment portfolio during this period. It emphasizes the need')
            st.dataframe(calculate_kpis.yearl_risk_return())
            
            ini_ret,int_vol,int_sharpe_ratio = calculate_kpis.get_ret_vol_sr(weights=initial_portfolio.Weight.values)
            st.write('Portfolio Return With initial Weight',round(ini_ret*100,2))
            st.write('Portfolio Risk With initial Weight',round(int_vol*100,2))
            st.write('Portfolio sharpe Ratio With initial Weight',round(int_sharpe_ratio,2))


        
       
                ## initial Weight's Of Assets 
        init_guess = initial_portfolio.Weight.values

        
        with tab2:
                #  if st.button('Optimize 0Portfolio'):

                     ### Run Optimizer
                     log_ret = daily_log_return.iloc[:,1:].copy()
                     optimizer = PortfolioOptimizer(log_ret)
                     opt_results = optimizer.optimize_portfolio(init_guess)
                     opt_ret,opt_vol,opt_sharpe_ratio = calculate_kpis.get_ret_vol_sr(weights=opt_results.x.round(2))

                     ### Optimize Weight
                     optimize_weight = opt_results.x
                     ### Initial Optimize Portfolio
                     optimize_initial_portfolio = Add_new_weight_to_portfolio(portfolio=initial_portfolio,weight=optimize_weight,total_investment=init_portfolio_inivestment)
                     ### Final Optimize Portfolio
                     optimize_final_portfolio = initial_portfolio.copy()
                     optimize_final_portfolio['Shares'] = optimize_initial_portfolio['Shares']
                     optimize_final_portfolio['Price'] = final_portfolio['Price']
                     optimize_final_portfolio['Value'] = optimize_final_portfolio['Shares'] * optimize_final_portfolio['Price']
                     optimize_final_portfolio['Weight'] = optimize_weight
                     st.subheader('Here is a comparison of how your portfolio would appear if the assets were allocated according to the new weights')

                     col1,col2 = st.columns(2)
                     with col1:
                          st.text('Optimized  Initial Protfolio : ' + str(start_date))
                          st.dataframe(optimize_initial_portfolio)
                          optimize_init_portfolio_inivestment = int(optimize_initial_portfolio['Value'].sum())
                          col1.metric(label="Optimize Initial Investment Valuation", value='{:,}'.format(optimize_init_portfolio_inivestment))

                     with col2:
                          st.text('Current Protfolio : ' + str(end_date))
                          st.dataframe(optimize_final_portfolio)
                          optimize_final_portfolio_inivestment = int(optimize_final_portfolio['Value'].sum())
                          optimize_total_return =  round((optimize_final_portfolio_inivestment - optimize_init_portfolio_inivestment) / optimize_init_portfolio_inivestment  *100 ,2)      
                          col2.metric("Current Investment Valuation",'{:,}'.format(optimize_final_portfolio_inivestment) , str(optimize_total_return)+' %')

                    #### Print optimal Weight Portfolio Return Risk And Sharpe Ratio
                     st.write('Portfolio Return With initial Weight',round(opt_ret*100,2))
                     st.write('Portfolio Risk With initial Weight',round(opt_vol*100,2))
                     st.write('Portfolio sharpe Ratio With initial Weight',round(opt_sharpe_ratio,2))

                     ### Use calculate_kpis class With calculate_portfolio_values to calculate Portfolio Valus for Given historical time with weight.
                     ## calculate portfolio value with original weight associated for given historical data
                     original_portfolio_value = calculate_kpis.calculate_portfolio_values(initial_portfolio=initial_portfolio,weight=init_guess)

                     ## Calculate portfolio value with optimize weight associated for given historical data
                     optimize_portfolio_value = calculate_kpis.calculate_portfolio_values(initial_portfolio=initial_portfolio,weight=optimize_weight)
                    
                    ## Merged Two Portfolio Values in to one with Coloums Date, Original Portfolio, Optimize Portfolio.  
                     merged_portfolio_value_df = pd.merge(original_portfolio_value, optimize_portfolio_value, on='Date', how='inner')
                    ## Rename Operation 
                     merged_portfolio_value_df = merged_portfolio_value_df.rename(columns={'Portfolio Value_x':'Original portfolio','Portfolio Value_y':'Optimize portfolio'})
                     with st.container():
                              # Create a figure object
                                fig = go.Figure()

                                # Add the Original Portfolio Line Plot  trace with a teal Color
                                fig.add_trace(go.Scatter(x=merged_portfolio_value_df['Date'], y=merged_portfolio_value_df['Original portfolio'], mode='lines', name='Original portfolio', line=dict(color='teal')))

                                # Add the Optimize Portfolio Line Plot  trace with a orange Color
                                fig.add_trace(go.Scatter(x=merged_portfolio_value_df['Date'], y=merged_portfolio_value_df['Optimize portfolio'], mode='lines', name='Optimize portfolio', line=dict(color='orange')))

                                # Customize the layout
                                fig.update_layout(title='Comparison of Original and Optimized Portfolio Values over Time', xaxis_title='Date', yaxis_title='Portfolio Values (Rupeess')

                                # Render the line chart in Streamlit
                                st.plotly_chart(fig)

                                st.write('By tracking the evolving values, we uncover patterns, trends, and divergences between the two portfolios. This analysis assesses if optimization strategies outperform the original portfolio, providing insights into their effectiveness. Examining the original portfolio helps understand its historical growth and fluctuations, serving as a benchmark for evaluating the optimized version.')
                                # st.dataframe(merged_portfolio_value_df)
                                
                                # st.line_chart(data=merged_portfolio_value_df, x='Date', y=['Original portfolio','Optimize portfolio'])
                     



                     

        with tab3:
            st.write('Tab 2')
            

        
