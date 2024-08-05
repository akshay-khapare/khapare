from iqoptionapi.stable_api import IQ_Option
import numpy as np
from time import time,sleep
from flask import Flask, request, jsonify
# import pandas as pd
from threading import Thread
from datetime import datetime
import requests
import json



app = Flask(__name__)
def predict_next_candle(data, lookback_period=3):
    # def predict_next_candle_vpt(data, lookback_period=3):
    if len(data) < lookback_period + 1:
        return "Insufficient data for prediction"

    # Calculate the trend over the lookback period
    trend_up = 0
    trend_down = 0

    for i in range(-lookback_period, -1):
        if data[i]['VPT'] > data[i - 1]['VPT']:
            trend_up += 1
        else:
            trend_down += 1

    # Determine the direction based on the trend count
    if trend_up > trend_down:
        return "PUT"
    elif trend_up < trend_down:
        return "CALL"
    else:
        return "d"



API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()


@app.route('/up', methods=['GET'])
def predict():
    pair = request.args.get('pair', 'EURUSD')
    timeframe =int(request.args.get('timeframe', 1))
    offset = int(request.args.get('offset', 5))
    signal = ''
    trend = ''
    percent = ''

    data= API.get_candles(pair, timeframe*60, offset, time())
    data.pop()
    # df = pd.DataFrame(data)


    vpt_values = [0]

# Calculate the PVT for each row
    for i in range(1, len(data)):
        prev_close = data[i - 1]['close']
        current_close = data[i]['close']
        volume = data[i]['volume']
        # Calculate VPT change and accumulate it
        vpt_change = ((current_close - prev_close) / prev_close) * volume
        vpt = vpt_values[-1] + vpt_change
        vpt_values.append(vpt)
# Add VT to each data entry
    for i in range(len(data)):
        data[i]['VPT'] = vpt_values[i]

    prediction = predict_next_candle(data)

    response = {
        'pair':pair,
        "prediction":prediction,
       
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
