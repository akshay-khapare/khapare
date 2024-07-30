
from flask import Flask, request, jsonify
import pandas as pd
import requests
import json


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





if __name__ == '__main__':
    app.run(debug=True)
