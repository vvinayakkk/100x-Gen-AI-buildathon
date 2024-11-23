from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import requests

class MemeResponse(BaseModel):
    template_name: str = Field(description="Name of the selected meme template")
    text_array: List[str] = Field(description="Array of text elements for the meme")

class MemeTemplate:
    def __init__(self, name: str, box_count: int, template_id: str):
        self.name = name
        self.box_count = box_count
        self.template_id = template_id

class MemeGenerator:
    def __init__(self, openai_api_key: str, imgflip_username: str, imgflip_password: str):
        self.llm = ChatOpenAI(api_key=openai_api_key, temperature=1.0)
        self.imgflip_username = imgflip_username
        self.imgflip_password = imgflip_password
        
        self.templates = {
    'Drake Hotline Bling': MemeTemplate('Drake Hotline Bling', 2, '181913649'),
    'Two Buttons': MemeTemplate('Two Buttons', 3, '87743020'),
    'Left Exit 12 Off Ramp': MemeTemplate('Left Exit 12 Off Ramp', 3, '124822590'),
    'Disaster Girl': MemeTemplate('Disaster Girl', 2, '97984'),
    'Epic Handshake': MemeTemplate('Epic Handshake', 3, '135256802'),
    "Gru's Plan": MemeTemplate("Gru's Plan", 4, '131940431'),
    'Always Has Been' : MemeTemplate('Always Has Been', 2, '252600902'),
    'Sad Pablo Escobar': MemeTemplate('Sad Pablo Escobar', 3, '80707627'),
    'Batman Slapping Robin': MemeTemplate('Batman Slapping Robin', 2, '438680'),
    'Waiting Skeleton': MemeTemplate('Waiting Skeleton', 2, '4087833'),
    'Anakin Padme 4 Panel': MemeTemplate('Anakin Padme 4 Panel', 3, '322841258'),
    'Woman Yelling At Cat': MemeTemplate('Woman Yelling At Cat', 2, '188390779'),
    'Buff Doge vs. Cheems': MemeTemplate('Buff Doge vs. Cheems', 4, '247375501'),
    "I Bet He's Thinking About Other Women": MemeTemplate("I Bet He's Thinking About Other Women", 2, '110163934'),
    'Mocking Spongebob': MemeTemplate('Mocking Spongebob', 2, '102156234'),
    'Trade Offer': MemeTemplate('Trade Offer', 3, '309868304'),
    'Tuxedo Winnie The Pooh': MemeTemplate('Tuxedo Winnie The Pooh', 2, '178591752'),
    'One Does Not Simply' : MemeTemplate('One Does Not Simply', 2, '61579'),
    'Monkey Puppet': MemeTemplate('Monkey Puppet', 2, '148909805'),
    'Bernie Sanders Once Again Asking': MemeTemplate('Bernie Sanders Once Again Asking', 2, '224015000'),
    'Success Kid': MemeTemplate('Success Kid', 2, '61544'),
    "Y'all Got Any More Of That" : MemeTemplate("Y'all Got Any More Of That", 2, '124055727'),
    'Ancient Aliens': MemeTemplate('Ancient Aliens', 2, '101470'),
    "This Is Where I'd Put My Trophy If I Had One" : MemeTemplate("This Is Where I'd Put My Trophy If I Had One", 2, '3218037'),
    'Hide the Pain Harold': MemeTemplate('Hide the Pain Harold', 2, '27813981'),
    'Oprah You Get A': MemeTemplate('Oprah You Get A', 2, '28251713'),
    'This Is Fine': MemeTemplate('This Is Fine', 2, '55311130'),
    'Trump Bill Signing': MemeTemplate('Trump Bill Signing', 2, '91545132'),
    'You Guys are Getting Paid': MemeTemplate('You Guys are Getting Paid', 2, '177682295'),
    'Megamind peeking': MemeTemplate('Megamind peeking', 2, '370867422'),
    'Blank Nut Button': MemeTemplate('Blank Nut Button', 2, '119139145'),
    "They don't know" : MemeTemplate("They don't know", 2, '284929871'),
    'Squidward window' : MemeTemplate('Squidward window', 2, '67452763'),
    'Roll Safe Think About It' : MemeTemplate('Roll Safe Think About It', 2, '89370399'),
    'A train hitting a school bus': MemeTemplate('A train hitting a school bus', 2, '247113703'),
    'where monkey' : MemeTemplate('where monkey', 2, '316466202'),
    '0 days without (Lenny, Simpsons)' : MemeTemplate('0 days without (Lenny, Simpsons)', 2, '427308417'),
    'Laughing Leo': MemeTemplate('Laughing Leo', 2, '259237855'),
    'Whisper and Goosebumps': MemeTemplate('Whisper and Goosebumps', 2, '101956210'),
    'Sleeping Shaq': MemeTemplate('Sleeping Shaq', 2, '99683372'),
    'Evil Kermit' : MemeTemplate('Evil Kermit', 2, '84341851'),
    'AJ Styles & Undertaker' : MemeTemplate('AJ Styles & Undertaker', 2, '234202281'),
    'Grant Gustin over grave': MemeTemplate('Grant Gustin over grave', 2, '221578498'),
    'Types of Headaches meme': MemeTemplate('Types of Headaches meme', 2, '119215120'),
    'Domino Effect': MemeTemplate('Domino Effect', 2, '162372564'),
    'Pawn Stars Best I Can Do': MemeTemplate('Pawn Stars Best I Can Do', 2, '77045868'),
    'Leonardo Dicaprio Cheers': MemeTemplate('Leonardo Dicaprio Cheers', 2, '5496396'),
    'The Rock Driving': MemeTemplate('The Rock Driving', 2, '21735'),
    'All My Homies Hate': MemeTemplate('All My Homies Hate', 2, '216523697'),
    'Two guys on a bus': MemeTemplate('Two guys on a bus', 2, '354700819'),
    'Anime Girl Hiding from Terminator': MemeTemplate('Anime Girl Hiding from Terminator', 2, '224514655'),
    'Disappointed Black Guy': MemeTemplate('Disappointed Black Guy', 2, '50421420'),
    'Grandma Finds The Internet' : MemeTemplate('Grandma Finds The Internet', 2, '61556'),
    'Futurama Fry': MemeTemplate('Futurama Fry', 2, '61520'),
    'The Scroll Of Truth': MemeTemplate('The Scroll Of Truth', 2, '123999232'),
    'Third World Skeptical Kid': MemeTemplate('Third World Skeptical Kid', 2, '101288'),
    "whe i'm in a competition and my opponent is" : MemeTemplate("whe i'm in a competition and my opponent is", 2, '360597639'),
    'Star Wars Yoda': MemeTemplate('Star Wars Yoda', 2, '14371066'),
    'Look At Me' : MemeTemplate('Look At Me', 2, '29617627'),
    'Drake Blank': MemeTemplate('Drake Blank', 2, '91998305'),
    'spiderman pointing at spiderman' : MemeTemplate('spiderman pointing at spiderman', 2, '110133729'),
    'Friendship ended': MemeTemplate('Friendship ended', 2, '137501417'),
    'Spongebob Ight Imma Head Out' : MemeTemplate('Spongebob Ight Imma Head Out', 2, '196652226'),
    'Megamind no bitches' : MemeTemplate('Megamind no bitches', 2, '371619279'),
    'George Bush 9/11': MemeTemplate('George Bush 9/11', 2, '208915813'),
    "c'mon do something": MemeTemplate("c'mon do something", 2, '20007896'),
    'Goose Chase': MemeTemplate('Goose Chase', 2, '398221598'),
    'Charlie Conspiracy (Always Sunny in Philidelphia)': MemeTemplate('Charlie Conspiracy (Always Sunny in Philidelphia)', 2, '92084495'),
    'The Most Interesting Man In The World': MemeTemplate('The Most Interesting Man In The World', 2, '61532'),
}
        
        self.output_parser = PydanticOutputParser(pydantic_object=MemeResponse)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an elite meme lord with a PhD in Internet Humor and Dank Memes. Your job is to create absolutely hilarious meme captions that will make people laugh out loud. Think Reddit's front page meets Twitter's viral tweets meets TikTok humor.
            make memes that are relatable and funny to a wide audience. Your goal is to create memes that will go viral and be shared across social media platforms.
            make sure it is always extremely funny and engaging. Your captions should be witty, clever, and relevant to the meme template you choose. 
            Available templates and their text panel counts:
            {template_info}

            Your mission:
            1. Choose the PERFECT meme template that will maximize the humor potential of the input text
            2. Create captions that are:
               - Extremely witty and clever
               - Use modern internet slang and meme language when appropriate
               - Include plot twists, irony, or unexpected humor
               - Reference popular culture and current trends
               - Are slightly exaggerated for comedic effect
               - Make use of perfect comedic timing
            3. Make sure the number of captions matches the template's box count
            4. Each caption should build on the previous one for maximum humor impact
            5. Don't just restate the input - transform it into meme gold!

            Format the output as a JSON with template_name and text_array fields.
            """),
            ("human", "{input_text}")
        ])

    def get_template_info(self):
        return "\n".join([f"- {name}: {template.box_count} panels" 
                         for name, template in self.templates.items()])

    def generate_meme_text(self, input_text: str) -> MemeResponse:
        chain = self.prompt | self.llm | self.output_parser
        
        result = chain.invoke({
            "template_info": self.get_template_info(),
            "input_text": input_text
        })
        
        if result.template_name not in self.templates:
            raise ValueError(f"Invalid template name: {result.template_name}")
            
        expected_length = self.templates[result.template_name].box_count
        if len(result.text_array) != expected_length:
            if len(result.text_array) < expected_length:
                result.text_array.extend([""] * (expected_length - len(result.text_array)))
            else:
                result.text_array = result.text_array[:expected_length]
                
        return result

    def create_meme_image(self, template_name: str, text_array: List[str]) -> dict:
        """
        Create a meme using the Imgflip API with form-encoded parameters
        """
        template = self.templates[template_name]
        url = 'https://api.imgflip.com/caption_image'
        
        # Create the base form data
        data = {
            'template_id': template.template_id,
            'username': self.imgflip_username,
            'password': self.imgflip_password,
        }
        
        # Add text boxes with proper form encoding
        for i, text in enumerate(text_array):
            data[f'boxes[{i}][text]'] = text
            data[f'boxes[{i}][color]'] = "#ffffff"
            data[f'boxes[{i}][outline_color]'] = "#000000"
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            
            if result['success']:
                return result['data']
            else:
                raise Exception(f"Imgflip API error: {result['error_message']}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create meme: {str(e)}")

    def generate_complete_meme(self, input_text: str) -> dict:
        """
        Complete pipeline to generate a meme from input text:
        1. Generate the meme text using LangChain
        2. Create the meme image using Imgflip API
        Returns the URL of the generated meme
        """
        # Generate meme text
        meme_response = self.generate_meme_text(input_text)
        
        # Create the meme image
        meme_data = self.create_meme_image(
            meme_response.template_name,
            meme_response.text_array
        )
        
        return {
            'template_name': meme_response.template_name,
            'captions': meme_response.text_array,
            'url': meme_data['url'],
            'page_url': meme_data['page_url']
        }

# Example usage
if __name__ == "__main__":
    
    generator = MemeGenerator(
        openai_api_key="",
        imgflip_username="",
        imgflip_password=""
    )
    
    input_text = """"i need a room full of mirrors so i can surround myself with winners"""
    
    try:
        result = generator.generate_complete_meme(input_text)
        print(f"Generated meme:")
        print(f"Template: {result['template_name']}")
        print(f"Captions: {result['captions']}")
        print(f"Meme URL: {result['url']}")
        print(f"Page URL: {result['page_url']}")
    except Exception as e:
        print(f"Error generating meme: {str(e)}")