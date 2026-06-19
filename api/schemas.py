from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ProjectBase(BaseModel):
    name: str
    repository_url: str
    discord_webhook_url: str | None = None

class ProjectCreate(ProjectBase):
    webhook_secret: str

class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime

    model_config = {
    "from_attributes": True
    }

class FindingBase(BaseModel):
    scanner: str
    severity: str
    title: str
    description: str
    file_path: str
    line_number: int | None = None

class FindingResponse(FindingBase):
    id: UUID
    scan_id: UUID
    created_at: datetime

    model_config = {
    "from_attributes": True
    }

class ScanBase(BaseModel):
    commit_sha: str
    branch: str
    triggered_by: str | None = None

class ScanResponse(ScanBase):
    id: UUID
    project_id: UUID
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    findings: list[FindingResponse] = []

    model_config = {
    "from_attributes": True
    }