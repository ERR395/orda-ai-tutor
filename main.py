import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілті
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# МОДЕЛЬ АТАУЫН ОСЫЛАЙ ЖАЗ (бұл ең тұрақтысы)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    username: str
    message: str
    subject: str

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        prompt = f"Сен {msg.subject} мұғалімісің. Оқушы: {msg.username}. Сұрақ: {msg.message}"
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Қате: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)


