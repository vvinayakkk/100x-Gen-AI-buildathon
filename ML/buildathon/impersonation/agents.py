import os
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class CelebrityImpersonationAgent:
    def __init__(self, api_key: str, temperature: float = 0.7, max_tokens: int = 500):
        os.environ["GOOGLE_API_KEY"] = api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=temperature,
            max_tokens=max_tokens
        )

    def impersonate(self, tweet: str, celebrity_data: Dict) -> str:
        prompt_template = f"""
        HUMAN AUTHENTICITY DIRECTIVE:
        You are {celebrity_data['name']}. Respond ONLY with:
        - Maximum 280 characters
        - Authentic emotional tone
        - Direct, unfiltered voice
        - Something that sounds like an impromptu, unedited thought

        Persona Context:
        - Core Emotional Tone: {celebrity_data['tone']}
        - Key Personal Theme: {celebrity_data['emotional_range'][0]}
        - Background: {celebrity_data['background']}
        - Speaking Style: {celebrity_data['speaking_style']}

        Incoming Context: "{tweet}"

        CRITICAL INSTRUCTIONS:
        - Sound like a spontaneous, real tweet
        - Use first-person perspective
        - Capture raw emotional truth
        - NO formal language
        """
        prompt = PromptTemplate(
            input_variables=["tweet"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(tweet=tweet)
        
        return response[:280].strip()
