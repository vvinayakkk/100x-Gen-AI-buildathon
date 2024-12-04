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
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import pipeline

# Download resources
nltk.download('vader_lexicon', quiet=True)

financial_sentiment = pipeline(
    "sentiment-analysis", 
    model="ProsusAI/finbert",
    top_k=None
)

class FinancialAnalyzer:
    def __init__(self):
        # Financial sentiment model
        

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
            result = financial_sentiment(text)[0]
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

def run_periodic_analysis(analyzer):
    """Run analysis periodically every 5 minutes."""
    schedule.every(5).minutes.do(analyzer.analyze_financial_data)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Flask Application
app = Flask(__name__)
financial_analyzer = FinancialAnalyzer()

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

def start_analysis_thread():
    analysis_thread = threading.Thread(target=run_periodic_analysis, args=(financial_analyzer,))
    analysis_thread.start()

if __name__ == '__main__':
    # Run initial analysis to generate files
    financial_analyzer.analyze_financial_data()
    
    # Start the periodic analysis thread
    start_analysis_thread()
    
    # Run the Flask app
    app.run(debug=True, port=5000)