import hmac
import hashlib
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import json

import models
from dependencies import get_db
router = APIRouter(
    prefix="/webhooks/github",
    tags=["Webhooks"]
)
@router.post("/{project_id}", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(project_id: UUID, request: Request, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature header"
        )
    
    body_bytes = await request.body()
    
    if not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature format"
        )
    
    signature_hash = signature_header[7:]

    secret_bytes = project.webhook_secret.encode("utf-8")
    computed_hash = hmac.new(
        secret_bytes, 
        body_bytes, 
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, signature_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signature mismatch"
        )
    
    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
        
    print(f"Webhook received for repository: {payload.get('repository', {}).get('full_name')}")

    return {"message": "Signature verified successfully"}