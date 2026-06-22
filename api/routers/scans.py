from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import models
import schemas
from dependencies import get_db

router = APIRouter(
    prefix="/scans",
    tags=["Scans"]
)

@router.get("/{scan_id}", response_model=schemas.ScanResponse)
def get_scan(scan_id: UUID, db: Session = Depends(get_db)):
    # Query the scan by UUID
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan
