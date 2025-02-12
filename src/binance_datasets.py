from dotenv import load_dotenv
import os

from binance import Client
import pandas as pd

# Load environment variables
load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

KLINES_COLUMNS = [
    "Open Time",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Close Time",
    "Quote Asset Volume",
    "Number of Trades",
    "Taker Buy Base Asset Volume",
    "Taker Buy Quote Asset Volume",
    "Ignore",
]
NUMERIC_KLINES_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Quote Asset Volume",
    "Taker Buy Base Asset Volume",
    "Taker Buy Quote Asset Volume",
]

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def load_binance_dataset(symbol: str, interval: str, start: str, end: str):
    data = client.get_historical_klines(
        symbol=symbol, interval=interval, start_str=start, end_str=end
    )

    BTC_df = pd.DataFrame(data, columns=KLINES_COLUMNS)

    BTC_df["Open Time"] = pd.to_datetime(BTC_df["Open Time"], unit="ms")
    BTC_df["Close Time"] = pd.to_datetime(BTC_df["Close Time"], unit="ms")

    BTC_df[NUMERIC_KLINES_COLUMNS] = BTC_df[NUMERIC_KLINES_COLUMNS].astype(float)

    BTC_df["delta"] = BTC_df["Close"] - BTC_df["Open"]

    BTC_df = BTC_df.set_index("Open Time")

    return BTC_df
