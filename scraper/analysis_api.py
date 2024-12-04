import os
import json
from flask import Flask, jsonify
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
import re

# Download necessary NLTK resources
nltk.download('vader_lexicon', quiet=True)

app = Flask(__name__)
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """Analyze sentiment of text."""
    sentiment = sia.polarity_scores(text)
    if sentiment['compound'] > 0.05:
        return 'Positive'
    elif sentiment['compound'] < -0.05:
        return 'Negative'
    return 'Neutral'

def get_financial_data(category):
    """Read latest financial data from specified category."""
    file_path = os.path.join('data', category, 'latest.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}")
        return []

@app.route('/analyze/stocks')
def analyze_stocks():
    """Analyze stock-related posts."""
    posts = get_financial_data('stocks')
    
    # Sentiment analysis
    sentiments = [analyze_sentiment(post['text']) for post in posts]
    sentiment_counts = Counter(sentiments)
    
    # Extract stock tickers
    tickers = [re.findall(r'\$[A-Z]+', post['text']) for post in posts]
    mentioned_tickers = [ticker for sublist in tickers for ticker in sublist]
    top_tickers = Counter(mentioned_tickers).most_common(5)
    
    return jsonify({
        'total_posts': len(posts),
        'sentiment_distribution': dict(sentiment_counts),
        'top_mentioned_stocks': top_tickers
    })

@app.route('/analyze/news')
def analyze_financial_news():
    """Analyze financial news posts."""
    posts = get_financial_data('financial_news')
    
    # Sentiment analysis
    sentiments = [analyze_sentiment(post['text']) for post in posts]
    sentiment_counts = Counter(sentiments)
    
    # Key topics extraction
    topics = []
    for post in posts:
        topics.extend(re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', post['text']))
    top_topics = Counter(topics).most_common(5)
    
    return jsonify({
        'total_posts': len(posts),
        'sentiment_distribution': dict(sentiment_counts),
        'key_topics': top_topics
    })

@app.route('/analyze/insights')
def analyze_investment_insights():
    """Analyze investment insight posts."""
    posts = get_financial_data('investment_insights')
    
    # Sentiment analysis
    sentiments = [analyze_sentiment(post['text']) for post in posts]
    sentiment_counts = Counter(sentiments)
    
    # Investment strategy keywords
    strategies = []
    for post in posts:
        strategies.extend(re.findall(r'\b(long|short|diversify|hedge|portfolio)\b', post['text'], re.IGNORECASE))
    top_strategies = Counter(strategies).most_common(5)
    
    return jsonify({
        'total_posts': len(posts),
        'sentiment_distribution': dict(sentiment_counts),
        'top_investment_strategies': top_strategies
    })

if __name__ == '__main__':
    app.run(debug=True, port=6000)