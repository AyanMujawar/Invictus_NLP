from pydantic import BaseModel, Field
from typing import Literal, List, Union, Dict

class Finding(BaseModel):
    violating_statement: str
    guideline_clause: str
    category: str
    severity: Literal["Low", "Medium", "High", "Critical"]
    explanation: str
    confidence: float = Field(ge=0, le=1)
    suggested_correction: str

class AuditReport(BaseModel):
    document_name: str
    findings: List[Finding]
    readiness_score: float
    summary: Union[str, Dict]
