# Import the necessary libraries
import os
import time
import logging
import datetime as dt
from threading import Thread
import create_database as cd
import strategy as stra
import trading_functions as tf
import setup_functions as sf
import setup_for_download_data as sdd
from setup import trading_app

now_ = dt.datetime.now()

# Set the month string to save the log file
if now_.month < 10:
    month = '0'+str(now_.month)
else:
    month = now_.month
# Set the day string to save the log file
if now_.day < 10:
    day = '0'+str(now_.day)
else:
    day = now_.day
# Set the hour string to save the log file
if now_.hour < 10:
    hour = '0'+str(now_.hour)
else:
    hour = now_.hour
# Set the minute string to save the log file
if now_.minute < 10:
    minute = '0'+str(now_.minute)
else:
    minute = now_.minute
# Set the second string to save the log file
if now_.second < 10:
    second = '0'+str(now_.second)
else:
    second = now_.second

# Save all the trading app info in the following log file
logging.basicConfig(filename=f'data/log/log_file_{now_.year}_{month}_{day}_{hour}_{minute}_{second}.log',
                    level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Function to run the app each period
def run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, 
            historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
            trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window):
    
    print('='*100)
    print('='*100)
    print('='*100)
    logging.info('='*100)
    logging.info('='*100)

    print('Running the app...wish you the best!')
    logging.info('Running the app...wish you the best!')

    # Get the previous, current and next trading periods
    previous_period, current_period, next_period = tf.get_the_closest_periods(dt.datetime.now(), data_frequency, trading_day_end_datetime, previous_day_start_datetime, day_start_datetime, market_close_time)
    
    # A while loop to run the app, we will break the loop whenever we finish running the app for the current period
    while True:
        # Create an object of the app class
        app = trading_app(logging, account, account_currency, symbol, timezone, data_frequency, historical_data_address, base_df_address, leverage, 
                          risk_management_target, stop_loss_multiplier, take_profit_multiplier, purged_window_size, embargo_period, market_open_time, market_close_time, 
                          previous_day_start_datetime, trading_day_end_datetime, day_end_datetime, current_period, previous_period, next_period, train_span, test_span, max_window)
                
        # Connect the app to the IB server
        print('Connecting the app to the IB server...')
        logging.info('Connecting the app to the IB server...')
        app.connect(host=host, port=port, clientId=client_id)
        
        # Set the app thread as the main one
        thread1 = Thread(target=app.run, daemon=True)
    
        # Start the app
        thread1.start()
            
        # Wait until the app is successfully connected
        time.sleep(5)
        
        print('='*100)
        print(f'Current period is {current_period}')
        logging.info(f'Current period is {current_period}')
        print(f'Trading day end datetime is {trading_day_end_datetime}')
        logging.info(f'Trading day end datetime is {trading_day_end_datetime}')
        print('='*100)
        
        # If now is before the market close datetime
        if dt.datetime.now() < market_close_time:
    
            # If now is before the trading day end datetime
            if dt.datetime.now() < trading_day_end_datetime:
                
                # If the current period hasn't been traded
                if app.periods_traded.loc[app.periods_traded['trade_time']==current_period]['trade_done'].values[0] == 0:
                    
                    # If the strategy time spent is filled
                    if app.previous_time_spent > 0:
                        if app.previous_time_spent >= (next_period - current_period).total_seconds():
                            app.previous_time_spent = 60
                        # If the previous time spent is less than the seconds left until the next trading period
                        if app.previous_time_spent < (next_period - dt.datetime.now()).total_seconds():
                            # Run the strategy, create the signal, and send orders if necessary
                            sf.run_strategy_for_the_period(app)
                            # If the strategy was successfully done
                            if app.strategy_end:
                                # Wait until we arrive at the next trading period
                                time.sleep(0 if (next_period-dt.datetime.now()).total_seconds()<0 else (next_period-dt.datetime.now()).total_seconds())
                                break
                            else:
                                # Couldn't connect to IB server, we'll try once again
                                print("Couldn't connect to the IB server, could be due to internet issues or the TWS/IB Gateway is not opened...")
                                logging.info("Couldn't connect to the IB server, could be due to internet issues or the TWS/IB Gateway is not opened...")
                        else:
                            print("Time up to the next period is not sufficient to run the strategy for the current period...")
                            logging.info("Time up to the next period is not sufficient to run the strategy for the current period...")
                            # Wait until we arrive at the next trading period
                            sf.wait_for_next_period(app)
                            time.sleep(0 if (next_period-dt.datetime.now()).total_seconds()<0 else (next_period-dt.datetime.now()).total_seconds())
                            break
                      
                    # If the strategy time spent is not fille, i.e., it's the first time we trade
                    else:
                        # Run the strategy, create the signal, and send orders if necessary
                        sf.run_strategy_for_the_period(app)
                        # If the strategy was successfully done
                        if app.strategy_end:
                            # Wait until we arrive at the next trading period
                            time.sleep(0 if (next_period-dt.datetime.now()).total_seconds()<0 else (next_period-dt.datetime.now()).total_seconds())
                            break
                        else:
                            # Couldn't connect to IB server, we'll try once again
                            print("Couldn't connect to the IB server, could be due to internet issues or the TWS/IB Gateway is not opened...")
                            logging.info("Couldn't connect to the IB server, could be due to internet issues or the TWS/IB Gateway is not opened...")
                
                # If the current period has already been traded
                else:
                    print("The current period has already been traded. Let's wait for the next period...")
                    logging.info("The current period has already been traded. Let's wait for the next period...")
                    # Wait until we arrive at the next trading period
                    sf.wait_for_next_period(app)
                    break
            # If now is after the trading day end datetime
            else:
                print("The trading end datetime has arrived. Let's close the existing position if exists and update the trading info...")
                logging.info("The trading end datetime has arrived. Let's close the existing position if exists and update the trading info...")
                # If the current period hasn't been traded
                if app.periods_traded.loc[app.periods_traded['trade_time']==trading_day_end_datetime]['trade_done'].values[0] == 0:
                    # Update the trading information and close the position if needed before the market closes
                    sf.update_and_close_positions(app)
                else:
                    print("The last position was already closed and the trading info was already updated...")
                    logging.info("The last position was already closed and the trading info was already updated...")
                    
                # Wait until we arrive at the next trading period
                print("Let's wait until the new trading day begins...")
                logging.info("Let's wait until the new trading day begins...")
                time.sleep(0 if (day_start_datetime-dt.datetime.now()).total_seconds()<0 else (day_start_datetime-dt.datetime.now()).total_seconds())
                break
        # If now is after the market close datetime
        else:   
            print('The market has closed...')       
            logging.info('The market has closed...')       
            break
                
