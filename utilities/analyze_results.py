import pandas as pd
import numpy as np
import os

df_college = pd.read_csv('datasets/electoral_college.csv')
# df_data = pd.read_csv('datasets/dummy_data.csv')
markets_path = "datasets/observed"
contributions_path = "datasets/calculated"
data_files = os.listdir(markets_path)
timestamped_files = {int(file[:10]): file for file in data_files}
most_recent_data = timestamped_files[max(timestamped_files)]
data_timestamp = most_recent_data[:10]
df_markets = pd.read_csv(os.path.join(markets_path,most_recent_data))
try:
    df_contributions = pd.read_csv(os.path.join(contributions_path,f"{data_timestamp}_contributions.csv"))
except FileNotFoundError as e:
    print("File not found - did you run utilities/simulate_election.py yet?")
except Exception as e:
    print(e)

df_all = pd.merge(df_markets,df_contributions,how='inner')
df_all['Undervaluation'] = df_all['Value'] - df_all['ContributionRate']
df_all['UndervalueRatio'] = df_all['Undervaluation'].abs()
sum_undervaluations = df_all['UndervalueRatio'].sum()
df_all['UndervalueRatio'] = df_all['UndervalueRatio'] / sum_undervaluations
df_all = df_all.sort_values(by='ContributionRate')
print(df_all)