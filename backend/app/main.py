from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db

# Do not instantiate heavy resources at import time (models, DB creation).
# Initialize them on application startup instead to avoid import-time failures.

app = FastAPI(title="CNN Image Classification API")

# Enable CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "model": "MobileNetV2 (CNN)"}

@app.post("/predict")
async def predict(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    contents = await file.read()
    clf = getattr(app.state, "classifier", None)
    if clf is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    label, confidence = clf.predict(contents)

    # Save prediction history to PostgreSQL
    from .models import PredictionLog

    log = PredictionLog(
        filename=file.filename,
        predicted_label=label,
        confidence=confidence
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "id": log.id,
        "filename": log.filename,
        "predicted_label": log.predicted_label,
        "confidence": f"{log.confidence}%",
        "created_at": log.created_at
    }

@app.get("/history")
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    from .models import PredictionLog
    logs = db.query(PredictionLog).order_by(PredictionLog.id.desc()).limit(limit).all()
    return logs


@app.on_event("startup")
def on_startup():
    # Create DB tables and load ML model on startup (avoid import-time side effects)
    Base.metadata.create_all(bind=engine)
    try:
        from .ml_model import CNNClassifier
        app.state.classifier = CNNClassifier()
    except Exception:
        # If model fails to load, ensure app still starts; endpoints will return 503.
        app.state.classifier = None