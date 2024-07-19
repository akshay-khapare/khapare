from iqoptionapi.stable_api import IQ_Option
import numpy as np
from time import time
from flask import Flask, request, jsonify

app = Flask(__name__)


class LogisticRegression:
    def __init__(self, learning_rate=0.01, num_iterations=10000):
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations

    def sigmoid(self, z):
        # Sigmoid function should always return values between 0 and 1
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        self.m, self.n = X.shape
        self.weights = np.zeros(self.n)
        self.bias = 0
        self.X = X
        self.y = y

        for i in range(self.num_iterations):
            self.update_weights()

    def update_weights(self):
        A = self.sigmoid(np.dot(self.X, self.weights) + self.bias)

        temp = (A - self.y.T)
        temp = np.reshape(temp, self.m)

        dW = np.dot(self.X.T, temp) / self.m
        db = np.sum(temp) / self.m

        self.weights -= self.learning_rate * dW
        self.bias -= self.learning_rate * db

    def predict(self, X):
        # Predict should also use the sigmoid function to ensure output is between 0 and 1
        return self.sigmoid(np.dot(X, self.weights) + self.bias)

    def predict_classes(self, X):
        y_pred = self.predict(X)
        y_pred_classes = [1 if i > 0.5 else 0 for i in y_pred]
        return y_pred_classes

# Custom StandardScaler implementation


class StandardScaler:
    def fit(self, X):
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)

    def transform(self, X):
        return (X - self.mean) / self.std


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
    data.pop()
    X = []
    y = []

    for i in range(len(data) - 1):
        candle = data[i]
        next_candle = data[i + 1]

        features = [
            candle['open'],
            candle['close'],
            candle['min'],
            candle['max'],
            candle['volume']
        ]
        X.append(features)

        label = 1 if next_candle['close'] > candle['close'] else 0
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    scaler = StandardScaler()
    scaler.fit(X)
    X_scaled = scaler.transform(X)

    model = LogisticRegression()
    model.fit(X_scaled, y)

    last_candle = data[-1]
    last_features = np.array([[
        last_candle['open'],
        last_candle['close'],
        last_candle['min'],
        last_candle['max'],
        last_candle['volume']
    ]])
    last_features_scaled = scaler.transform(last_features)

    prediction = model.predict_classes(last_features_scaled)[0]
    probability = model.predict(last_features_scaled)[0]

    response = {
        "signal": "Up" if prediction == 1 else "Down",
        "probability_up": probability,
        "probability_down": 1 - probability,
        "trend": "Up" if last_candle['close'] > last_candle['open'] else "Down"
    }

    return jsonify(response)


# @app.route('/up', methods=['GET'])
# def predict():
#     pair = request.args.get('pair', 'EURUSD')
#     timeframe = request.args.get('timeframe', 1)
#     offset = request.args.get('offset', 3)
#     signal = ''
#     trend = ''
#     percent = ''

#     data = API.get_candles(pair, timeframe*60, offset, time())
#     X = []
#     y = []

#     for i in range(len(data) - 1):
#         candle = data[i]
#         next_candle = data[i + 1]

#     # Features: open, close, min, max, volume
#         features = [
#             candle['open'],
#             candle['close'],
#             candle['min'],
#             candle['max'],
#             candle['volume']
#         ]
#         X.append(features)

#     # Label: 1 if next candle closes higher, 0 otherwise
#         label = 1 if next_candle['close'] > candle['close'] else 0
#         y.append(label)

#     X = np.array(X)
#     y = np.array(y)

# # Check the distribution of classes
#     unique, counts = np.unique(y, return_counts=True)
#     # print(f"Class distribution: {dict(zip(unique, counts))}")

# # Ensure there are at least two classes
#     if len(unique) < 2:
#         signal = 'No signal'
#     #     print(
#     # "Not enough classes in the data. Adjust the data to have at least two classes.")
#     else:
#         # Normalize the features
#         scaler = StandardScaler()
#         X_scaled = scaler.fit_transform(X)

#         # Train the logistic regression model
#         model = LogisticRegression()
#         model.fit(X_scaled, y)

#         # Prepare the last candle data for prediction
#         last_candle = data[-1]
#         last_features = np.array([[
#             last_candle['open'],
#             last_candle['close'],
#             last_candle['min'],
#             last_candle['max'],
#             last_candle['volume']
#         ]])
#         last_features_scaled = scaler.transform(last_features)

#         # Make prediction
#         prediction = model.predict(last_features_scaled)
#         probability = model.predict_proba(last_features_scaled)[0]

#         trend = "Up" if last_candle['close'] > last_candle['open'] else "Down"
#         signal = 'Up' if prediction[0] == 1 else 'Down'
#         percent = f'{probability[1]:.2f}'

#     #     print(
#     # f"{'Up' if prediction[0] == 1 else 'Down'} {probability[1]:.2f}, Down - {probability[0]:.2f} {trend}", data_atual)

#     return jsonify({
#         'pair': pair,
#         'signal': signal,
#         'trend': trend,
#         'percent': percent
#     })


if __name__ == '__main__':
    app.run(debug=True)
