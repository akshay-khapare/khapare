from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from datetime import datetime
from time import sleep, time
import warnings
from flask import Flask, request, jsonify

app = Flask(__name__)

warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow")


tf.get_logger().setLevel('ERROR')

warnings.filterwarnings('ignore', category=FutureWarning, module='keras')


API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()


@app.route('/v', methods=['GET'])
def predict():
    pair = request.args.get('pair', 'EURUSD')
    timeframe = request.args.get('timeframe', 1)
    offset = request.args.get('offset', 3)

    candles_data = API.get_candles(pair, timeframe*60, offset, time())
    df = pd.DataFrame(candles_data)
    df['next_close'] = df['close'].shift(-1)
    df['direction'] = (df['next_close'] > df['close']).astype(int)
    df['price_range'] = df['max'] - df['min']
    df['price_change'] = df['close'] - df['open']
    df['price_change_pct'] = df['price_change'] / df['open']
    df['volume_change'] = df['volume'].pct_change().fillna(0)
    df = df.dropna()

    features = df[['direction']]
    labels = df['direction']

    scaler = StandardScaler()
    features = scaler.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=42)

# Build the TensorFlow model
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(64, activation='relu',
                              input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

# Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy',
                  metrics=['accuracy'])

# Train the model
    model.fit(X_train, y_train, epochs=1, batch_size=1,
              validation_split=0, verbose=0)

# Evaluate the model
    loss, accuracy = model.evaluate(X_test, y_test)
# print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Make predictions
    predictions = (model.predict(X_test) > 0.5).astype(int)

# Print actual and predicted directions
    results = pd.DataFrame(
        {'Actual': y_test, 'Predicted': predictions.flatten()})
# print(results)

# Print up and down directions
# print("\nUp predictions:")
    if not results[results['Predicted'] == 1].empty:
        direction = 'UP'
    elif not results[results['Predicted'] == 0].empty:
        direction = 'DOWN'
    else:
        direction = 'NONE'

    # print(f' {direction} {accuracy * 100:.2f}%')

    return jsonify({
        'direction': direction,
        'accuracy': f'{accuracy * 100:.2f}%'
    })


if __name__ == '__main__':
    app.run(debug=True)
