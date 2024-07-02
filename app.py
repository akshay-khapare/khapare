from flask import Flask, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
from time import sleep, time
import pytz
import time as tm
from quotexpy import Quotex
from quotexpy.utils import asset_parse
from quotexpy.utils.account_type import AccountType
from quotexpy.utils.operation_type import OperationType
from quotexpy.utils.duration_time import DurationTime
# from my_connection import MyConnection
from datetime import datetime, timedelta
import pytz
from flask import Flask, request, jsonify
import os
import asyncio
from pathlib import Path

app = Flask(__name__)


# app = Flask(__name__)


class SingletonDecorator:
    """
    A decorator that turns a class into a singleton.
    """

    def __init__(self, cls):
        self.cls = cls
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.cls(*args, **kwargs)
        return self.instance


@SingletonDecorator
class MyConnection:
    """
    This class represents a connection object and provides methods for connecting to a client.
    """

    def __init__(self, client_instance):
        self.client = client_instance

    async def connect(self, attempts=5):
        check, reason = await self.client.connect()
        if not check:
            attempt = 0
            while attempt <= attempts:
                if not self.client.check_connect():
                    check, reason = await self.client.connect()
                    if check:
                        print("Reconectado com sucesso!!!")
                        break
                    print("Erro ao reconectar.")
                    attempt += 1
                    if Path(os.path.join(".", "session.json")).is_file():
                        Path(os.path.join(".", "session.json")).unlink()
                    print(
                        f"Tentando reconectar, tentativa {attempt} de {attempts}")
                elif not check:
                    attempt += 1
                else:
                    break
                await asyncio.sleep(5)
            return check, reason
        return check, reason

    def close(self):
        """
        Closes the client connection.
        """
        self.client.close()


email = "govindkhapare2001@gmail.com"
password = "Akshay@2001"

client = Quotex(email=email,
                password=password,
                headless=False)
client.debug_ws_enable = False

API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()
data_atual = datetime.now().strftime('%Y-%m-%d')


def cataloga(pair, days, timeframe, timezone, date):
    ema1 = 1
    data = []
    datas_testadas = []
    time_ = time()
    sair = False

    # Define the user timezone
    user_tz = pytz.timezone(timezone)

    while not sair:
        velas = API.get_candles(pair, (timeframe * 60), 1000, time_)
        velas.reverse()
        posicao = 0
        for x in velas:
            candle_time = datetime.fromtimestamp(
                x['from'], tz=pytz.utc).astimezone(user_tz)
            if candle_time.strftime('%Y-%m-%d') != data_atual:
                if candle_time.strftime('%Y-%m-%d') not in datas_testadas:
                    datas_testadas.append(candle_time.strftime('%Y-%m-%d'))
                if len(datas_testadas) <= days:
                    x.update({'cor': 'verde' if x['open'] < x['close']
                             else 'vermelha' if x['open'] > x['close'] else 'doji'})
                    # velas_tendencia1 = velas[posicao:posicao + ema1]
                    # tendencia1 = trend(velas_tendencia1, ema1)
                    x.update({'trend': ''})
                    data.append(x)
                else:
                    sair = True
                    break
            posicao += 1
        time_ = int(velas[-1]['from'] - 1)

    analise = {}
    for velas in data:
        horario = datetime.fromtimestamp(
            velas['from'], tz=pytz.utc).astimezone(user_tz).strftime('%H:%M:%S')
        if horario not in analise:
            analise.update(
                {horario: {'candle': '', '%': 0, 'put': 0, 'dir': '', 'trend': ''}})
        analise[horario]['candle'] += 'g' if velas['cor'] == 'verde' else 'r' if velas['cor'] == 'vermelha' else 'd'
        verde_count = analise[horario]['candle'].count('g')
        vermelha_count = analise[horario]['candle'].count('r')
        doji_count = analise[horario]['candle'].count('d')
        total_count = verde_count + vermelha_count + doji_count
        analise[horario]['trend'] = velas['trend']
        try:
            analise[horario]['%'] = round(100 * (verde_count / total_count))
            analise[horario]['put'] = round(
                100 * (vermelha_count / total_count))
        except:
            pass
    for horario in analise:
        if analise[horario]['%'] == 100:
            analise[horario]['dir'] = 'CALL'
        if analise[horario]['put'] == 0:
            analise[horario]['dir'] == 'PUT '
            # analise[horario]['%'], analise[horario]['dir'] = 100 - \
            #     analise[horario]['%'], 'PUT '
    return analise


