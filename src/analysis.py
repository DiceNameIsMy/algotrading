from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from pandas import Series
from scipy import signal
from binance_datasets import load_binance_dataset
from poly_datasets import PMDataset
from data import FIDELITY_MAPPING


def load_mathing_binance_data(pm_data: list[PMDataset], fidelity: int):
    # Load data from binance
    start_date = min(pm_data, key=lambda d: d.date_from).date_from.isoformat()
    end_date = max(pm_data, key=lambda d: d.date_to).date_to.isoformat()

    binance_df = load_binance_dataset(
        "BTCUSDT", FIDELITY_MAPPING[fidelity], start_date, end_date
    )

    return binance_df


def compute_delta_correlation(
    pm_data: list[PMDataset],
    deltas: Series,
    offset_amplitude: int = 3,
) -> tuple[list, range]:
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

    return corr_data, corr_offsets


def plot_delta_correlation(
    pm_data: list[PMDataset], fidelity: int, corr_amplitude: int = 3
):
    """
    Computes correlations between poly data and cryptocurrency
    price change and makes its plot.

    If plot is high with a negative offset, it means that
    cryptocurrency price change is leading the polymarket share price change.
    """

    # Load data from binance
    binance_df = load_mathing_binance_data(pm_data, fidelity)

    # Merge pm and binance data
    poly_datasets_to_process: list[PMDataset] = []
    binance_deltas = []

    for data in pm_data:
        if len(data.open) < corr_amplitude * 2:
            print(f"Skipping {data.label} due to insufficient data")
            continue

        binance_delta = binance_df.loc[data.index, "delta"]

        # rescaled_binance_delta = binance_delta / binance_delta.abs().max()
        binance_deltas.append(binance_delta)

        poly_datasets_to_process.append(data)

    # Compute correlations with offset
    corr_data, corr_offsets = compute_delta_correlation(
        poly_datasets_to_process, binance_deltas, corr_amplitude
    )

    # Plot the data
    width = 10
    height = 2.8 * len(poly_datasets_to_process)

    fig, axes = plt.subplots(
        figsize=(width, height), ncols=2, nrows=len(poly_datasets_to_process)
    )

    if len(poly_datasets_to_process) == 1:
        axes = np.array([axes])

    for i, data in enumerate(poly_datasets_to_process):

        # Plot offsetted correlations
        left_ax: Axes = axes[i][0]
        left_ax.plot(corr_offsets, corr_data[i], label=data.label, marker="o")
        left_ax.set_title("Correlation with offset")
        left_ax.set_xlabel("Offset")
        left_ax.set_ylabel("Corr. coef.")
        left_ax.set_ylim(-1, 1)
        left_ax.legend()
        left_ax.grid(True)

        # Plot polymarket probability
        if len(data.index) > 200:
            q = len(data.index) // 100
            y = signal.decimate(data.open, q)
            x = data.index[::q]
        else:
            y = data.open
            x = data.index

        right_ax: Axes = axes[i][1]
        right_ax.plot(x, y, label=f"open_{data.label}")
        right_ax.set_title("Poly probability")
        right_ax.set_xlabel("Time")
        right_ax.set_xticks(right_ax.get_xticks())
        right_ax.set_xticklabels(right_ax.get_xticklabels(), rotation=45)
        right_ax.set_ylabel("Probability")
        right_ax.set_ylim(0, 1)
        right_ax.legend()
        right_ax.grid(True)

    plt.tight_layout()
    plt.show()
