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
from langchain.prompts import PromptTemplate
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

# Enhanced Route Patterns (same as before)
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
        Initialize the Intent Router with Gemini integration
        
        :param api_key: Google Gemini API Key
        """
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            google_api_key=api_key,
            temperature=0.2  # Low temperature for more deterministic responses
        )
        
        # Create prompt template for route classification
        self.prompt_template = PromptTemplate(
            input_variables=["instruction", "tweet"],
            template="""
            You are an expert intent classifier. Given the following user instruction 
            and original tweet context, classify it into one of these routes: 
            1. screenshot_research
            2. persona_simulation
            3. thread_generation
            4. fact_checking
            5. sentiment_analysis
            6. meme_generation
            7. tweet_helper

            User Instruction: {instruction}
            Original Tweet: {tweet}

            Provide your response as the EXACT route name. 
            Be precise and consider the primary intent of the instruction.
            """)
        
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