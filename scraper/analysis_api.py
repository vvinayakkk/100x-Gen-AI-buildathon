import os
import json
import asyncio
import logging
from datetime import datetime
import traceback

from atproto import Client
import numpy as np
import pandas as pd
import torch
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class TrendAnalyzer:
    def __init__(self, logger=None):
        """
        Initialize TrendAnalyzer with logging and ML models
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Ensure directories exist
        self.ensure_directories_exist()
        
        # Initialize models
        self._init_models()

    def ensure_directories_exist(self):
        """Create necessary directories if they don't exist."""
        directories = [
            'logs', 
            'data/trends', 
            'analysis_results'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _init_models(self):
        """Initialize machine learning models"""
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
                google_api_key="AIzaSyDFCC3WxFXkar2cuZWBLNkFweuzIVB1hRE"  # Replace with your API key
            )
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
            raise

    def advanced_sentiment_analysis(self, texts):
        """Advanced sentiment analysis for given texts"""
        sentiments = []
        for text in texts:
            result = self.financial_sentiment(text)[0]
            sentiments.append({
                'text': text,
                'sentiment': result[0]['label'],
                'confidence': result[0]['score']
            })
        
        sentiments_sorted = sorted(sentiments, key=lambda x: x['confidence'], reverse=True)
        return {
            'top_positive': [s for s in sentiments_sorted if s['sentiment'] == 'positive'][:5],
            'top_negative': [s for s in sentiments_sorted if s['sentiment'] == 'negative'][:5],
            'total_analyzed': len(texts)
        }

    def _perform_topic_clustering(self, texts):
        """Perform topic clustering using TF-IDF and KMeans"""
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

    def generate_ai_insights(self, texts, category):
        """Generate AI insights using Gemini with category-specific prompts"""
        try:
            prompts = {
                'financial': PromptTemplate(
                    input_variables=['texts'],
                    template="""Analyze these financial market texts and provide:
                    1. Current market sentiment and key financial trends
                    2. Emerging investment opportunities
                    3. Potential economic risks and challenges
                    4. Sector-specific insights
                    5. Short-term and long-term market outlook
                    
                    first generete the insights and then summarize them in a way that it is under 280 characters.

                    Detailed Financial Texts: {texts}"""
                ),
                'crypto': PromptTemplate(
                    input_variables=['texts'],
                    template="""Analyze these cryptocurrency and blockchain texts and provide:
                    1. Current cryptocurrency market trends
                    2. Emerging blockchain technologies
                    3. Regulatory landscape updates
                    4. Potential investment strategies
                    5. Market sentiment and volatility indicators
                    
                    Detailed Crypto Texts: {texts}
                    
                    first generete the insights and then summarize them in a way that it is under 280 characters.
                    
                    """

                    
                ),
                'tech': PromptTemplate(
                    input_variables=['texts'],
                    template="""Analyze these technology industry texts and provide:
                    1. Cutting-edge technological innovations
                    2. Emerging tech trends
                    3. Potential disruptive technologies
                    4. Industry investment opportunities
                    5. Impact of recent technological developments
                    
                    Detailed Tech Texts: {texts}
                    
                    first generete the insights and then summarize them in a way that it is under 280 characters.
                    
                    """
                ),
                'entertainment': PromptTemplate(
                    input_variables=['texts'],
                    template="""Analyze these entertainment industry texts and provide:
                    1. Current entertainment trends
                    2. Emerging content and media innovations
                    3. Audience engagement insights
                    4. Potential industry shifts
                    5. Notable upcoming releases and developments
                    
                    first generete the insights and then summarize them in a way that it is under 280 characters.

                    Detailed Entertainment Texts: {texts}"""
                )
            }

            # Select the appropriate prompt based on category
            prompt = prompts.get(category, prompts['tech'])

            chain = LLMChain(llm=self.gemini_llm, prompt=prompt)
            result = chain.run(
                texts='\n'.join(texts[:10]),
                category=category
            )
            
            return str(result)
        except Exception as e:
            self.logger.error(f"AI insights generation error for {category}: {e}")
            return f"Trending insights for {category}: Key developments observed"

    def analyze_trend_data(self, category):
        """Analyze trend data for a specific category"""
        try:
            # Load trend data
            filepath = os.path.join('data', 'trends', f'{category}_trends.json')
            
            with open(filepath, 'r', encoding='utf-8') as f:
                trend_data = json.load(f)
            
            # Extract texts from top posts
            texts = [post['text'] for post in trend_data.get('postMetrics', {}).get('topPosts', [])]
            
            if not texts:
                self.logger.warning(f"No texts found for {category} trends")
                return None
            
            # Perform analyses
            sentiments = self.advanced_sentiment_analysis(texts)
            topics = self._perform_topic_clustering(texts)
            
            # Generate AI insights (synchronous for now)
            ai_insights = self.generate_ai_insights(texts, category)
            
            # Prepare trend analysis
            trend_analysis = {
                'category': category,
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
            
            self.logger.info(f"Analysis completed for {category}")
            return trend_analysis
        
        except Exception as e:
            self.logger.error(f"Error in {category} trend analysis: {e}")
            traceback.print_exc()
            return None

class BlueskyPoster:
    def __init__(self, logger=None):
        """Initialize Bluesky Poster"""
        self.logger = logger or logging.getLogger(__name__)
        self.client = Client()
        
        # Initialize Gemini for post generation
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            google_api_key="AIzaSyDFCC3WxFXkar2cuZWBLNkFweuzIVB1hRE"  # Replace with your API key
        )

    def format_post(self, text, max_length=300):
        """Format post for Bluesky"""
        text = ' '.join(text.split())
        if len(text) > max_length:
            sentences = text.split('. ')
            truncated_text = ''
            for sentence in sentences:
                if len(truncated_text) + len(sentence) + 3 <= max_length:
                    truncated_text += sentence + '. '
                else:
                    break
            text = (truncated_text.strip() + '...').strip()[:max_length]
        return text

    def generate_post(self, analysis_file):
        """Generate Bluesky post from trend analysis"""
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            category = analysis_data['category']
            insights = str(analysis_data.get('ai_insights', ''))
            
            # Robust sentiment handling
            sentiments = analysis_data.get('sentiment_analysis', {})
            top_sentiment = 'Recent trends'
            
            # Try multiple ways to extract a meaningful sentiment text
            try:
                # First, try the nested structure
                if sentiments.get('top_positive'):
                    top_sentiment = sentiments['top_positive'][0].get('text', top_sentiment)
                
                # If that fails, try a different approach
                elif 'sentiment' in sentiments:
                    top_sentiment = next(
                        (item.get('text', top_sentiment) 
                        for item in sentiments.get('sentiment', []) 
                        if item.get('sentiment') == 'positive'),
                        top_sentiment
                    )
            except Exception:
                # If all else fails, use a generic trend text
                pass
            
            # Safe hashtag handling
            top_hashtags = analysis_data.get('topHashtags', [])
            # Convert hashtags to strings and ensure they start with #
            safe_hashtags = [f'#{tag}' if not str(tag).startswith('#') else str(tag) 
                            for tag in top_hashtags[:2]]
            default_hashtags = {
                'financial': ['#Finance', '#Investment'],
                'tech': ['#TechTrends', '#Innovation'],
                'crypto': ['#Crypto', '#Blockchain'],
                'entertainment': ['#EntertainmentNews', '#PopCulture']
            }
            
            # Use default hashtags if no hashtags found
            hashtags = safe_hashtags if safe_hashtags else default_hashtags.get(category, ['#Trends'])
            hashtag_string = ' '.join(hashtags)

            # More robust prompt creation
            emoji_map = {
                'financial': '📈',
                'tech': '🚀',
                'crypto': '₿',
                'entertainment': '🎬'
            }
            emoji = emoji_map.get(category, '✨')

            # More distinctive prompts for each category
            prompts = {
                'financial': f"""{emoji} Financial Pulse: {top_sentiment}
    - Market insights
    - Investment snapshot
    {hashtag_string}

    Crisp market update.""",
                
                'tech': f"""{emoji} Tech Frontier: {top_sentiment}
    - Innovation highlights
    - Tech trend snapshot
    {hashtag_string}

    Cutting-edge insights.""",
                
                'crypto': f"""{emoji} Crypto Momentum: {top_sentiment}
    - Blockchain updates
    - Crypto market pulse
    {hashtag_string}

    Quick crypto insights.""",
                
                'entertainment': f"""{emoji} Entertainment Buzz: {top_sentiment}
    - Pop culture highlights
    - Trending entertainment
    {hashtag_string}

    What's hot right now."""
            }
            
            # Fallback to a generic prompt if category not found
            prompt = prompts.get(category, prompts['tech'])
            
            # Use Gemini to refine and format the post
            prompt_template = PromptTemplate(
                input_variables=['insights', 'prompt'],
                template="""Refine this post to be engaging, informative, and within 280 characters:

    Original Prompt: {prompt}

    Additional Context: {insights}

    Guideline:
    - keep it under 200 characters
    - Capture key insights
    - Use an engaging tone
    - Fit within character limit
    - Maintain core message
    - give the ai insights first and then summarize them in a way that it is under 200 characters.
    - dont use bold or italic text in the post just normal text and emojies.
    """
            )
            
            chain = LLMChain(llm=self.gemini_llm, prompt=prompt_template)
            post_text = chain.run({
                'insights': insights,
                'prompt': prompt
            })
            
            # Ensure post is not empty and fits character limit
            formatted_post = self.format_post(str(post_text))
            
            # Additional check to prevent empty posts
            if not formatted_post or len(formatted_post) < 10:
                # Fallback to a generic post if generation fails
                fallback_posts = {
                    'financial': f"📈 Market pulse: Navigating financial landscapes with smart insights! {hashtag_string}",
                    'tech': f"🚀 Tech frontier: Innovations reshaping our digital world! {hashtag_string}",
                    'crypto': f"₿ Crypto chronicles: Blockchain breaking barriers! {hashtag_string}",
                    'entertainment': f"🎬 Entertainment spotlight: Where creativity meets excitement! {hashtag_string}"
                }
                formatted_post = fallback_posts.get(category, fallback_posts['tech'])
            
            return formatted_post
        
        except Exception as e:
            self.logger.error(f"Post generation error: {e}")
            traceback.print_exc()
            return None

    def post_to_bluesky(self, post):
        """Post to Bluesky"""
        if not post:
            return False
        
        try:

            self.client.login('smartbot.bsky.social', 'abcd@123')
            self.client.send_post(text=post)
            return True
        except Exception as e:
            self.logger.error(f"Bluesky posting failed: {e}")
            traceback.print_exc()
            return False

