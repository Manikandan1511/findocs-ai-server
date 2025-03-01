from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload import router as upload_router
from app.api.search import router as search_router

# ✅ Initialize FastAPI
app = FastAPI(title="AI Document Management System", version="1.0")

# ✅ Enable CORS (Allow frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to restrict domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register API Routes
app.include_router(upload_router, prefix="/api")
app.include_router(search_router, prefix="/api")

# ✅ Root Endpoint
@app.get("/")
def root():
    return {"message": "AI Document Management System is Running 🚀"}