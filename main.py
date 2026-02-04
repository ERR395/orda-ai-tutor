import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# 1. API Кілтін баптау
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. Модельді нақтылау (Логтағы қатені түзету үшін 'gemini-1.5-flash-latest' қолданамыз)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

app = FastAPI()

# 3. CORS баптаулары (Браузерден қосылу үшін)
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
    return {"status": "Online", "message": "Orda AI Tutor Server is running"}

@app.get("/study/{username}")
def start_study(username: str, subject: str):
    return {
        "message": f"Сәлем, {username}! Мен сенің {subject} бойынша мұғаліміңмін. Неден бастаймыз?"
    }

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # AI-ға сұраныс жіберу
        prompt = f"Сен {msg.subject} пәнінің мұғалімісің. Оқушының аты {msg.username}. Сұрақ: {msg.message}"
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Кешіріңіз, қате шықты: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
