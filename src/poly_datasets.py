from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd


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
