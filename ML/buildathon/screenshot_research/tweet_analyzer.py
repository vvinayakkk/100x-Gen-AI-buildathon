import cv2
import numpy as np
from paddleocr import PaddleOCR
import os
import logging
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import google.generativeai as genai
import re

class TweetAnalyzer:
    def __init__(self):
        load_dotenv()
        
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found")

        genai.configure(api_key=GOOGLE_API_KEY)
        self.llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        except Exception as e:
            logging.error(f"OCR initialization failed: {e}")
            self.ocr = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._init_prompts()

    def _init_prompts(self):
        self.analysis_prompt = PromptTemplate(
            input_variables=["tweet_text"],
            template="""
            Analyze this tweet content concisely:
            1. Summary
            2. Main topics
            3. Key insights
            4. Sentiment
            5. Suggested reply

            Tweet: {tweet_text}
            """
        )

    def _clean_text(self, text):
        """Remove markdown, extra whitespaces, and unnecessary formatting."""
        # Remove markdown symbols
        text = re.sub(r'[*_#]', '', text)
        
        # Remove extra newlines and whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def extract_text_from_image(self, image_path):
        try:
            image = cv2.imread(image_path)
            result = self.ocr.ocr(image)
            
            text_results = [line[1][0] for line in result[0]] if result[0] else []
            return ' '.join(text_results).strip()
        except Exception as e:
            self.logger.error(f"Text extraction error: {e}")
            return ""

    async def analyze_tweet(self, text):
        try:
            analysis_chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
            raw_analysis = await analysis_chain.arun(tweet_text=text)
            return self._clean_text(raw_analysis)
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return "Analysis failed"

    async def process_tweet_image(self, image_path):
        try:
            text = self.extract_text_from_image(image_path)
            if not text:
                return "No text extracted"
            
            analysis = await self.analyze_tweet(text)
            return {
                "extracted_text": text,
                "analysis": analysis
            }
        except Exception as e:
            return f"Processing error: {e}"