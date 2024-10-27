import re

# Initialize an empty list to hold the extracted data
extracted_data = []

# Open the log file
with open('./sample_data/dieharder/out.txt', 'r') as file:
    for line in file:
        # Use regex to match the desired line format
        match = re.match(r'^\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d\.]+)\s*\|\s*(\S+)', line)
        if match:
            # Extract the matched groups and append to the list            # Extract the matched groups and append to the list: 
            #           \S+ {string}     | \d+ {digits} | \d+ {digits} | \d+ {digits} | [\d\.]+ {floats} | \S+ {string}
            # example:  diehard_birthdays|   0          |         100  |        100   |        0.72433123|     PASSED             test_name = match.group(1)
            ntup = int(match.group(2))
            tsamples = int(match.group(3))
            psamples = int(match.group(4))
            p_value = float(match.group(5))
            assessment = match.group(6)

            extracted_data.append({
                'test_name': test_name,
                'ntup': ntup,
                'tsamples': tsamples,
                'psamples': psamples,
                'p_value': p_value,
                'assessment': assessment,
            })

# Print the extracted data
for item in extracted_data:
    print(item)

"""
{'test_name': 'diehard_birthdays', 'ntup': 0, 'tsamples': 100, 'psamples': 100, 'p_value': 0.72433123, 'assessment': 'PASSED'}
{'test_name': 'diehard_operm5', 'ntup': 0, 'tsamples': 1000000, 'psamples': 100, 'p_value': 0.73716717, 'assessment': 'PASSED'}
{'test_name': 'diehard_rank_32x32', 'ntup': 0, 'tsamples': 40000, 'psamples': 100, 'p_value': 0.79027914, 'assessment': 'PASSED'}
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = extracted_data
# Create a DataFrame
df = pd.DataFrame(data)

# Plotting P-Value Distribution
plt.figure(figsize=(10, 6))
plt.hist(df['p_value'], bins=20, color='blue', alpha=0.7)
plt.axvline(0.05, color='red', linestyle='dashed', linewidth=1)
plt.title('Distribution of P-Values')
plt.xlabel('P-Value')
plt.ylabel('Frequency')
plt.grid()
plt.show()

# Bar plot of test outcomes
outcomes_count = df['assessment'].value_counts()
plt.figure(figsize=(8, 5))
outcomes_count.plot(kind='bar', color=['green', 'orange', 'red'])
plt.title('Test Outcomes')
plt.xlabel('Outcome')
plt.ylabel('Count')
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.show()

# Assuming df is already defined and contains the necessary columns

# Extract 'tsamples', ensuring they are unique and sorted
sample_sizes = sorted(set(df['tsamples'].tolist()))  # Unique and sorted list
print(f"Extracted sample_sizes (unique and sorted): {sample_sizes}")

# Add sample sizes to the DataFrame as a new column (if needed)
# Note: This will create NaN for other rows if the lengths do not match
df['sample_sizes'] = pd.Series(sample_sizes)

# Check if 'sample_sizes' is successfully added
print("DataFrame after adding sample sizes:")
print(df.head())  # Print the first few rows to verify

# Proceed with plotting if 'sample_sizes' is in df
if 'sample_sizes' in df.columns:
    plt.figure(figsize=(10, 6))
    plt.scatter(df['sample_sizes'], df['p_value'], color='blue', alpha=0.7)
    plt.title('Sample Size vs. P-Value')
    plt.xlabel('Sample Size')
    plt.ylabel('P-Value')
    plt.xscale('log')  # Using a logarithmic scale for sample sizes
    plt.grid()
    plt.show()
else:
    print("Column 'sample_sizes' not found in the DataFrame. Please check the earlier steps.")

