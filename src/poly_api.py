import os
from dataclasses import dataclass
from functools import lru_cache
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

import pandas as pd
from py_clob_client.client import get
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient

load_dotenv()

POLY_HOST = "https://clob.polymarket.com"
POLY_PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")


@dataclass(frozen=True)
class TSOptions:
    fidelity_in_minutes: int
    interval_to_load: tuple[datetime, datetime]


class MyClobClient(ClobClient):
    def get_timeseries(self, market: str, options: TSOptions):
        """
        Parameters:
            market: aka token_id
            start_ts
            end_ts
            fidelity

        Returns:
            TODO
        """

        # Source: https://docs.polymarket.com/#timeseries-data
        request_url = f"{self.host}/prices-history?market={market}"
        request_url += f"&fidelity={options.fidelity_in_minutes}"
        request_url += f"&startTs={int(options.interval_to_load[0].timestamp())}"
        request_url += f"&endTs={int(options.interval_to_load[1].timestamp())}"

        return get(request_url)


poly_client = MyClobClient(POLY_HOST, key=POLY_PRIVATE_KEY, chain_id=POLYGON)
poly_client.set_api_creds(poly_client.create_or_derive_api_creds())


@lru_cache(maxsize=128)
def get_poly_timeseries(condition_id: str, options: TSOptions) -> pd.DataFrame:
    market = poly_client.get_market(condition_id)

    data = None
    for token in market["tokens"]:
        token_id = token["token_id"]
        outcome = token["outcome"]

        response = poly_client.get_timeseries(token_id, options)

        ts = response["history"]
        prob = [x["p"] for x in ts]

        # TODO: Replacing might hurt the data. Consider not using it.
        # Dates sometimes looks like 2021-10-01T00:00:03,
        # but binance data is like 2021-10-01T00:00:00.
        # because of that it's not possible to join the dataframes.
        # I consider rounding in that case to be insignificant.
        timestamps = [
            datetime.fromtimestamp(x["t"], tz=timezone.utc).replace(
                second=0, microsecond=0, tzinfo=None
            )
            for x in ts
        ]

        if data is None:
            data = pd.DataFrame(index=timestamps)
            data.index.name = "date"

        data[outcome] = prob

    return data


def load_market_data(market_id: str, options: TSOptions) -> pd.DataFrame | None:
    market = poly_client.get_market(market_id)

    # Load the data in max. 15 day intervals. Polymarket does not give data otherwise.
    start, end = options.interval_to_load
    delta = timedelta(days=15)
    intervals = []

    while start < end:
        if (start + delta) > end:  # Interval is smaller than 15 days
            intervals.append((start, end))
        else:
            intervals.append((start, start + delta))

        start = start + delta

    market_data: pd.DataFrame | None = None
    for interval in intervals:
        interval_options = TSOptions(
            fidelity_in_minutes=options.fidelity_in_minutes,
            interval_to_load=interval,
        )
        df = get_poly_timeseries(market_id, interval_options).copy()

        df.rename(columns={"Yes": market["market_slug"]}, inplace=True)
        df.drop(columns=["No"], inplace=True)
        if df.empty:
            continue

        if market_data is None:
            market_data = df
        else:
            market_data = pd.concat([market_data, df])

    if market_data is None:
        print(
            f"Didn't find any data for market `{market_id[:10]}...`, ",
            f"slug: `{market['market_slug']}"
        )

    return market_data


def load_markets_data(market_ids: list[str], options: TSOptions) -> pd.DataFrame:
    all_markets_data: pd.DataFrame | None = None

    for market_id in market_ids:
        market_data = load_market_data(market_id, options)
        if market_data is None:
            continue

        if all_markets_data is None:
            all_markets_data = market_data
        else:
            all_markets_data = pd.concat([all_markets_data, market_data], axis=1)

    return all_markets_data
