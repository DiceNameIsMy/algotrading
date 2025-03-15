from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import pandas as pd
from pandas import Series
from scipy import signal

from poly_datasets import PMDataset


def compute_delta_correlation(
    pm_data: list[PMDataset],
    deltas: Series,
    offset_amplitude: int = 3,
) -> list[list[np.ndarray]]:
    corr_offsets = range(-offset_amplitude, offset_amplitude + 1)

    corr_data = []
    for i in range(len(pm_data)):
        poly_delta = pm_data[i].delta
        BTC_delta = deltas[i]

        col_corr_data = []
        for offset in corr_offsets:
            offset_poly_delta = np.roll(poly_delta, offset)
            offset_BTC_delta = BTC_delta

            if offset > 0:
                offset_poly_delta = offset_poly_delta[offset:]
                offset_BTC_delta = BTC_delta[offset:]
            elif offset < 0:
                offset_poly_delta = offset_poly_delta[:offset]
                offset_BTC_delta = BTC_delta[:offset]

            correlation_with_offset = np.corrcoef(offset_BTC_delta, offset_poly_delta)[
                0, 1
            ]

            col_corr_data.append(correlation_with_offset)
        corr_data.append(col_corr_data)

    return corr_data


def plot_delta_correlation(
    markets: list[PMDataset],
    binance_df: pd.DataFrame,
    corr_coef: list[list[np.ndarray]],
    offset_amplitude: int,
):
    """
    Computes correlations between poly data and cryptocurrency
    price change and makes its plot.

    If plot is high with a negative offset, it means that
    cryptocurrency price change is leading the polymarket share price change.

    Only markets with correlation coefficient above 0.1 are plotted.
    """
    corr_offsets = range(-offset_amplitude, offset_amplitude + 1)

    # Plot the data
    width = 10
    height = 2.8 * len(markets)

    fig, axes = plt.subplots(figsize=(width, height), ncols=3, nrows=len(markets))

    if len(markets) == 1:
        axes = np.array([axes])

    for i, data in enumerate(markets):

        # Plot offsetted correlations
        left_ax: Axes = axes[i][0]
        left_ax.plot(corr_offsets, corr_coef[i], marker="o")
        left_ax.set_title(data.label)
        left_ax.set_xlabel("Offset")
        left_ax.set_ylabel("Corr. coef.")
        left_ax.set_ylim(-1, 1)
        left_ax.grid(True)

        binance_open = binance_df.loc[data.index, "Open"]

        # Plot polymarket probability
        if len(data.index) > 200:
            q = len(data.index) // 100
            poly_y = signal.decimate(data.open, q)
            binance_y = signal.decimate(binance_open, q)
            x = data.index[::q]
            binance_x = binance_open.index[::q]
        else:
            poly_y = data.open
            binance_y = binance_open
            x = data.index
            binance_x = binance_open.index

        outcome = markets[i].resolved_as
        if outcome == "yes":
            color = "green"
        elif outcome == "no":
            color = "red"
        elif outcome == "unknown":
            color = "blue"
        else:
            color = "black"
            print(f"Unknown outcome for market {markets[i].label}: {outcome}")

        mid_ax: Axes = axes[i][1]
        mid_ax.plot(x, poly_y, color=color)
        mid_ax.set_title("Poly probability")
        mid_ax.set_xlabel("Time")
        mid_ax.set_xticks(mid_ax.get_xticks())
        mid_ax.set_xticklabels(mid_ax.get_xticklabels(), rotation=45)
        mid_ax.set_ylabel("Probability")
        mid_ax.set_ylim(0, 1)
        mid_ax.grid(True)

        right_ax: Axes = axes[i][2]
        right_ax.plot(binance_x, binance_y)
        right_ax.set_title("Price on binance")
        right_ax.set_xlabel("Time")
        right_ax.set_xticks(right_ax.get_xticks())
        right_ax.set_xticklabels(right_ax.get_xticklabels(), rotation=45)
        right_ax.set_ylabel("USD")
        right_ax.grid(True)

    plt.tight_layout()
    plt.show()
