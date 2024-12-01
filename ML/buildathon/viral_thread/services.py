# tweet_generator/services.py

import os
from typing import List, Dict
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline
from textblob import TextBlob
import logging
import re
from datetime import datetime
import random
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TweetMetricsAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def count_emojis(self, text: str) -> int:
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return len(emoji_pattern.findall(text))

    def analyze(self, text: str) -> Dict:
        sentiment_result = self.sentiment_analyzer(text)[0]
        blob = TextBlob(text)

        return {
            "sentiment": sentiment_result["label"],
            "confidence": sentiment_result["score"],
            "subjectivity": blob.sentiment.subjectivity,
            "polarity": blob.sentiment.polarity,
            "emoji_count": self.count_emojis(text),
            "character_count": len(text),
            "word_count": len(text.split())
        }

class TwitterStyleAnalyzer:
    def __init__(self):
        self.style_indicators = {
            "emotional_triggers": ["wild", "insane", "crying", "screaming", "based", "real", "unhinged", "no way", "literally dead"],
            "engagement_words": ["ratio", "hot take", "thread", "debate me", "fight me", "thoughts?", "disagree?"],
            "power_words": ["actually", "literally", "objectively", "factually", "historically", "technically"],
            "meme_phrases": ["ngl", "fr fr", "iykyk", "lowkey", "highkey", "based", "chad", "W", "L", "no cap", "bussin"],
            "sass_words": ["bestie", "literally", "imagine", "apparently", "supposedly", "girlie", "bestie"],
            "dark_humor": ["oof", "rip", "dead", "crying", "screaming", "help"],
            "internet_slang": ["tbh", "imo", "idk", "nvm", "dm", "rt", "fyi", "aka"],
            "viral_formats": ["POV:", "NOT THE", "it's giving", "the way that", "y'all"],
            "argument_starters": ["respectfully", "with peace and love", "no offense but", "hot take"],
            "current_year_slang": ["slay", "periodt", "ate", "understood the assignment", "main character"],
            "transitions": ["meanwhile", "however", "but wait", "plot twist", "on the flip side", "here's the tea"],
            "perspective_markers": ["unpopular opinion", "hot take", "controversial but", "hear me out", "plot twist"]
        }

        self.time_periods = {
            "morning": (5, 11),
            "afternoon": (12, 16),
            "evening": (17, 20),
            "night": (21, 4)
        }

    def get_optimal_posting_time(self) -> str:
        current_hour = datetime.now().hour
        for period, (start, end) in self.time_periods.items():
            if start <= current_hour <= end:
                return period
        return "night"

    def analyze_style(self, text: str) -> Dict:
        metrics = {
            "sass_level": 0,
            "meme_density": 0,
            "engagement_potential": 0,
            "dark_humor_score": 0,
            "slang_usage": 0,
            "argument_strength": 0,
            "viral_format_count": 0,
            "contemporary_score": 0,
            "perspective_balance": 0
        }

        text_lower = text.lower()

        # Calculate comprehensive style metrics
        sass_count = sum(word in text_lower for word in self.style_indicators["sass_words"])
        meme_count = sum(phrase in text_lower for phrase in self.style_indicators["meme_phrases"])
        engagement_count = sum(word in text_lower for word in self.style_indicators["engagement_words"])
        dark_humor_count = sum(word in text_lower for word in self.style_indicators["dark_humor"])
        slang_count = sum(word in text_lower for word in self.style_indicators["internet_slang"])
        argument_count = sum(phrase in text_lower for phrase in self.style_indicators["argument_starters"])
        viral_format_count = sum(format in text_lower for format in self.style_indicators["viral_formats"])
        contemporary_count = sum(slang in text_lower for slang in self.style_indicators["current_year_slang"])
        perspective_count = sum(marker in text_lower for marker in self.style_indicators["perspective_markers"])

        # Calculate normalized scores (0-100)
        word_count = len(text_lower.split())
        metrics["sass_level"] = min((sass_count / max(word_count, 1)) * 200, 100)
        metrics["meme_density"] = min((meme_count / max(word_count, 1)) * 200, 100)
        metrics["engagement_potential"] = min((engagement_count / max(word_count, 1)) * 200, 100)
        metrics["dark_humor_score"] = min((dark_humor_count / max(word_count, 1)) * 200, 100)
        metrics["slang_usage"] = min((slang_count / max(word_count, 1)) * 200, 100)
        metrics["argument_strength"] = min((argument_count / max(word_count, 1)) * 200, 100)
        metrics["viral_format_count"] = viral_format_count
        metrics["contemporary_score"] = min((contemporary_count / max(word_count, 1)) * 200, 100)
        metrics["perspective_balance"] = min((perspective_count / max(word_count, 1)) * 200, 100)

        # Calculate overall metrics
        metrics["clout_factor"] = min(
            (metrics["sass_level"] + metrics["meme_density"] + metrics["engagement_potential"]) / 3,
            100
        )

        metrics["twitter_native_score"] = min(
            (metrics["slang_usage"] + metrics["contemporary_score"] + metrics["viral_format_count"] * 20) / 3,
            100
        )

        metrics["ratio_potential"] = min(
            (metrics["argument_strength"] + metrics["dark_humor_score"] + metrics["sass_level"]) / 3,
            100
        )

        # Generate style tags
        metrics["style_tags"] = []
        if metrics["sass_level"] > 70: metrics["style_tags"].append("extra_sassy")
        if metrics["meme_density"] > 70: metrics["style_tags"].append("meme_lord")
        if metrics["dark_humor_score"] > 70: metrics["style_tags"].append("edgy")
        if metrics["engagement_potential"] > 70: metrics["style_tags"].append("engagement_bait")
        if metrics["contemporary_score"] > 70: metrics["style_tags"].append("extremely_online")
        if metrics["perspective_balance"] > 70: metrics["style_tags"].append("balanced_take")

        return metrics

