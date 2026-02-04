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

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # Қолжетімді модельді автоматты табу
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Тізімдегі бірінші модельді аламыз (flash немесе pro)
        target_model = available_models[0] if available_models else "models/gemini-pro"
        
        model = genai.GenerativeModel(target_model)
        
        instruction = f"Сен Orda колледжінің {msg.subject} мұғалімісің. Оқушы: {msg.username}. Қазақша, өте қысқа жауап бер."
        response = model.generate_content(f"{instruction}\nСұрақ: {msg.message}")
        
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Жүйелік қате: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
