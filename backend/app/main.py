from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import analysis, feedback
from .database.database import client
from .core.config import settings 
from .routes import verification

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Analyzes content and cross-references with external sources.",
    version="2.0.0"
)

# --- Event Handlers for DB Connection ---
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    print("MongoDB connection closed.")

# --- CORS Middleware ---
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["Analysis"])
app.include_router(feedback.router, prefix=settings.API_V1_STR, tags=["Feedback"])
app.include_router(verification.router, prefix=settings.API_V1_STR, tags=["Verification"])

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}. Visit /docs for documentation."}