# Run the trading all inside a loop for the whole week                        
def run_trading_setup_loop(host, port, account, client_id, data_frequency, london_start_hour, local_restart_hour, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, 
                         historical_data_address, base_df_address, purged_window_size, embargo_period, train_span, test_span, max_window):  
                  
    print('='*100)
    print('='*100)
    print('='*100)
    logging.info('='*100)
    logging.info('='*100)
    logging.info('='*100)

    # Get the local timezone hours that match the Easter timezone hours
    restart_hour, restart_minute, day_end_hour, day_end_minute, trading_start_hour = tf.get_end_hours(timezone, london_start_hour, local_restart_hour)
    # Get the market open and close datetimes of the current week
    market_open_time, market_close_time = tf.define_trading_week(timezone, trading_start_hour, day_end_minute)
    
    # Get the corresponding auto-restart and day-end datetimes to be used while trading
    auto_restart_start_datetime, auto_restart_datetime_before_end, auto_restart_end_datetime, \
        day_start_datetime, day_datetime_before_end, trading_day_end_datetime, day_end_datetime, previous_day_start_datetime = \
            tf.get_restart_and_day_close_datetimes(data_frequency, dt.datetime.now(), day_end_hour, day_end_minute, restart_hour, restart_minute, trading_start_hour)

    print(f'market open time is {market_open_time}')
    logging.info(f'market open time is {market_open_time}')
    print(f'market close time is {market_close_time}')
    logging.info(f'market close time is {market_close_time}')
    
    print(f'\t - auto_restart_start_datetime is {auto_restart_start_datetime}')
    logging.info(f'\t - auto_restart_start_datetime is {auto_restart_start_datetime}')
    print(f'\t - auto_restart_datetime_before_end is {auto_restart_datetime_before_end}')
    logging.info(f'\t - auto_restart_datetime_before_end is {auto_restart_datetime_before_end}')
    print(f'\t - auto_restart_end_datetime is {auto_restart_end_datetime}')
    logging.info(f'\t - auto_restart_end_datetime is {auto_restart_end_datetime}')
    if dt.datetime.now()>=market_open_time:
       print(f'\t - previous_day_start_datetime is {previous_day_start_datetime}')
       logging.info(f'\t - previous_day_start_datetime is {previous_day_start_datetime}')
    print(f'\t - day_datetime_before_end is {day_datetime_before_end}')
    logging.info(f'\t - day_datetime_before_end is {day_datetime_before_end}')
    print(f'\t - trading_day_end_datetime is {trading_day_end_datetime}')
    logging.info(f'\t - trading_day_end_datetime is {trading_day_end_datetime}')
    print(f'\t - day_end_datetime is {day_end_datetime}')
    logging.info(f'\t - day_end_datetime is {day_end_datetime}')
    print(f'\t - day_start_datetime is {day_start_datetime}')
    logging.info(f'\t - day_start_datetime is {day_start_datetime}')

    # Check if now is sooner than the market opening datetime
    if dt.datetime.now() < market_open_time:
        print("Let's wait until the market opens...")
        logging.info("Let's wait until the market opens...")
        # If we are outside the week's market hours, we wait until we're in
        while dt.datetime.now() <= market_open_time: continue
    
    # Check if now is sooner than the day start datetime
    if dt.datetime.now() < previous_day_start_datetime:
        print("Let's wait until the trading day starts...")
        logging.info("Let's wait until the trading day starts...")
        # Start trading at the trading start datetime
        while dt.datetime.now() <= previous_day_start_datetime: continue
        
    # If we're inside the week's market hours
    while dt.datetime.now() >= market_open_time and dt.datetime.now() <= market_close_time:
        # Get the local timezone hours that match the Easter timezone hours
        restart_hour, restart_minute, day_end_hour, day_end_minute, trading_start_hour = tf.get_end_hours(timezone, london_start_hour, local_restart_hour)
        
        # Get the corresponding autorestart and day-end datetimes to be used while trading
        auto_restart_start_datetime, auto_restart_datetime_before_end, auto_restart_end_datetime, \
            day_start_datetime, day_datetime_before_end, trading_day_end_datetime, day_end_datetime, previous_day_start_datetime = \
                tf.get_restart_and_day_close_datetimes(data_frequency, dt.datetime.now(), day_end_hour, day_end_minute, restart_hour, restart_minute, trading_start_hour)
                
        # Set the highest hour
        highest_hour = restart_hour if restart_hour > day_end_hour else day_end_hour
        
        # Set the highest minute
        highest_minute = auto_restart_datetime_before_end.minute if highest_hour == restart_hour else day_end_datetime.minute
    
        # If now is sooner than the last day and the auto-restart hour
        if ((dt.datetime.now().weekday() <= (market_close_time.weekday()-1)) and (dt.datetime.now().hour < highest_hour) \
            and (dt.datetime.now().minute < highest_minute)): 
            
            # If the auto-restart datetime is sooner than the day start datetime
            if auto_restart_datetime_before_end < day_start_datetime:
                # A while loop to run the app
                while True:
                    # If now is less than the autorestart datetime
                    if (dt.datetime.now() < auto_restart_datetime_before_end):
                        # Run the app
                        run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
                                    trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window)
                    # If now is higher than the auto-restart datetime
                    else:
                        # Break the while loop
                        break
                # Wait until now is higher than auto-restart start datetime
                while (dt.datetime.now() >= auto_restart_datetime_before_end) and (dt.datetime.now() < auto_restart_start_datetime): continue
            # If the autorestart datetime is later than the day start datetime
            else:
                # A while loop to run the app
                while True:                
                    # If now is sooner than the day datetime before the day closes
                    if (dt.datetime.now() < day_datetime_before_end):
                        # Run the app
                        run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
                                    trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window)
                    # If now is later than the day datetime before the day closes
                    else:
                        # Break the while loop
                        break
                        
                # A while loop to run the app
                while True:                
                    # If now is later than the day datetime before the day closes and sooner than the trading day end datetime
                    if (dt.datetime.now() >= day_datetime_before_end) and (dt.datetime.now() < trading_day_end_datetime):
                        # Run the app
                        run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
                                    trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window)
                    # If now is later than the trading day end datetime
                    else:
                        # Break the while loop
                        break
                # A while loop to run the app
                while True:                
                    # If now is later than the trading day end datetime and sooner than the day end datetime
                    if (dt.datetime.now() >= trading_day_end_datetime) and (dt.datetime.now() < day_end_datetime):
                        # Run the app
                        run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
                                    trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window)
                    # If now is later than the day-end datetime
                    else:
                        # Break the while loop
                        break
                                        
                print("Let's wait until we start the trading day once again")
                logging.info("Let's wait until we start the trading day once again")
                while (dt.datetime.now() >= day_end_datetime) and (dt.datetime.now() < day_start_datetime): continue
            
        # If now is last day and later than the auto-restart hour                                                                                
        else:
            
            # A while loop to run the app
            while True:                
                # If now is sooner than the day datetime before the day closes
                if (dt.datetime.now() <= day_datetime_before_end):
                    # Run the app
                    run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
                            trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window)
                # If now is later than the day datetime before the day closes
                else:
                    # Break the while loop
                    break
            # A while loop to run the app
            while True:                
                # If now is later than the day datetime before the day closes and sooner than the trading day end datetime
                if (dt.datetime.now() >= day_datetime_before_end) and (dt.datetime.now() < trading_day_end_datetime): 
                    # Run the app
                    run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
                            trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window)
                # If now is later than the trading day end datetime
                else:
                    # Break the while loop
                    break
            # A while loop to run the app
            while True:                
                # If now is later than the trading day end datetime and sooner than the day end datetime
                if (dt.datetime.now() >= trading_day_end_datetime) and (dt.datetime.now() < day_end_datetime):
                    # Run the app
                    run_app(host, port, account, client_id, timezone, now_, account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, historical_data_address, base_df_address, data_frequency, purged_window_size, embargo_period, 
                            trading_day_end_datetime, day_end_datetime, previous_day_start_datetime, day_start_datetime, market_open_time, market_close_time, train_span, test_span, max_window)
                # If now is later than the day-end datetime
                else:
                    # Break the while loop
                    break
                                        
            print("Let's wait until the trading week close datetime arrives")
            logging.info("Let's wait until the trading week close datetime arrives")
            while (dt.datetime.now() >= day_end_datetime) and (dt.datetime.now() < day_start_datetime): continue
    
