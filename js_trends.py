import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from pytrends.request import TrendReq
from pytrends import exceptions

# Initialize Google Trends API
pytrends = TrendReq(hl='en-US', tz=360)

# JavaScript frameworks to compare (old and new)
frameworks = [
    "React", "Vue", "Angular", "Svelte", "Ember", "Backbone", "Meteor", "Knockout", 
    "Alpine.js", "Solid", "Preact", "Lit", "Qwik", "Hyperapp", "Dojo"
]
years = list(range(2010, 2025))  # Adjust based on available data

def fetch_google_trends(framework, retries=3, delay=10):
    """Fetch interest over time from Google Trends with retry logic."""
    for attempt in range(retries):
        try:
            pytrends.build_payload([framework], timeframe='today 5-y', geo='')
            data = pytrends.interest_over_time()
            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])
            return data.infer_objects(copy=False)  # Ensure proper dtype inference
        except exceptions.TooManyRequestsError:
            print(f"Rate limit reached for {framework}, retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"Failed to fetch data for {framework} after {retries} attempts.")
    return pd.DataFrame()

# Collect data for all frameworks
data_dict = {}
for framework in frameworks:
    data = fetch_google_trends(framework)
    if not data.empty:
        data_dict[framework] = data

# Convert to DataFrame
if data_dict:
    trend_df = pd.concat(data_dict.values(), axis=1)
    trend_df.columns = data_dict.keys()
    trend_df = trend_df.infer_objects(copy=False)  # Ensure proper dtype inference
    trend_df.fillna(0, inplace=True)

    # Generate synthetic usage, interest, and retention data (for illustration purposes)
    usage_df = trend_df * 0.8  # Example adjustment
    retention_df = trend_df * 0.6  # Example adjustment

    # Get top 5 frameworks based on average interest
    top_frameworks = trend_df.mean().nlargest(5).index.tolist()

    # Save data
    trend_df.to_csv("js_framework_trends.csv")
    usage_df.to_csv("js_framework_usage.csv")
    retention_df.to_csv("js_framework_retention.csv")

def plot_trends():
    """Plot the trends comparison with usage, interest, and retention in separate subplots."""
    if not data_dict:
        print("No data available to plot.")
        return
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 14), sharex=True)
    metrics = [("Interest", trend_df), ("Usage", usage_df), ("Retention", retention_df)]
    colors = ["b", "g", "r", "c", "m"]

    for idx, (title, df) in enumerate(metrics):
        ax = axes[idx]
        for i, framework in enumerate(top_frameworks):
            ax.plot(df.index, df[framework].rolling(3).mean(), label=framework, color=colors[i], linewidth=2)
        ax.set_title(f"JavaScript Frameworks - {title}")
        ax.set_ylabel("Popularity Metrics")
        ax.legend()
        ax.grid(True)
    
    axes[-1].set_xlabel("Year")
    plt.tight_layout()
    plt.show()

plot_trends()
