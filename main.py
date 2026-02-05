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

# Мұнда 'current_code' деген жаңа жол қостық
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
        
        # Нұсқаулықты құрастыру
        instruction = f"Сен Orda колледжінің {msg.subject} мұғалімісің. Оқушы: {msg.username}. Қазақша жауап бер."
        
        # Егер оқушының редакторында код болса, оны AI-ға көрсетеміз
        context = ""
        if msg.current_code and len(msg.current_code) > 0:
            context = f"\n\n[Оқушының экранындағы қазіргі код]:\n```\n{msg.current_code}\n```\nОсы кодқа қатысты сұрақ болуы мүмкін.\n"
        
        full_prompt = f"{instruction}{context}\nОқушының сұрағы: {msg.message}"
        
        response = model.generate_content(full_prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Қате: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

