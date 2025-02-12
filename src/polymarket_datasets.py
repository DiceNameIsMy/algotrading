import pandas as pd


def load_pm_dataset(filename: str):
    pm_df = pd.read_csv(
        f"../data/{filename}", parse_dates=["Date (UTC)"], index_col="Date (UTC)"
    )
    # pm_df = pm_df.fillna(1)

    bet_cols = pm_df.columns[pm_df.columns.str.startswith("$")]

    new_bet_cols = [col.split(",")[0].split("$")[1] for col in bet_cols]

    rename_mapping = {f"${col},000": col for col in new_bet_cols}
    pm_df = pm_df.rename(columns=rename_mapping)

    for column in new_bet_cols:
        # Compute how probability had changed after 1 day
        pm_df[f"open_{column}"] = pm_df[column]
        pm_df[f"close_{column}"] = pm_df[column].shift(-1)
        pm_df[f"delta_{column}"] = pm_df[f"close_{column}"] - pm_df[f"open_{column}"]

    pm_df = pm_df.drop(columns=new_bet_cols)

    return pm_df
