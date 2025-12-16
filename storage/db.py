import sqlite3
from pathlib import Path
import pandas as pd

    

DB_PATH = Path("data/market_data.db")

class MarketDataDB:
    def __init__(self):
        DB_PATH.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False,
            timeout=30
        )
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS ticks (
            timestamp TEXT,
            symbol TEXT,
            price REAL,
            qty REAL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def insert_ticks(self, ticks):
        query = """
        INSERT INTO ticks (timestamp, symbol, price, qty)
        VALUES (?, ?, ?, ?)
        """
        rows = [
            (t["timestamp"].isoformat(), t["symbol"], t["price"], t["qty"])
            for t in ticks
        ]
        self.conn.executemany(query, rows)
        self.conn.commit()
        
    def fetch_ticks(self, symbols, lookback_minutes=30):
        query = f"""
        SELECT timestamp, symbol, price, qty
        FROM ticks
        WHERE symbol IN ({','.join(['?']*len(symbols))})
        AND timestamp >= datetime('now', ?)
        ORDER BY timestamp
        """
        params = symbols + [f"-{lookback_minutes} minutes"]
        df = pd.read_sql_query(query, self.conn, params=params)
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            format="ISO8601",
            utc=True,
            errors="coerce"
        )

        return df