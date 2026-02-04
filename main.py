import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілтін баптау
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# СЕНІҢ ҚАТЕҢДІ ТҮЗЕТЕТІН ЖОЛ: Модельді тізімнен автоматты түрде таңдау
# Егер flash-1.5 істемесе, ол автоматты түрде gemini-pro-ға ауысады
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

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
    return {"status": "Server is up and running"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # Сұранысты жіберу (Қазақша жауап беруді талап ету)
        response = model.generate_content(f"Сен {msg.subject} мұғалімісің. Оқушы аты: {msg.username}. Сұраққа қазақша жауап бер: {msg.message}")
        return {"reply": response.text}
    except Exception as e:
        # Егер тағы қате шықса, нақты себебін экранға шығарамыз
        return {"reply": f"Жүйелік қате: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
