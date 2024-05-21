import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# This script will focus on a strategy for making investments in the various markets
# in such a way that minimizes risk. We will then test this strategy with
# more monte-carlo simulations!

# filesystem shenanigans to cope with my disordered data sets
df_college = pd.read_csv("datasets/electoral_college.csv")
# df_data = pd.read_csv('datasets/dummy_data.csv')
data_path = "datasets/calculated"
data_files = os.listdir(data_path)
timestamped_files = {int(file[:10]): file for file in data_files}
most_recent_data = timestamped_files[max(timestamped_files)]
df_raw = pd.read_csv(os.path.join(data_path, most_recent_data))

# print(df.head())


# Check out the distribution of undervalued markets:
def visualize(df, column="Undervaluation"):
    plt.figure(figsize=(10, 6))
    plt.hist(df[column], bins=30, edgecolor="k", alpha=0.7)
    plt.title(f"Histogram of {column}")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()


# Position size for each market will be:
# (Total capital) * (Undervaluation) / sum(Undervaluations)
# Or in other words, the UndervalueRatio
TOTAL_CAPITAL = 10000

# HOWEVER, some markets are basically guaranteed to fail
# So anything <=0.1 ContributionRate will be excluded
# Also, anything <= 0.01 Undervaluation will be excluded
# So we need to recalculate UndervalueRatio again after filtering :')
# But it can still be convenient - as a baseline, to make sure our filtering is healthy


def preselect(df, min_contribution=0.1, min_valuation=0.01) -> pd.DataFrame:
    df_results = df[df["ContributionRate"] > min_contribution]
    df_results = df_results[df_results["UndervalueRatio"] > min_valuation]
    df_results["UndervalueRatio"] = df_results["Undervaluation"].abs()
    sum_undervaluations = df_results["UndervalueRatio"].sum()
    df_results["UndervalueRatio"] = df_results["UndervalueRatio"] / sum_undervaluations
    return df_results


df_filtered = preselect(df_raw)


print(df_filtered.head())
print(df_filtered.shape)
print(df_filtered["Undervaluation"].sum())
print(df_filtered["UndervalueRatio"].sum())


# Distribute our capital amount, and return an array of investments
def distribute_capital(capital, df_markets) -> list:
    investments = df_markets["UndervalueRatio"] * capital
    investments = np.floor(investments).astype(int)
    return investments.tolist()


print(distribute_capital(TOTAL_CAPITAL, df_raw))
print(distribute_capital(TOTAL_CAPITAL, df_filtered))
