import google.generativeai as genai
import os
from dotenv import load_dotenv
import PIL.Image
import textwrap

from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
# model = genai.GenerativeModel('gemini-pro')
model = genai.GenerativeModel('gemini-pro-vision')
# chat = model.start_chat(history=[])

# respone= chat.send_message(["write an essay on gemini"], stream=True)

# for chunk in respone:
#     print(chunk.text, end="")
    
img = PIL.Image.open('matrix_profile.jpg')   
response = model.generate_content(["Describe this image.", img], stream=True)
response.resolve() 
for chunk in response:
    print(chunk.text, end="")