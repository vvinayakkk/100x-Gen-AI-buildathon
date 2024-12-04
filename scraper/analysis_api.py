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

if __name__ == '__main__':
    # Run initial analysis to generate files
    financial_analyzer.analyze_financial_data()
    trend_crypto_analyzer.analyze_crypto_data()
    trend_crypto_analyzer.analyze_trend_data()
    
    # Start the periodic analysis thread
    start_analysis_thread()
    
    # Run the Flask app
    app.run(debug=True, port=5000)