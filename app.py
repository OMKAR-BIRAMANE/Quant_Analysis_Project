# import asyncio
# from ingestion.websocket_client import BinanceWebSocketClient
# from storage.db import MarketDataDB
# from storage.resampler import resample_ticks
# from analytics.spread_ols import compute_hedge_ratio, compute_spread
# from analytics.zscore import compute_zscore
# from analytics.rolling_corr import compute_rolling_corr

# tick_buffer = []
# db = MarketDataDB()

# async def flush_to_db(interval=5):
#     while True:
#         await asyncio.sleep(interval)
#         if tick_buffer:
#             print(f"💾 Flushing {len(tick_buffer)} ticks to DB")
#             db.insert_ticks(tick_buffer.copy())
#             tick_buffer.clear()
# # async def test_analytics():
# #     await asyncio.sleep(20)

# #     df = db.fetch_ticks(["BTCUSDT", "ETHUSDT"])
# #     bars = resample_ticks(df, "1s")

# #     btc = bars["BTCUSDT"]["close"]
# #     eth = bars["ETHUSDT"]["close"]

# #     beta = compute_hedge_ratio(btc, eth)
# #     spread = compute_spread(btc, eth, beta)
# #     zscore = compute_zscore(spread)
# #     corr = compute_rolling_corr(btc, eth)

# #     print(f"\nHedge Ratio (BTC ~ ETH): {beta:.4f}")
# #     print("\nLatest Spread:")
# #     print(spread.tail())
# #     print("\nLatest Z-Score:")
# #     print(zscore.tail())
# #     print("\nLatest Rolling Correlation:")
# #     print(corr.tail())

# async def main():
#     symbols = ["BTCUSDT", "ETHUSDT"]
#     ws_client = BinanceWebSocketClient(symbols, tick_buffer)

#     await asyncio.gather(
#         ws_client.connect(),
#         flush_to_db(),
#         # test_analytics()
#         # test_resample()
#     )


# # async def test_resample():
# #     await asyncio.sleep(15)  # wait for data
# #     df = db.fetch_ticks(["BTCUSDT", "ETHUSDT"])
# #     bars = resample_ticks(df, "1S")
# #     for sym, data in bars.items():
# #         print(f"\n{sym} 1S bars:")
# #         print(data.tail())


# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
import threading
import streamlit as st

from ingestion.websocket_client import BinanceWebSocketClient
from storage.db import MarketDataDB
from frontend.dashboard import run_dashboard

tick_buffer = []
db = MarketDataDB()

async def flush_to_db(interval=5):
    while True:
        await asyncio.sleep(interval)
        if tick_buffer:
            db.insert_ticks(tick_buffer.copy())
            tick_buffer.clear()

async def start_ingestion():
    symbols = ["BTCUSDT", "ETHUSDT"]
    ws_client = BinanceWebSocketClient(symbols, tick_buffer)
    await asyncio.gather(
        ws_client.connect(),
        flush_to_db()
    )

def start_background_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_ingestion())

if __name__ == "__main__":
    threading.Thread(target=start_background_loop, daemon=True).start()
    run_dashboard()
