import pytest
from sqlalchemy.orm import Session
import models

def test_create_project(db_session: Session):
    project = models.Project(
        name="Test",
        repository_url="https://github.com/test/repo.git",
        webhook_secret="some_secret",
        github_token="some_token"
    )
    
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    queried_project = db_session.query(models.Project).first()
    assert queried_project is not None
    assert queried_project.name == "Test"
    assert queried_project.github_token == "some_token"
    

def test_project_cascade_delete(db_session: Session):
    project = models.Project(
        name="Test",
        repository_url="https://github.com/test/repo.git",
        webhook_secret="some_secret",
        github_token="some_token"
    )

    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    
    scan = models.Scan(
        project_id=project.id, 
        commit_sha="4e8f192b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f", 
        branch="main", 
        status="pending"
    )
    
    db_session.add(scan)
    db_session.commit()
    db_session.refresh(scan)
    
    finding = models.Finding(
        scan_id=scan.id, 
        scanner="gitleaks", 
        severity="critical", 
        title="Hardcoded AWS Credentials",
        description="Found a hardcoded private key in config.py.",
        file_path="api/config.py"
    )
    
    db_session.add(finding)
    db_session.commit()

    assert db_session.query(models.Project).count() == 1
    assert db_session.query(models.Scan).count() == 1
    assert db_session.query(models.Finding).count() == 1

    db_session.delete(project)
    db_session.commit()

    assert db_session.query(models.Project).filter_by(id=project.id).first() is None
    assert db_session.query(models.Scan).filter_by(id=scan.id).first() is None
    assert db_session.query(models.Finding).filter_by(id=finding.id).first() is None