def protrader(pair, days, timeframe, timezone, date):
    data = []
    datas_testadas = []
    time_ = date_to_epoch(date)
    sair = False

    # Define the user timezone
    user_tz = pytz.timezone(timezone)

    while not sair:
        velas = API.get_candles(pair, (timeframe * 60), 10000, time_)
        velas.reverse()
        posicao = 0
        for x in velas:
            candle_time = datetime.fromtimestamp(
                x['from'], tz=pytz.utc).astimezone(user_tz)

            if candle_time.strftime('%Y-%m-%d') not in datas_testadas:
                datas_testadas.append(candle_time.strftime('%Y-%m-%d'))
            if len(datas_testadas) <= days:
                x.update({'cor': 'verde' if x['open'] < x['close']
                         else 'vermelha' if x['open'] > x['close'] else 'doji'})
                data.append(x)
            else:
                sair = True
                break
            posicao += 1
        time_ = int(velas[-1]['from'] - 1)

    analise = {}
    for velas in data:
        horario = datetime.fromtimestamp(
            velas['from'], tz=pytz.utc).astimezone(user_tz).strftime('%H:%M:%S')
        if horario not in analise:
            analise.update(
                {horario: {'candle': '', '%': 0, 'put': 0, 'dir': ''}})
        analise[horario]['candle'] += 'g' if velas['cor'] == 'verde' else 'r' if velas['cor'] == 'vermelha' else 'd'
        verde_count = analise[horario]['candle'].count('g')
        vermelha_count = analise[horario]['candle'].count('r')
        doji_count = analise[horario]['candle'].count('d')
        total_count = verde_count + vermelha_count + doji_count
        try:
            analise[horario]['%'] = round(100 * (verde_count / total_count))
            analise[horario]['put'] = round(
                100 * (vermelha_count / total_count))
        except:
            pass
    for horario in analise:
        if analise[horario]['%'] == 100:
            analise[horario]['dir'] = 'CALL'
        elif analise[horario]['put'] == 100:
            analise[horario]['dir'] = 'PUT '
            # analise[horario]['%'] = 100 - analise[horario]['%']
            # analise[horario]['dir'] = 'PUT'
        else:
            analise[horario]['dir'] = 'NEUTRAL'
    return analise


@app.route('/v1', methods=['GET'])
def get_cataloga():
    pair = request.args.get('pair', 'EURUSD')
    days = int(request.args.get('days', 3))
    porcentagem = int(request.args.get('porcentagem', 100))
    timeframe = int(request.args.get('timeframe', 1))
    timezone = request.args.get('timezone', 'Asia/KOlkata')
    date = request.args.get(
        'date', datetime.now().strftime('%Y-%m-%d'))
    martingale = request.args.get('martingale', '1')
    result = cataloga(pair, days, timeframe, timezone, date)

    return jsonify(result)


@app.route('/v2', methods=['GET'])
def get_pro():
    pair = request.args.get('pair', 'EURUSD')
    days = int(request.args.get('days', 3))
    porcentagem = int(request.args.get('porcentagem', 100))
    timeframe = int(request.args.get('timeframe', 1))
    timezone = request.args.get('timezone', 'Asia/KOlkata')
    date = request.args.get(
        'date', datetime.now().strftime('%Y-%m-%d'))
    martingale = request.args.get('martingale', '1')
    result = protrader(pair, days, timeframe, timezone, date)

    return jsonify(result)


