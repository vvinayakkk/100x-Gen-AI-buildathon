from django.shortcuts import render

# Create your views here.
# fact_checker/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import wikipedia
from langchain import PromptTemplate, LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings

class EnhancedFactChecker:
    def __init__(self):
        # Initialize NLTK
        self._setup_nltk()

        # Initialize Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.gemini = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1
        )

        # Initialize ML pipeline for zero-shot classification
        self.classifier = pipeline("zero-shot-classification")

        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(stop_words='english')

        # Setup LangChain prompt template
        self.fact_check_prompt = PromptTemplate(
            input_variables=["claim"],
            template="""
            Please analyze the following claim and provide a detailed fact-check in 100 concised characters:
            Claim: {claim}

            Provide your analysis in the following format:
            1. Verification status
            2. Supporting evidence
            3. Confidence score (0-100)
            4. Sources
            Remember 300 characters not words.Shrink it to 100 characters.
            Summarise in 100 characters or less.
            """
        )
        self.chain = LLMChain(llm=self.gemini, prompt=self.fact_check_prompt)

    def _setup_nltk(self):
        """Download required NLTK resources"""
        resources = ['punkt', 'stopwords', 'averaged_perceptron_tagger']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                nltk.download(resource)

    def _search_wikipedia(self, query, max_results=3):
        """Search Wikipedia for relevant information"""
        try:
            search_results = wikipedia.search(query, results=max_results)
            wiki_data = []

            for title in search_results:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    wiki_data.append({
                        'title': page.title,
                        'content': page.summary,
                        'url': page.url
                    })
                except (wikipedia.exceptions.DisambiguationError, 
                       wikipedia.exceptions.PageError):
                    continue

            return wiki_data
        except Exception as e:
            print(f"Wikipedia search error: {str(e)}")
            return []

    def _analyze_with_gemini(self, claim, context=""):
        """Use Gemini for advanced analysis"""
        prompt = f"""
        Analyze the following claim for factual accuracy in 300 characters not words :
        Claim: {claim}

        Additional context: {context}

        Please provide:
        1. Factual accuracy assessment
        2. Key points of verification
        3. Potential misinformation indicators
        4. Confidence level (0-100)
        Remeber to summarise to 300 characters or less
        """

        try:
            response = self.gemini.generate_text(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini analysis error: {str(e)}")
            return None

    def _check_claim_probability(self, claim):
        """Use zero-shot classification to assess claim probability"""
        try:
            result = self.classifier(
                claim,
                candidate_labels=["fact", "opinion", "misinformation"],
                hypothesis_template="This text is {}."
            )
            return {
                'labels': result['labels'],
                'scores': [float(score) for score in result['scores']]  # Convert to float for JSON serialization
            }
        except Exception as e:
            print(f"Classification error: {str(e)}")
            return None

    def _analyze_temporal_consistency(self, claim):
        """Analyze temporal aspects and future claims"""
        date_pattern = r'\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{4}\b'
        dates = re.findall(date_pattern, claim)
        current_year = datetime.now().year

        temporal_analysis = {
            'dates_found': dates,
            'has_future_dates': False,
            'temporal_inconsistencies': []
        }

        for date in dates:
            try:
                year = int(date) if len(date) == 4 else int(date.split('/')[-1])
                if year > current_year:
                    temporal_analysis['has_future_dates'] = True
                    temporal_analysis['temporal_inconsistencies'].append(
                        f"Claims future date: {year}"
                    )
            except ValueError:
                continue

        return temporal_analysis
    
    # def simple_gemini_chat(self, query):
    #     """Handles a simple chat interaction using LangChain."""
    #     try:
    #         response = self.chat_chain.invoke({"query": query})  # Using invoke instead of run
    #         return {
    #             'query': query,
    #             'response': response['text']  # Accessing the text field from response
    #         }
    #     except Exception as e:
    #         print(f"Chat error: {str(e)}")
    #         return {
    #             'query': query,
    #             'error': f"Error generating response: {str(e)}"
    #         }
        
    def _calculate_credibility_score(self, analyses):
        """Calculate overall credibility score based on all analyses"""
        score = 1.0

        # Adjust score based on probability analysis
        if analyses['probability']:
            fact_score = analyses['probability']['scores'][
                analyses['probability']['labels'].index('fact')
            ]
            misinfo_score = analyses['probability']['scores'][
                analyses['probability']['labels'].index('misinformation')
            ]
            score *= (fact_score / (fact_score + misinfo_score))

        # Adjust for temporal inconsistencies
        if analyses['temporal']['has_future_dates']:
            score *= 0.5

        # Adjust based on Wikipedia findings
        if analyses['wikipedia']['found_articles'] > 0:
            score *= 1.2

        # Cap score between 0 and 1
        return max(0.0, min(1.0, score))

    def _get_verdict(self, credibility_score):
        """Convert credibility score to verdict"""
        if credibility_score > 0.8:
            return "Highly Likely True"
        elif credibility_score > 0.6:
            return "Likely True"
        elif credibility_score > 0.4:
            return "Uncertain"
        elif credibility_score > 0.2:
            return "Likely False"
        else:
            return "Highly Likely False"

    def comprehensive_fact_check(self, claim):
        """Perform comprehensive fact-checking using multiple methods"""
        results = {
            'claim': claim,
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }

        # Parallel execution of different analysis methods
        with ThreadPoolExecutor() as executor:
            # Submit all analysis tasks
            wiki_future = executor.submit(self._search_wikipedia, claim)
            probability_future = executor.submit(self._check_claim_probability, claim)
            temporal_future = executor.submit(self._analyze_temporal_consistency, claim)

            # Get Wikipedia data
            wiki_data = wiki_future.result()
            if wiki_data:
                context = "\n".join([d['content'] for d in wiki_data])
            else:
                context = ""

            # Submit Gemini analysis with Wikipedia context
            gemini_future = executor.submit(self._analyze_with_gemini, claim, context)

            # Collect all results
            results['analyses']['wikipedia'] = {
                'found_articles': len(wiki_data),
                'articles': wiki_data
            }

            results['analyses']['probability'] = probability_future.result()
            results['analyses']['temporal'] = temporal_future.result()
            results['analyses']['gemini'] = gemini_future.result()

        # Use LangChain for final analysis
        try:
            langchain_analysis = self.chain.run(claim=claim)
            results['analyses']['langchain'] = langchain_analysis
        except Exception as e:
            print(f"LangChain analysis error: {str(e)}")
            results['analyses']['langchain'] = None

        # Calculate final credibility score
        credibility_score = self._calculate_credibility_score(results['analyses'])
        results['credibility_score'] = credibility_score
        results['verdict'] = self._get_verdict(credibility_score)

        return results
    
    

class FactCheckView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fact_checker = EnhancedFactChecker()

    def post(self, request):
        claim = request.data.get('claim')
        
        if not claim:
            return Response(
                {'error': 'Please provide a claim to fact check'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            results = self.fact_checker.comprehensive_fact_check(claim)
            filtered_response = {
                'analyses': results.get('analyses', {}),
                'langchain': results.get('analyses', {}).get('langchain', None)
            }
            return Response(filtered_response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error processing claim: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SimpleGeminiChatView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fact_checker = EnhancedFactChecker()

    def post(self, request):
        query = request.data.get('query')

        if not query:
            return Response(
                {'error': 'Please provide a query for the chat'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = self.fact_checker.simple_gemini_chat(query)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error processing query: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
