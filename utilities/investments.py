import pandas as pd
import matplotlib.pyplot as plt
import os

# This script will focus on a strategy for making investments in the various markets in such a way that minimizes risk

df_college = pd.read_csv('datasets/electoral_college.csv')
# df_data = pd.read_csv('datasets/dummy_data.csv')
data_path = "datasets/calculated"
data_files = os.listdir(data_path)
timestamped_files = {int(file[:10]): file for file in data_files}
most_recent_data = timestamped_files[max(timestamped_files)]
df = pd.read_csv(os.path.join(data_path,most_recent_data))

print(df.head())

plt.figure(figsize=(10, 6))
plt.hist(df['Undervaluation'], bins=30, edgecolor='k', alpha=0.7)
plt.title('Histogram of Undervaluation')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()