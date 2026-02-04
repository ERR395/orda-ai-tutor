import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілтін баптау
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# МОДЕЛЬДІ АВТОМАТТЫ ТАҢДАУ ФУНКЦИЯСЫ
def get_working_model():
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Бірінші flash-ті тексеру, болмаса тізімдегі біріншісін алу
    for model_name in available_models:
        if 'gemini-1.5-flash' in model_name:
            return genai.GenerativeModel(model_name)
    return genai.GenerativeModel(available_models[0])

# Жұмыс істеп тұрған модельді бірден іске қосамыз
chat_model = get_working_model()

class ChatMessage(BaseModel):
    username: str
    message: str
    subject: str

@app.get("/")
def home():
    return {"status": "Active", "model": chat_model.model_name}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        prompt = f"Сен {msg.subject} мұғалімісің. Оқушы аты: {msg.username}. Қазақша жауап бер: {msg.message}"
        response = chat_model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Жүйелік қате: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