@app.route('/v3', methods=['GET'])
def v3():
    # Parameters from request (you might want to handle these properly)
    pair = request.args.get('pair', 'EURUSD')
    days = int(request.args.get('days', 3))
    porcentagem = int(request.args.get('porcentagem', 100))
    timeframe = int(request.args.get('timeframe', 1))
    timezone = request.args.get('timezone', 'Asia/Kolkata')
    date = request.args.get(
        'date', datetime.now().strftime('%Y-%m-%d'))
    martingale = request.args.get('martingale', '1')

    prct_call = abs(porcentagem)
    prct_put = abs(100 - porcentagem)

    catalogacao = {pair: catalog(
        pair, days, prct_call, prct_put, timeframe, date, martingale, timezone)}

    results = []
    for par in catalogacao:
        for horario in sorted(catalogacao[par]):
            ok = False

            if catalogacao[par][horario]['%'] >= porcentagem:
                ok = True
            else:
                for i in range(int(martingale)):
                    if int(catalogacao[par][horario]['mg' + str(i + 1)]['%']) >= porcentagem:
                        ok = True
                        break

            if ok:
                result = {
                    "pair": par,
                    "time": horario,
                    "dir": catalogacao[par][horario]['dir'].strip(),
                    "percent": catalogacao[par][horario]['%'],
                    "trend": catalogacao[par][horario]['trend'],
                }
                if martingale.strip() != '':
                    result["martingale"] = []
                    for i in range(int(martingale)):
                        mg_percentual = catalogacao[par][horario]['mg' +
                                                                  str(i + 1)]['%']
                        result["martingale"].append({
                            f'mg{i+1}': i + 1,
                            "percent": mg_percentual if mg_percentual != 'N/A' else None,
                            'dir': catalogacao[par][horario]['mg' +
                                                             str(i + 1)]['dir']
                        })
                results.append(result)

    return jsonify(results)


