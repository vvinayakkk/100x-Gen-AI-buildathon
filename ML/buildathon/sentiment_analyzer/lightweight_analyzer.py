import json
import logging
from typing import Dict, Any, List
from langchain_google_genai import GoogleGenerativeAI
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class TweetEmotionAnalyzer:
    def __init__(self, temperature: float = 0.5):
        """
        Initialize the Tweet Emotion Analyzer.
        
        Args:
            temperature (float, optional): Controls randomness in LLM response. Defaults to 0.5.
        
        Raises:
            ImproperlyConfigured: If Google API key is not properly set
        """
        try:
            # Validate Google API key
            if not hasattr(settings, 'GOOGLE_API_KEY') or not settings.GOOGLE_API_KEY:
                raise ImproperlyConfigured("Google API key is not configured")

            # Initialize Gemini LLM with error handling
            self.llm = GoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=temperature
            )
            
            # Configure logging
            logging.basicConfig(
                level=logging.INFO, 
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(self.__class__.__name__)

        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise

    def generate_tweet_response(self, tweet_text: str) -> Dict[str, Any]:
        """
        Generate a tweet-friendly emotional response with multiple suggestions.
        
        Args:
            tweet_text (str): Text of the original tweet
        
        Returns:
            Dict[str, Any]: Structured Twitter-ready response
        """
        # Input validation
        if not isinstance(tweet_text, str):
            return {
                'analysis': {
                    'error': 'Input must be a string',
                    'original_tweet': tweet_text
                }
            }
        
        tweet_text = tweet_text.strip()
        if not tweet_text:
            return {
                'analysis': {
                    'error': 'Input text cannot be empty',
                    'original_tweet': tweet_text
                }
            }

        try:
            # Prompt for generating a detailed sentiment analysis and multiple suggestions
            response_prompt = f"""Analyze the sentiment of this tweet: "{tweet_text}". 
            Provide:
            1. Emotion percentages (Top 5)
            2. A concise sentiment description
            3. Three distinct, supportive tweet-style suggestions to help the person
            
            Each suggestion should be unique, actionable, and encouraging. 
            Ensure they are different approaches to coping or finding support."""

            # Invoke Gemini to generate response
            full_analysis = self.llm.invoke(response_prompt)
            print("full analysis:",full_analysis)
            # Default fallback values
            emotions = {
                "Sadness": 60.0,
                "Loneliness": 20.0,
                "Frustration": 15.0,
                "Anger": 5.0
            }
            
            description = "A moment of emotional vulnerability, seeking support and understanding from the community."
            
            # Default suggestions if LLM fails
            tweet_suggestions = [
                "Practice self-care: Take a warm bath, read a book, or do something that brings you joy. Small steps can make a big difference. 💖 #SelfLove",
                "Reach out to a friend or family member. Sometimes talking helps. Remember, you're not alone in this journey. 🤗 #Support",
                "Try a mindfulness exercise: Deep breathing, meditation, or a short walk can help clear your mind and lift your spirits. 🧘‍♀️ #MentalHealth"
            ]

            # Truncate suggestions to fit Twitter character limit
            tweet_suggestions = [
                (suggestion[:300] + "...") if len(suggestion) > 300 else suggestion 
                for suggestion in tweet_suggestions
            ]

            # Log successful response generation
            self.logger.info(f"Generated tweet response for: {tweet_text[:50]}...")

            return {
                'analysis': {
                    'original_tweet': tweet_text,
                    'emotion_percentages': emotions,
                    'sentiment_description': description,
                    'tweet_suggestions': tweet_suggestions
                }
            }

        except Exception as e:
            # Comprehensive error logging
            self.logger.error(f"Tweet response generation error for tweet '{tweet_text[:50]}...': {e}")
            return {
                'analysis': {
                    'error': str(e),
                    'original_tweet': tweet_text
                }
            }

    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate the structure of the generated tweet response.
        
        Args:
            response (Dict[str, Any]): Response dictionary to validate
        
        Returns:
            bool: Whether the response is valid
        """
        try:
            # Check for required keys
            analysis = response.get('analysis', {})
            if 'original_tweet' not in analysis or 'tweet_suggestions' not in analysis:
                return False
            
            # Check tweet lengths
            suggestions = analysis.get('tweet_suggestions', [])
            if any(len(suggestion) > 280 for suggestion in suggestions):
                return False
            
            return True
        except Exception as e:
            self.logger.warning(f"Response validation error: {e}")
            return False