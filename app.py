from iqoptionapi.stable_api import IQ_Option
import numpy as np
from time import time
from flask import Flask, request, jsonify
import pandas as pd

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

    data = API.get_candles(pair, timeframe*60, offset, time())
    data.pop()
    volume_window = 3
    price_window = 3
    df = pd.DataFrame(data)

# Calculate Volume Moving Average (VMA) and Price Moving Average (PMA)
    df['vma'] = df['volume'].rolling(window=volume_window).mean()
    df['pma'] = df['close'].rolling(window=price_window).mean()

# Identify volume spikes (current volume > VMA)
    df['volume_spike'] = df['volume'] > df['vma']

# Determine trend based on Price Moving Average
    df['price_above_pma'] = df['close'] > df['pma']

# Predict the next candle direction
    last_volume_spike = df['volume_spike'].iloc[-1]
    last_price_above_pma = df['price_above_pma'].iloc[-1]

    if last_volume_spike and last_price_above_pma:
        prediction = "up"
    elif last_volume_spike and not last_price_above_pma:
        prediction = "down"
    else:
    # If no clear signal from volume spike, use last close vs. open comparison
        last_close = df['close'].iloc[-1]
        if last_close < df['open'].iloc[-1]:
            prediction = "call"
        elif last_close > df['open'].iloc[-1]:
            prediction = "put"
        else:
            prediction = "neutral"

    response = {
        'pair':pair,
        "prediction":prediction,
       
    }

    return jsonify(response)


# @app.route('/down', methods=['GET'])
# def predict():
#     pair = request.args.get('pair', 'EURUSD')
#     timeframe = request.args.get('timeframe', 1)
#     offset = request.args.get('offset', 3)
#     signal = ''
#     trend = ''
#     percent = ''

#     data = API.get_candles(pair, timeframe*60, offset, time())
#     data.pop()
#     X = []
#     y = []

#     for i in range(len(data) - 1):
#         candle = data[i]
#         next_candle = data[i + 1]

#         features = [
#             candle['open'],
#             candle['close'],
#             candle['min'],
#             candle['max'],
#             candle['volume']
#         ]
#         X.append(features)

#         label = 1 if next_candle['close'] < candle['close'] else 0
#         y.append(label)

#     X = np.array(X)
#     y = np.array(y)

#     scaler = StandardScaler()
#     scaler.fit(X)
#     X_scaled = scaler.transform(X)

#     model = LogisticRegression()
#     model.fit(X_scaled, y)

#     last_candle = data[-1]
#     last_features = np.array([[
#         last_candle['open'],
#         last_candle['close'],
#         last_candle['min'],
#         last_candle['max'],
#         last_candle['volume']
#     ]])
#     last_features_scaled = scaler.transform(last_features)

#     prediction = model.predict_classes(last_features_scaled)[0]
#     probability = model.predict(last_features_scaled)[0]

#     response = {
#         "signal": "Up" if prediction == 1 else "Down",
#         "probability_up": probability,
#         "probability_down": 1 - probability,
#         "trend": "Up" if last_candle['close'] > last_candle['open'] else "Down"
#     }

#     return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
