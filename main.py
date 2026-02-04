from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import google.generativeai as genai
import models, database

# 1. API КІЛТ
genai.configure(api_key="AIzaSyDvvGGXG_43z6dXiagkyJ7Vx2pQPWg5sfI")
model = genai.GenerativeModel('gemini-flash-latest')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

class CodeSubmission(BaseModel):
    username: str
    code: str
    subject: str

class ChatMessage(BaseModel):
    username: str
    message: str
    subject: str

@app.get("/")
def home():
    return {"message": "AI Tutor Server Ready (Python, HTML, JS, C++)"}

# 1. САБАҚ БАСТАУ (Жаңа пәндер қосылды)
@app.get("/study/{username}")
def study(username: str, subject: str = "python", db: Session = Depends(database.get_db)):
    user = db.query(models.Student).filter(models.Student.username == username).first()
    if not user:
        user = models.Student(username=username, current_topic="Intro")
        db.add(user)
        db.commit()

    # ПӘНДЕРГЕ АРНАЛҒАН ТАПСЫРМАЛАР
    if subject == "html":
        task_prompt = "HTML құрылымын (html, head, body) 2 сөйлеммен түсіндір де, сайттың тақырыбын (h1) жазуды тапсыр."
    elif subject == "js": # JavaScript
        task_prompt = "JavaScript тілі сайтты 'тірілтетінін' 2 сөйлеммен айт. console.log('Solem') деп жазуды тапсыр."
    elif subject == "cpp": # C++
        task_prompt = "C++ тілінің күрделі әрі жылдам екенін айт. #include <iostream> және std::cout арқылы сәлемдесуді тапсыр."
    else: # Python (default)
        task_prompt = "Python-да print() функциясын 2 сөйлеммен түсіндір де, экранға сөз шығаруды тапсыр."

    prompt = f"""
    Сен Орда колледжінің мұғалімісің. Оқушы аты: {username}. Пән: {subject}.
    
    ТАПСЫРМА:
    {task_prompt}
    
    ТАЛАПТАР:
    1. Қазақша сөйле.
    2. Өте қысқа жаз (артық судыратып сөйлеме).
    3. Теорияны тек ең маңызды жерін айт.
    """
    
    try:
        response = model.generate_content(prompt)
        return {"message": response.text}
    except Exception as e:
        return {"message": "Сервер қатесі."}

# 2. ЧАТ (Амандаспау ережесі сақталды)
@app.post("/chat")
def chat(msg: ChatMessage):
    prompt = f"""
    Сен {msg.subject} пәнінің мұғалімісің. Оқушы аты: {msg.username}.
    Оқушының сұрағы: "{msg.message}"
    
    ҚАТАҢ ЕРЕЖЕЛЕР:
    1. ЕШҚАШАН АМАНДАСПА (Сәлем, Қайырлы күн деп жазба).
    2. Бірден сұраққа жауап бер.
    3. Жауабың ӨТЕ ҚЫСҚА БОЛСЫН (Максимум 2-3 сөйлем).
    4. Тек нақты сұраққа жауап бер.
    """
    try:
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": "Қате шықты."}

# 3. КОД ТЕКСЕРУ
@app.post("/check_code")
def check_code(submission: CodeSubmission):
    prompt = f"""
    Пән: {submission.subject}.
    Оқушы коды:
    {submission.code}
    
    Тексеру ережесі:
    1. Кодтың синтаксисі дұрыс па?
    2. Егер C++ болса, кітапханалар (iostream) бар ма?
    3. Қате болса, қысқаша түзететін жолды көрсет.
    """
    try:
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"result": "Тексеру қатесі."}