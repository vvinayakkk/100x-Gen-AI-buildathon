import os
import json
import schedule
import time
import threading
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import pipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from flask import Flask, jsonify
from flask_cors import CORS
from atproto import Client
import json
from datetime import datetime

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/analyze/*": {
        "origins": ["http://localhost:5173"],  # Your frontend origin
        "methods": ["GET", "OPTIONS"],  # Allowed methods
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

class BlueskyPoster:
    def __init__(self):
        print("\n[INIT] Initializing BlueskyPoster...")
        self.client = Client()
        self.client.login('', '')
        print("[INIT] Successfully logged into Bluesky")
        
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=""
        )
        print("[INIT] BlueskyPoster initialization complete")

    def format_post(self, text, max_length=300):
        """Format post to meet Bluesky requirements."""
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Ensure post doesn't exceed max length
        if len(text) > max_length:
            # Find the last complete sentence that fits
            sentences = text[:max_length-3].split('. ')
            formatted_text = '. '.join(sentences[:-1]) + '...'
            return formatted_text[:max_length]
        return text

    def generate_post(self, analysis_data, category):
        """Generate Twitter-style post based on category and analysis data."""
        if not analysis_data:
            print(f"[ERROR] No analysis data provided for {category}")
            return None

        # Extract required fields with safe fallbacks
        total_posts = analysis_data.get('total_posts', 0)
        sentiment_data = analysis_data.get('sentiment_analysis', {})
        topics = analysis_data.get('topic_clusters', {})
        insights = analysis_data.get('ai_insights', '')

        prompt_templates = {
            'financial': """Write a casual but informative tweet-style market update (under 280 chars). Format: 
            📈 Market Pulse: [key insight]
            
            Trending: [2-3 key points separated by •]
            
            Keep it conversational and easy to read. No markdown or asterisks.""",
            
            'tech': """Write a casual but informative tweet-style tech update (under 280 chars). Format:
            🔮 Tech Watch: [key insight]
            
            Hot Topics: [2-3 key points separated by •]
            
            Keep it conversational and easy to read. No markdown or asterisks.""",
            
            'crypto': """Write a casual but informative tweet-style crypto update (under 280 chars). Format:
            ₿ Crypto Update: [key insight]
            
            Trending: [2-3 key points separated by •]
            
            Keep it conversational and easy to read. No markdown or asterisks.""",
            
            'entertainment': """Write a casual but informative tweet-style entertainment update (under 280 chars). Format:
            🎬 Entertainment Buzz: [key insight]
            
            Trending: [2-3 key points separated by •]
            
            Keep it conversational and easy to read. No markdown or asterisks."""
        }

        try:
            prompt = PromptTemplate(
                input_variables=['data_summary'],
                template=prompt_templates.get(category.lower(), prompt_templates['financial'])
            )

            chain = LLMChain(llm=self.gemini_llm, prompt=prompt)
            
            data_summary = {
                'posts_analyzed': total_posts,
                'key_sentiment': sentiment_data.get('top_positive', [])[:2],
                'main_topics': topics,
                'key_insights': insights[:200]
            }
            
            result = chain.run(data_summary=json.dumps(data_summary))
            return self.format_post(result)
            
        except Exception as e:
            print(f"[ERROR] Failed to generate {category} post: {str(e)}")
            return None

    def format_post(self, text, max_length=280):
        """Format post to meet Twitter requirements and style."""
        # Clean up any markdown or extra formatting
        text = text.replace('**', '')
        text = text.replace('*', '')
        text = text.replace('###', '')
        text = text.replace('#', '')
        
        # Remove extra whitespace and normalize spacing
        text = ' '.join(text.split())
        
        # Clean up bullet points and separators
        text = text.replace(' - ', ' • ')
        text = text.replace(' -- ', ' • ')
        
        # Ensure post doesn't exceed max length
        if len(text) > max_length:
            sentences = text[:max_length-1].split('•')
            formatted_text = '•'.join(sentences[:-1]).strip()
            return formatted_text
            
        return text
    
    def post_updates(self):
        """Post all analysis updates to Bluesky."""
        print("\n[POSTING] Starting update cycle...")
        
        analyses = {
            'financial': 'financial_news_analysis.json',
            'tech': 'tech_trend_analysis.json',
            'crypto': 'crypto_analysis.json',
            'entertainment': 'entertainment_trend_analysis.json'
        }

        for category, filename in analyses.items():
            try:
                filepath = os.path.join('analysis_results', filename)
                if not os.path.exists(filepath):
                    print(f"[WARNING] Analysis file not found: {filename}")
                    continue
                    
                with open(filepath, 'r') as f:
                    analysis_data = json.load(f)
                
                post = self.generate_post(analysis_data, category)
                
                if post:
                    self.client.send_post(text=post)
                    print(f"[SUCCESS] Posted {category} update ({len(post)} chars)")
                    time.sleep(2)  # Rate limiting
            
            except Exception as e:
                print(f"[ERROR] Failed to post {category} update: {str(e)}")
                continue

        print("[POSTING] Update cycle completed")

def run_analysis_and_post(financial_analyzer, trend_analyzer, poster):
    """Combined function to run all analyses and posting."""
    try:
        financial_analyzer.analyze_financial_data()
        trend_analyzer.analyze_crypto_data()
        trend_analyzer.analyze_trend_data()
        poster.post_updates()
    except Exception as e:
        print(f"[ERROR] Analysis cycle failed: {str(e)}")

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
# Download resources
nltk.download('vader_lexicon', quiet=True)

class FinancialAnalyzer:
    def __init__(self):
        # Financial sentiment model
        self.financial_sentiment = pipeline(
            "sentiment-analysis", 
            model="ProsusAI/finbert",
            top_k=None
        )

        # Gemini for advanced analysis
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            google_api_key="AIzaSyDFCC3WxFXkar2cuZWBLNkFweuzIVB1hRE"
        )

        # Output directory
        self.output_dir = 'analysis_results'
        os.makedirs(self.output_dir, exist_ok=True)

    def advanced_financial_sentiment(self, texts):
        """Advanced financial sentiment analysis with top 5 positive and negative results."""
        sentiments = []
        for text in texts:
            result = self.financial_sentiment(text)[0]
            sentiments.append({
                'text': text,
                'sentiment': result[0]['label'],
                'confidence': result[0]['score']
            })
        
        # Sort sentiments by confidence score
        sentiments_sorted = sorted(sentiments, key=lambda x: x['confidence'], reverse=True)
        
        # Separate positive and negative sentiments
        positive = [s for s in sentiments_sorted if s['sentiment'] == 'positive']
        negative = [s for s in sentiments_sorted if s['sentiment'] == 'negative']
        
        # Return top 5 of each
        return {
            'top_positive': positive[:5],
            'top_negative': negative[:5],
            'total_analyzed': len(texts)
        }

    def topic_clustering(self, texts):
        """Cluster financial texts into topics."""
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        X = vectorizer.fit_transform(texts)
        
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(X)
        
        return {
            'clusters': kmeans.labels_.tolist(),
            'centroids': kmeans.cluster_centers_.tolist()
        }

    def gemini_analysis(self, texts):
        """Advanced AI-powered financial analysis."""
        prompt = PromptTemplate(
            input_variables=['texts'],
            template="""Analyze the following financial texts and provide:
            1. Key market trends
            2. Potential investment opportunities
            3. Risk assessment
            4. Sentiment summary
            
            Texts: {texts}"""
        )

        chain = LLMChain(llm=self.gemini_llm, prompt=prompt)
        result = chain.run(texts='\n'.join(texts[:10]))  # Limit to first 10 texts
        return result

    def analyze_financial_data(self):
        """Comprehensive financial analysis."""
        categories = ['stocks', 'financial_news', 'investment_insights']
        
        comprehensive_analysis = {}
        
        for category in categories:
            file_path = os.path.join('data', category, 'latest.json')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    posts = json.load(f)
            except Exception as e:
                print(f"Error reading {category} data: {e}")
                continue
            
            texts = [post['text'] for post in posts]
            
            # Sentiment Analysis
            sentiments = self.advanced_financial_sentiment(texts)
            
            # Topic Clustering
            topics = self.topic_clustering(texts)
            
            # Gemini Advanced Analysis
            ai_insights = self.gemini_analysis(texts)
            
            comprehensive_analysis[category] = {
                'total_posts': len(posts),
                'sentiment_analysis': sentiments,
                'topic_clusters': topics,
                'ai_insights': ai_insights
            }
            
            # Save to file
            output_file = os.path.join(self.output_dir, f'{category}_analysis.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_analysis[category], f, indent=2)
        
        return comprehensive_analysis

class TrendCryptoAnalyzer:
    def __init__(self):
        # Sentiment analysis pipeline
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="ProsusAI/finbert",
            top_k=None
        )

        # Gemini for advanced analysis
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            google_api_key="AIzaSyDFCC3WxFXkar2cuZWBLNkFweuzIVB1hRE"
        )

        # Output directory
        self.output_dir = 'analysis_results'
        os.makedirs(self.output_dir, exist_ok=True)

    def advanced_sentiment_analysis(self, texts):
        """Advanced sentiment analysis with top positive and negative results."""
        sentiments = []
        for text in texts:
            result = self.sentiment_pipeline(text)[0]
            sentiments.append({
                'text': text,
                'sentiment': result[0]['label'],
                'confidence': result[0]['score']
            })
        
        # Sort sentiments by confidence score
        sentiments_sorted = sorted(sentiments, key=lambda x: x['confidence'], reverse=True)
        
        # Separate positive and negative sentiments
        positive = [s for s in sentiments_sorted if s['sentiment'] == 'positive']
        negative = [s for s in sentiments_sorted if s['sentiment'] == 'negative']
        
        return {
            'top_positive': positive[:5],
            'top_negative': negative[:5],
            'total_analyzed': len(texts)
        }

    def topic_clustering(self, texts):
        """Cluster texts into topics."""
        if not texts:
            return {'clusters': [], 'centroids': []}
        
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        X = vectorizer.fit_transform(texts)
        
        # Adjust number of clusters based on data size
        n_clusters = min(3, len(texts))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        
        return {
            'clusters': kmeans.labels_.tolist(),
            'centroids': kmeans.cluster_centers_.tolist()
        }

    def gemini_trend_analysis(self, texts, category):
        """Advanced AI-powered trend analysis."""
        prompt = PromptTemplate(
            input_variables=['texts', 'category'],
            template="""Analyze the following {category} trend texts and provide:
            1. Key emerging trends
            2. Most discussed subtopics
            3. Potential future directions
            4. Sentiment and engagement summary
            
            Texts: {texts}"""
        )

        chain = LLMChain(llm=self.gemini_llm, prompt=prompt)
        result = chain.run(
            texts='\n'.join(texts[:10]),  # Limit to first 10 texts
            category=category
        )
        return result

    def analyze_crypto_data(self):
        """Comprehensive crypto analysis."""
        file_path = os.path.join('data', 'crypto', 'latest.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        except Exception as e:
            print(f"Error reading crypto data: {e}")
            return {}
        
        texts = [post['text'] for post in posts]
        
        # Sentiment Analysis
        sentiments = self.advanced_sentiment_analysis(texts)
        
        # Topic Clustering
        topics = self.topic_clustering(texts)
        
        # Gemini Advanced Analysis
        ai_insights = self.gemini_trend_analysis(texts, 'crypto')
        
        crypto_analysis = {
            'total_posts': len(posts),
            'sentiment_analysis': sentiments,
            'topic_clusters': topics,
            'ai_insights': ai_insights
        }
        
        # Save to file
        output_file = os.path.join(self.output_dir, 'crypto_analysis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(crypto_analysis, f, indent=2)
        
        return crypto_analysis

    def analyze_trend_data(self):
        """Comprehensive trend analysis for different categories."""
        trend_categories = ['tech', 'finance', 'crypto', 'entertainment']
        comprehensive_trend_analysis = {}
        
        for category in trend_categories:
            file_path = os.path.join('data', 'trends', f'{category}_trends.json')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    trend_data = json.load(f)
            except Exception as e:
                print(f"Error reading {category} trend data: {e}")
                continue
            
            # Prepare texts from top posts
            texts = [post['text'] for post in trend_data.get('postMetrics', {}).get('topPosts', [])]
            
            # Sentiment Analysis
            sentiments = self.advanced_sentiment_analysis(texts)
            
            # Topic Clustering
            topics = self.topic_clustering(texts)
            
            # Gemini Advanced Analysis
            ai_insights = self.gemini_trend_analysis(texts, category)
            
            trend_analysis = {
                'topHashtags': trend_data.get('topHashtags', []),
                'postMetrics': trend_data.get('postMetrics', {}),
                'sentiment_analysis': sentiments,
                'topic_clusters': topics,
                'ai_insights': ai_insights
            }
            
            comprehensive_trend_analysis[category] = trend_analysis
            
            # Save each category's analysis
            output_file = os.path.join(self.output_dir, f'{category}_trend_analysis.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(trend_analysis, f, indent=2)
        
        return comprehensive_trend_analysis

def run_periodic_analysis(financial_analyzer, trend_crypto_analyzer):
    """Run analysis periodically every 5 minutes."""
    schedule.every(5).minutes.do(financial_analyzer.analyze_financial_data)
    schedule.every(5).minutes.do(trend_crypto_analyzer.analyze_crypto_data)
    schedule.every(5).minutes.do(trend_crypto_analyzer.analyze_trend_data)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Flask Application
app = Flask(__name__)
financial_analyzer = FinancialAnalyzer()
trend_crypto_analyzer = TrendCryptoAnalyzer()
# Existing Financial Analysis Routes

@app.after_request
def after_request(response):
    # Allow specific origin instead of *
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/analyze/stocks')
def get_stock_analysis():
    with open(os.path.join('analysis_results', 'stocks_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

@app.route('/analyze/news')
def get_news_analysis():
    with open(os.path.join('analysis_results', 'financial_news_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

@app.route('/analyze/insights')
def get_insights_analysis():
    with open(os.path.join('analysis_results', 'investment_insights_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

# New Crypto and Trend Analysis Routes
@app.route('/analyze/crypto')
def get_crypto_analysis():
    with open(os.path.join('analysis_results', 'crypto_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

@app.route('/analyze/trends/tech')
def get_tech_trends():
    with open(os.path.join('analysis_results', 'tech_trend_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

@app.route('/analyze/trends/finance')
def get_finance_trends():
    with open(os.path.join('analysis_results', 'finance_trend_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

@app.route('/analyze/trends/crypto')
def get_crypto_trends():
    with open(os.path.join('analysis_results', 'crypto_trend_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

@app.route('/analyze/trends/entertainment')
def get_entertainment_trends():
    with open(os.path.join('analysis_results', 'entertainment_trend_analysis.json'), 'r') as f:
        return jsonify(json.load(f))

def start_analysis_thread():
    analysis_thread = threading.Thread(target=run_periodic_analysis, args=(financial_analyzer, trend_crypto_analyzer))
    analysis_thread.start()

def run_scheduler():
    """Run the scheduler continuously."""
    while True:
        schedule.run_pending()time.sleep(1)

if __name__ == '__main__':
    print("\n[STARTUP] Initializing analysis system...")
    
    financial_analyzer = FinancialAnalyzer()
    trend_crypto_analyzer = TrendCryptoAnalyzer()
    bluesky_poster = BlueskyPoster()
    
    # Run initial analysis cycle
    print("[STARTUP] Running initial analyses...")
    run_analysis_and_post(financial_analyzer, trend_crypto_analyzer, bluesky_poster)
    
    # Schedule periodic runs
    schedule.every(10).minutes.do(
        run_analysis_and_post, 
        financial_analyzer, 
        trend_crypto_analyzer, 
        bluesky_poster
    )
    
    # Start scheduler in a daemon thread with continuous loop
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    print("[STARTUP] Scheduler thread started")
    
    # Run Flask app
    app = Flask(__name__)
    CORS(app)
    app.run(debug=False, port=5000)