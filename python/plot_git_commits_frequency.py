import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv(file_git_commits_csv)

# Convert the 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Group by date and sum the commits
df_grouped = df.groupby('date').sum().reset_index()

# Create a date range from the start to the end date in the data
date_range = pd.date_range(start=df_grouped['date'].min(), end=df_grouped['date'].max())

# Reindex the DataFrame to include all dates in the range and fill missing dates with 0 commits
df_grouped = df_grouped.set_index('date').reindex(date_range, fill_value=0).rename_axis('date').reset_index()

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(df_grouped['date'], df_grouped['commits'], marker='o', linestyle='-')
plt.xlabel('Date (YYYY-MM.DD)')
plt.ylabel('Number of Commits')
plt.title('Number of Git Commits Over Time')
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m.%d'))
plt.gcf().autofmt_xdate()  # Rotate date labels for better readability
plt.show()
