import pandas as pd
import numpy as np

# Create a list of all US state codes
state_codes = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC" #District of Columbia has 3 votes
]

# Generate a dataframe
df = pd.DataFrame({
    'State': state_codes,
    'Party': ['blue'] * len(state_codes),
    'Value': np.round(np.random.uniform(0.01, 0.99, size=len(state_codes)), 2)
})

# Define the file path
file_path = 'datasets/dummy_data.csv'

# Save the dataframe to a CSV file
df.to_csv(file_path, index=False)