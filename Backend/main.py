from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import everyone's hard work!
from routers import patient_routes, bed_routes, emergency_routes, appointment_routes

app = FastAPI(title="Intelligent Health Hub API", version="1.0")

# 🚀 BULLETPROOF CORS SETTINGS: 
# Explicitly allow the React Vite server to connect without security blocks.
# 🚀 BULLETPROOF CORS SETTINGS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:8080",    # Add this line!
        "http://127.0.0.1:8080"     # Add this line!
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔌 Plug in Person 1's Data Retrieval routes
app.include_router(patient_routes.router)

# 🔌 Plug in Person 2's Concurrency routes
app.include_router(bed_routes.router)

# 🔌 Plug in Person 3's Algorithm routes
app.include_router(emergency_routes.router)
app.include_router(appointment_routes.router)

@app.get("/")
def health_check():
    return {"status": "SUCCESS", "message": "The combined Master Backend is alive!"}