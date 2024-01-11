import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

respone= chat.send_message(["write a essay on gemini"], stream=True)

for chunk in respone:
    print(chunk.text, end="")
