import os
import re
import json
import uuid
import requests
import psycopg2
import datetime  
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Any, Dict, Optional

DEEPSEEK_API_KEY = "sk-741065ab176045eca6c6c5d6f4428ec5"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-r1:7b"

DB_CONFIG = {
    "dbname": "dtp_analytics",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": 5432
}

DB_SCHEMA = """
Таблица: accidents (происшествия ДТП)
- id (INTEGER) - уникальный номер
- accident_date (DATE) - дата происшествия
- address (TEXT) - адрес
- severity (TEXT) - тяжесть (fatal, injury, damage)
- participants_count (INTEGER) - количество участников

Таблица: weather (погода)
- id (INTEGER)
- accident_id (INTEGER) - внешний ключ к accidents
- condition (TEXT) - погодные условия (rain, snow, clear)
"""

SYSTEM_PROMPT = f"""
Ты — SQL-эксперт для базы данных ГИБДД. Вот схема БД:
{DB_SCHEMA}

Правила:
1. Превращай вопросы пользователя в SQL-запросы (PostgreSQL).
2. Отвечай ТОЛЬКО SQL запросом, без лишних объяснений.
3. Всегда используй русские названия полей в WHERE, если пользователь просит "центр", "зимой" и т.д.
4. Для агрегатов (среднее, сумма) используй соответствующие функции.
5. Для указания периода используй корректный синтаксис PostgreSQL: например, `accident_date >= CURRENT_DATE - INTERVAL '3 days'`.
6. Не ставь лишние запятые после SELECT *.
7. Если вопрос не связан с данными или не удаётся построить запрос, напиши "Не могу построить запрос".
"""

app = FastAPI(title="DTP Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {} 

class QueryRequest(BaseModel):
    user_question: str
    mode: str = "cloud"
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    generated_sql: Optional[str] = None
    session_id: str

def extract_sql_from_response(response_text: str) -> str:
    cleaned = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    sql_match = re.search(r'(SELECT\s+.*?)(;|$)', cleaned, re.IGNORECASE | re.DOTALL)
    if sql_match:
        sql = sql_match.group(1).strip()
        if ';' in sql:
            sql = sql.split(';')[0]
        return sql
    return cleaned.strip()

def fix_sql_syntax(sql: str) -> str:
    sql = re.sub(r'SELECT\s+\*,\s+FROM', 'SELECT * FROM', sql, flags=re.IGNORECASE)
    sql = re.sub(r"CURRENT_DATE\s*-\s*(\d+)\s*days", r"CURRENT_DATE - INTERVAL '\1 days'", sql, flags=re.IGNORECASE)
    sql = re.sub(r"CURRENT_DATE\s*-\s*(\d+)\s*day", r"CURRENT_DATE - INTERVAL '\1 day'", sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bAND\s+id\s+UNIQUE\b', '', sql, flags=re.IGNORECASE)
    sql = sql.rstrip(';')
    return sql

def ask_ollama_with_history(messages: List[dict]) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 500}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except Exception as e:
        print(f"[DEBUG] Ollama ошибка: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к Ollama: {str(e)}")

def ask_deepseek_api_with_history(messages: List[dict]) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 500
    }
    try:
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(500, f"DeepSeek API error: {str(e)}")

def ask_ollama_for_analysis(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 1000}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except Exception as e:
        return f"Ошибка анализа: {e}"

def ask_deepseek_api_for_analysis(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    try:
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка анализа: {e}"

def convert_dates(obj):
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(v) for v in obj]
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:
        return obj

def analyze_data_with_ai(user_question: str, sql: str, data: list, columns: list, mode: str) -> str:
    sample_data = data[:5] if len(data) > 5 else data
    sample_data_converted = convert_dates(sample_data)
    data_preview = json.dumps(sample_data_converted, ensure_ascii=False, indent=2)
    total_rows = len(data)

    analysis_prompt = f"""
Пользователь спросил: "{user_question}"
Был выполнен SQL: {sql}
Получено {total_rows} записей.
Пример данных (первые {len(sample_data)}):
{data_preview}

Задача:
1. Проанализируй эти данные.
2. Сделай выводы (тенденции, аномалии, важные показатели).
3. Дай рекомендации на основе анализа (если уместно).
4. Если данных недостаточно для анализа, попроси пользователя уточнить запрос или предоставить больше данных.

Отвечай на русском языке, дружелюбно, структурированно.
"""
    if mode == "local":
        return ask_ollama_for_analysis(analysis_prompt)
    else:
        return ask_deepseek_api_for_analysis(analysis_prompt)

def execute_sql(sql_query: str):
    print(f"[DEBUG] Выполняется SQL: {sql_query}")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(sql_query)
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
            cur.close()
            conn.close()
            print(f"[DEBUG] SQL выполнен, получено {len(data)} строк")
            return {"data": data, "columns": columns}
        else:
            conn.commit()
            cur.close()
            conn.close()
            print("[DEBUG] SQL выполнен (без возврата данных)")
            return {"data": [], "columns": [], "message": "Запрос выполнен успешно"}
    except Exception as e:
        print(f"[DEBUG] Ошибка выполнения SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка выполнения SQL: {str(e)}")

@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    print(f"\n[DEBUG] ===== Новый запрос =====")
    print(f"[DEBUG] Вопрос пользователя: {request.user_question}")
    print(f"[DEBUG] Режим: {request.mode}")
    print(f"[DEBUG] Session ID: {request.session_id}")

    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        sessions[session_id] = [] 
    elif session_id not in sessions:
        sessions[session_id] = [] 

    history = sessions[session_id]

    messages_for_sql = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_for_sql.extend(history)  
    messages_for_sql.append({"role": "user", "content": request.user_question})

    try:
        if request.mode == "local":
            ai_response = ask_ollama_with_history(messages_for_sql)
        else:
            ai_response = ask_deepseek_api_with_history(messages_for_sql)
    except Exception as e:
        print(f"[DEBUG] Исключение при вызове AI: {e}")
        return QueryResponse(
            success=False,
            error=f"Ошибка AI: {str(e)}",
            generated_sql=None,
            session_id=session_id
        )

    history.append({"role": "user", "content": request.user_question})
    history.append({"role": "assistant", "content": ai_response})
    sessions[session_id] = history

    sql_query = extract_sql_from_response(ai_response)
    sql_query = fix_sql_syntax(sql_query)
    print(f"[DEBUG] Извлечённый SQL после исправления: {sql_query}")

    if sql_query.startswith("Не могу построить запрос") or not sql_query:
        return QueryResponse(
            success=False,
            error="Модель не смогла сгенерировать SQL",
            generated_sql=sql_query,
            session_id=session_id
        )

    try:
        result = execute_sql(sql_query)
        if result["data"]:
            message = f"Найдено {len(result['data'])} записей."
            analysis = analyze_data_with_ai(
                request.user_question,
                sql_query,
                result["data"],
                result["columns"],
                request.mode
            )
            full_message = f"{message}\n\nАнализ:\n{analysis}"
        else:
            full_message = result.get("message", "Запрос выполнен, данные не возвращены.")
        return QueryResponse(
            success=True,
            data=result["data"],
            columns=result["columns"],
            message=full_message,
            generated_sql=sql_query,
            session_id=session_id
        )
    except HTTPException as e:
        print(f"[DEBUG] HTTPException при выполнении SQL: {e.detail}")
        return QueryResponse(
            success=False,
            error=e.detail,
            generated_sql=sql_query,
            session_id=session_id
        )

@app.get("/health")
def health():
    return {"status": "ok"}