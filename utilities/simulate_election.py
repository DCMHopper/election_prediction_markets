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


# Run many simulations at once
def monte_election_batched(data, n_runs=10000, batch_size=10000):
    wins: int = 0
    total_votes: int = 0
    THRESHOLD: int = 270
    STATE_COUNT: int = 51  # Include DC, but not ME1,2 or NE1,2

    n_batches = n_runs // batch_size
    remainder_runs = n_runs % batch_size
    win_contributions = np.zeros(STATE_COUNT)

    # Batches run sequentially - adjust n_batches if hardware is a limitation
    for _ in repeat(None, n_batches):
        batch_wins, batch_sum, batch_contributions = process_batch(
            data, THRESHOLD, batch_size
        )
        wins += batch_wins
        total_votes += batch_sum
        win_contributions += batch_contributions

    if remainder_runs > 0:
        batch_wins, batch_sum, batch_contributions = process_batch(
            data, THRESHOLD, remainder_runs
        )
        wins += batch_wins
        total_votes += batch_sum
        win_contributions += batch_contributions

    win_chance = wins / n_runs
    average_votes = total_votes / n_runs

    win_contribution_percentages = win_contributions / wins
    df_results = pd.DataFrame(
        {
            "State": df_data["State"],
            "Contributions": win_contributions,
            "ContributionRate": win_contribution_percentages,
        }
    )

    return win_chance, average_votes, df_results


def process_batch(data, threshold, n_runs):
    randoms = np.random.random(size=(n_runs, len(data)))
    # We use the market value of a state as proxy for its likelihood to go Blue in the election
    condition_mask = randoms < np.tile(data["Value"].values, (n_runs, 1))
    # np.tile for calculating many simulations at once
    votes = np.where(condition_mask, np.tile(data["Votes"].values, (n_runs, 1)), 0).sum(
        axis=1
    )

    wins = np.sum(votes > threshold)
    batch_sum = np.sum(votes)

    # We count how many wins each state is a part of as part of our hunt for undervalued contracts
    # Just trust that this will line up with our state labels for now
    win_contributions = np.zeros(len(data))

    for i in range(len(data)):
        win_contributions[i] += np.sum((votes > threshold) & (condition_mask[:, i]))

    return wins, batch_sum, win_contributions


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
    win_chance, avg_votes, df_results = monte_election_batched(df_merged, gens)
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
