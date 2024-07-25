from iqoptionapi.stable_api import IQ_Option
import numpy as np
from time import time,sleep
from flask import Flask, request, jsonify
import pandas as pd
from threading import Thread
from datetime import datetime

def find_support_and_resistance(data):
    # Extract min and max prices from the last 5 candles
    lows = [candle['min'] for candle in data]
    highs = [candle['max'] for candle in data]
    
    support = min(lows)
    resistance = max(highs)
    
    return support, resistance

def predict_next_candle_direction(data):
    # Get support and resistance levels
    support, resistance = find_support_and_resistance(data)
    
    # Use the latest closing price to determine the action
    last_close = data[-1]['close']
    last_open = data[-1]['open']
    
    # Define a small margin to determine proximity
    margin = 0.00005
    
    # Check proximity to support and resistance
    if last_close >= resistance - margin:
        return 'down'  # Close to resistance, likely to reverse
    elif last_close <= support + margin:
        return 'up'    # Close to support, likely to bounce back
    else:
        # Use last candle's direction as a continuation if not near levels
        return 'call' if last_close > last_open else 'put' if last_close < last_open else 'neutral'

app = Flask(__name__)



API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()


@app.route('/up', methods=['GET'])
def predict():
    pair = request.args.get('pair', 'EURUSD')
    timeframe = request.args.get('timeframe', 1)
    offset = request.args.get('offset', 5)
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
