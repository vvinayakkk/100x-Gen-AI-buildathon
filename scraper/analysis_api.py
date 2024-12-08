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
import asyncio
import logging
# Replace LLMChain with a direct runnable sequence
# chain = prompt | self.gemini_llm
# result = chain.invoke({
#     'texts': '\n'.join(texts[:10]),
#     'category': category
# })

# Custom Logging Configuration
def setup_logging():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging with timestamp in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'bluesky_poster_{timestamp}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class AsyncBlueskyPoster:
    def __init__(self, logger):
        self.logger = logger
        self.client = Client()
        self.logger.info("AsyncBlueskyPoster initialized successfully")
        
        # Initialize models and configurations
        self._init_models()

    def format_post(self, text, max_length=300):
        """
        Format post for Bluesky, ensuring it fits within character limit.
        
        Args:
            text (str): The original text to be formatted
            max_length (int): Maximum allowed length for the post
        
        Returns:
            str: Formatted post text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Truncate if longer than max_length
        if len(text) > max_length:
            # Try to cut at a sentence boundary
            sentences = text.split('. ')
            truncated_text = ''
            for sentence in sentences:
                if len(truncated_text) + len(sentence) + 3 <= max_length:
                    truncated_text += sentence + '. '
                else:
                    break
            
            # Trim and add ellipsis if needed
            text = (truncated_text.strip() + '...').strip()[:max_length]
        
        return text

    def _init_models(self):
        """Initialize machine learning models and configurations."""
        try:
            # Financial sentiment model
            self.financial_sentiment = pipeline(
                "sentiment-analysis", 
                model="ProsusAI/finbert",
                top_k=None
            )

            # Gemini for advanced analysis
            self.gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-pro", 
                google_api_key="AIzaSyDFCC3WxFXkar2cuZWBLNkFweuzIVB1hRE"  # Add your Google API key
            )
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
            raise

    def advanced_sentiment_analysis(self, texts):
        """Advanced sentiment analysis."""
        sentiments = []
        for text in texts:
            result = self.financial_sentiment(text)[0]
            sentiments.append({
                'text': text,
                'sentiment': result[0]['label'],
                'confidence': result[0]['score']
            })
        
        sentiments_sorted = sorted(sentiments, key=lambda x: x['confidence'], reverse=True)
        positive = [s for s in sentiments_sorted if s['sentiment'] == 'positive']
        negative = [s for s in sentiments_sorted if s['sentiment'] == 'negative']
        
        return {
            'top_positive': positive[:5],
            'top_negative': negative[:5],
            'total_analyzed': len(texts)
        }

    async def analyze_trend_data(self, category):
        """Async analysis for trend data."""
        self.logger.info(f"Analyzing {category} trends")
        
        try:
            # Read trend data from specific path
            filepath = os.path.join('data', 'trends', f'{category}_trends.json')
            
            with open(filepath, 'r', encoding='utf-8') as f:
                trend_data = json.load(f)
            
            # Prepare texts from top posts
            texts = [post['text'] for post in trend_data.get('postMetrics', {}).get('topPosts', [])]
            
            if not texts:
                self.logger.warning(f"No texts found for {category} trends")
                return None
            
            # Perform analyses
            sentiments = self.advanced_sentiment_analysis(texts)
            topics = self._perform_topic_clustering(texts)
            ai_insights = await self._generate_ai_insights(texts, category)
            
            trend_analysis = {
                'topHashtags': trend_data.get('topHashtags', []),
                'postMetrics': trend_data.get('postMetrics', {}),
                'sentiment_analysis': sentiments,
                'topic_clusters': topics,
                'ai_insights': ai_insights
            }
            
            # Save analysis result
            output_file = os.path.join('analysis_results', f'{category}_trend_analysis.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(trend_analysis, f, indent=2)
            
            return trend_analysis
        
        except Exception as e:
            self.logger.error(f"Error in {category} trend analysis: {e}")
            return None

    def _perform_topic_clustering(self, texts):
        """Perform topic clustering using TF-IDF and KMeans."""
        if not texts:
            return {'clusters': [], 'centroids': []}
        
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        X = vectorizer.fit_transform(texts)
        
        n_clusters = min(3, len(texts))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        
        return {
            'clusters': kmeans.labels_.tolist(),
            'centroids': kmeans.cluster_centers_.tolist()
        }

    async def _generate_ai_insights(self, texts, category):
        """Generate AI insights using Gemini."""
        try:
            prompt = PromptTemplate(
                input_variables=['texts', 'category'],
                template="""Analyze the following {category} trend texts and provide a concise, structured summary:
                Key Trends: Identify the top 3 emerging trends
                - Highlight most discussed subtopics
                - Note overall sentiment direction
                - Suggest potential future implications

                Format your response as a clear, readable text suitable for a social media post.
                
                Texts: {texts}"""
            )

            chain = LLMChain(llm=self.gemini_llm, prompt=prompt)
            result = chain.run(
                texts='\n'.join(texts[:10]),
                category=category
            )
            
            # Ensure result is a string
            return str(result)
        except Exception as e:
            self.logger.error(f"AI insights generation error for {category}: {e}")
            return f"Trending insights for {category}: Key developments observed"

    async def generate_bluesky_post(self, analysis_result, category):
        """Generate a Bluesky post from analysis results."""
        if not analysis_result:
            self.logger.warning(f"No analysis result for {category}")
            return None

        try:
            # Predefined prompt templates
            prompt_templates = {
                'financial': """Analyze market trends and create a tweet-style market update (under 280 chars and above 200):
                📈 Market Pulse: Provide a key financial insight
                - Highlight 2-3 trending points using • separator
                Focus on current market dynamics.""",
                
                'tech': """Analyze tech trends and create a tweet-style tech update (under 280 chars and above 200):
                🔮 Tech Watch: Share a key technology insight
                - Highlight 2-3 hot tech topics using • separator
                Focus on innovative trends.""",
                
                'crypto': """Analyze crypto trends and create a tweet-style crypto update (under 280 chars and above 200):
                ₿ Crypto Update: Provide a key cryptocurrency insight
                - Highlight 2-3 trending crypto points using • separator
                Focus on market movements.""",
                
                'entertainment': """Analyze entertainment trends and create a tweet-style entertainment update (under 280 chars and above 200):
                🎬 Entertainment Buzz: Share a key entertainment insight
                - Highlight 2-3 trending entertainment topics using • separator
                Focus on current pop culture trends."""
            }

            # Extract key information
            insights = str(analysis_result.get('ai_insights', ''))
            sentiment_analysis = analysis_result.get('sentiment_analysis', {})
            top_hashtags = analysis_result.get('topHashtags', [])
            
            # Prepare prompt
            prompt = PromptTemplate(
                input_variables=['insights', 'category'],
                template=prompt_templates.get(category, prompt_templates['tech'])
            )

            # Use Gemini to generate a concise post
            chain = LLMChain(llm=self.gemini_llm, prompt=prompt)
            
            # Generate post with explicit string conversion
            post_text = chain.run({
                'insights': insights,
                'category': category
            })
            
            # Ensure post_text is a string
            if not isinstance(post_text, str):
                post_text = str(post_text)
            
            return self.format_post(post_text)
        except Exception as e:
            self.logger.error(f"Post generation error for {category}: {e}")
            # Log the full error details for debugging
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    async def post_to_bluesky(self, post):
        """Post to Bluesky with error handling."""
        if not post:
            return
        
        try:
            self.client.login('smartbot.bsky.social', 'abcd@123')  # Add your Bluesky credentials
            self.client.send_post(text=post)
            # self.logger.info(f"Posted to Bluesky: {post}")
        except Exception as e:
            self.logger.error(f"Bluesky posting failed: {e}")

    async def run_analysis_and_post(self):
        """Main async workflow for analysis and posting."""
        categories = ['tech', 'finance', 'crypto', 'entertainment']
        
        try:
            for category in categories:
                analysis_result = await self.analyze_trend_data(category)
                post = await self.generate_bluesky_post(analysis_result, category)
                await self.post_to_bluesky(post)
                
                # Add a small delay between posts
                await asyncio.sleep(2)
        
        except Exception as e:
            self.logger.error(f"Complete workflow error: {e}")

async def main():
    """Main async entry point."""
    logger = setup_logging()
    logger.info("Bluesky Auto Poster Daemon Starting...")
    
    poster = AsyncBlueskyPoster(logger)
    
    while True:
        try:
            await poster.run_analysis_and_post()
            # Run every 15 minutes
            await asyncio.sleep(900)  # 15 * 60 seconds
        except Exception as e:
            logger.error(f"Daemon loop error: {e}")
            await asyncio.sleep(60)  # Wait a minute before retry

if __name__ == '__main__':
    asyncio.run(main())
