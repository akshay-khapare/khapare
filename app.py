from iqoptionapi.stable_api import IQ_Option
import numpy as np
from time import time,sleep
from flask import Flask, request, jsonify
import pandas as pd
from threading import Thread
from datetime import datetime


def calculate_vpt(data):
    vpt = 0
    for i in range(1, len(data)):
        previous_close = data[i-1]['close']
        current_close = data[i]['close']
        current_volume = data[i]['volume']
        vpt += ((current_close - previous_close) / previous_close) * current_volume
    return vpt

def calculate_moving_average(prices, period):
    return sum(prices[-period:]) / period

def predict_next_candle_direction(data):
    # Calculate Volume Price Trend (VPT)
    vpt = calculate_vpt(data)
    
    # Calculate short-term and long-term moving averages
    closing_prices = [candle['close'] for candle in data]
    short_term_ma = calculate_moving_average(closing_prices, period=2)
    long_term_ma = calculate_moving_average(closing_prices, period=4)
    
    # Determine trend direction based on moving averages
    if short_term_ma > long_term_ma:
        trend = 'up'
    elif short_term_ma < long_term_ma:
        trend = 'down'
    else:
        trend = None
    
    # Combine VPT with trend to predict direction
    if vpt < 0 and trend == 'up':
        return 'down'  # Positive VPT and bullish trend
    elif vpt > 0 and trend == 'down':
        return 'up'  # Negative VPT and bearish trend
    else:
        # Fallback to last candle's direction if no clear signal
        last_candle = data[-1]
        return 'call' if last_candle['close'] > last_candle['open'] else 'put'if last_candle['close'] < last_candle['open'] else 'neutral'


app = Flask(__name__)



API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()


@app.route('/up', methods=['GET'])
def predict():
    pair = request.args.get('pair', 'EURUSD')
    timeframe =int(request.args.get('timeframe', 1))
    offset = int(request.args.get('offset', 6))
    signal = ''
    trend = ''
    percent = ''

    list=[]



    data = API.get_candles(pair, timeframe*60, offset, time())
    data.pop()
    next_candle_direction = predict_next_candle_direction(data)

    response = {
        'pair':pair,
        "prediction":next_candle_direction,
       
    }

    return jsonify(response)


# @app.route('/down', methods=['GET'])
# def predict():
#     pair = request.args.get('pair', 'EURUSD')
#     timeframe = request.args.get('timeframe', 1)
#     offset = request.args.get('offset', 5)
#     signal = ''
#     trend = ''
#     percent = ''

#     list=[]
#     # while True:

#     data = API.get_candles(pair, timeframe*60, offset, time())
#     data.pop()
#     next_candle_direction = predict_next_candle_direction(data)

#     response = {
#         'pair':pair,
#         "prediction":next_candle_direction,
       
#     }

    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)
