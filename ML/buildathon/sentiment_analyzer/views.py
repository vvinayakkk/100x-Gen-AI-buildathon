from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .lightweight_analyzer import TweetEmotionAnalyzer
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

@csrf_exempt
def analyze_tweet(request):
    if request.method == "POST":
        try:
            # Parse incoming JSON data
            body = json.loads(request.body.decode('utf-8'))
            tweet_text = body.get("tweet_text")

            if not tweet_text:
                return JsonResponse({"error": "Tweet text is required"}, status=400)

            # Perform analysis with simple Gemini analyzer
            analyzer = TweetEmotionAnalyzer()
            analysis = analyzer.generate_tweet_response(tweet_text)

            # Send Gemini's direct response back
            return JsonResponse({"analysis": analysis}, status=200)

        except json.JSONDecodeError:
            logging.error("Invalid JSON payload.")
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        except Exception as e:
            logging.error(f"Error during tweet analysis: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    logging.warning("Invalid HTTP method used.")
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)