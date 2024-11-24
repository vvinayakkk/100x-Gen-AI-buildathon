from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
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
        
        # Import templates from meme_templates.py
        from .meme_templates import templates
        self.templates = templates
        
        self.output_parser = PydanticOutputParser(pydantic_object=MemeResponse)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an elite meme lord with a PhD in Internet Humor and Dank Memes. Your job is to create absolutely hilarious meme captions that will make people laugh out loud. Think Reddit's front page meets Twitter's viral tweets meets TikTok humor.

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
        template = self.templates[template_name]
        url = 'https://api.imgflip.com/caption_image'
        
        data = {
            'template_id': template.template_id,
            'username': self.imgflip_username,
            'password': self.imgflip_password,
        }
        
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
        meme_response = self.generate_meme_text(input_text)
        
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
