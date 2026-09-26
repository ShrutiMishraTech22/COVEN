"""Pydantic schemas — mirror docs/API_CONTRACT.md exactly."""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    laptop = "laptop"; phone = "phone"; network = "network"
    email = "email"; usb = "usb"; cctv = "cctv"; other = "other"


class EvidenceType(str, Enum):
    file = "file"; log = "log"; email = "email"
    image = "image"; video = "video"; document = "document"


class IntegrityStatus(str, Enum):
    verified = "verified"; unverified = "unverified"; modified = "modified"


class Case(BaseModel):
    case_id: str
    name: str
    investigator: str
    description: Optional[str] = None
    created_at: datetime


class CaseCreate(BaseModel):
    name: str
    investigator: str
    description: Optional[str] = None


class Transformation(BaseModel):
    action: str
    timestamp: datetime


class Evidence(BaseModel):
    evidence_id: str
    case_id: str
    source: SourceType
    type: EvidenceType
    original_filename: str
    timestamp: datetime
    hash: str
    metadata: dict[str, Any] = {}
    acquisition_info: dict[str, Any] = {}
    transformation_history: list[Transformation] = []
    integrity_status: IntegrityStatus = IntegrityStatus.unverified


class Event(BaseModel):
    event_id: str
    evidence_id: str
    case_id: str
    timestamp: datetime
    actor: Optional[str] = None
    device: Optional[str] = None
    action: str
    object: Optional[str] = None
    location: Optional[str] = None
    source: SourceType
    confidence: float = 0.0


class ReliabilityBreakdown(BaseModel):
    model_confidence: float
    evidence_integrity: float
    source_reliability: float
    cross_source_agreement: float
    reproducibility: float


class Finding(BaseModel):
    finding_id: str
    case_id: str
    model: str
    model_version: str
    confidence: float
    supporting_evidence: list[str] = []
    contradicting_evidence: list[str] = []
    provenance: dict[str, Any] = {}
    reliability: float
    reliability_breakdown: ReliabilityBreakdown
    explanation: str


class ContradictionSeverity(str, Enum):
    high = "high"; medium = "medium"; low = "low"


class ContradictionType(str, Enum):
    location = "location"; temporal = "temporal"; identity = "identity"
    metadata = "metadata"; source = "source"


class Contradiction(BaseModel):
    contradiction_id: str
    case_id: str
    severity: ContradictionSeverity
    type: ContradictionType
    evidence_ids: list[str]
    description: str
    possible_explanations: list[str] = []


class Hypothesis(BaseModel):
    hypothesis_id: str
    case_id: str
    description: str
    confidence: float
    reliability: float
    supporting_evidence: list[str] = []
    contradicting_evidence: list[str] = []
    missing_evidence: list[str] = []
    explanation: str


class GraphNode(BaseModel):
    id: str
    type: str
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class EvidenceGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
