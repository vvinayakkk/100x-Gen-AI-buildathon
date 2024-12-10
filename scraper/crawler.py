import asyncio
import json
import logging
import os
import re
from typing import Dict, List, Any
from datetime import datetime, timedelta, timezone

import aiofiles
# Using atproto for AT Protocol interactions
from atproto import AsyncClient
from dotenv import load_dotenv


# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging to write to both console and file
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [Line: %(lineno)d]',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'bluesky_crawler.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


# Global logger
logger = setup_logging()


class BlueskyAdvancedCrawler:
    def __init__(self):
        # Log initialization start
        logger.info("Initializing BlueskyAdvancedCrawler")

        # Load environment variables
        load_dotenv()

        # Initialize Bluesky async client
        self.client = AsyncClient()

        # Define base data store path
        base_path = os.path.join(os.path.dirname(__file__), 'data')
        logger.info(f"Base data path set to: {base_path}")

        # Optimized categories structure
        self.categories = {
            'stock_updates': os.path.join(base_path, 'stocks', 'latest.json'),
            'financial_news': os.path.join(base_path, 'financial_news', 'latest.json'),
            'investment_insights': os.path.join(base_path, 'investment_insights', 'latest.json'),
            'crypto_news': os.path.join(base_path, 'crypto', 'latest.json'),
            'trends': {
                'tech': os.path.join(base_path, 'trends', 'tech_trends.json'),
                'finance': os.path.join(base_path, 'trends', 'finance_trends.json'),
                'crypto': os.path.join(base_path, 'trends', 'crypto_trends.json'),
                'entertainment': os.path.join(base_path, 'trends', 'entertainment_trends.json')
            }
        }
        logger.info("Categories and paths configured successfully")

    async def authenticate(self):
        """Authenticate with Bluesky"""
        try:
            logger.info("Attempting to authenticate with Bluesky")
            await self.client.login(
                os.getenv('BLUESKY_HANDLE_'),
                os.getenv('BLUESKY_PASSWORD_')
            )
            logger.info('Authentication successful')
        except Exception as e:
            logger.error(f'Authentication failed: {e}')
            raise

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract unique hashtags from text"""
        hashtags = list(set(re.findall(r'#(\w+)', text)))
        logger.debug(f"Extracted {len(hashtags)} unique hashtags from text")
        return hashtags

    async def search_posts(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Async method to search posts with error handling"""
        logger.info(f"Searching posts for term: {search_term}")
        try:
            now = datetime.now(timezone.utc)
            one_hour_ago = now - timedelta(hours=1)
            # Use app.bsky.feed.searchPosts method from atproto
            results = await self.client.app.bsky.feed.search_posts({"q": search_term, "limit": limit})
            logger.info(f"Found {len(results.posts)} posts for term: {search_term}")

            processed_posts = [
                {
                    'text': post.record.text,
                    'created_at': post.record.created_at,
                    'likes': post.like_count,
                    'hashtags': self.extract_hashtags(post.record.text)
                }
                for post in results.posts if self.parse_created_at(post.record.created_at) > one_hour_ago
            ]
            logger.debug(f"Processed {len(processed_posts)} posts")
            return processed_posts
        except Exception as e:
            logger.error(f'Search error for {search_term}: {e}')
            return []

    def parse_created_at(self,created_at):
        """Attempt to parse the 'created_at' timestamp with various formats."""

        if '.' in created_at:
            date_part, time_part = created_at.split('.')
            time_part = time_part.ljust(6, '0')
            created_at = date_part

        formats = [
            '%Y-%m-%dT%H:%M:%S.%f%z',  # With fractional seconds and timezone
            '%Y-%m-%dT%H:%M:%S%z',  # Without fractional seconds, with timezone
            '%Y-%m-%dT%H:%M:%S.%fZ',  # With fractional seconds, Z timezone
            '%Y-%m-%dT%H:%M:%SZ',  # Without fractional seconds, Z timezone
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S'
        ]
        for fmt in formats:
            try:
                parsed_datetime = datetime.strptime(created_at, fmt)
                if '%z' in fmt or 'Z' in created_at:
                    return parsed_datetime.astimezone(timezone.utc)  # Convert to UTC timezone-aware
                    # If the datetime is naive (no timezone), assume UTC
                return parsed_datetime.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        raise ValueError(f"Time data '{created_at}' does not match any known formats")

    async def crawl_financial_content(self):
        """Comprehensive financial content crawler with async operations"""
        logger.info("Starting financial content crawl")
        search_terms = {
            'stocks': ['stocks', 'finance', 'investment', 'market', 'trading'],
            'crypto': ['bitcoin', 'ethereum', 'crypto', 'blockchain'],
            'trends': {
                'tech': ['ai', 'technology', 'startup'],
                'finance': ['fintech', 'investment', 'market'],
                'crypto': ['cryptocurrency', 'blockchain'],
                'entertainment': ['movies', 'streaming', 'entertainment']
            }
        }

        all_posts = {
            'stock_updates': [],
            'financial_news': [],
            'investment_insights': [],
            'crypto_news': [],
            'trends': {category: [] for category in search_terms['trends']}
        }

        # Use asyncio.gather for concurrent search operations
        search_tasks = []
        for category, terms in search_terms.items():
            if category == 'trends':
                continue
            for term in terms:
                search_tasks.append(self.search_posts(term))

        # Collect results from all search tasks
        logger.info(f"Gathering results from {len(search_tasks)} search tasks")
        search_results = await asyncio.gather(*search_tasks)

        # Process and categorize posts
        for results in search_results:
            for post in results:
                # Categorization logic
                if any(keyword in post['text'].lower() for keyword in ['stock', 'market', 'trading']):
                    all_posts['stock_updates'].append(post)
                if any(keyword in post['text'].lower() for keyword in ['financial', 'economy', 'report']):
                    all_posts['financial_news'].append(post)
                if any(keyword in post['text'].lower() for keyword in ['investment', 'strategy']):
                    all_posts['investment_insights'].append(post)
                if 'crypto' in post['text'].lower():
                    all_posts['crypto_news'].append(post)

        logger.info("Finished crawling financial content")
        await self.save_posts(all_posts)
        await self.analyze_trends()

    def _get_all_file_paths(self):
        """Recursively extract all file paths from the categories dictionary"""
        logger.debug("Extracting all file paths from categories")
        paths = []
        for value in self.categories.values():
            if isinstance(value, str):
                paths.append(value)
            elif isinstance(value, dict):
                paths.extend(self._get_dict_paths(value))
        logger.info(f"Found {len(paths)} file paths")
        return paths

    def _get_dict_paths(self, d):
        """Helper method to get paths from nested dictionaries"""
        paths = []
        for value in d.values():
            if isinstance(value, str):
                paths.append(value)
            elif isinstance(value, dict):
                paths.extend(self._get_dict_paths(value))
        return paths

    async def save_posts(self, posts: Dict[str, List[Dict[str, Any]]]):
        """Async post saving with error handling"""
        logger.info("Starting to save posts")

        # Create directories if they don't exist
        all_paths = self._get_all_file_paths()
        for path in [os.path.dirname(file_path) for file_path in all_paths]:
            os.makedirs(path, exist_ok=True)
            logger.debug(f"Ensuring directory exists: {path}")

        async def save_category(category, data):
            try:
                if isinstance(self.categories[category],dict):
                    for item in self.categories[category]:
                        async with aiofiles.open(item, 'w') as f:
                            await f.write(json.dumps(data, indent=2))
                else:
                    async with aiofiles.open(self.categories[category], 'w') as f:
                        await f.write(json.dumps(data, indent=2))
                logger.info(f'Saved {len(data)} {category} posts')
            except Exception as e:
                logger.error(f'Error saving {self.categories[category]} {category} posts: {e}',stack_info=True)

        # Use asyncio.gather for concurrent file writes
        await asyncio.gather(
            *[save_category(category, data) for category, data in posts.items() if data]
        )
        logger.info("Completed saving posts for all categories")

    async def analyze_trends(self):
        """Advanced trend analysis with async processing"""
        logger.info("Starting trend analysis")
        trend_categories = {
            'tech': [
                'ai', 'technology', 'startup',
                'machine learning', 'cloud computing',
                'cybersecurity', 'robotics',
                'quantum computing', 'virtual reality',
                'augmented reality', 'internet of things'
            ],
            'finance': [
                'investing', 'market', 'stocks',
                'cryptocurrency', 'fintech',
                'trading', 'mutual funds',
                'venture capital', 'derivatives',
                'bonds', 'portfolio management'
            ],
            'crypto': [
                'blockchain', 'bitcoin', 'ethereum',
                'defi', 'nft', 'altcoins',
                'smart contracts', 'crypto mining',
                'decentralized finance', 'web3',
                'digital wallet', 'token economics'
            ],
            'entertainment': [
                'movies', 'streaming', 'entertainment',
                'gaming', 'esports', 'podcasts',
                'social media', 'virtual concerts',
                'content creation', 'streaming platforms',
                'digital media', 'interactive entertainment'
            ]
        }
        trend_analysis = {}

        # Async trend search and analysis
        for category, terms in trend_categories.items():
            logger.info(f"Analyzing trends for category: {category}")
            trend_tasks = [self.search_posts(term) for term in terms]
            search_results = await asyncio.gather(*trend_tasks)

            hashtag_frequency = {}
            post_metrics = {
                'total_posts': 0,
                'average_likes': 0,
                'top_posts': []
            }

            for results in search_results:
                for post in results:
                    post_metrics['total_posts'] += 1
                    post_metrics['average_likes'] += post['likes']
                    post_metrics['top_posts'].append(post)

                    for hashtag in post['hashtags']:
                        hashtag_frequency[hashtag] = hashtag_frequency.get(hashtag, 0) + 1

            # Calculate metrics
            post_metrics['average_likes'] = (
                post_metrics['average_likes'] / post_metrics['total_posts']
                if post_metrics['total_posts'] > 0 else 0
            )

            # Sort and process hashtags
            sorted_hashtags = sorted(
                hashtag_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]

            trend_analysis[category] = {
                'top_hashtags': [
                    {
                        'hashtag': hashtag,
                        'count': count,
                        'percentage': round((count / post_metrics['total_posts']) * 100, 2)
                    }
                    for hashtag, count in sorted_hashtags
                ],
                'post_metrics': {
                    'total_posts': post_metrics['total_posts'],
                    'average_likes': round(post_metrics['average_likes'], 2),
                    'top_posts': sorted(
                        post_metrics['top_posts'],
                        key=lambda x: x['likes'],
                        reverse=True
                    )[:10]
                }
            }

        logger.info("Completed trend analysis")
        await self.save_trend_analysis(trend_analysis)
        return trend_analysis


    async def save_trend_analysis(self, trend_data: Dict[str, Any]):
        """Save trend analysis results"""
        trend_store_path = os.path.join(os.path.dirname(self.categories['trends']['tech']), 'analysis')
        os.makedirs(trend_store_path, exist_ok=True)
        logger.info(f"Trend analysis store path: {trend_store_path}")

        async def save_category(category, data):
            try:
                async with aiofiles.open(self.categories['trends'][category], 'w') as f:
                    await f.write(json.dumps(data, indent=2))
                logger.info(f'Saved trend analysis for {category}')
            except Exception as e:
                logger.error(f'Error saving {category} trend data: {e}')

        # Save all trend categories concurrently
        await asyncio.gather(
            *[save_category(category, data) for category, data in trend_data.items()]
        )
        logger.info("Completed saving trend analysis for all categories")

    async def start_crawling(self):
        """Main crawling process with periodic updates"""
        logger.info("Starting crawling process")
        await self.authenticate()

        # Initial crawl
        await self.crawl_financial_content()

        # Periodic crawling
        while True:
            try:
                logger.info("Waiting for next crawl cycle")
                await asyncio.sleep(30 * 60)  # 5-minute interval
                await self.crawl_financial_content()
            except Exception as e:
                logger.error(f'Periodic crawl error: {e}')


async def main():
    try:
        logger.info("Starting Bluesky Advanced Crawler")
        crawler = BlueskyAdvancedCrawler()
        await crawler.start_crawling()
    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())