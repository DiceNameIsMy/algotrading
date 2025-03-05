import os
from datetime import datetime

from dotenv import load_dotenv

import pandas as pd
from py_clob_client.client import get
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient

load_dotenv()

POLY_HOST = "https://clob.polymarket.com"
POLY_PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")


class MyClobClient(ClobClient):
    def get_timeseries(
        self,
        market: str,
        fidelity_in_minutes: int,
    ):
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
        request_url = "{}{}?market={}&interval={}&fidelity={}".format(
            self.host,
            "/prices-history",
            market,
            "max",
            fidelity_in_minutes,
        )
        return get(request_url)


poly_client = MyClobClient(POLY_HOST, key=POLY_PRIVATE_KEY, chain_id=POLYGON)
poly_client.set_api_creds(poly_client.create_or_derive_api_creds())


def get_poly_timeseries(condition_id: str, fidelity_in_minutes: int) -> pd.DataFrame:
    market = poly_client.get_market(condition_id)

    data = None
    for token in market["tokens"]:
        token_id = token["token_id"]
        outcome = token["outcome"]
        ts = poly_client.get_timeseries(token_id, fidelity_in_minutes)["history"]
        prob = [x["p"] for x in ts]
        timestamps = [datetime.fromtimestamp(x["t"]) for x in ts]

        if data is None:
            data = pd.DataFrame(index=timestamps)
            data.index.name = "date"

        data[outcome] = prob

    return data
