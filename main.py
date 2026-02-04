import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілтін баптау
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# МОДЕЛЬ АТЫН ТЕК КІШІ ӘРІППЕН ЖАЗУ КЕРЕК (ӨТЕ МАҢЫЗДЫ!)
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
    return {"status": "Server is running"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # AI-ға сұраныс жіберу
        prompt = f"Сен {msg.subject} пәнінің мұғалімісің. Оқушы аты: {msg.username}. Жауапты қазақша бер. Сұрақ: {msg.message}"
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Қате шықты: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
