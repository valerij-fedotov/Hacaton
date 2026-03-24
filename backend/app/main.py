from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import fields, forms, tables, records

app = FastAPI(title="DTP Form Constructor API", version="2.0.0", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://91.194.3.53:5173"
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fields.router)
app.include_router(forms.router)
app.include_router(tables.router)
app.include_router(records.router)

@app.get("/")
async def root():
    return {"message": "DTP Form Constructor API"}