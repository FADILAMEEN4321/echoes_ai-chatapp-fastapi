from fastapi import FastAPI, WebSocket
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai



load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])


app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        message = await websocket.receive()

        if isinstance(message, bytes):
            data = json.loads(message.decode())
        else:
            if message == "<FIN>":
                await websocket.close()
                break

            respone = chat.send_message([message["text"]], stream=True)
            print(respone)

        for chunk in respone:
            await websocket.send_text(chunk.text)
        await websocket.send_text("<FIN>")        

@app.get('/fetch-messages', response_model=list[dict])
async def fetch_messages():
    return [{'role': message.role, "text": message.parts[0].text} for message in chat.history]

@app.get('/')
def hello():
    return {'hello'}



# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="127.0.0.1", port=8000)


