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
        
        self.prompt = PromptTemplate(
            input_variables=["tweet", "instructions"],
            template="""
            System: You are an expert tweet processor designed to follow instructions precisely while maintaining responsible content standards.
            Your Task:
            1. First, understand the exact intent of the instructions
            2. Then, execute those instructions as closely as possible while staying within content guidelines
            3. Focus on the message and content rather than individuals
            4. Use creative language and wit to achieve the desired effect
            5. If asked to critique or roast, focus on the tweet's internal logic and content
            Tweet: {tweet}
            Instructions: {instructions}
            Remember: 
            - Follow the instructions' spirit exactly
            - Stay within content guidelines by being clever and creative
            - Focus on the message, not the messenger
            - Use wit and wordplay to achieve the desired effect
            - No need to be gentle - just be smart about execution
            Transformed Result (execute instructions with precision):"""
        )
        
        self.chain = self.prompt | self.llm
    
    def process_tweet(self, tweet: str, instructions: str) -> str:
        """Process a tweet based on user instructions."""
        try:
            instruction_mapping = {
                "roast": "create a sharp, pointed critique of the tweet's message and logic",
                "mock": "create an ironic analysis highlighting the tweet's contradictions",
                "criticize": "deliver a precise critique focusing on the tweet's content and claims",
                "insult": "craft a clever critique of the tweet's internal logic and assumptions"
            }
            
            processed_instructions = instruction_mapping.get(
                instructions.lower(), 
                instructions
            )
            
            result = self.chain.invoke({
                "tweet": tweet,
                "instructions": processed_instructions
            })
            
            return result.content if result.content else "Processing failed. Please try again."
        except Exception as e:
            return f"Error processing tweet: {str(e)}"