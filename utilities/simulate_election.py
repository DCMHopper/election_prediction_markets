import pandas as pd
import numpy as np
import os
import argparse
from itertools import repeat

# Messy data loading to account for irregular updates
# TODO: make this all a mysql database or something

df_college = pd.read_csv("datasets/electoral_college.csv")
# df_data = pd.read_csv('datasets/dummy_data.csv')
data_path = "datasets/observed"
data_files = os.listdir(data_path)
timestamped_files = {int(file[:10]): file for file in data_files}
most_recent_data = timestamped_files[max(timestamped_files)]
df_data = pd.read_csv(os.path.join(data_path, most_recent_data))

# Vectorized a single run, but not the monte carlo
# This code only here for posterity
#
# def run_election(data) -> int:
#     votes: int = 0
#     randoms = np.random.random(size=len(data))
#     condition_mask = data['Value'] >= randoms
#     votes = data.loc[condition_mask, 'Votes'].sum()
#     return int(votes)

# def monte_election(preds, weights, generations) -> float:
#     wins: int = 0
#     THRESHOLD: int = 270
#     data = pd.merge(preds,weights,how='inner')
#     for _ in repeat(None,generations):
#         if run_election(data) >= THRESHOLD: wins+=1

#     return wins / generations


# Helper function to pad investment data
def pad_investment_data(data, investment_data):
    all_states = data["State"].values
    investment_states = investment_data["State"].values
    missing_states = set(all_states) - set(investment_states)

    # Create a dataframe with missing states and zero investments
    missing_data = pd.DataFrame(
        {"State": list(missing_states), "Investment": [0] * len(missing_states)}
    )

    # Concatenate the original investment data with the missing data
    padded_investment_data = pd.concat(
        [investment_data, missing_data], ignore_index=True
    )
    padded_investment_data = (
        padded_investment_data.set_index("State").reindex(data["State"]).reset_index()
    )
    return padded_investment_data


# Main election simulation function
def monte_election_batched(data, n_runs=10000, batch_size=10000, investment_data=None):
    wins: int = 0
    total_votes: int = 0
    THRESHOLD: int = 270
    STATE_COUNT: int = 51  # Include DC, but not ME1,2 or NE1,2

    n_batches = n_runs // batch_size
    remainder_runs = n_runs % batch_size
    win_contributions = np.zeros(STATE_COUNT)

    roi_total = 0
    roi_greater_count = 0
    if investment_data is not None:
        investment_data = pad_investment_data(data, investment_data)
        total_investment = investment_data["Investment"].sum()
    else:
        total_investment = 0

    # Batches run sequentially - adjust n_batches if hardware is a limitation
    for _ in repeat(None, n_batches):
        batch_wins, batch_sum, batch_contributions, batch_roi, batch_roi_greater = (
            process_batch(data, THRESHOLD, batch_size, investment_data)
        )
        wins += batch_wins
        total_votes += batch_sum
        win_contributions += batch_contributions
        roi_total += batch_roi
        roi_greater_count += batch_roi_greater

    if remainder_runs > 0:
        batch_wins, batch_sum, batch_contributions, batch_roi, batch_roi_greater = (
            process_batch(data, THRESHOLD, remainder_runs, investment_data)
        )
        wins += batch_wins
        total_votes += batch_sum
        win_contributions += batch_contributions
        roi_total += batch_roi
        roi_greater_count += batch_roi_greater

    win_chance = wins / n_runs
    average_votes = total_votes / n_runs
    win_contribution_percentages = win_contributions / wins
    expected_roi = roi_total / wins if investment_data is not None else None
    roi_greater_percentage = (
        roi_greater_count / wins if investment_data is not None else None
    )

    df_results = pd.DataFrame(
        {
            "State": data["State"],
            "Contributions": win_contributions,
            "ContributionRate": win_contribution_percentages,
        }
    )

    return win_chance, average_votes, df_results, expected_roi, roi_greater_percentage


# Process a batch of simulations
def process_batch(data, threshold, n_runs, investment_data=None):
    randoms = np.random.random(size=(n_runs, len(data)))
    condition_mask = randoms < np.tile(data["Value"].values, (n_runs, 1))
    votes = np.where(condition_mask, np.tile(data["Votes"].values, (n_runs, 1)), 0).sum(
        axis=1
    )

    wins = np.sum(votes > threshold)
    batch_sum = np.sum(votes)
    win_contributions = np.zeros(len(data))

    for i in range(len(data)):
        win_contributions[i] += np.sum((votes > threshold) & (condition_mask[:, i]))

    if investment_data is not None:
        roi = np.zeros(n_runs)
        for i in range(len(data)):
            roi += np.where(
                (votes > threshold) & (condition_mask[:, i]),
                investment_data["Investment"].values[i] / data["Value"].values[i],
                0,
            )
        total_roi = np.sum(roi)
        roi_greater = np.sum(roi > investment_data["Investment"].sum())
    else:
        total_roi = 0
        roi_greater = 0

    return wins, batch_sum, win_contributions, total_roi, roi_greater


# This wrapper function makes it slightly more convenient to call simulation code
# with or without a set of investments to test
def monte_election(data, n_runs=10000, batch_size=10000, investment_data=None):
    results = monte_election_batched(data, n_runs, batch_size, investment_data)
    if investment_data is None:
        return results[:3]
    return results


def main():
    # Parser allows me to control # of runs from the CLI, but I may still take it out later
    parser = argparse.ArgumentParser(
        description="a utility to simulate `gens` number of elections"
    )
    parser.add_argument(
        "gens",
        type=int,
        default=1000,
        help="number of generations to run monte carlo for",
    )
    args = parser.parse_args()
    gens = args.gens
    df_merged = pd.merge(df_data, df_college, how="inner")
    win_chance, avg_votes, df_results = monte_election(df_merged, gens)
    print(
        f"Batched results: {win_chance*100}% chance to win, with an average of {avg_votes} votes!"
    )

    # Calculate the undervaluation of each state's contract, assuming a Blue win
    # The case of a Red win can be covered by buying shares of the national result market
    df_all = pd.merge(df_merged, df_results, how="inner")
    df_all["Undervaluation"] = df_all["Value"] - df_all["ContributionRate"]
    df_all["UndervalueRatio"] = df_all["Undervaluation"].abs()
    sum_undervaluations = df_all["UndervalueRatio"].sum()
    df_all["UndervalueRatio"] = df_all["UndervalueRatio"] / sum_undervaluations
    print(df_all.sort_values(by="ContributionRate"))

    # Write to csv for now
    result_filename = f"datasets/calculated/{most_recent_data[:10]}_contributions.csv"
    df_all.to_csv(result_filename, index=False)


if __name__ == "__main__":
    main()
