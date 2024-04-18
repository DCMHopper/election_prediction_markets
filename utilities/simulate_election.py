import pandas as pd
import numpy as np
import argparse
from itertools import repeat

df_college = pd.read_csv('datasets/electoral_college.csv')
df_data = pd.read_csv('datasets/dummy_data.csv')

print(df_data.head())

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

    n_batches = n_runs // batch_size
    remainder_runs = n_runs % batch_size

    for _ in repeat(None,n_batches):
        batch_wins, batch_sum = process_batch(data, THRESHOLD, batch_size)
        wins += batch_wins
        total_votes += batch_sum

    if remainder_runs > 0:
        batch_wins, batch_sum = process_batch(data, THRESHOLD, remainder_runs)
        wins += batch_wins
        total_votes += batch_sum

    win_chance = wins / n_runs
    average_votes = total_votes / n_runs

    return win_chance, average_votes

def process_batch(data, threshold, n_runs):
    randoms = np.random.random(size=(n_runs, len(data)))
    condition_mask = randoms < np.tile(data['Value'].values, (n_runs, 1))
    votes = np.where(condition_mask, np.tile(data['Votes'].values, (n_runs, 1)), 0).sum(axis=1)

    wins = np.sum(votes > threshold)
    batch_sum = np.sum(votes)

    return wins, batch_sum


def main():
    parser = argparse.ArgumentParser(description='a utility to simulate `gens` number of elections')
    parser.add_argument('gens',type=int,default=1000,help='number of generations to run monte carlo for')
    args = parser.parse_args()
    gens = args.gens
    df_merged = pd.merge(df_data,df_college,how='inner')
    win_chance, avg_votes = monte_election_batched(df_merged,gens)
    print(f"Batched results: {win_chance}% chance to win, with an average of {avg_votes} votes!")

if __name__ == "__main__":
    main()