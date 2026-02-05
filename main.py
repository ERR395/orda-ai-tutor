import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

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
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = available_models[0] if available_models else "models/gemini-1.5-flash"
        model = genai.GenerativeModel(target_model)

        # Егер бұл "Кодты тексер" (Check Code) батырмасы болса
        if "ТЕКСЕРУ_РЕЖИМІ" in msg.message:
            prompt = (
                f"Сен Python (және {msg.subject}) интерпретаторысың. "
                f"Мына кодты тексер: \n{msg.current_code}\n"
                "ЕРЕЖЕ:"
                "1. Егер код ДҰРЫС болса: Тек қана нәтижесін (output) шығар. Ешқандай түсіндірме жазба."
                "2. Егер код ҚАТЕ болса: Алдымен Python қатесін (мысалы, NameError...) ағылшынша жаз, "
                "содан кейін '|||' белгісін қой, содан кейін қазақша қысқаша түсіндір (неге қате екенін)."
            )
            response = model.generate_content(prompt)
            return {"reply": response.text}

        # Егер жай сөйлесу болса
        else:
            instruction = f"Сен Orda колледжінің мұғалімісің. Оқушы: {msg.username}. Пән: {msg.subject}. Қысқаша жауап бер."
            full_prompt = f"{instruction}\nСұрақ: {msg.message}"
            if msg.current_code:
                full_prompt += f"\nКонтекст (код): {msg.current_code}"
            
            response = model.generate_content(full_prompt)
            return {"reply": response.text}

    except Exception as e:
        return {"reply": f"Сервер қатесі: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
