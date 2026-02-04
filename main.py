import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# API Кілтін Render-ден алу
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Модельді баптау (Ең тұрақты нұсқасы)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

# Браузермен байланыс орнату (CORS)
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
    return {"status": "Orda AI Server is active"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # AI-ға нақты нұсқаулық: Қысқа жаз және қазақша жауап бер
        instruction = (
            f"Сен 'Orda' жоғары колледжінің мұғалімісің. "
            f"Оқушының аты: {msg.username}. Пән: {msg.subject}. "
            f"Қазақ тілінде жауап бер. Жауабың өте қысқа болсын (2-3 сөйлемнен аспасын)."
        )
        
        full_prompt = f"{instruction}\nСұрақ: {msg.message}"
        
        response = model.generate_content(full_prompt)
        return {"reply": response.text}
    
    except Exception as e:
        # Қате шықса, оны пайдаланушыға түсінікті етіп көрсету
        return {"reply": f"Кешіріңіз, қате шықты. API кілтін немесе интернетті тексеріңіз. Себебі: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Render үшін портты баптау
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
