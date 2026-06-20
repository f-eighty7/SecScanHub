from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from uuid import UUID

# Automatically create the database tables if the dont exist yet.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SecScanHub Gateway API",
    description="Automated security scanning receiver and dashboard API",
    version="0.1.0-beta"
)

### Registering a project
@app.post("/projects", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Create the database record
    db_project = models.Project(**project_in.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)  # This loads the database-generated ID and timestamp
    return db_project

### Listing Projects
@app.get("/projects", response_model=list[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()
    return projects

### Getting a Single Project:
@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

### List Scans for a Project
@app.get("/projects/{project_id}/scans", response_model=list[schemas.ScanResponse])
def list_project_scans(project_id: UUID, db: Session = Depends(get_db)):
    # 1. Check if the project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    # 2. Get all scans belonging to this project
    scans = db.query(models.Scan).filter(models.Scan.project_id == project_id).all()
    return scans

### Get a Single Scan (with Findings)
@app.get("/scans/{scan_id}", response_model=schemas.ScanResponse)
def get_scan(scan_id: UUID, db: Session = Depends(get_db)):
    # Query the scan by UUID
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan