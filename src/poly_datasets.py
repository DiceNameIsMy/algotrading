from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd


all_markets: list["Market"] = []


@dataclass
class Market:
    date_from: datetime
    date_to: datetime
    market_ids: list[str]

    def __post_init__(self):
        all_markets.append(self)


class Markets:
    # https://polymarket.com/event/what-price-will-bitcoin-hit-in-january?tid=1742039982785
    what_price_will_bitcoin_hit_in_january = Market(
        datetime.fromisoformat("2025-01-02 19:00"),
        datetime.fromisoformat("2025-01-30 23:00"),
        [
            "0xc2c1038424a37a044781d1915e82ddbea1515d79cdb8966a2bf0a658b178b21c",
            "0x69c7ea583787dee4228468864414f33c84c3ab58c2eaba37ca7a5c0aed4e899e",
            "0xd7fa09afd9c184f94edb6f15f5f98640dc3f5418ffbd520a10ef3f4775414c73",
            "0x78dd44195111f89210b059180792a1fa156d1f211392e76575dc36846e815987",
            "0x7c662197ecf9c6c2441c1cb57e8c8a761a5782eeb0c219dc14daf3f165d188a1",
            "0x0f3131c874579825ecdbbda8c7aeed071aa908d7c993792c393285900e68906f",
            "0x44c5b4d851e8c06698c13b54e8ba33e37637e13bdb3f375ce0b6727b2aa06b48",
            "0x0bdabf234110590a6475e88f386ec7512f0f0d8038989e39259f0eb995650594",
            "0xcdab757d22e9ca242163475ed1426e6a8d2c9a579b39198f7cec223024ee2e89",
            "0x8d29692749f246da11fb329a2ecaf95d08cc6c97d3f8ebe0c052d1ce42057595",
            "0xda728da52dda8a465dd49a1e9a6daa000b2116bd799b18ec383c68e68c693bda",
            "0x263c7f77dc9cc2a68ce238794051b4801ae0d0aa0b1242a54726a8860a1809e8",
            "0xd100eaa5eb47d06b9f3f4ff37ad34c1e588b3f322cd8d7d408c379a2ce3ea03e",
            "0x906a2b90f30c62e09dce56fababafafbc4338cb8dac94ac6c3038327d0447180",
        ],
    )

    # https://polymarket.com/event/bitcoin-price-on-march-14?tid=1742032413563
    bitcoin_price_on_march_7 = Market(
        datetime.fromisoformat("2025-02-28 19:00"),
        datetime.fromisoformat("2025-03-07 22:00"),
        [
            "0x845afc0daac64d1d5d955e39b3c4763c271b90c13d84593479b9fbe7b794030b",
            "0x7ce43fde974369950c4c8c1c37649f6ce0f8e7017153f15ba71f32ebb2ac4595",
            "0x9aa80760a847e9a85dada5010081ffcd8b597d9b1578a07707b7dcf7b53a9ebd",
            "0xf31c8ef606ed3dbf4ba7fca3ca59d7acba59aa8326a94b57a02d35ef0dc58521",
            "0x16a61d52c743f876b6abc7ffa6baa94ad27f0eeaa01412c89b8dab8ddd519665",
            "0xaf2cef753e5f289fbd9c912c6026f14d46dcacdc7773bf3521b0edb08d8c727f",
            "0xbb0224941da5cce71e72eab569f6b71cb6e3a6ac9e6da1f784c5e5cffdf29757",
        ],
    )
    # https://polymarket.com/event/bitcoin-price-on-march-14?tid=1742032413563
    bitcoin_price_on_march_14 = Market(
        datetime.fromisoformat("2025-03-07 18:00"),
        datetime.fromisoformat("2025-03-14 21:00"),
        [
            "0xd9fc380bb3c5c06e3b332d7a5d3051ee0b74d3e51dc9676c5bb6b5055ce92f6d",
            "0xea348e8bfe03af4a195286ffe25f0f733c2d54fe50f9d54835e6775f6613aa9a",
            "0x4e720ef02e20df66202c30f53d4d1b233ebe4fd6da023b2468026f4f29102ac1",
            "0x64565382a32c6f61639e1fdb33ba6f93115511c027882acedc7414c402a9cb8f",
            "0x2f9f585b5f816394fc36677d676ab643cb7b05b6db31a0bdb7e6338fc33c93ca",
            "0xe85f139d7a784177f3861d3e650b6031a45ff16454a513ba212a3ac19b44e426",
            "0x80bfbfba1a642809b7dadc738f960b3ca19fef3b0c0f6b8f00670b268f6416f3",
        ],
    )
    # https://polymarket.com/event/what-price-will-ethereum-hit-in-february
    what_price_will_ethereum_hit_in_february = Market(
        datetime.fromisoformat("2025-02-15 13:00"),
        datetime.fromisoformat("2025-03-01 08:00"),
        [
            "0x801d91039a80a3a37051d6d764ce86993fbc72cbc06d181181140bddf805e229",
            "0x809e6669b05b2638a5edd2976ba29826abd658ea8a1ca84f2264832524435283",
            "0x6d8fa015af65a82464488cd749d6d8ceabbd13a50d271c1150ed4a1e46ac4866",
            "0x46fa9fac90e98d6374fbb184de654f3db0bc62422ef8437608a33dff96bb8264",
            "0x8ebfb8c9e14a3c655052282a1f54e48478b17f650c99d7d21a50dc3ded14644a",
            "0x9ba01d345a01ddc6c4e9618a710a01d3a4e0e6733f1a220128c912c2fc6d941d",
            "0x2eb5474300ef53d1484ad877798347e4d891b2b055af7ba5c0cec72c49f023b9",
            "0x86d6cfbfea488fc92fd0a6671938aa7e78995029183b1fadcfda36957acbbd61",
            "0x58b1424e159fec117d4bb7d8b50fdcb887c06e8212a752a0188a0d928b58ff9e",
            "0xff68e0a5f17dcc0dab8646c623fe9a301a128fc8e0f32d64f978ad027fe26bd8",
            "0xd70a0cbbfaf8cec20a3df55b9129b15e57875f3f2e6978807b784107a6214d2a",
            "0x60a1de8082178cbd00c3e9e664a256e189d09b293bda730317e249ca8c0f553b",
            "0x10ca979276d1cf3f4c9325b25c5fd565ff56ee8f914372570590e5c6e1ca8953",
        ],
    )


