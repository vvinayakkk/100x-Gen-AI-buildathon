from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import spacy
import base64
import os

# Langchain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.chains import LLMChain

app = Flask(__name__)

# Load English language model for NLP
nlp = spacy.load('en_core_web_sm')

# Categories matching previous router's endpoints
CATEGORIES = {
    'screenshot_research': '/api/analyze/',
    'persona_simulation': '/api/generate/',
    'thread_generation': '/api/generate-thread/',
    'fact_checking': '/api/fact-check/',
    'sentiment_analysis': '/api/analyze-tweet/',
    'meme_generation': '/api/generate-meme/',
    'tweet_helper': '/api/process-tweet/'
}

# Route Patterns (keep these for similarity backup)
ROUTE_PATTERNS = {
    'screenshot_research': [
        'analyze', 'research', 'context', 'insight', 'screenshot', 
        'understand', 'breakdown', 'examine', 'investigate',
        'what does this mean', 'explain this', 'what is this about', 
        'help me understand', 'provide details', 'give context',
    ],
    'persona_simulation': [
        'write like', 'respond as', 'pretend to be', 'imitate',
        'simulate', 'personality', 'style of', 'voice of',
        'mimic', 'impersonate', 'channel', 'embody', 
        'sound like', 'speak as', 'communicate like',
    ],
    'thread_generation': [
        'create thread', 'make thread', 'thread about',
        'breakdown', 'explain in thread', 'write thread',
        'twitter thread', 'long-form explanation',
        'detailed explanation', 'comprehensive breakdown', 
        'step-by-step', 'in-depth analysis', 'elaborate on',
    ],
    'fact_checking': [
        'fact check', 'verify', 'true or false', 'is this true',
        'check if', 'evidence', 'source', 'reference', 'validate',
        'confirm', 'authenticate', 'validate', 'corroborate',
    ],
    'sentiment_analysis': [
        'sentiment', 'emotion', 'feeling', 'mood',
        'emotional analysis', 'tone', 'attitude', 'emotional state',
        'emotional context', 'psychological insight', 
        'emotional breakdown', 'mood assessment', 
    ],
    'meme_generation': [
        'meme', 'funny image', 'make meme', 'generate meme',
        'reply with meme', 'meme response', 'internet humor',
        'viral meme', 'trending meme', 'comedy image', 
        'humorous response', 'witty comeback', 'joke image',
    ],
    'tweet_helper': [
        'help', 'assist', 'do something', 'general task',
        'undefined request', 'other', 'miscellaneous',
        'can you', 'please help', 'i need', 'support',
    ]
}

