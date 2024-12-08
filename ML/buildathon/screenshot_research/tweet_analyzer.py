import cv2
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
import datetime
import logging
from typing import Dict, List, Tuple, Optional
import os
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
from dotenv import load_dotenv

class TweetAnalyzer:
    def __init__(self):
        """Initialize the Tweet Analyzer with necessary models and configurations."""
        # Load environment variables
        load_dotenv()

        # Initialize Google API
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=GOOGLE_API_KEY)

        # Initialize Gemini Pro
        self.llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)

        # Initialize OCR
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        except Exception as e:
            logging.error(f"Failed to initialize PaddleOCR: {e}")
            self.ocr = None

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize prompt templates
        self.init_prompts()

    def init_prompts(self):
        """Initialize prompt templates for different analysis tasks."""
        self.analysis_prompt = PromptTemplate(
            input_variables=["tweet_text"],
            template="""
            Analyze this tweet content and provide:
            1. A concise summary
            keep it informative only relevant to the tweet, make sure not to give markdown format strictly
            Tweet content: {tweet_text} 

            Provide the analysis in a clear, structured format not in markdown normal text without any markdown.
            """
        )

        self.metadata_prompt = PromptTemplate(
            input_variables=["tweet_text"],
            template="""
            Extract and analyze the following metadata from this tweet:
            1. Mentioned usernames (starting with @)
            2. Hashtags (starting with #)
            3. URLs
            4. Any dates or timestamps mentioned
            5. Any locations mentioned
            6. Any organizations referenced
            Keep it as concised as possible to minimum response
            keep it informative only relevant to the tweet, make sure not to give markdown format strictly
            Tweet content: {tweet_text}

            Format the response as a structured list of findings.
            """
        )

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from tweet screenshot using PaddleOCR."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image file")

            result = self.ocr.ocr(image)

            text_results = []
            if result[0]:
                for line in result[0]:
                    text_results.append(line[1][0])

            full_text = ' '.join(text_results)
            return full_text.strip()

        except Exception as e:
            self.logger.error(f"Error extracting text from image: {e}")
            return ""

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess the image for better OCR results."""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            denoised = cv2.fastNlMeansDenoising(binary)
            return denoised
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            return None

    async def analyze_with_gemini(self, text: str) -> Dict:
        """Analyze tweet content using Gemini Pro through Langchain."""
        try:
            # Create analysis chain
            analysis_chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
            metadata_chain = LLMChain(llm=self.llm, prompt=self.metadata_prompt)

            # Run analysis
            analysis_result = await analysis_chain.arun(tweet_text=text)
            metadata_result = await metadata_chain.arun(tweet_text=text)

            return {
                "analysis": analysis_result,
                "metadata": metadata_result
            }

        except Exception as e:
            self.logger.error(f"Error in Gemini analysis: {e}")
            return {
                "analysis": "Error in analysis",
                "metadata": "Error in metadata extraction"
            }

    async def generate_report(self, image_path: str) -> Dict:
        """Generate comprehensive analysis report for a tweet screenshot."""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "source_image": image_path,
            "extracted_text": None,
            "analysis": None,
            "error": None
        }

        try:
            # Preprocess image
            preprocessed_image = self.preprocess_image(image_path)
            if preprocessed_image is None:
                raise ValueError("Failed to preprocess image")

            # Extract text
            text = self.extract_text_from_image(image_path)
            if not text:
                raise ValueError("No text could be extracted from image")
            report["extracted_text"] = text

            # Analyze with Gemini
            analysis_results = await self.analyze_with_gemini(text)
            report["analysis"] = analysis_results

        except Exception as e:
            report["error"] = str(e)
            self.logger.error(f"Error generating report: {e}")

        return report

    def format_report(self, report: Dict) -> str:
        """Format the analysis report into a readable string."""
        if report.get("error"):
            return f"Error analyzing tweet: {report['error']}"

        formatted_report = []
        formatted_report.append("🐦 Tweet Analysis Report")
        formatted_report.append("=" * 50)

        # Original Text
        formatted_report.append("\n📝 Extracted Text:")
        formatted_report.append(report["extracted_text"])
        formatted_report.append("\n" + "=" * 50)

        # Gemini Analysis
        if report["analysis"]:
            formatted_report.append("\n🤖 Thread Analysis:")
            formatted_report.append(report["analysis"]["analysis"])
            formatted_report.append("\n" + "-" * 30)

            formatted_report.append("\n📊 Metadata Analysis:")
            formatted_report.append(report["analysis"]["metadata"])

        return "\n".join(formatted_report)