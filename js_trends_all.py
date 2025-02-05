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

    # Save data
    trend_df.to_csv("js_framework_trends.csv")
    usage_df.to_csv("js_framework_usage.csv")
    retention_df.to_csv("js_framework_retention.csv")

def plot_trends():
    """Plot the trends comparison with usage, interest, and retention."""
    if not data_dict:
        print("No data available to plot.")
        return
    
    plt.figure(figsize=(14, 7))
    for framework in data_dict.keys():
        plt.plot(trend_df.index, trend_df[framework], label=f"{framework} - Interest", linestyle='solid')
        plt.plot(trend_df.index, usage_df[framework], label=f"{framework} - Usage", linestyle='dashed')
        plt.plot(trend_df.index, retention_df[framework], label=f"{framework} - Retention", linestyle='dotted')
    plt.xlabel("Year")
    plt.ylabel("Popularity Metrics")
    plt.title("JavaScript Frameworks: Interest, Usage, and Retention Trends")
    plt.legend()
    plt.grid(True)
    plt.show()

plot_trends()
