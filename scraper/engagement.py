import duckdb
import matplotlib.dates as mdates
import pandas as pd
import requests


def fetch_all_posts(actor_did):
    base_url = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
    all_posts = []
    params = {
        "actor": actor_did,
        "limit": 100
    }

    while True:
        response = requests.get(base_url, params=params)

        # Check for API errors
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = response.json()

        # Append posts to the list
        if "feed" in data:
            all_posts.extend(data["feed"])

        # Check for pagination cursor
        if "cursor" in data:
            params["cursor"] = data["cursor"]
        else:
            break  # No more data to fetch

    return all_posts


# Replace with the DID of the desired account
actor_did = "did:plc:asih6sgpr6avgvczz3vxgfqt"
all_posts = fetch_all_posts(actor_did)

posts_data = []
total_like = 0
total_repost = 0
for post in all_posts:
    post_record = post.get("post", {})
    posts_data.append({
        "post_uri": post_record.get("uri", ""),
        "author_handle": post_record.get("author", {}).get("handle", ""),
        "post_text": post_record.get("record", {}).get("text", ""),
        "created_at": post_record.get("record", {}).get("createdAt", ""),
        "replies": post_record.get("replyCount", 0),
        "reposts": post_record.get("repostCount", 0),
        "likes": post_record.get("likeCount", 0),
        "quotes": post_record.get("quoteCount", 0),
        "total_engagement": post_record.get("replyCount", 0) +
                            post_record.get("repostCount", 0) +
                            post_record.get("likeCount", 0) +
                            post_record.get("quoteCount", 0),
    })
    total_like += post_record.get("likeCount", 0)
    total_repost += post_record.get("repostCount", 0)

# print([post for post in posts_data if post['total_engagement']>30])

df = pd.DataFrame(posts_data)
# print(df)


con = duckdb.connect()
con.register("posts_table", df)

result = con.execute('''
    -- Query to fetch detailed post data
    SELECT 
        post_text,
        post_uri,
        author_handle,
        created_at,
        total_engagement,
        replies,
        reposts,
        likes,
        quotes,
        bar(total_engagement, 0, (SELECT MAX(total_engagement) FROM posts_table), 30) AS engagement_chart
    FROM posts_table
    ORDER BY total_engagement DESC
    LIMIT 10
''').fetchdf()

totals = con.execute('''
    -- Query to calculate total likes, reposts, replies, and overall engagement
    SELECT 
        SUM(likes) AS total_likes,
        SUM(reposts) AS total_reposts,
        SUM(replies) AS total_replies,
        SUM(total_engagement) AS total_engagement
    FROM posts_table
''').fetchdf()

# Display results
print("Top 10 Posts:")
print(result)
print("\nTotal Engagement Metrics:")
print(totals)

df['created_at'] = pd.to_datetime(df['created_at'])
df['engagement_date'] = df['created_at'].dt.date

con = duckdb.connect()
con.register("posts_table", df)

daily_growth = con.execute('''
    WITH daily_engagement AS (
        SELECT 
            engagement_date,
            SUM(total_engagement) AS daily_total_engagement
        FROM posts_table
        GROUP BY engagement_date
        ORDER BY engagement_date
    ),
    growth_calculation AS (
        SELECT 
            engagement_date,
            daily_total_engagement,
            LAG(daily_total_engagement) OVER (ORDER BY engagement_date) AS previous_day_engagement,
            daily_total_engagement - LAG(daily_total_engagement) OVER (ORDER BY engagement_date) AS engagement_growth,
            CASE
                WHEN LAG(daily_total_engagement) OVER (ORDER BY engagement_date) IS NOT NULL
                THEN ROUND(
                    (daily_total_engagement - LAG(daily_total_engagement) OVER (ORDER BY engagement_date)) * 100.0 /
                    LAG(daily_total_engagement) OVER (ORDER BY engagement_date), 2)
                ELSE NULL
            END AS growth_percentage
        FROM daily_engagement
    )
    SELECT 
        engagement_date,
        daily_total_engagement,
        previous_day_engagement,
        engagement_growth,
        growth_percentage
    FROM growth_calculation
''').fetchdf()

print("Daily Engagement Growth:")
print(daily_growth)

daily_growth = daily_growth.iloc[1:-1]

import matplotlib.pyplot as plt

# Plotting the daily engagement growth
plt.figure(figsize=(10, 6))

# Plot total engagement
plt.plot(daily_growth['engagement_date'], daily_growth['daily_total_engagement'], label='Total Engagement', color='b',
         marker='o')

# Plot engagement growth
plt.plot(daily_growth['engagement_date'], daily_growth['engagement_growth'], label='Engagement Growth', color='g',
         marker='o')

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

# Adding labels and title
plt.title('Daily Engagement and Growth')
plt.xlabel('Date')
plt.ylabel('Engagement')
plt.xticks(rotation=45)
plt.legend()

# Displaying the plot
plt.tight_layout()
plt.show()
