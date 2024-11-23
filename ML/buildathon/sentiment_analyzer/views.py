from django.http import JsonResponse
from .analyzer import UltraAdvancedTweetAnalyzer
from django.views.decorators.csrf import csrf_exempt
import gc
import json
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)

@csrf_exempt
def analyze_tweet(request):
    if request.method == "POST":
        try:
            print("hi")
            # Parse incoming JSON data
            body = json.loads(request.body.decode('utf-8'))
            tweet_text = body.get("tweet_text")
            print(tweet_text)
            logging.debug(f"Received tweet text: {tweet_text}")

            if not tweet_text:
                return JsonResponse({"error": "Tweet text is required"}, status=400)

            # Perform analysis
            logging.debug("Initializing analyzer...")
            analyzer = UltraAdvancedTweetAnalyzer()

            # Call the analysis method
            logging.debug("Performing tweet analysis...")
            analysis = analyzer.hyper_tweet_analysis(tweet_text)

            logging.debug(f"Analysis result: {analysis}")

            # Clean up to free memory
            del analyzer
            gc.collect()

            # Send analysis back to frontend
            return JsonResponse({"analysis": analysis}, status=200)

        except json.JSONDecodeError:
            logging.error("Invalid JSON payload.")
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        except Exception as e:
            logging.error(f"Error during tweet analysis: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    logging.warning("Invalid HTTP method used.")
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)
