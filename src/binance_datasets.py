from datetime import datetime
import os
from functools import lru_cache

from dotenv import load_dotenv

from binance import Client
import pandas as pd

from data import FIDELITY_MAPPING
from poly_datasets import PMDataset

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


@lru_cache()
def load_binance_dataset(symbol: str, fidelity: str, start: datetime, end: datetime):
    data = client.get_historical_klines(
        symbol=symbol,
        interval=FIDELITY_MAPPING[fidelity],
        start_str=start.isoformat(),
        end_str=end.isoformat(),
    )

    BTC_df = pd.DataFrame(data, columns=KLINES_COLUMNS)

    BTC_df["Open Time"] = pd.to_datetime(BTC_df["Open Time"], unit="ms")
    BTC_df["Close Time"] = pd.to_datetime(BTC_df["Close Time"], unit="ms")

    BTC_df[NUMERIC_KLINES_COLUMNS] = BTC_df[NUMERIC_KLINES_COLUMNS].astype(float)

    BTC_df["delta"] = BTC_df["Close"] - BTC_df["Open"]

    BTC_df = BTC_df.set_index("Open Time")

    return BTC_df


def load_matching_binance_data(pm_data: list[PMDataset], fidelity: int, currency: str):
    # Load data from binance
    start_date = min(pm_data, key=lambda d: d.date_from).date_from
    end_date = max(pm_data, key=lambda d: d.date_to).date_to

    print(f"Loading from binance at intervals: from {start_date} until {end_date}")

    binance_df = load_binance_dataset(currency, fidelity, start_date, end_date)

    return binance_df
