import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілті
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

class ChatMessage(BaseModel):
    username: str
    message: str
    subject: str
    current_code: str = "" 

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # Модельді автоматты таңдау
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = available_models[0] if available_models else "models/gemini-1.5-flash"
        
        model = genai.GenerativeModel(target_model)
        
        # --- МАҢЫЗДЫ ӨЗГЕРІС: ҚЫСҚА ЖАУАП СҰРАУ ---
        instruction = (
            f"Сен Orda колледжінің {msg.subject} мұғалімісің. Оқушы: {msg.username}. "
            "Жауабың өте қысқа, нақты және түсінікті болсын (максимум 2-3 сөйлем). "
            "Ұзын лекция оқыма. Тек сұраққа жауап бер."
        )
        
        context = ""
        if msg.current_code and len(msg.current_code) > 0:
            context = f"\n\n[Оқушының коды]:\n```\n{msg.current_code}\n```\n"
        
        full_prompt = f"{instruction}{context}\nОқушы: {msg.message}"
        
        response = model.generate_content(full_prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Қате: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
