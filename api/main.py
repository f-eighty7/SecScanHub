from fastapi import FastAPI, Response
import models
from database import engine
from routers import projects, scans, webhooks
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Automatically create the database tables if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SecScanHub Gateway API",
    description="Automated security scanning receiver and dashboard API",
    version="0.1.0-beta"
)

# Register routers
app.include_router(projects.router)
app.include_router(scans.router)
app.include_router(webhooks.router)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)