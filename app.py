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


async def get_candle_v2(pair, timeframe):
    email = "govindkhapare2001@gmail.com"
    password = "Akshay@2001"
    client = Quotex(email=email,
                    password=password,
                    headless=False)
    client.debug_ws_enable = False
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    if check_connect:
        candles = await client.get_candle_v2(pair, timeframe)
        columns = ["from", "open", "close", "max", "min", "volume", "to"]
        velas = [dict(zip(columns, entry)) for entry in candles]
        return velas
    return []


@app.route('/candles', methods=['GET'])
async def get_candles():
    pair = request.args.get('pair')
    timeframe = int(request.args.get('timeframe'))
    if pair and timeframe:
        candles = await get_candle_v2(pair, timeframe)
        return jsonify(candles)
    else:
        return jsonify({'error': 'pair and timeframe are required'}), 400

if __name__ == '__main__':
    app.run(debug=True)