# A main function to run everything
def main(account, timezone, port, account_currency, symbol, data_frequency, local_restart_hour, historical_data_address, base_df_address, train_span, test_span_days, 
         max_window, host, client_id, purged_window_size, embargo_period, seed, random_seeds, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, smtp_username, to_email, password):   
     
    # Set the London-timezone hour as the trading start hour
    london_start_hour = 23
    
    # The historical minute-frequency data address
    historical_minute_data_address = f'data/app_{symbol}_df.csv'
        
    # Set the test span
    test_span = test_span_days*tf.get_periods_per_day(data_frequency)
    
    # Add the test span value to the train span
    train_span += test_span
    
    # Get the local timezone hours that match the Easter timezone hours
    restart_hour, restart_minute, day_end_hour, day_end_minute, trading_start_hour = tf.get_end_hours(timezone, london_start_hour, local_restart_hour)
    
    # Get the market open and close datetimes of the current week
    market_open_time, market_close_time = tf.define_trading_week(timezone, trading_start_hour, day_end_minute)
    
    month_string = str(market_open_time.month) if market_open_time.month>=10 else '0'+str(market_open_time.month)
    day_string = str(market_open_time.day-1) if (market_open_time.day-1)>=10 else '0'+str(market_open_time.day-1)

    # If you don't have historical minute-frequency data
    if os.path.exists(historical_minute_data_address)==False:
        print('='*100)
        print('='*100)
        print('='*100)
        print('Creating the whole historical minute-frequency data...')
        sdd.run_hist_data_download_app(historical_minute_data_address, historical_data_address, symbol, timezone, data_frequency, 'false', '10 D', train_span, market_open_time)
        print('='*100)
        print('='*100)
        print('='*100)
        print('Optimizating the strategy parameters...')
        # Optimize the strategy parameters
        stra.strategy_parameter_optimization(market_open_time, seed, random_seeds, data_frequency, max_window, historical_minute_data_address, train_span, test_span)
    # If you do have a historical minute-frequency data
    else:
        # Update the historical minute-frequency and the resampled data
        sdd.run_hist_data_download_app(historical_minute_data_address, historical_data_address, symbol, timezone, data_frequency, 'true', '10 D', train_span, market_open_time)

        # If it's the first time you begin to go live trading
        if (os.path.exists(f'data/models/model_object_{market_open_time.year}_{month_string}_{day_string}.pickle')==False):
            print('='*100)
            print('='*100)
            print('='*100)
            print('Optimizating the strategy parameters...')
            # Optimize the strategy parameters
            stra.strategy_parameter_optimization(market_open_time, seed, random_seeds, data_frequency, max_window, historical_minute_data_address, base_df_address, purged_window_size, embargo_period, train_span, test_span)
        
    if os.path.exists("data/database.xlsx")==False:
        print('='*100)
        print('='*100)
        print('='*100)
        print('Creating the trading information database...')
        # Create the Excel workbook to save the trading information
        cd.create_trading_info_workbook(smtp_username, to_email , password)
        
    print('='*100)
    print('='*100)
    print('='*100)
    print('Running the trading app for the week...')
    # Run the app loop
    run_trading_setup_loop(host, port, account, client_id, data_frequency, london_start_hour, local_restart_hour, timezone, dt.datetime.now(), account_currency, symbol, leverage, risk_management_target, stop_loss_multiplier, take_profit_multiplier, 
                         historical_data_address, base_df_address, purged_window_size, embargo_period, train_span, 1, max_window)
        
    print('='*100)
    print('='*100)
    print('='*100)
    print('Updating the minute-frequency and resampled data...')
    # Update the historical minute-frequency and the resampled data
    sdd.run_hist_data_download_app(historical_minute_data_address, historical_data_address, symbol, timezone, data_frequency, 'true', '10 D', train_span, market_open_time)
    
    # Get the local timezone hours that match the Easter timezone hours
    restart_hour, restart_minute, day_end_hour, day_end_minute, trading_start_hour = tf.get_end_hours(timezone, london_start_hour, local_restart_hour)
    
    # Get the market open and close datetimes of the current week
    market_open_time, market_close_time = tf.define_trading_week(timezone, trading_start_hour, day_end_minute)

    if (os.path.exists(f'data/model_object_{market_open_time.year}_{month_string}_{day_string}.pickle')==False):
        print('='*100)
        print('='*100)
        print('='*100)
        print('Optimizating the strategy parameters...')

        # Optimize the strategy parameters once the market closes
        stra.strategy_parameter_optimization(market_open_time, seed, random_seeds, data_frequency, max_window, historical_minute_data_address, base_df_address, purged_window_size, embargo_period, train_span, test_span)
