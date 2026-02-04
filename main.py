import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import google.generativeai as genai

# Деректер қорын бір файлға жинау
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

# AI Баптау
genai.configure(api_key="AIzaSyDvvGGXG_43z6dXiagkyJ7Vx2pQPWg5sfI")
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# CORS баптау (Бұл өте маңызды!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class ChatMessage(BaseModel):
    username: str
    message: str
    subject: str

@app.get("/")
def home():
    return {"status": "Online", "message": "Orda AI Server is running!"}

@app.get("/study/{username}")
def study(username: str, subject: str = "python"):
    prompt = f"Сен IT мұғалімісің. Қазақша жауап бер. {subject} тілі туралы қысқаша мәлімет беріп, бір тапсырма бер."
    response = model.generate_content(prompt)
    return {"message": response.text}

@app.post("/chat")
def chat(msg: ChatMessage):
    response = model.generate_content(msg.message)
    return {"reply": response.text}
