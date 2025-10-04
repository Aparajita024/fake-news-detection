from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import analysis, feedback
from .database.database import client

app = FastAPI(
    title="Advanced Fake News Detection API",
    description="Analyzes content and cross-references with external sources.",
    version="2.0.0"
)

# --- Event Handlers for DB Connection ---
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    print("MongoDB connection closed.")

# --- CORS Middleware ---
# Allows your React/Vue/Angular frontend to communicate with this backend
origins = [
    "http://localhost:3000", # Example for React
    "http://localhost:5173", # Example for Vite/Vue
    "http://localhost:4200", # Example for Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
# Include the routes from the different modules
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Fake News Detection API. Visit /docs for documentation."}