from matplotlib import pyplot as plt
import numpy as np
from sklearn.preprocessing import MaxAbsScaler
from binance_datasets import load_binance_dataset
from poly_datasets import PMDataset


def plot_delta_correlation(
    pm_data: list[PMDataset], interval: str, corr_amplitude: int = 3
):
    """
    Computes correlations between poly data and cryptocurrency
    price change and makes its plot.

    If plot is high with a negative offset, it means that
    cryptocurrency price change is leading the polymarket share price change.
    """

    # Load data from binance
    start_date = min(pm_data, key=lambda d: d.date_from).date_from.isoformat()
    end_date = max(pm_data, key=lambda d: d.date_to).date_to.isoformat()

    binance_df = load_binance_dataset("BTCUSDT", interval, start_date, end_date)

    # Merge pm and binance data
    pm_datasets = []
    deltas = []
    binance_deltas = []
    for data in pm_data:
        if len(data.open) < corr_amplitude * 2:
            print(f"Skipping {data.label} due to insufficient data")
            continue

        binance_delta = binance_df.loc[data.index, "delta"]

        scaler = MaxAbsScaler()

        # delta = scaler.fit_transform(data.delta.reshape(-1, 1)).flatten()
        deltas.append(data.delta)

        binance_delta = scaler.fit_transform(
            binance_delta.values.reshape(-1, 1)
        ).flatten()
        binance_deltas.append(binance_delta)

        pm_datasets.append(data)

    # Compute correlations with offset
    corr_offsets = range(-corr_amplitude, corr_amplitude + 1)
    corr_data = []
    for i in range(len(pm_datasets)):
        data: PMDataset = pm_datasets[i]
        delta = deltas[i]
        BTC_delta = binance_deltas[i]

        col_corr_data = []
        for offset in corr_offsets:
            offset_poly_delta = np.roll(delta, offset)
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

    # Plot the data
    fig, axes = plt.subplots(
        nrows=len(pm_datasets), ncols=2, figsize=(10, 2.8 * len(pm_datasets))
    )

    if len(pm_datasets) == 1:
        axes = np.array([axes])

    for i, data in enumerate(pm_datasets):

        # Plot offsetted correlations
        axes[i][0].plot(corr_offsets, corr_data[i], label=data.label, marker='o')
        axes[i][0].set_title("Correlation with offset")
        axes[i][0].set_xlabel("Offset")
        axes[i][0].set_ylabel("Corr. coef.")
        axes[i][0].set_ylim(-1, 1)
        axes[i][0].legend()
        axes[i][0].grid(True)

        # Plot polymarket probability
        axes[i][1].plot(data.index, data.open, label=f"open_{data.label}")
        axes[i][1].set_title("Polymarket probability")
        axes[i][1].set_xlabel("Time")
        axes[i][1].set_xticks(axes[i][1].get_xticks())
        axes[i][1].set_xticklabels(axes[i][1].get_xticklabels(), rotation=45)
        axes[i][1].set_ylabel("Probability")
        axes[i][1].legend()
        axes[i][1].grid(True)

    plt.tight_layout()
    plt.show()
