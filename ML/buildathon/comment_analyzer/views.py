import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

class CommentSummarizer:
    def __init__(self):
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        self.init_prompts()

    def init_prompts(self):
        self.summary_prompt = PromptTemplate(
            input_variables=["tweet_context", "comments_data"],
            template="""🔍 Advanced Comment Analysis Framework

Tweet Context: {tweet_context}

Comment Analysis Directive:
- Synthesize insights from user comments
- Capture diverse perspectives
- Highlight most significant viewpoints
- Consider comment likes and engagement

Comprehensive Comment Data:
{comments_data}

Comprehensive Summarization Objectives:
1. 🌐 Sentiment Landscape
   - Detailed overview of community reaction
   - Comprehensive emotional tone analysis

2. 🏆 In-Depth Insights
   - Most significant perspectives
   - Nuanced community sentiments
   - Critical and emerging observations

3. 📊 Advanced Engagement Metrics
   - Detailed analysis of comment impacts
   - Thorough exploration of user perspectives
   - Comprehensive theme identification

Output Requirements:
- Provide a comprehensive, detailed narrative
- Use engaging and analytical language
- Incorporate contextual insights
- Ensure depth and breadth of analysis

Deliver a small concised summary that captures the complete essence of community discourse!
"""
        )

    def extract_comments_data(self, comments):
        """
        Transform comments into a structured text format for analysis
        """
        comments_text = []
        for comment in comments:
            comment_entry = (
                f"User: {comment['user']} (@{comment['username']})\n"
                f"Comment: {comment['comment']}\n"
                f"Likes: {comment['likes']}\n"
                f"Timestamp: {comment['timestamp']}\n"
                "---"
            )
            comments_text.append(comment_entry)
        
        return "\n".join(comments_text)

    def summarize_comments(self, tweet_context, comments):
        print("hi")
        """Comprehensive comment summarization with structured JSON output."""
        try:
            # Extract structured comments data
            comments_data = self.extract_comments_data(comments)
            
            # Initialize summary chain
            summary_chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
            
            # Generate comprehensive summary
            summary_result = summary_chain.run(
                tweet_context=tweet_context, 
                comments_data=comments_data
            )
            
            # Split the summary into sections
            sections = {
                "Sentiment Landscape": "",
                "In-Depth Insights": "",
                "Advanced Engagement Metrics": ""
            }
            
            current_section = None
            for line in summary_result.splitlines():
                line = line.strip()
                if line.startswith("🌐 Sentiment Landscape"):
                    current_section = "Sentiment Landscape"
                    continue
                elif line.startswith("🏆 In-Depth Insights"):
                    current_section = "In-Depth Insights"
                    continue
                elif line.startswith("📊 Advanced Engagement Metrics"):
                    current_section = "Advanced Engagement Metrics"
                    continue
                
                if current_section and line:
                    sections[current_section] += f" {line}"
            
            # Truncate each section to 300 characters for brevity
            for key in sections:
                sections[key] = sections[key].strip()[:300] + "..." if len(sections[key]) > 300 else sections[key].strip()
            
            return {
                "success": True,
                "summary": sections,
                "total_comments": len(comments),
                "analysis_depth": "comprehensive"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Instantiate summarizer
comment_summarizer = CommentSummarizer()

@csrf_exempt
@require_http_methods(["POST"])
def summarize_tweet_comments(request):
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Extract tweet context and comments
        tweet_context = data.get('tweet_context', '')
        comments = data.get('comments', [])
        
        # Validate input
        if not comments:
            return JsonResponse({
                'error': '🚫 No comments provided for summarization',
                'success': False
            }, status=400)
        
        # Generate summary
        summary_result = comment_summarizer.summarize_comments(tweet_context, comments)
        
        return JsonResponse(summary_result)
    
    except Exception as e:
        return JsonResponse({
            'error': f'🔥 Summarization Failed: {str(e)}',
            'success': False
        }, status=500)