import pandas as pd
import numpy as np
import os
import argparse
from itertools import repeat

df_college = pd.read_csv('datasets/electoral_college.csv')
# df_data = pd.read_csv('datasets/dummy_data.csv')
data_path = "datasets/observed"
data_files = os.listdir(data_path)
timestamped_files = {int(file[:10]): file for file in data_files}
most_recent_data = timestamped_files[max(timestamped_files)]
df_data = pd.read_csv(os.path.join(data_path,most_recent_data))

# Vectorized a single run, but not the monte carlo
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

def monte_election_batched(data, n_runs=10000, batch_size=10000):
    wins: int = 0
    total_votes: int = 0
    THRESHOLD: int = 270
    STATE_COUNT: int = 51

    n_batches = n_runs // batch_size
    remainder_runs = n_runs % batch_size
    win_contributions = np.zeros(STATE_COUNT)

    for _ in repeat(None,n_batches):
        batch_wins, batch_sum, batch_contributions = process_batch(data, THRESHOLD, batch_size)
        wins += batch_wins
        total_votes += batch_sum
        win_contributions += batch_contributions

    if remainder_runs > 0:
        batch_wins, batch_sum, batch_contributions = process_batch(data, THRESHOLD, remainder_runs)
        wins += batch_wins
        total_votes += batch_sum
        win_contributions += batch_contributions

    win_chance = wins / n_runs
    average_votes = total_votes / n_runs

    win_contribution_percentages = (win_contributions / wins) * 100
    df_results = pd.DataFrame({
        'State': df_data['State'],
        'Contributions': win_contributions,
        'ContributionPercentage': win_contribution_percentages
    })

    return win_chance, average_votes, df_results

def process_batch(data, threshold, n_runs):
    randoms = np.random.random(size=(n_runs, len(data)))
    condition_mask = randoms < np.tile(data['Value'].values, (n_runs, 1))
    votes = np.where(condition_mask, np.tile(data['Votes'].values, (n_runs, 1)), 0).sum(axis=1)

    wins = np.sum(votes > threshold)
    batch_sum = np.sum(votes)

    win_contributions = np.zeros(len(data))

    for i in range(len(data)):
        win_contributions[i] += np.sum((votes > threshold) & (condition_mask[:, i]))

    return wins, batch_sum, win_contributions


def main():
    parser = argparse.ArgumentParser(description='a utility to simulate `gens` number of elections')
    parser.add_argument('gens',type=int,default=1000,help='number of generations to run monte carlo for')
    args = parser.parse_args()
    gens = args.gens
    df_merged = pd.merge(df_data,df_college,how='inner')
    win_chance, avg_votes, df_results = monte_election_batched(df_merged,gens)
    print(f"Batched results: {win_chance*100}% chance to win, with an average of {avg_votes} votes!")
    print(df_results)

if __name__ == "__main__":
    main()