import asyncio
import json
import websockets
from datetime import datetime

BINANCE_WS_URL = "wss://fstream.binance.com/ws"

class BinanceWebSocketClient:
    def __init__(self, symbols, tick_buffer):
        self.symbols = symbols
        self.tick_buffer = tick_buffer

    async def connect(self):
        streams = "/".join([f"{sym.lower()}@trade" for sym in self.symbols])
        url = f"{BINANCE_WS_URL}/{streams}"

        async with websockets.connect(url) as ws:
            print("✅ Connected to Binance WebSocket")
            async for message in ws:
                self.on_message(message)

    def on_message(self, message):
        data = json.loads(message)

        tick = {
            "timestamp": datetime.fromtimestamp(data["T"] / 1000),
            "symbol": data["s"],
            "price": float(data["p"]),
            "qty": float(data["q"]),
        }

        self.tick_buffer.append(tick)
