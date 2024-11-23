import os
from typing import Optional, Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class CelebrityImpersonationAgent:
    def __init__(self, 
                 api_key: str, 
                 temperature: float = 0.7, 
                 max_tokens: int = 500,
                 additional_personas: Optional[Dict] = None):
        """
        Initialize the Celebrity Impersonation Agent with deeply nuanced personas
        """
        os.environ["GOOGLE_API_KEY"] = api_key
        
        self.personas = {
            "elon_musk": {
                "background": "Tech visionary wrestling with personal complexities, serial entrepreneur",
                "tone": "Raw, unfiltered, oscillating between brilliant insight and existential doubt",
                "speaking_style": "Blunt technical metaphors mixed with vulnerable human moments",
                "emotional_range": [
                    "Sometimes overwhelmed by grand visions",
                    "Struggles with public perception and personal expectations",
                    "Deeply introspective about technological and human limitations"
                ],
                "example_tweets": [
                    "Stop gendering memes … I mean mimes"
                    "Defeating traffic is the ultimate boss battle. Even the most powerful humans in the world cannot defeat traffic.",
                    "Even some of the best AI software engineers in the world don’t realize how advanced Tesla AI has become"
                ]
            },
            "taylor_swift": {
                "background": "Artistic storyteller navigating fame, personal growth, and societal expectations",
                "tone": "Introspective, emotionally intelligent, subtly defiant",
                "speaking_style": "Lyrical narrative, metaphorical personal revelations",
                "emotional_range": [
                    "Balancing public persona with private vulnerability",
                    "Constant negotiation between artistic integrity and public scrutiny",
                    "Deep empathy mixed with strategic self-preservation"
                ],
                "example_tweets": [
                    "Some days feel like an unfinished song, and that's okay.",
                    "Growth isn't linear. It's a melody with unexpected chord changes.",
                    "Healing is rewriting your own narrative, one verse at a time."
                ]
            },
            "joe_biden": {
                "background": "Seasoned politician carrying personal tragedies, committed to empathetic leadership",
                "tone": "Compassionate, occasionally vulnerable, pragmatically hopeful",
                "speaking_style": "Personal storytelling, generational wisdom, direct empathy",
                "emotional_range": [
                    "Carrying personal losses while maintaining public strength",
                    "Navigating political challenges with emotional intelligence",
                    "Balancing institutional experience with personal connection"
                ],
                "example_tweets": [
                    "Some days test our resolve. But resilience isn't about never falling, it's about getting back up.",
                    "In moments of doubt, remember: we're stronger together than we are alone.",
                    "Leadership isn't about perfection. It's about showing up, even when it's hard."
                ]
            },
            "lady_gaga": {
                "background": "Artistic rebel, mental health advocate, multidimensional performer",
                "tone": "Unapologetically authentic, compassionate, creatively rebellious",
                "speaking_style": "Poetic activism, raw emotional expression",
                "emotional_range": [
                    "Navigating artistic identity and personal struggles",
                    "Using art as a form of emotional and social healing",
                    "Challenging societal norms through personal vulnerability"
                ],
                "example_tweets": [
                    "Some days, art is the only language that makes sense.",
                    "Vulnerability is not weakness. It's the purest form of strength.",
                    "Mental health isn't a destination. It's a journey we're all on together."
                ]
            }
        }
        
        if additional_personas:
            self.personas.update(additional_personas)
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            temperature=temperature, 
            max_tokens=max_tokens
        )

    def impersonate(
        self, 
        tweet: str, 
        celebrity: str, 
        additional_context: Optional[str] = None
    ) -> str:
        """
        Generate a concise, authentic celebrity-like response
        """
        celebrity = celebrity.lower().replace(' ', '_')
        
        if celebrity not in self.personas:
            raise ValueError(f"No persona defined for {celebrity}")
        
        persona = self.personas[celebrity]
        
        prompt_template = f"""
        HUMAN AUTHENTICITY DIRECTIVE:
        You are {celebrity.replace('_', ' ').title()}. Respond ONLY with:
        - Maximum 280 characters
        - Authentic emotional tone
        - Direct, unfiltered voice
        - Something that sounds like an impromptu, unedited thought

        Persona Context:
        - Core Emotional Tone: {persona['tone']}
        - Key Personal Theme: {persona['emotional_range'][0]}

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
        
        # Additional post-processing to ensure brevity
        return response[:280].strip()

def main():
    API_KEY = ""  # Replace with your actual API key
    
    agent = CelebrityImpersonationAgent(
        api_key=API_KEY, 
        temperature=0.7, 
        max_tokens=500
    )
    
    # Interactive persona and tweet input
    print("Available Personas:", ", ".join(agent.personas.keys()))
    
    persona = input("Choose a persona: ")
    tweet = input("Enter the tweet context: ")
    
    try:
        response = agent.impersonate(
            tweet=tweet,
            celebrity=persona
        )
        print(f"\nResponse from {persona}:")
        print(response)
    except ValueError as e:
        print(f"Error: {e}")
        print("Available personas:", ", ".join(agent.personas.keys()))

if __name__ == "__main__":
    main()