class EnhancedViralThreadGenerator:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.llm = GoogleGenerativeAI(model="gemini-pro",
                                    google_api_key=settings.GOOGLE_API_KEY)
        self.tweet_metrics = TweetMetricsAnalyzer()
        self.style_analyzer = TwitterStyleAnalyzer()
        self.setup_prompts()
        self.setup_chains()

    def setup_prompts(self):
        self.hook_template = PromptTemplate(
            input_variables=["topic"],
            template="""
            Create an attention-grabbing first tweet about {topic}.
            Make it controversial but not extreme, setting up for both supporting and opposing views.
            Use peak Twitter language, max sass, and current slang. Include relevant emojis.
            Make it provocative, spicy, and memorable. Under 280 characters.
            Mix memes, dark humor, and actual insights.
            Use current Twitter formats like "POV:", "NOT THE", "it's giving".
            Make it feel extremely online while still being smart.
            """
        )

        self.thread_template = PromptTemplate(
            input_variables=["topic", "hook", "perspective"],
            template="""
            Generate 2 {perspective} tweets continuing from this hook about {topic}:
            "{hook}"

            Make the thread:
            1. Peak Twitter energy (bestie, periodt, slay, etc.)
            2. Include spicy takes and well-reasoned arguments
            3. Mix humor with insights
            4. Use current meme formats and callbacks
            5. Add thought-provoking points
            6. Keep building momentum
            7. Each tweet under 280 characters
            8. Heavy emoji and slang usage

            Maintain the {perspective} perspective while acknowledging potential counterpoints.
            Make it feel authentic and viral-worthy.
            Format as a list of 2 tweets, separated by newlines.
            """
        )

        self.counterpoint_template = PromptTemplate(
            input_variables=["topic", "previous_tweet"],
            template="""
            Create a spicy counterpoint tweet to this take about {topic}:
            "{previous_tweet}"

            Make it:
            1. Challenge the previous point while staying respectful
            2. Use Twitter language and current slang
            3. Include emojis and meme formats
            4. Keep it under 280 characters
            5. Make it quotable and engaging
            """
        )

        self.finale_template = PromptTemplate(
            input_variables=["topic"],
            template="""
            Create a balanced concluding tweet about {topic}.
            Acknowledge multiple perspectives while adding your own spicy take.
            Make it memorable and quotable.
            Use peak Twitter energy and current slang.
            Include relevant emojis.
            Under 280 characters.
            End with a call for engagement.
            """
        )

    def setup_chains(self):
        self.hook_chain = LLMChain(llm=self.llm, prompt=self.hook_template, verbose=True)
        self.thread_chain = LLMChain(llm=self.llm, prompt=self.thread_template, verbose=True)
        self.counterpoint_chain = LLMChain(llm=self.llm, prompt=self.counterpoint_template, verbose=True)
        self.finale_chain = LLMChain(llm=self.llm, prompt=self.finale_template, verbose=True)

    def optimize_tweet(self, tweet: str) -> str:
        style_metrics = self.style_analyzer.analyze_style(tweet)

        if style_metrics["twitter_native_score"] < 70:
            enhance_prompt = PromptTemplate(
                input_variables=["tweet"],
                template="""
                Make this tweet absolutely unhinged (in a good way).
                Max out the sass, add current memes, and make it extremely online.
                Keep the core message but make it Twitter native af:
                {tweet}
                """
            )

            enhance_chain = LLMChain(llm=self.llm, prompt=enhance_prompt)
            enhanced_tweet = enhance_chain.run(tweet=tweet)

            new_style_metrics = self.style_analyzer.analyze_style(enhanced_tweet)
            if new_style_metrics["twitter_native_score"] > style_metrics["twitter_native_score"]:
                return enhanced_tweet

        return tweet

    def generate_thread(self, topic: str) -> Dict:
        logger.info(f"Generating viral thread about: {topic}")

        try:
            # Generate hook
            hook = self.hook_chain.run(topic=topic)
            hook = self.optimize_tweet(hook.strip())

            # Generate supporting tweets
            supporting_content = self.thread_chain.run(
                topic=topic,
                hook=hook,
                perspective="supporting"
            )
            supporting_tweets = supporting_content.strip().split('\n')

            # Generate opposing tweets
            opposing_content = self.thread_chain.run(
                topic=topic,
                hook=hook,
                perspective="opposing"
            )
            opposing_tweets = opposing_content.strip().split('\n')

            # Generate additional counterpoints
            counterpoints = []
            for tweet in supporting_tweets + opposing_tweets:
                if random.random() < 0.3:  # 30% chance for each tweet to get a counterpoint
                    counterpoint = self.counterpoint_chain.run(
                        topic=topic,
                        previous_tweet=tweet
                    )
                    counterpoints.append(self.optimize_tweet(counterpoint.strip()))

            # Generate finale
            finale = self.finale_chain.run(topic=topic)
            finale = self.optimize_tweet(finale.strip())

            # Combine all tweets with transitions
            transitions = [
                "Now here's where it gets spicy... 👀",
                "BUT WAIT bestie, consider this... 🤔",
                "Plot twist incoming... 🌀",
                "Hot take loading... 🔥",
                "Unpopular opinion time... 💅",
                "Let's flip the script real quick... 🔄",
                "Tea time besties... ☕️",
                "The discourse™️ continues... 🎭",
                "Meanwhile, in another timeline... 🌌",
                "Prepare for a reality check... ⚡️"
            ]

            # Interleave supporting and opposing tweets
            middle_tweets = []
            for s, o in zip(supporting_tweets, opposing_tweets):
                if random.random() < 0.3:  # 30% chance for transition before supporting tweet
                    middle_tweets.append(random.choice(transitions))
                middle_tweets.append(s)
                if random.random() < 0.3:  # 30% chance for transition before opposing tweet
                    middle_tweets.append(random.choice(transitions))
                middle_tweets.append(o)

            # Insert counterpoints randomly
            for counterpoint in counterpoints:
                position = random.randint(0, len(middle_tweets))
                if random.random() < 0.3:  # 30% chance for transition before counterpoint
                    middle_tweets.insert(position, random.choice(transitions))
                middle_tweets.insert(position, counterpoint)

            # Combine all tweets
            all_tweets = [hook] + middle_tweets + [finale]

            # Generate metrics for each tweet
            optimized_thread = []
            for i, tweet in enumerate(all_tweets):
                if tweet:
                    optimized_tweet = self.optimize_tweet(tweet)

                    # Get comprehensive metrics
                    tweet_metrics = self.tweet_metrics.analyze(optimized_tweet)
                    style_metrics = self.style_analyzer.analyze_style(optimized_tweet)

                    optimized_thread.append({
                        # "position": i + 1,
                        "content": optimized_tweet
                        # "metrics": {
                        #     "basic_metrics": tweet_metrics,
                        #     "style_metrics": style_metrics,
                        #     "optimal_posting_time": self.style_analyzer.get_optimal_posting_time()
                        }
                    )

            return optimized_thread

        except Exception as e:
            logger.error(f"Error generating thread: {str(e)}")
            raise