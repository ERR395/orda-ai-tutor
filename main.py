import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілтін алу
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# ПРОБЛЕМАНЫ ШЕШЕТІН ЖОЛ: 
# Модель атауын нақты v1 нұсқасы үшін gemini-1.5-flash деп жазамыз
model = genai.GenerativeModel('gemini-1.5-flash')

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

@app.get("/")
def home():
    return {"status": "Server is working"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # Сұранысты жіберу
        response = model.generate_content(f"Сен {msg.subject} мұғалімісің. Оқушы аты: {msg.username}. Жауапты қазақша бер: {msg.message}")
        return {"reply": response.text}
    except Exception as e:
        # Егер 1.5 нұсқасы әлі де істемесе, автоматты түрде gemini-pro-ға ауысу
        try:
            old_model = genai.GenerativeModel('gemini-pro')
            response = old_model.generate_content(f"Сен {msg.subject} мұғалімісің. Сұрақ: {msg.message}")
            return {"reply": response.text}
        except Exception as e2:
            return {"reply": f"Қате: {str(e2)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
