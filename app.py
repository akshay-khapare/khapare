from iqoptionapi.stable_api import IQ_Option
import numpy as np
from sklearn.preprocessing import StandardScaler
from time import time
from sklearn.linear_model import LogisticRegression
from flask import Flask, request, jsonify

app = Flask(__name__)


API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()


@app.route('/down', methods=['GET'])
def predict():
    pair = request.args.get('pair', 'EURUSD')
    timeframe = request.args.get('timeframe', 1)
    offset = request.args.get('offset', 3)
    signal = ''
    trend = ''
    percent = ''

    data = API.get_candles(pair, timeframe*60, offset, time())
    X = []
    y = []

    for i in range(len(data) - 1):
        candle = data[i]
        next_candle = data[i + 1]

    # Features: open, close, min, max, volume
        features = [
            candle['open'],
            candle['close'],
            candle['min'],
            candle['max'],
            candle['volume']
        ]
        X.append(features)

    # Label: 1 if next candle closes higher, 0 otherwise
        label = 1 if next_candle['close'] < candle['close'] else 0
        y.append(label)

    X = np.array(X)
    y = np.array(y)

# Check the distribution of classes
    unique, counts = np.unique(y, return_counts=True)
    # print(f"Class distribution: {dict(zip(unique, counts))}")

# Ensure there are at least two classes
    if len(unique) < 2:
        signal = 'No signal'
    #     print(
    # "Not enough classes in the data. Adjust the data to have at least two classes.")
    else:
        # Normalize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train the logistic regression model
        model = LogisticRegression()
        model.fit(X_scaled, y)

        # Prepare the last candle data for prediction
        last_candle = data[-1]
        last_features = np.array([[
            last_candle['open'],
            last_candle['close'],
            last_candle['min'],
            last_candle['max'],
            last_candle['volume']
        ]])
        last_features_scaled = scaler.transform(last_features)

        # Make prediction
        prediction = model.predict(last_features_scaled)
        probability = model.predict_proba(last_features_scaled)[0]

        trend = "Up" if last_candle['close'] > last_candle['open'] else "Down"
        signal = 'Up' if prediction[0] == 1 else 'Down'
        percent = f'{probability[1]:.2f}'

    #     print(
    # f"{'Up' if prediction[0] == 1 else 'Down'} {probability[1]:.2f}, Down - {probability[0]:.2f} {trend}", data_atual)

    return jsonify({
        'pair': pair,
        'signal': signal,
        'trend': trend,
        'percent': percent
    })


@app.route('/up', methods=['GET'])
def predict():
    pair = request.args.get('pair', 'EURUSD')
    timeframe = request.args.get('timeframe', 1)
    offset = request.args.get('offset', 3)
    signal = ''
    trend = ''
    percent = ''

    data = API.get_candles(pair, timeframe*60, offset, time())
    X = []
    y = []

    for i in range(len(data) - 1):
        candle = data[i]
        next_candle = data[i + 1]

    # Features: open, close, min, max, volume
        features = [
            candle['open'],
            candle['close'],
            candle['min'],
            candle['max'],
            candle['volume']
        ]
        X.append(features)

    # Label: 1 if next candle closes higher, 0 otherwise
        label = 1 if next_candle['close'] > candle['close'] else 0
        y.append(label)

    X = np.array(X)
    y = np.array(y)

# Check the distribution of classes
    unique, counts = np.unique(y, return_counts=True)
    # print(f"Class distribution: {dict(zip(unique, counts))}")

# Ensure there are at least two classes
    if len(unique) < 2:
        signal = 'No signal'
    #     print(
    # "Not enough classes in the data. Adjust the data to have at least two classes.")
    else:
        # Normalize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train the logistic regression model
        model = LogisticRegression()
        model.fit(X_scaled, y)

        # Prepare the last candle data for prediction
        last_candle = data[-1]
        last_features = np.array([[
            last_candle['open'],
            last_candle['close'],
            last_candle['min'],
            last_candle['max'],
            last_candle['volume']
        ]])
        last_features_scaled = scaler.transform(last_features)

        # Make prediction
        prediction = model.predict(last_features_scaled)
        probability = model.predict_proba(last_features_scaled)[0]

        trend = "Up" if last_candle['close'] > last_candle['open'] else "Down"
        signal = 'Up' if prediction[0] == 1 else 'Down'
        percent = f'{probability[1]:.2f}'

    #     print(
    # f"{'Up' if prediction[0] == 1 else 'Down'} {probability[1]:.2f}, Down - {probability[0]:.2f} {trend}", data_atual)

    return jsonify({
        'pair': pair,
        'signal': signal,
        'trend': trend,
        'percent': percent
    })


if __name__ == '__main__':
    app.run(debug=True)
