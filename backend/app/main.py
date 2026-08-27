from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.questionnaire_routes import router as q_router

app = FastAPI(title="Prakriti API")


# CORS CONFIG (required for frontend connection)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:9000",
    "http://127.0.0.1:9000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)
app.include_router(q_router)

@app.get("/")
def root():
    return {"message": "API running"}