@dataclass
class PolyOrderBookLogs:
    date_from: datetime
    date_to: datetime

    index: pd.DatetimeIndex
    ask: float
    bid: float


@dataclass
class PMDataset:
    label: str
    date_from: datetime
    date_to: datetime
    resolved_as: str  # "yes" or "no" or "unknown"

    index: pd.DatetimeIndex
    open: np.ndarray
    close: np.ndarray
    delta: np.ndarray

    def subset(self, start: datetime, end: datetime):
        start_idx = self.index.get_loc(start)
        end_idx = self.index.get_loc(end)
        return PMDataset(
            label=self.label,
            date_from=start,
            date_to=end,
            resolved_as=self.resolved_as,
            index=self.index[start_idx : end_idx + 1],
            open=self.open[start_idx : end_idx + 1],
            close=self.close[start_idx : end_idx + 1],
            delta=self.delta[start_idx : end_idx + 1],
        )


@dataclass
class PolyEventData:
    label: str
    date_from: datetime
    date_to: datetime

    markets_data: list[PMDataset]


def _load_pm_dataset(filename: str) -> pd.DataFrame:
    pm_df = (
        pd.read_csv(
            f"../data/{filename}", parse_dates=["Date (UTC)"], index_col="Date (UTC)"
        )
        .rename(columns={"Date (UTC)": "date"})
        .drop(columns=["Timestamp (UTC)"])
    )
    outcomes = {col: "unknown" for col in pm_df.columns}

    pm_df.attrs["outcomes"] = outcomes

    return pm_df


def process_pm_df(pm_df: pd.DataFrame) -> list[PMDataset]:
    result = []

    for column in pm_df.columns:

        # Find the time window where values exist
        non_nan_idxs = pm_df[column].dropna().index
        if non_nan_idxs.empty:
            print(f"Column {column} has no data. Skipping")
            continue

        start = non_nan_idxs.min()
        end = non_nan_idxs[-1]

        open_data = pm_df[column][start:end]
        close_data = pm_df[column][start:end].shift(-1)
        delta_data = close_data - open_data

        result.append(
            PMDataset(
                label=column,
                date_from=start,
                date_to=end,
                resolved_as=pm_df.attrs["outcomes"][column],
                index=open_data[:-1].index,
                open=open_data[:-1].values,
                close=close_data[:-1].values,
                delta=delta_data[:-1].values,
            )
        )

    return result


def load_pm_dataset(filename: str) -> list[PMDataset]:
    pm_df = _load_pm_dataset(filename)

    return process_pm_df(pm_df)
