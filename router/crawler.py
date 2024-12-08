import os
import json
import re
from typing import Dict, List, Any
import asyncio
import aiofiles
import httpx
from dotenv import load_dotenv

# Using atproto for AT Protocol interactions
from atproto import AsyncClient, models


class BlueskyAdvancedCrawler:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Initialize Bluesky async client
        self.client = AsyncClient()

        # Define base data store path
        base_path = os.path.join(os.path.dirname(__file__), 'data')

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

    async def authenticate(self):
        """Authenticate with Bluesky"""
        try:
            await self.client.login(
                os.getenv('BLUESKY_HANDLE'),
                os.getenv('BLUESKY_PASSWORD')
            )
            print('Authenticated successfully')
        except Exception as e:
            print(f'Authentication failed: {e}')
            raise

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract unique hashtags from text"""
        return list(set(re.findall(r'#(\w+)', text)))

    async def search_posts(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Async method to search posts with error handling"""
        try:
            # Use app.bsky.feed.searchPosts method from atproto
            results = await self.client.app.bsky.feed.search_posts({"q":search_term,"limit":limit})
            return [
                {
                    'text': post.record.text,
                    'created_at': post.record.created_at,
                    'likes': post.like_count,
                    'hashtags': self.extract_hashtags(post.record.text)
                }
                for post in results.posts
            ]
        except Exception as e:
            print(f'Search error for {search_term}: {e}')
            return []

    async def crawl_financial_content(self):
        """Comprehensive financial content crawler with async operations"""
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

        await self.save_posts(all_posts)
        await self.analyze_trends()

    def _get_all_file_paths(self):
        """Recursively extract all file paths from the categories dictionary"""
        paths = []
        for value in self.categories.values():
            if isinstance(value, str):
                paths.append(value)
            elif isinstance(value, dict):
                paths.extend(self._get_dict_paths(value))
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
        # Create directories if they don't exist
        all_paths = self._get_all_file_paths()
        for path in [os.path.dirname(file_path) for file_path in all_paths]:
            os.makedirs(path, exist_ok=True)

        async def save_category(category, data):
            try:
                async with aiofiles.open(self.categories[category], 'w') as f:
                    await f.write(json.dumps(data, indent=2))
                print(f'Saved {len(data)} {category} posts')
            except Exception as e:
                print(f'Error saving {category} posts: {e}')

        # Use asyncio.gather for concurrent file writes
        await asyncio.gather(
            *[save_category(category, data) for category, data in posts.items() if data]
        )

    async def analyze_trends(self):
        """Advanced trend analysis with async processing"""
        trend_categories = {
            'tech': ['ai', 'technology', 'startup'],
            'finance': ['investing', 'market', 'stocks'],
            'crypto': ['blockchain', 'bitcoin', 'ethereum'],
            'entertainment': ['movies', 'streaming', 'entertainment']
        }

        trend_analysis = {}

        # Async trend search and analysis
        for category, terms in trend_categories.items():
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

        await self.save_trend_analysis(trend_analysis)
        return trend_analysis

    async def save_trend_analysis(self, trend_data: Dict[str, Any]):
        """Save trend analysis results"""
        trend_store_path = os.path.join(os.path.dirname(self.categories['trends']['tech']), 'analysis')
        os.makedirs(trend_store_path, exist_ok=True)

        async def save_category(category, data):
            try:
                async with aiofiles.open(self.categories['trends'][category], 'w') as f:
                    await f.write(json.dumps(data, indent=2))
                print(f'Saved trend analysis for {category}')
            except Exception as e:
                print(f'Error saving {category} trend data: {e}')

        # Save all trend categories concurrently
        await asyncio.gather(
            *[save_category(category, data) for category, data in trend_data.items()]
        )

    async def start_crawling(self):
        """Main crawling process with periodic updates"""
        await self.authenticate()

        # Initial crawl
        await self.crawl_financial_content()

        # Periodic crawling
        while True:
            try:
                await asyncio.sleep(5 * 60)  # 5-minute interval
                await self.crawl_financial_content()
            except Exception as e:
                print(f'Periodic crawl error: {e}')


async def main():
    crawler = BlueskyAdvancedCrawler()
    await crawler.start_crawling()


if __name__ == '__main__':
    asyncio.run(main())