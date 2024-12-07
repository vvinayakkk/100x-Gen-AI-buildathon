from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os

class FlexibleTweetProcessor:
    def __init__(self):
        """Initialize the processor with Google API key from environment."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            temperature=0.9
        )
        
        self.general_prompt = PromptTemplate(
            input_variables=["context", "instructions"],
            template="""System: You are a versatile AI assistant specializing in creative and precise responses for Twitter-style content.
            
            Context: {context}
            
            Specific Instructions: {instructions}
            
            Guidelines:
            - Provide a response that is concise, engaging, and tailored to the Twitter format
            - Use wit, creativity, and clarity
            - Ensure the response is informative and captures the essence of the query
            - If the context is a tweet, analyze it with a sharp, insightful perspective
            
            Your Response (creative and precise):"""
        )
        
        self.critique_prompt = PromptTemplate(
            input_variables=["tweet", "instructions"],
            template="""System: You are an expert tweet critic with razor-sharp wit and analytical skills.
            
            Tweet: {tweet}
            
            Critique Instructions: {instructions}
            
            Execution Guidelines:
            - Deconstruct the tweet's logic with surgical precision
            - Use clever wordplay and irony
            - Focus on content and underlying assumptions
            - Be entertainingly critical without being needlessly harsh
            
            Critical Analysis (witty and incisive):"""
        )

        self.generic_prompt = PromptTemplate(
            input_variables=["instructions"],
            template="""System: You are an AI assistant capable of answering generic questions accurately and concisely.
            
            Specific Instructions: {instructions}
            
            Your Response (direct and informative):"""
        )
        
    def _select_prompt(self, context, instructions):
        """
        Select the appropriate prompt based on the nature of the instructions.
        This function now also checks for generic questions.
        """
        critique_keywords = ['roast', 'mock', 'criticize', 'insult']
        generic_keywords = ['what', 'how', 'why', 'explain', 'define']
        
        # Check if the instructions are more aligned with a generic question
        if any(keyword in instructions.lower() for keyword in generic_keywords):
            return {
                'prompt': self.generic_prompt,
                'inputs': {
                    'instructions': instructions
                }
            }
        elif any(keyword in instructions.lower() for keyword in critique_keywords):
            return {
                'prompt': self.critique_prompt,
                'inputs': {
                    'tweet': context,
                    'instructions': instructions
                }
            }
        else:
            return {
                'prompt': self.general_prompt,
                'inputs': {
                    'context': context,
                    'instructions': instructions
                }
            }
    
    def process_tweet(self, context: str, instructions: str) -> str:
        """Process a tweet or query based on user instructions."""
        try:
            # Select appropriate prompt
            prompt_config = self._select_prompt(context, instructions)
            
            # Create chain with selected prompt
            chain = prompt_config['prompt'] | self.llm
            
            # Invoke the chain with appropriate inputs
            result = chain.invoke(prompt_config['inputs'])
            
            # If the request is generic, add a "savage" comment
            if any(keyword in instructions.lower() for keyword in ['what', 'how', 'why', 'define']):
                result.content += "\n\nP.S. I'm answering this for you, but just so you know, I'm built for more advanced features than answering simple questions. 😏 Don't ask me silly stuff like that again! JK, just kidding—I'm always here for you. 😉"

            return result.content if result.content else "Processing failed. Please try again."
        
        except Exception as e:
            return f"Error processing request: {str(e)}"