def catalog(pair, days, prct_call, prct_put, timeframe, date, martingale, timezone):
    ema = 1
    data = []
    datas_testadas = []
    time_ = time()
    sair = False
    user_tz = pytz.timezone(timezone)

    while not sair:
        velas = API.get_candles(pair, (timeframe * 60), 10, time_)
        velas.reverse()
        posicao = 0
        for x in velas:
            candle_time = datetime.fromtimestamp(
                x['from'], tz=pytz.utc).astimezone(user_tz)
            if candle_time.strftime('%Y-%m-%d') != date:
                if candle_time.strftime('%Y-%m-%d') != date:
                    if candle_time.strftime('%Y-%m-%d') not in datas_testadas:
                        datas_testadas.append(candle_time.strftime('%Y-%m-%d'))
                    if len(datas_testadas) <= days:
                        x.update({'cor': 'verde' if x['open'] < x['close']
                                  else 'vermelha' if x['open'] > x['close'] else 'doji'})
                        # df = pd.DataFrame(velas)
                        # df['vma'] = df['volume'].rolling(window=3).mean()
                        # df['vm'] = df['volume'] - df['vma']

                        # def predict_direction(row):
                        #     if row['vm'] > 0:
                        #         return 1  # Up
                        #     elif row['vm'] < 0:
                        #         return -1  # Down
                        #     else:
                        #         return 0  # Neutral
                        # df['prediction'] = df.apply(predict_direction, axis=1)
                        # prediction = df['prediction'].iloc[-1]
                        x.update({'trend': ''})
                        data.append(x)
                    else:
                        sair = True
                        break
                posicao += 1
        time_ = int(velas[-1]['from'] - 1)

    analise = {}
    for velas in data:
        horario = datetime.fromtimestamp(
            velas['from'], tz=pytz.utc).astimezone(user_tz).strftime('%H:%M')
        if horario not in analise:
            analise[horario] = {'verde': 0, 'vermelha': 0,
                                'doji': 0, '%': 0, 'dir': '', 'trend': '',
                                'contra_verde': 0,
                                'contra_vermelha': 0}
        analise[horario][velas['cor']] += 1
        if velas['cor'] == 'verde':

            analise[horario]['contra_verde'] += 1
        if velas['cor'] == 'vermelha':
            analise[horario]['contra_vermelha'] += 1
        analise[horario]['trend'] = velas['trend']
        try:
            analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (
                analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
        except ZeroDivisionError:
            pass

    for horario in analise:
        if analise[horario]['%'] == 100 and analise[horario]['doji'] == 0 and analise[horario]['vermelha'] == 0:
            analise[horario]['dir'] = 'CALL'
        if analise[horario]['%'] == 0 and analise[horario]['doji'] == 0 and analise[horario]['verde'] == 0:
            analise[horario]['%'], analise[horario]['dir'] = 100 - \
                analise[horario]['%'], 'PUT'
        # if analise[horario]['dir'] == 'PUT ':
            # analise[horario]['trend'] = round(
            #     100 - ((analise[horario]['contra_vermelha'])*100))

        # else:
        #     analise[horario]['trend'] = round(
        #         100 - ((analise[horario]['contra_verde'])*100))

    # Adding martingale calculation
    for horario in sorted(analise):
        if martingale.strip() != '':
            mg_time = horario
            soma = {'verde': analise[horario]['verde'], 'vermelha': analise[horario]
                    ['vermelha'], 'doji': analise[horario]['doji']}

            for i in range(int(martingale)):
                analise[horario].update(
                    {'mg' + str(i + 1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0, 'dir': ''}})
                mg_time = str(datetime.strptime((datetime.now()).strftime(
                    '%Y-%m-%d ') + str(mg_time), '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]

                if mg_time in analise:
                    a = analise[horario]['dir']
                    b = analise[horario]['mg' + str(i + 1)]['vermelha']
                    c = analise[horario]['mg' + str(i + 1)]['doji']
                    analise[horario]['mg' +
                                     str(i + 1)]['verde'] += analise[mg_time]['verde'] + soma['verde']
                    analise[horario]['mg' +
                                     str(i + 1)]['vermelha'] += analise[mg_time]['vermelha'] + soma['vermelha']
                    analise[horario]['mg' +
                                     str(i + 1)]['doji'] += analise[mg_time]['doji'] + soma['doji']
                    analise[horario]['mg' + str(i + 1)]['dir'] = f'{a}'
                    analise[horario]['mg' + str(i + 1)]['%'] = round(100 * (analise[horario]['mg' + str(i + 1)]['verde' if analise[horario]['dir'] == 'CALL' else 'vermelha'if analise[horario]['dir'] == 'PUT' else 'doji'] / (
                        analise[horario]['mg' + str(i + 1)]['verde'] + analise[horario]['mg' + str(i + 1)]['vermelha'] + analise[horario]['mg' + str(i + 1)]['doji'])))
                    soma['verde'] += analise[mg_time]['verde']
                    soma['vermelha'] += analise[mg_time]['vermelha']
                    soma['doji'] += analise[mg_time]['doji']
                else:
                    analise[horario]['mg' + str(i + 1)]['%'] = 'N/A'

    return analise


@app.route('/v4', methods=['GET'])
def v4():
    pair = request.args.get('pair', 'EURUSD')
    days = int(request.args.get('days', 3))
    porcentagem = int(request.args.get('porcentagem', 100))
    timeframe = int(request.args.get('timeframe', 1))
    timezone = request.args.get('timezone', 'Asia/Kolkata')
    date = request.args.get(
        'date', datetime.now().strftime('%Y-%m-%d'))
    martingale = request.args.get('martingale', '1')

    prct_call = abs(porcentagem)
    prct_put = abs(100 - porcentagem)

    catalogacao = {pair: catalogg(
        pair, days, prct_call, prct_put, timeframe, date, martingale, timezone)}
    results = []
    for par in catalogacao:
        # print(par)
        for horario in sorted(catalogacao[par]):
            ok = False

            if catalogacao[par][horario]['%'] >= porcentagem:
                ok = True
            else:
                for i in range(int(martingale)):
                    if catalogacao[par][horario]['mg' + str(i + 1)]['%'] >= porcentagem:
                        ok = True
                        break

            if ok:
                result = {
                    "pair": par,
                    "time": horario,
                    "dir": catalogacao[par][horario]['dir'].strip(),
                    "percent": catalogacao[par][horario]['%'],

                }
                if martingale.strip() != '':
                    result["martingale"] = []
                    for i in range(int(martingale)):
                        mg_percentual = catalogacao[par][horario]['mg' +
                                                                  str(i + 1)]['%']
                        mg_dir = catalogacao[par][horario]['mg' +
                                                           str(i + 1)].get('dir', '')
                        result["martingale"].append({
                            f'mg{i+1}': i + 1,
                            "percent": mg_percentual if mg_percentual != 'N/A' else None,
                            "dir": mg_dir
                        })
                results.append(result)

    return jsonify(results)


def catalogg(pair, days, prct_call, prct_put, timeframe, date, martingale, timezone):
    ema1 = 1
    ema7 = 7
    data = []
    datas_testadas = []
    time_ = time()

    sair = False
    user_tz = pytz.timezone(timezone)

    while not sair:
        velas = API.get_candles(pair, (timeframe * 60), 10000, time_)
        velas.reverse()
        posicao = 0
        for x in velas:
            candle_time = datetime.fromtimestamp(
                x['from'], tz=pytz.utc).astimezone(user_tz)

            if candle_time.strftime('%Y-%m-%d') not in datas_testadas:
                datas_testadas.append(candle_time.strftime('%Y-%m-%d'))
            if len(datas_testadas) <= days:

                x.update({'cor': 'verde' if x['open'] < x['close']
                         else 'vermelha' if x['open'] > x['close'] else 'doji'})

                data.append(x)
            else:
                sair = True
                break
            posicao += 1
        time_ = int(velas[-1]['from'] - 1)

    analise = {}
    for velas in data:
        horario = datetime.fromtimestamp(
            velas['from'], tz=pytz.utc).astimezone(user_tz).strftime('%H:%M')
        if horario not in analise:

            analise[horario] = {'verde': 0, 'vermelha': 0,
                                'doji': 0, '%': 0, 'dir': ''}
        analise[horario][velas['cor']] += 1

        try:
            analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (
                analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
        except ZeroDivisionError:
            pass

    for horario in analise:
        if analise[horario]['%'] == 100:
            analise[horario]['dir'] = 'CALL'
        if analise[horario]['%'] == 0:
            analise[horario]['%'], analise[horario]['dir'] = 100 - \
                analise[horario]['%'], 'PUT'

    # Adding martingale calculation
    for horario in sorted(analise):
        if martingale.strip() != '':
            mg_time = horario
            soma = {'verde': analise[horario]['verde'], 'vermelha': analise[horario]
                    ['vermelha'], 'doji': analise[horario]['doji']}

            for i in range(int(martingale)):
                posicao = 0
                analise[horario].update(
                    {'mg' + str(i + 1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0, 'dir': ''}})
                mg_time = str(datetime.strptime((datetime.now()).strftime(
                    '%Y-%m-%d ') + str(mg_time), '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]

                if mg_time in analise:

                    mg_candles = [vela for vela in data if datetime.fromtimestamp(
                        vela['from'], tz=pytz.utc).astimezone(user_tz).strftime('%H:%M') == mg_time]
                    # mg_trend = trend(mg_candles, ema1) if mg_candles else 0

                    analise[horario]['mg' +
                                     str(i + 1)]['verde'] += analise[mg_time]['verde'] + soma['verde']
                    analise[horario]['mg' +
                                     str(i + 1)]['vermelha'] += analise[mg_time]['vermelha'] + soma['vermelha']
                    analise[horario]['mg' +
                                     str(i + 1)]['doji'] += analise[mg_time]['doji'] + soma['doji']
                    # analise[horario]['mg' + str(i + 1)]['trend'] = mg_trend
                    analise[horario]['mg' + str(i + 1)]['dir'] = 'CALL' if analise[horario]['mg' + str(
                        i + 1)]['%'] == 100 else 'PUT' if analise[horario]['mg' + str(
                            i + 1)]['%'] == 0 else 'DOJI'
                    analise[horario]['mg' + str(i + 1)]['%'] = round(100 * (analise[horario]['mg' + str(i + 1)]['verde' if analise[horario]['dir'] == 'CALL' else 'vermelha'] / (
                        analise[horario]['mg' + str(i + 1)]['verde'] + analise[horario]['mg' + str(i + 1)]['vermelha'] + analise[horario]['mg' + str(i + 1)]['doji'])))
                    soma['verde'] += analise[mg_time]['verde']
                    soma['vermelha'] += analise[mg_time]['vermelha']
                    soma['doji'] += analise[mg_time]['doji']
                else:
                    analise[horario]['mg' + str(i + 1)]['%'] = 'N/A'
                posicao += 1

    return analise


@app.route('/v5', methods=['GET'])
def v5():
    # Parameters from request (you might want to handle these properly)
    par = request.args.get('par', 'EURUSD')
    dias = int(request.args.get('dias', 3))
    porcentagem = int(request.args.get('porcentagem', 100))
    timeframe = int(request.args.get('timeframe', 1))
    timezone = request.args.get('timezone', 'Asia/Kolkata')
    date = request.args.get(
        'date', datetime.now().strftime('%Y-%m-%d'))
    martingale = request.args.get('martingale', '1')

    prct_call = abs(porcentagem)
    prct_put = abs(100 - porcentagem)

    catalogacao = {par: v55(
        par, dias, prct_call, prct_put, timeframe, date, martingale, timezone)}

    results = []
    for par in catalogacao:
        for horario in sorted(catalogacao[par]):
            ok = False

            if catalogacao[par][horario]['%'] >= porcentagem:
                ok = True
            else:
                for i in range(int(martingale)):
                    if catalogacao[par][horario]['mg' + str(i + 1)]['%'] >= porcentagem:
                        ok = True
                        break

            if ok:
                result = {
                    "pair": par,
                    "time": horario,
                    "dir": catalogacao[par][horario]['dir'].strip(),
                    "percent": catalogacao[par][horario]['%']
                }
                if martingale.strip() != '':
                    result["martingale"] = []
                    for i in range(int(martingale)):
                        mg_percentual = catalogacao[par][horario]['mg' +
                                                                  str(i + 1)]['%']
                        result["martingale"].append({
                            f'mg{i+1}': i + 1,
                            "percent": mg_percentual if mg_percentual != 'N/A' else None
                        })
                results.append(result)

    return jsonify(results)


def v55(par, dias, prct_call, prct_put, timeframe, date, martingale, timezone):
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = []
    datas_testadas = []
    time_ = date_to_epoch(date)

    sair = False
    user_tz = pytz.timezone(timezone)

    while not sair:
        velas = API.get_candles(par, (timeframe * 60), 10000, time_)
        velas.reverse()

        posicao = 0
        for x in velas:
            candle_time = datetime.fromtimestamp(
                x['from'], tz=pytz.utc).astimezone(user_tz)
            if candle_time.strftime('%Y-%m-%d') != data_atual:

                if candle_time.strftime('%Y-%m-%d') not in datas_testadas:
                    datas_testadas.append(candle_time.strftime('%Y-%m-%d'))
                if len(datas_testadas) <= dias:
                    x.update({'cor': 'verde' if x['open'] < x['close']
                              else 'vermelha' if x['open'] > x['close'] else 'doji'})

                    x.update({'trend': ''})

                    data.append(x)
                else:
                    sair = True
                    break
            posicao += 1
        time_ = int(velas[-1]['from'] - 1)

    analise = {}
    for velas in data:
        horario = datetime.fromtimestamp(
            velas['from'], tz=pytz.utc).astimezone(user_tz).strftime('%H:%M')
        if horario not in analise:
            analise[horario] = {'verde': 0, 'vermelha': 0,
                                'doji': 0, '%': 0, 'dir': '', 'trend': ''}
        analise[horario][velas['cor']] += 1
        analise[horario]['trend'] = velas['trend']
        try:
            analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (
                analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
        except ZeroDivisionError:
            pass

    for horario in analise:
        if analise[horario]['%'] == 100:
            analise[horario]['dir'] = 'CALL'
        if analise[horario]['%'] == 0:
            analise[horario]['%'], analise[horario]['dir'] = 100 - \
                analise[horario]['%'], 'PUT'

    # Adding martingale calculation
    for horario in sorted(analise):
        if martingale.strip() != '':
            mg_time = horario
            soma = {'verde': analise[horario]['verde'], 'vermelha': analise[horario]
                    ['vermelha'], 'doji': analise[horario]['doji']}

            for i in range(int(martingale)):
                analise[horario].update(
                    {'mg' + str(i + 1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0}})
                mg_time = str(datetime.strptime((datetime.now()).strftime(
                    '%Y-%m-%d ') + str(mg_time), '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]

                if mg_time in analise:
                    analise[horario]['mg' +
                                     str(i + 1)]['verde'] += analise[mg_time]['verde'] + soma['verde']
                    analise[horario]['mg' +
                                     str(i + 1)]['vermelha'] += analise[mg_time]['vermelha'] + soma['vermelha']
                    analise[horario]['mg' +
                                     str(i + 1)]['doji'] += analise[mg_time]['doji'] + soma['doji']
                    analise[horario]['mg' + str(i + 1)]['%'] = round(100 * (analise[horario]['mg' + str(i + 1)]['verde' if analise[horario]['dir'] == 'CALL' else 'vermelha'] / (
                        analise[horario]['mg' + str(i + 1)]['verde'] + analise[horario]['mg' + str(i + 1)]['vermelha'] + analise[horario]['mg' + str(i + 1)]['doji'])))
                    soma['verde'] += analise[mg_time]['verde']
                    soma['vermelha'] += analise[mg_time]['vermelha']
                    soma['doji'] += analise[mg_time]['doji']
                else:
                    analise[horario]['mg' + str(i + 1)]['%'] = 'N/A'

    return analise


def date_to_epoch(date_str, time_str='00:10:00'):
    # Combine date and time strings
    full_date_str = f'{date_str} {time_str}'

    # Convert the combined string to a datetime object
    dt = datetime.strptime(full_date_str, '%Y-%m-%d %H:%M:%S')

    # Convert the datetime object to seconds since epoch
    return int(tm.mktime(dt.timetuple()))


# def trend(velas_tendencia, ema):
#     fechamento = round(velas_tendencia[0]['close'], 4)
#     df = pd.DataFrame(velas_tendencia)
#     EMA = df['close'].ewm(span=ema, adjust=False).mean()
#     for data in EMA:
#         EMA_line = data

#     if EMA_line > fechamento:
#         dir = 'vermelha'
#     elif fechamento > EMA_line:
#         dir = 'verde'
#     else:
#         dir = False

#     return dir

def run(y):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    z = loop.run_until_complete(y)
    return z


async def get_candle_v2(pair, timeframe):
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()

    if check_connect:
        candles = await client.get_candle_v2(pair, timeframe)
        columns = ["from", "open", "close", "max", "min", "volume", "to"]
        velas = [dict(zip(columns, entry)) for entry in candles]
        return velas
    else:
        return {"error": message}


@app.route('/q', methods=['POST'])
def get_candles():
    data = request.get_json()
    pair = data.get('pair')
    timeframe = data.get('timeframe')

    if not pair or not timeframe:
        return jsonify({"error": "Missing 'pair' or 'timeframe' parameter"}), 400

    try:
        candles = run(get_candle_v2(pair, timeframe))
        return jsonify(candles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