def setup_logging():
    """Set up logging configuration"""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'trend_poster_{timestamp}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

async def main():
    """Main workflow"""
    logger = setup_logging()
    logger.info("Trend Analysis and Bluesky Poster Starting...")
    
    # Initialize components
    trend_analyzer = TrendAnalyzer(logger)
    bluesky_poster = BlueskyPoster(logger)
    
    # Categories to process
    categories = ['finance', 'crypto', 'entertainment', 'tech']
    
    try:
        # Analyze trends for each category
        for category in categories:
            # Analyze trend and save results
            trend_analysis = trend_analyzer.analyze_trend_data(category)
            
            if trend_analysis:
                # Generate Bluesky post from analysis
                analysis_file = os.path.join('analysis_results', f'{category}_trend_analysis.json')
                post = bluesky_poster.generate_post(analysis_file)
                
                # Post to Bluesky
                if post:
                    bluesky_poster.post_to_bluesky(post)
                
                # Add a small delay between posts
                await asyncio.sleep(2)
    
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        traceback.print_exc()

async def run_workflow_periodically():
    """Run the main workflow periodically every 10 minutes"""
    logger = setup_logging()
    logger.info("Starting periodic Trend Analysis and Bluesky Poster...")
    
    while True:
        try:
            # Initialize components
            trend_analyzer = TrendAnalyzer(logger)
            bluesky_poster = BlueskyPoster(logger)
            
            # Categories to process
            categories = ['finance', 'crypto', 'entertainment', 'tech']
            
            # Analyze trends for each category
            for category in categories:
                # Analyze trend and save results
                trend_analysis = trend_analyzer.analyze_trend_data(category)
                
                if trend_analysis:
                    # Generate Bluesky post from analysis
                    analysis_file = os.path.join('analysis_results', f'{category}_trend_analysis.json')
                    post = bluesky_poster.generate_post(analysis_file)
                    
                    # Post to Bluesky
                    if post:
                        bluesky_poster.post_to_bluesky(post)
                    
                    # Add a small delay between posts
                    await asyncio.sleep(2)
            
            # Log the completion of a workflow cycle
            logger.info("Workflow cycle completed. Waiting for next cycle...")
            
            # Wait for 10 minutes before next run
            await asyncio.sleep(900)  # 600 seconds = 10 minutes
        
        except Exception as e:
            logger.error(f"Periodic workflow error: {e}")
            traceback.print_exc()
            
            # Wait 10 minutes even if an error occurs
            await asyncio.sleep(900)

async def main():
    """Main entry point with periodic workflow"""
    # Create a task for the periodic workflow
    workflow_task = asyncio.create_task(run_workflow_periodically())
    
    # Wait indefinitely to keep the script running
    await workflow_task

if __name__ == '__main__':
    asyncio.run(main())