from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import models
import schemas
from dependencies import get_db

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.post("", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Create the database record
    db_project = models.Project(**project_in.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)  # This loads the database-generated ID and timestamp
    return db_project

@router.get("", response_model=list[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()
    return projects

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.get("/{project_id}/scans", response_model=list[schemas.ScanResponse])
def list_project_scans(project_id: UUID, db: Session = Depends(get_db)):
    # 1. Check if the project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    # 2. Get all scans belonging to this project
    scans = db.query(models.Scan).filter(models.Scan.project_id == project_id).all()
    return scans
