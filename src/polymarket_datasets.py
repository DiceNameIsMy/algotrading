from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd


@dataclass
class PMDataset:
    label: str
    date_from: datetime
    date_to: datetime

    index: pd.DatetimeIndex
    open: np.ndarray
    close: np.ndarray
    delta: np.ndarray


def _load_pm_dataset(filename: str) -> pd.DataFrame:
    pm_df = pd.read_csv(
        f"../data/{filename}", parse_dates=["Date (UTC)"], index_col="Date (UTC)"
    )
    bet_cols = pm_df.columns[pm_df.columns.str.startswith("$")]
    new_bet_cols = [col.split(",")[0].split("$")[1] for col in bet_cols]

    rename_mapping = {f"${col},000": col for col in new_bet_cols}
    rename_mapping["Date (UTC)"] = "date"

    pm_df = pm_df.rename(columns=rename_mapping).drop(columns=["Timestamp (UTC)"])

    return pm_df


def load_pm_dataset(filename: str) -> list[PMDataset]:
    pm_df = _load_pm_dataset(filename)

    result = []

    for column in pm_df.columns:

        # Find the time window where values exist
        non_nan_idxs = pm_df[column].dropna().index
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
                index=open_data[:-1].index,
                open=open_data[:-1].values,
                close=close_data[:-1].values,
                delta=delta_data[:-1].values,
            )
        )

    return result
