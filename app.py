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
    offset = int(request.args.get('offset', 4))
    signal = ''
    trend = ''
    percent = ''

    data= API.get_candles(pair, timeframe*60, offset, time())
    data.pop()
    # df = pd.DataFrame(data)


    data[0] = 'g' if data[0]['open'] < data[0]['close'] else 'r' if data[0]['open'] > data[0]['close'] else 'd'
    data[1] = 'g' if data[1]['open'] < data[1]['close'] else 'r' if data[1]['open'] > data[1]['close'] else 'd'
    # data[2] = 'g' if data[2]['open'] < data[2]['close'] else 'r' if data[2]['open'] > data[2]['close'] else 'd'
    # data[3] = 'g' if data[3]['open'] < data[3]['close'] else 'r' if data[3]['open'] > data[3]['close'] else 'd'
    # data[4] = 'g' if data[4]['open'] < data[4]['close'] else 'r' if data[4]['open'] > data[4]['close'] else 'd'
    cores_velas = data[0] + ' / ' + data[1]
    # + ' / ' + data[3] + ' / ' + data[4]  
    q4= "PUT" if cores_velas.count('g') > cores_velas.count('r') and cores_velas.count('d') == 0 else "CALL" if cores_velas.count('r') > cores_velas.count('g') and cores_velas.count('d') == 0 else "doji"



    response = {
        'pair':pair,
        "prediction":q4,
       
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
