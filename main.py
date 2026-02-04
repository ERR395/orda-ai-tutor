import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілтін орнату
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# МОДЕЛЬ АТАУЫН ОСЫЛАЙ ЖАЗУ КЕРЕК
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# Басқа сайттардан қосылуға рұқсат беру
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

# БҰЛ ЖЕР СЕРВЕРДІҢ ЖҰМЫСЫН ТЕКСЕРУ ҮШІН ҚАЖЕТ
@app.get("/")
def home():
    return {"status": "Server is running!", "model": "Gemini-1.5-Flash"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        prompt = f"Сен {msg.subject} пәнінің мұғалімісің. Оқушының аты {msg.username}. Жауапты қазақша бер. Сұрақ: {msg.message}"
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Қате орын алды: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