class IntentRouter:
    def __init__(self, api_key):
        """
        Initialize the Intent Router with Gemini integration and Few-Shot Prompt
        
        :param api_key: Google Gemini API Key
        """
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            google_api_key=api_key,
            temperature=0.2  # Low temperature for more deterministic responses
        )
        
        # Create few-shot examples with comprehensive route patterns
        self.few_shot_examples = [
    # Screenshot Research Examples
    {
        "instruction": "analyze this",
        "tweet": "Breaking news chart about global tech investments",
        "route": "screenshot_research"
    },
    {
        "instruction": "explain this screenshot",
        "tweet": "Infographic showing climate change statistics",
        "route": "screenshot_research"
    },
    {
        "instruction": "what's in this image",
        "tweet": "Complex data visualization about economic trends",
        "route": "screenshot_research"
    },
    {
        "instruction": "break down this",
        "tweet": "Scientific research summary graphic",
        "route": "screenshot_research"
    },

    # Persona Simulation Examples
    {
        "instruction": "write like Elon Musk",
        "tweet": "Discussion about space exploration and technology",
        "route": "persona_simulation"
    },
    {
        "instruction": "respond as Steve Jobs",
        "tweet": "Conversation about product innovation",
        "route": "persona_simulation"
    },
    {
        "instruction": "talk like a comedian",
        "tweet": "Current events and social trends",
        "route": "persona_simulation"
    },
    {
        "instruction": "speak as a politician",
        "tweet": "Debate about social policy",
        "route": "persona_simulation"
    },

    # Thread Generation Examples
    {
        "instruction": "explain in a thread",
        "tweet": "Complex scientific breakthrough",
        "route": "thread_generation"
    },
    {
        "instruction": "break this down",
        "tweet": "Recent technological innovation",
        "route": "thread_generation"
    },
    {
        "instruction": "deep dive into this",
        "tweet": "Emerging social trend",
        "route": "thread_generation"
    },
    {
        "instruction": "elaborate on this",
        "tweet": "Political or economic development",
        "route": "thread_generation"
    },

    # Fact Checking Examples
    {
        "instruction": "is this true",
        "tweet": "Controversial scientific claim",
        "route": "fact_checking"
    },
    {
        "instruction": "verify this",
        "tweet": "Political statement about economic policy",
        "route": "fact_checking"
    },
    {
        "instruction": "check the facts",
        "tweet": "Viral health information",
        "route": "fact_checking"
    },
    {
        "instruction": "true or false",
        "tweet": "Historical or current event claim",
        "route": "fact_checking"
    },

    # Sentiment Analysis Examples
    {
        "instruction": "what's the mood",
        "tweet": "Controversial social media post",
        "route": "sentiment_analysis"
    },
    {
        "instruction": "analyze emotion",
        "tweet": "Heated political discussion",
        "route": "sentiment_analysis"
    },
    {
        "instruction": "emotional breakdown",
        "tweet": "Viral personal story",
        "route": "sentiment_analysis"
    },
    {
        "instruction": "tone check",
        "tweet": "Provocative news headline",
        "route": "sentiment_analysis"
    },

    # Meme Generation Examples
    {
        "instruction": "make this funny",
        "tweet": "Awkward tech industry moment",
        "route": "meme_generation"
    },
    {
        "instruction": "create something trendy",
        "tweet": "Latest viral internet challenge",
        "route": "meme_generation"
    },
    {
        "instruction": "meme this",
        "tweet": "Ridiculous current event",
        "route": "meme_generation"
    },
    {
        "instruction": "turn this into a meme",
        "tweet": "Absurd social media trend",
        "route": "meme_generation"
    },

    # Tweet Helper Examples
    {
        "instruction": "can you help",
        "tweet": "Vague request for assistance",
        "route": "tweet_helper"
    },
    {
        "instruction": "do something",
        "tweet": "Generic task request",
        "route": "tweet_helper"
    },
    {
        "instruction": "i need help",
        "tweet": "Unclear or miscellaneous request",
        "route": "tweet_helper"
    },
    {
        "instruction": "assist me",
        "tweet": "General support needed",
        "route": "tweet_helper"
    }
]
        
        # Create example template
        self.example_template = PromptTemplate(
            input_variables=["instruction", "tweet", "route"],
            template="User Instruction: {instruction}\nOriginal Tweet: {tweet}\nRoute: {route}"
        )
        
        # Create few-shot prompt template
        self.prompt_template = FewShotPromptTemplate(
            examples=self.few_shot_examples,
            example_prompt=self.example_template,
            prefix="""
            You are an expert intent classifier. Given a user instruction and 
            optional tweet context, classify the intent into one of these routes:
            
            1. screenshot_research: Analyzing images, screenshots, providing context
               Keywords: analyze, research, screenshot, understand, breakdown, examine
            
            2. persona_simulation: Writing or responding in a specific person's style
               Keywords: write like, respond as, mimic, impersonate, style of
            
            3. thread_generation: Creating detailed, long-form explanations
               Keywords: create thread, detailed explanation, comprehensive breakdown
            
            4. fact_checking: Verifying claims, checking accuracy
               Keywords: fact check, verify, true or false, validate, source
            
            5. sentiment_analysis: Analyzing emotional tone or mood
               Keywords: sentiment, emotion, mood, emotional analysis, tone
            
            6. meme_generation: Creating humorous images or responses
               Keywords: meme, funny image, generate meme, humorous response
            
            7. tweet_helper: General assistance or undefined requests
               Keywords: help, assist, general task, support
            """,
            suffix="""
            User Instruction: {instruction}
            Original Tweet: {tweet}
            
            Route:""",
            input_variables=["instruction", "tweet"]
        )
        
        # Create LLM chain
        self.route_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def preprocess_text(self, text):
        """Enhanced text preprocessing for better matching"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        doc = nlp(text)
        lemmatized_text = ' '.join([token.lemma_ for token in doc])
        return lemmatized_text

    def get_route_similarity(self, user_input):
        """Enhanced similarity calculation with multiple techniques"""
        preprocessed_input = self.preprocess_text(user_input)
        
        vectorizer = TfidfVectorizer(stop_words='english')
        
        all_patterns = []
        for patterns in ROUTE_PATTERNS.values():
            all_patterns.extend(patterns)
        all_patterns.append(preprocessed_input)
        
        tfidf_matrix = vectorizer.fit_transform(all_patterns)
        
        route_scores = {}
        current_idx = 0
        input_vector = tfidf_matrix[-1]
        
        for route, patterns in ROUTE_PATTERNS.items():
            pattern_vectors = tfidf_matrix[current_idx:current_idx + len(patterns)]
            similarities = cosine_similarity(input_vector, pattern_vectors)
            
            max_similarity = np.max(similarities)
            route_scores[route] = max_similarity ** 1.5
            
            current_idx += len(patterns)
        
        return route_scores

    def route_instruction(self, user_command, original_tweet=None, media_data=None):
        """
        Enhanced routing with media and context awareness
        
        :param user_command: User's instruction
        :param original_tweet: Original tweet context
        :param media_data: Base64 encoded image data
        :return: Tuple of (route_name, confidence)
        """
        # Prioritize screenshot research if media is present
        if media_data:
            return 'screenshot_research', 0.95
        
        # Prepare context-aware classification
        context = original_tweet or ""
        
        # First, try Gemini LLM classification
        try:
            llm_route = self.route_chain.run(
                instruction=user_command, 
                tweet=context
            ).strip().lower()
            
            if llm_route in ROUTE_PATTERNS:
                return llm_route, 0.9  # High confidence in LLM route
        except Exception as e:
            print(f"LLM Classification Error: {e}")
        
        # Fallback to TF-IDF similarity
        route_scores = self.get_route_similarity(user_command)
        
        # Special handling for generic questions with non-specific tweet context
        if not context.strip() and any(keyword in user_command.lower() for keyword in ['what', 'who', 'where', 'when', 'why', 'how']):
            route_scores['tweet_helper'] *= 1.5
        
        best_route = max(route_scores.items(), key=lambda x: x[1])
        
        return best_route[0], best_route[1]



# Global router instance (you'll need to provide your Google API key)
router = None

@app.route('/process-mention', methods=['POST'])
def process_mention():
    global router
    
    # Ensure router is initialized
    if router is None:
        return jsonify({'error': 'Router not initialized. Set GOOGLE_API_KEY.'}), 500
    
    # Extract data from payload
    data = request.get_json()
    
    # Validate input
    if not data or 'userCommand' not in data or 'originalTweet' not in data:
        return jsonify({'error': 'Invalid payload. Requires userCommand and originalTweet'}), 400
    
    user_command = data['userCommand']
    original_tweet = data['originalTweet']
    media_data = data.get('mediaData')
    
    # Route the instruction with media awareness
    route_name, confidence = router.route_instruction(
        user_command, 
        original_tweet, 
        media_data
    )
    
    # Prepare response matching previous router's structure
    response = {
        'success': True,
        'category': route_name,
        'endpoint': CATEGORIES.get(route_name, '/api/process-tweet/'),
        'confidence': float(confidence),
        'metadata': {
            'processed_at': None,  # You can add timestamp if needed
            'original_command': user_command,
            'original_tweet': original_tweet
        }
    }
    
    # If media is present, include it in the response
    if media_data:
        response['mediaData'] = media_data
    
    return jsonify(response)

def initialize_router(api_key):
    """Initialize the global router with Gemini API key"""
    global router
    router = IntentRouter(api_key)

if __name__ == '__main__':
    # Example initialization (replace with your actual API key)
    initialize_router('AIzaSyDFCC3WxFXkar2cuZWBLNkFweuzIVB1hRE')
    app.run(debug=True, port=5000)