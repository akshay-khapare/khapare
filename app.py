from iqoptionapi.stable_api import IQ_Option
import numpy as np
from time import time,sleep
from flask import Flask, request, jsonify
import pandas as pd
from threading import Thread
from datetime import datetime
import requests
import json

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
    if vpt > 0 :
        return 'call'  # Positive VPT and bullish trend
    elif vpt < 0 :
        return 'put'  # Negative VPT and bearish trend
    else:
        # Fallback to last candle's direction if no clear signal
        last_candle = data[-1]
        return 'up' if last_candle['close'] > last_candle['open'] else 'down'if last_candle['close'] < last_candle['open'] else 'neutral'


app = Flask(__name__)


def convert_currency_pair(pair):
    return pair[:3] + '_' + pair[3:]
API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()


@app.route('/up', methods=['GET'])
def predict():
    pair = request.args.get('pair', 'EURUSD')
    timeframe =int(request.args.get('timeframe', 1))
    offset = int(request.args.get('offset', 4))
    signal = ''
    trend = ''
    percent = ''

    converted_pair = convert_currency_pair(pair)

    url_hist = f'https://api-fxpractice.oanda.com/v3/instruments/{converted_pair}/candles?granularity=M{timeframe}&count={offset}'
    headers = {
    'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'
}

    response = requests.get(url_hist, headers=headers   )
# if r  ponse.status_code == 200:
    f = response.json()
    # data=f['candles']
    data = []
    for candle in f['candles']:
        if candle['complete']:  # Only include complete candles
            open_price = float(candle['mid']['o'])
            close_price = float(candle['mid']['c'])
            min_price = float(candle['mid']['l'])
            max_price = float(candle['mid']['h'])
            volume = candle['volume']    
            candle_data = {
                'open': open_price,
                'close': close_price,
                'min': min_price,
                'max': max_price,
                'volume': volume
            }
            data.append(candle_data)



    df = pd.DataFrame(data)
    df['volume_change'] = df['volume'].diff().fillna(0)
    vpt = [0]

# Calculate VPT for each data point
    for i in range(1, len(data)):
        prev_close = data[i-1]['open']
        close = data[i]['open']
        volume = data[i]['volume']
        vpt.append(vpt[-1] + ((close - prev_close) / prev_close) * volume)

# Predict the direction for the next candle based on VPT
    def predict_next_direction(vpt):
        if len(vpt) < 2:
            return "Not enough data to predict"

    # Compae the last two VPT values
        if vpt[-1] > vpt[-2]:
            return "up"
        elif vpt[-1] < vpt[-2]:
            return "down"
        else:
            return "neutral"
    latest_data = df.iloc[-1]
    if  latest_data['volume_change'] > 0:
        t= "up"
    elif latest_data['volume_change'] < 0:
        t= "down"
    else:
        t= "Neutral"
    next_direction = predict_next_direction(vpt)
    direction= next_direction if(next_direction==t) else 'neutral'

    response = {
        'pair':pair,
        "prediction":direction,
       
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
