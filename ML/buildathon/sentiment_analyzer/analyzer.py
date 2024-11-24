# analyzer.py

import gc
import torch
import spacy
import numpy as np
import networkx as nx
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer
import gensim.downloader as api
from sklearn.cluster import KMeans
import logging
class UltraAdvancedTweetAnalyzer:
    def __init__(self):
        # Initialize basic models first
        self.nlp = spacy.load('en_core_web_lg')
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.word2vec = api.load('word2vec-google-news-300')

        # Initialize pipelines with proper tokenizer configurations
        self.models = {
            'emotion_deep': pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                tokenizer=AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base", use_fast=False)
            ),
            'sentiment_multi': pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                tokenizer=AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment", use_fast=False)
            ),
            'toxicity_advanced': pipeline(
                "text-classification",
                model="unitary/unbiased-toxic-roberta",
                tokenizer=AutoTokenizer.from_pretrained("unitary/unbiased-toxic-roberta", use_fast=False)
            ),
            'language_detection': pipeline(
                "text-classification",
                model="papluca/xlm-roberta-base-language-detection",
                tokenizer=AutoTokenizer.from_pretrained("papluca/xlm-roberta-base-language-detection", use_fast=False)
            ),
            'semantic_role': pipeline(
                "ner",
                model="dslim/bert-base-NER",
                tokenizer=AutoTokenizer.from_pretrained("dslim/bert-base-NER", use_fast=False)
            )
        }

    def hyper_tweet_analysis(self, tweet_text):
        """Main analysis method"""
        try:
            if not isinstance(tweet_text, str):
                return {'error': 'Input must be a string'}
                
            if len(tweet_text.strip()) == 0:
                return {'error': 'Input text cannot be empty'}

            logging.debug("Starting comprehensive analysis...")

            # Semantic Analysis
            semantic_graph = self._create_semantic_network(tweet_text)
            linguistic_fingerprint = self._generate_linguistic_fingerprint(tweet_text)
            
            # Basic Analysis
            basic_analysis = {
                'text': tweet_text,
                'linguistic_analysis': {
                    'syntax_tree': self._generate_syntax_tree(tweet_text),
                    'dependency_graph': self._extract_dependency_structure(tweet_text),
                    'complexity_metrics': self._compute_linguistic_complexity(tweet_text)
                },
                'semantic_analysis': {
                    'semantic_network': {
                        'nodes': list(semantic_graph.nodes()),
                        'edges': list(semantic_graph.edges())
                    },
                    'entities': self._extract_entities(tweet_text)
                }
            }

            # Advanced Analysis Components
            emotion_analysis = self._deep_emotion_analysis(tweet_text)
            sentiment_analysis = self._multi_sentiment_analysis(tweet_text)
            toxicity_assessment = self._advanced_toxicity_detection(tweet_text)
            linguistic_complexity = self._compute_linguistic_complexity(tweet_text)
            named_entities = self._extract_entities(tweet_text)
            
            # Combine all analyses into final format
            analysis = {
                'text': tweet_text,
                'emotion_profile': {
                    'detailed_emotions': emotion_analysis['detailed_emotions'],
                    'dominant_emotion': emotion_analysis['dominant_emotion']
                },
                'sentiment_layers': {
                    'rating': sentiment_analysis['rating'],
                    'confidence': sentiment_analysis['confidence']
                },
                'linguistic_complexity': linguistic_complexity,
                'named_entities': named_entities,
                'toxicity_assessment': toxicity_assessment,
                'basic_analysis': basic_analysis
            }
            
            logging.debug("Analysis completed successfully")
            return analysis

        except Exception as e:
            logging.error(f"Error during tweet analysis: {str(e)}", exc_info=True)
            return {'error': str(e)}
        
    def _extract_entities(self, text):
        """Named entity extraction using spaCy"""
        doc = self.nlp(text)
        return [
            {
                'text': ent.text,
                'type': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            }
            for ent in doc.ents
        ]
    
    def _create_semantic_network(self, text):
        """Create a semantic network from tweet text"""
        doc = self.nlp(text)
        G = nx.Graph()

        # Add tokens as nodes
        for token in doc:
            G.add_node(token.text, pos=token.pos_)

        # Connect semantically related tokens
        for token1 in doc:
            for token2 in doc:
                if token1 != token2:
                    try:
                        similarity = token1.similarity(token2)
                        if similarity > 0.5:
                            G.add_edge(token1.text, token2.text, weight=float(similarity))
                    except:
                        pass

        return G

    def _generate_syntax_tree(self, text):
        """Generate a detailed syntax tree representation"""
        doc = self.nlp(text)
        return [
            {
                'token': token.text,
                'pos': token.pos_,
                'dependency': token.dep_,
                'head': token.head.text
            } for token in doc
        ]

    def _deep_emotion_analysis(self, text):
        """Comprehensive emotion profiling with balanced probabilities"""
        try:
            # Get raw emotions from the model
            emotions_output = self.models['emotion_deep'](text, return_all_scores=True)[0]
            
            # Convert to dictionary and apply softmax for proper probability distribution
            emotion_scores = {item['label']: float(item['score']) for item in emotions_output}
            
            # Apply softmax to ensure probabilities sum to 1
            scores = np.array(list(emotion_scores.values()))
            exp_scores = np.exp(scores - np.max(scores))  # Subtract max for numerical stability
            softmax_scores = exp_scores / exp_scores.sum()
            
            # Create final emotion dictionary with normalized probabilities
            emotion_dict = dict(zip(emotion_scores.keys(), softmax_scores))
            
            # Find dominant emotion
            dominant_emotion = max(emotion_dict.items(), key=lambda x: x[1])[0]
            
            # Ensure all emotion categories are present
            final_emotions = {
                'anger': emotion_dict.get('anger', 0.0),
                'disgust': emotion_dict.get('disgust', 0.0),
                'fear': emotion_dict.get('fear', 0.0),
                'joy': emotion_dict.get('joy', 0.0),
                'neutral': emotion_dict.get('neutral', 0.0),
                'sadness': emotion_dict.get('sadness', 0.0),
                'surprise': emotion_dict.get('surprise', 0.0)
            }
            
            return {
                'detailed_emotions': final_emotions,
                'dominant_emotion': dominant_emotion
            }
        except Exception as e:
            logging.error(f"Error in emotion analysis: {str(e)}")
            # Fallback with balanced neutral emotions
            return {
                'detailed_emotions': {
                    'anger': 0.14285714,
                    'disgust': 0.14285714,
                    'fear': 0.14285714,
                    'joy': 0.14285714,
                    'neutral': 0.14285714,
                    'sadness': 0.14285714,
                    'surprise': 0.14285714
                },
                'dominant_emotion': 'neutral'
            }

    def _multi_sentiment_analysis(self, text):
        """Multi-layered sentiment analysis"""
        try:
            sentiment = self.models['sentiment_multi'](text)[0]
            # Convert numeric rating to stars format
            stars = f"{int(float(sentiment['label'].split()[0])) } stars"
            return {
                'rating': stars,
                'confidence': float(sentiment['score'])
            }
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {str(e)}")
            return {
                'rating': '3 stars',
                'confidence': 0.0
            }

    def _compute_linguistic_complexity(self, text):
        """Advanced linguistic complexity metrics"""
        try:
            doc = self.nlp(text)
            return {
                'token_diversity': len(set(token.text.lower() for token in doc)) / max(len(doc), 1),
                'syntactic_complexity': len([token for token in doc if token.pos_ in ['VERB', 'NOUN', 'ADJ']]) / max(len(doc), 1),
                'avg_word_length': float(np.mean([len(token.text) for token in doc]) if doc else 0)
            }
        except Exception as e:
            logging.error(f"Error in complexity analysis: {str(e)}")
            return {
                'token_diversity': 0.0,
                'syntactic_complexity': 0.0,
                'avg_word_length': 0.0
            }

    def _extract_dependency_structure(self, text):
        """Extract dependency structure"""
        doc = self.nlp(text)
        return {
            token.text: {
                'children': [child.text for child in token.children],
                'ancestors': [ancestor.text for ancestor in token.ancestors]
            } for token in doc
        }

    def _advanced_toxicity_detection(self, text):
        """Advanced toxicity assessment"""
        try:
            toxicity = self.models['toxicity_advanced'](text)[0]
            return {
                'toxicity_label': toxicity['label'],
                'toxicity_score': float(toxicity['score'])
            }
        except Exception as e:
            logging.error(f"Error in toxicity detection: {str(e)}")
            return {
                'toxicity_label': 'non-toxic',
                'toxicity_score': 0.0
            }

    def _generate_linguistic_fingerprint(self, text):
        """Generate a unique linguistic fingerprint"""
        doc = self.nlp(text)
        return {
            'pos_distribution': {
                pos: len([t for t in doc if t.pos_ == pos])
                for pos in set(token.pos_ for token in doc)
            },
            'unique_token_ratio': len(set(token.text.lower() for token in doc)) / len(doc) if len(doc) > 0 else 0
        }