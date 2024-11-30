from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import spacy

app = Flask(__name__)

# Load English language model for NLP
nlp = spacy.load('en_core_web_sm')

# Enhanced Route Patterns with More Comprehensive Keywords
ROUTE_PATTERNS = {
    'screenshot_research': [
        # Core intent keywords
        'analyze', 'research', 'context', 'insight', 'screenshot', 
        'understand', 'breakdown', 'examine', 'investigate',
        
        # Specific research-related phrases
        'what does this mean', 'explain this', 'what is this about', 
        'help me understand', 'provide details', 'give context',
        
        # Visual and content-related terms
        'image analysis', 'content breakdown', 'visual insights', 
        'textual context', 'deep dive', 'comprehensive review'
    ],
    'persona_simulation': [
        # Impersonation and style-related keywords
        'write like', 'respond as', 'pretend to be', 'imitate',
        'simulate', 'personality', 'style of', 'voice of',
        
        # Specific persona-related terms
        'mimic', 'impersonate', 'channel', 'embody', 
        'sound like', 'speak as', 'communicate like',
        
        # Specific types of personas
        'celebrity', 'historical figure', 'character', 
        'public persona', 'brand voice', 'influencer style'
    ],
    'thread_generation': [
        # Thread creation keywords
        'create thread', 'make thread', 'thread about',
        'breakdown', 'explain in thread', 'write thread',
        'twitter thread', 'long-form explanation',
        
        # Elaboration and explanation terms
        'detailed explanation', 'comprehensive breakdown', 
        'step-by-step', 'in-depth analysis', 'elaborate on',
        
        # Topic-related keywords
        'explain thoroughly', 'provide overview', 'break down',
        'deep explanation', 'comprehensive guide'
    ],
    'fact_checking': [
        # Verification keywords
        'fact check', 'verify', 'true or false', 'is this true',
        'check if', 'evidence', 'source', 'reference', 'validate',
        
        # Credibility and accuracy terms
        'confirm', 'authenticate', 'validate', 'corroborate',
        'cross-reference', 'accuracy check', 'truth verification',
        
        # Specific fact-checking approaches
        'find sources', 'check credibility', 'prove', 'disprove',
        'verify claim', 'check accuracy', 'investigate truth'
    ],
    'sentiment_analysis': [
        # Emotion and tone keywords
        'sentiment', 'emotion', 'feeling', 'mood',
        'emotional analysis', 'tone', 'attitude', 'emotional state',
        
        # Detailed emotional analysis terms
        'emotional context', 'psychological insight', 
        'emotional breakdown', 'mood assessment', 
        'emotional interpretation', 'sentiment depth',
        
        # Specific emotional dimensions
        'positive/negative tone', 'emotional nuance', 
        'emotional subtlety', 'feeling intensity'
    ],
    'meme_generation': [
        # Meme-related keywords
        'meme', 'funny image', 'make meme', 'generate meme',
        'reply with meme', 'meme response', 'internet humor',
        
        # Specific meme types and contexts
        'viral meme', 'trending meme', 'comedy image', 
        'humorous response', 'witty comeback', 'joke image',
        
        # Meme creation instructions
        'create funny image', 'generate humor', 'witty meme',
        'comedic response', 'humorous illustration'
    ],
    'tweet_helper': [
        # Catch-all and miscellaneous keywords
        'help', 'assist', 'do something', 'general task',
        'undefined request', 'other', 'miscellaneous',
        
        # Generic instruction terms
        'can you', 'please help', 'i need', 'support',
        'general assistance', 'not sure', 'anything else',
        
        # Wide-ranging instruction modifiers
        'general', 'misc', 'unspecified', 'random',
        'catch-all', 'default', 'not categorized'
    ]
}

def preprocess_text(text):
    """Enhanced text preprocessing for better matching"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Optional: Lemmatization for more robust matching
    doc = nlp(text)
    lemmatized_text = ' '.join([token.lemma_ for token in doc])
    return lemmatized_text

def get_route_similarity(user_input):
    """Enhanced similarity calculation with multiple techniques"""
    preprocessed_input = preprocess_text(user_input)
    
    # Create feature vectors for input and patterns
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Prepare documents for vectorization
    all_patterns = []
    for patterns in ROUTE_PATTERNS.values():
        all_patterns.extend(patterns)
    all_patterns.append(preprocessed_input)
    
    # Transform text to TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(all_patterns)
    
    # Calculate similarities for each route
    route_scores = {}
    current_idx = 0
    input_vector = tfidf_matrix[-1]
    
    for route, patterns in ROUTE_PATTERNS.items():
        pattern_vectors = tfidf_matrix[current_idx:current_idx + len(patterns)]
        similarities = cosine_similarity(input_vector, pattern_vectors)
        
        # Enhanced scoring: take maximum similarity and apply exponential decay
        max_similarity = np.max(similarities)
        route_scores[route] = max_similarity ** 1.5  # Exponential decay to penalize lower similarities
        
        current_idx += len(patterns)
    
    return route_scores

def extract_intent(text):
    """Enhanced intent extraction with more detailed analysis"""
    doc = nlp(text)
    
    # Enhanced intent extraction
    verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
    nouns = [token.lemma_ for token in doc if token.pos_ == 'NOUN']
    
    # Additional context extraction
    intent_details = {
        'verbs': verbs,
        'nouns': nouns,
        'entities': [(ent.text, ent.label_) for ent in doc.ents],
        'dependencies': [
            (token.text, token.dep_, token.head.text) 
            for token in doc 
            if token.dep_ in ['ROOT', 'dobj', 'nsubj', 'pobj']
        ],
        'primary_action': verbs[0] if verbs else None
    }
    
    return intent_details

@app.route('/', methods=['POST'])
def process_instruction():
    data = request.get_json()
    if not data or 'instruction' not in data:
        return jsonify({'error': 'No instruction provided'}), 400
    
    instruction = data['instruction']
    
    # Get similarity scores for each route
    route_scores = get_route_similarity(instruction)
    
    # Get NLP analysis
    intent_analysis = extract_intent(instruction)
    
    # Enhanced route selection with multiple fallback mechanisms
    # 1. Maximum similarity route
    best_route = max(route_scores.items(), key=lambda x: x[1])
    
    # 2. Dynamic confidence thresholding
    confidence_thresholds = {
        'screenshot_research': 0.3,
        'persona_simulation': 0.3,
        'thread_generation': 0.3,
        'fact_checking': 0.3,
        'sentiment_analysis': 0.3,
        'meme_generation': 0.3,
        'tweet_helper': 0.1
    }
    
    # Determine route with adaptive thresholding
    route_name = 'tweet_helper'
    confidence = 0
    
    for route, score in route_scores.items():
        if score > confidence_thresholds.get(route, 0.2):
            if score > confidence:
                route_name = route
                confidence = score
    
    response = {
        'route': route_name,
        'confidence': float(confidence),
        'intent_analysis': intent_analysis,
        'all_route_scores': {k: float(v) for k, v in route_scores.items()}
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)