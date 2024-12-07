import asyncio
import logging
import os
from typing import List

import dotenv
import httpx
from atproto import AsyncClient, models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - [Line: %(lineno)d]'
)
logger = logging.getLogger(__name__)


class BlueSkyBot:
    MAX_IMAGE_SIZE = 10_000_000

    def __init__(self):
        # Load environment variables
        dotenv.load_dotenv()

        # Initialize Bluesky async client
        self.client = AsyncClient()
        self.session = httpx.AsyncClient()  # Use httpx for more modern async requests

    async def login(self):
        """Login to Bluesky"""
        try:
            await self.client.login(
                os.getenv('BLUESKY_HANDLE'),
                os.getenv('BLUESKY_PASSWORD')
            )
            logger.info(f'Logged in as: {os.getenv("BLUESKY_HANDLE")}')
        except Exception as e:
            logger.error(f'Login failed: {e}')
            raise

    @staticmethod
    def split_content_into_chunks(content: str, max_length: int = 299) -> List[str]:
        """Split content into chunks that fit Bluesky's character limit"""
        # Use regex to split sentences more robustly
        import re
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current_chunk = ''

        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + ' '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence[:max_length]

        if current_chunk:
            chunks.append(current_chunk.strip())

        return list(reversed(chunks))

    async def process_and_upload_image(self, image_url: str):
        """Download, process, and upload an image"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                image_data = response.content
                return image_data

            # Process image
            # with Image.open(io.BytesIO(image_data)) as img:
            #     img.thumbnail((1000, 1000))
            #     buffer = io.BytesIO()
            #     img.save(buffer, format='JPEG')
            #     processed_image = buffer.getvalue()
            #
            # # Check image size
            # if len(processed_image) > self.MAX_IMAGE_SIZE:
            #     raise ValueError('Processed image exceeds maximum size')
            #
            # # Upload to Bluesky
            # blob = await self.client.com.atproto.repo.upload_blob(processed_image)
            # return {
            #     '$type': 'app.bsky.embed.images',
            #     'images': [{
            #         'alt': 'Default response image',
            #         'image': blob.blob
            #     }]
            # }

        except Exception as e:
            logger.error(f'Image processing error: {e}')
            return None

    async def process_middleware_response(self, mention, root_post=None):
        """Process response from middleware API"""
        try:
            # Extract relevant text
            user_text = mention.record.text.split('bsky.social')[-1].strip()
            root_text = root_post.record.text if root_post else ''

            data = {
                'userCommand': user_text,
                'originalTweet': root_text
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{os.getenv('API_MIDDLEWARE')}/process-mention",
                    json=data
                )
                response_data = response.json()

            return await self.handle_response_category(response_data, mention, root_post)

        except Exception as e:
            logger.error(f'Middleware processing error: {e}')
            return False

    async def handle_response_category(self, response_data, mention, root_post):
        """Handle different response categories"""
        category = response_data.get('category')
        result = response_data.get('result', {})

        try:
            if category == "persona_simulation":
                ai_response = str(result.get('response', ''))
                reply_chunks = self.split_content_into_chunks(ai_response)
                for chunk in reply_chunks:
                    await self.reply_to_mention(mention, root_post, chunk)

            elif category == "thread_generation":
                ai_texts = result[:5][::-1]
                for ai_text in ai_texts:
                    await self.reply_to_mention(mention, root_post, str(ai_text['content'])[:299])

            elif category == "fact_checking":
                articles = result.get('analyses', {}).get('wikipedia', {}).get('articles', [])
                if articles:
                    reply_chunks = self.split_content_into_chunks(articles[0]['content'])
                    for chunk in reply_chunks:
                        await self.reply_to_mention(mention, root_post, chunk)

            elif category == "sentiment_analysis":
                dominant_emotion = result.get('analysis', {}).get('emotion_profile', {}).get('dominant_emotion', '')
                detailed_emotions = result.get('analysis', {}).get('emotion_profile', {}).get('detailed_emotions', {})

                # Generate emotion percentage string for chart
                data_str = ','.join(str(int(float(val) * 100)) for val in detailed_emotions.values())
                chart_url = f"{os.getenv('CHART')}{data_str}"

                image_embed = await self.process_and_upload_image(chart_url)
                if image_embed:
                    await self.reply_to_mention(
                        mention,
                        root_post,
                        f"By my analysis this tweet is: {dominant_emotion}",
                        image_embed
                    )

            elif category == "meme_generation":
                url = result.get('url')
                image_embed = await self.process_and_upload_image(url)
                if image_embed:
                    result = await self.reply_to_mention(
                        mention,
                        root_post,
                        "Here's a response for you!",
                        image_embed
                    )

            elif category == "tweet_helper":
                ai_texts = result.get('result', '')
                reply_chunks = self.split_content_into_chunks(ai_texts)
                for chunk in reply_chunks:
                    await self.reply_to_mention(mention, root_post, chunk)

            return True

        except Exception as e:
            logger.error(f'Error handling response: {e}')
            return False

    async def reply_to_mention(self, mention, root_post, reply_text, image_embed=None):
        """Reply to a specific mention"""
        try:
            post_params = {
                'text': reply_text,
                'reply': {
                    'root': {
                        'uri': root_post.uri if root_post else mention.uri,
                        'cid': root_post.cid if root_post else mention.cid,
                    },
                    'parent': {
                        'uri': mention.uri,
                        'cid': mention.cid,
                    }
                }
            }

            reply_to_root = models.create_strong_ref(root_post if root_post else mention)
            reply_to_parent = models.create_strong_ref(mention)

            if image_embed:
                post_params['embed'] = image_embed
                await self.client.send_image(image_alt=reply_text, image=image_embed, text=reply_text,
                                             reply_to=models.AppBskyFeedPost.ReplyRef(parent=reply_to_parent,
                                                                                      root=reply_to_root))
            else:
                # await self.client.post(**post_params)
                await self.client.send_post(text=reply_text,
                                            reply_to=models.AppBskyFeedPost.ReplyRef(parent=reply_to_parent,
                                                                                     root=reply_to_root))
            logger.info('Successfully replied to mention')

        except Exception as e:
            logger.error(f'Reply error: {e}')

    async def get_root_post(self, uri):
        """Retrieve the root post for a given URI"""
        try:
            thread = await self.client.app.bsky.feed.get_post_thread({'uri': uri, 'depth': 0})
            post = thread.thread.post if thread.thread and hasattr(thread.thread, 'post') else None

            return post
        except Exception as e:
            logger.error(f'Error getting root post: {e}')
            return None

    async def check_mentions(self):
        """Check and process new mentions"""
        try:
            # Get notifications
            notifications = await self.client.app.bsky.notification.list_notifications()

            # Filter unread mentions
            mentions = [
                notif for notif in notifications.notifications
                if notif.reason == 'mention' and not notif.is_read
            ]

            if not mentions:
                return

            logger.info(f'Processing {len(mentions)} new mentions...')

            for mention in mentions:
                # Get the root post if it's a reply
                root_post = await self.get_root_post(mention.record.reply.parent.uri) if hasattr(mention.record,
                                                                                                 'reply') else None

                # Process the mention
                await self.process_middleware_response(mention, root_post)

                # Mark notifications as read
                await self.client.app.bsky.notification.update_seen({
                    'seen_at': self.client.get_current_time_iso()
                })
                logger.error("Marked as read!")

        except Exception as e:
            logger.error(f'Check mentions error: {e}')
            # Attempt re-login if authentication error
            if 'auth' in str(e).lower():
                await self.login()

    async def run_bot(self):
        """Main bot run method"""
        await self.login()
        logger.info('Bot started! Checking mentions every 30 seconds...')

        while True:
            await self.check_mentions()
            await asyncio.sleep(30)


async def main():
    bot = BlueSkyBot()
    try:
        await bot.run_bot()
    except Exception as e:
        logger.error(f'Bot crashed: {e}')
        # Optional: Add restart logic or notification mechanism


if __name__ == '__main__':
    asyncio.run(main())
