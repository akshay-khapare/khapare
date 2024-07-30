
from flask import Flask, request, jsonify
import pandas as pd
import requests
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
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



    # data = API.get_candles(pair, timeframe*60, offset, time())
    # data.pop()
    next_candle_direction = predict_next_candle_direction(data)
    df = pd.DataFrame(data)
    df['price_change'] = df['close'] - df['open']
    df['avg_price'] = (df['open'] + df['close'] + df['min'] + df['max']) / 4
    # Define target: 1 if the next candle is up, 0 if down
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    # Drop the last row as it has no target
    df.dropna(inplace=True)
    # Features and target
    X = df[['price_change', 'avg_price', 'volume']]
    y = df['target']
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    # Predict
    y_pred = model.predict(X_test)
    # Evaluate
    accuracy = accuracy_score(y_test, y_pred)
    # print(f"Accuracy: {accuracy:.2f}")
    # Predict the direction of the next candle
    last_row = df.iloc[-1][['price_change', 'avg_price', 'volume']].values.reshape(1, -1)
    prediction = model.predict(last_row)
    direction = "up" if prediction[0] == 1 else "down"
        # print( direction,f"Accuracy: {accuracy:.2f}",data_atual)

    response = {
        'pair':pair,
        "prediction":direction,
        'accuracy':f'{accuracy:.2f}'
       
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
