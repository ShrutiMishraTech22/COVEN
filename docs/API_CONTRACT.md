# TrustGraph API Contract (v1)

This is the single source of truth for endpoint shapes. Both frontend and backend
build against this file. If you need to change a field, edit this file FIRST,
message your teammate, then change code. Never let backend and frontend drift.

Base URL (local dev): `http://localhost:8000/api`

---

## Core Schemas

### Evidence
```json
{
  "evidence_id": "EV-031",
  "case_id": "CASE-001",
  "source": "laptop | phone | network | email | usb | cctv | other",
  "type": "file | log | email | image | video | document",
  "original_filename": "confidential.pdf",
  "timestamp": "2026-09-10T09:51:00Z",
  "hash": "sha256:8d92...",
  "metadata": { "any": "key-value pairs, EXIF, headers, etc" },
  "acquisition_info": { "collector": "string", "method": "string" },
  "transformation_history": [ { "action": "string", "timestamp": "iso8601" } ],
  "integrity_status": "verified | unverified | modified"
}
```

### Event (normalized, produced from Evidence)
```json
{
  "event_id": "EVT-031",
  "evidence_id": "EV-031",
  "case_id": "CASE-001",
  "timestamp": "2026-09-10T09:51:00Z",
  "actor": "person or account identifier",
  "device": "device identifier",
  "action": "file_access | login | usb_connect | network_connect | email_sent | ...",
  "object": "what was acted on, e.g. filename or recipient",
  "location": "Delhi | Mumbai | IP address | null",
  "source": "same enum as Evidence.source",
  "confidence": 0.0
}
```

### Finding (an AI-generated conclusion)
```json
{
  "finding_id": "FIND-001",
  "case_id": "CASE-001",
  "model": "string",
  "model_version": "string",
  "confidence": 0.87,
  "supporting_evidence": ["EV-031", "EV-044"],
  "contradicting_evidence": ["EV-105"],
  "provenance": { "trace": "conclusion -> evidence chain" },
  "reliability": 0.78,
  "reliability_breakdown": {
    "model_confidence": 0.87,
    "evidence_integrity": 1.0,
    "source_reliability": 0.90,
    "cross_source_agreement": 0.72,
    "reproducibility": 0.95
  },
  "explanation": "human-readable reasoning"
}
```

### Contradiction
```json
{
  "contradiction_id": "CONTRA-001",
  "case_id": "CASE-001",
  "severity": "high | medium | low",
  "type": "location | temporal | identity | metadata | source",
  "evidence_ids": ["EV-031", "EV-105"],
  "description": "Phone GPS shows Delhi, laptop login shows Mumbai at same timestamp",
  "possible_explanations": ["VPN", "timestamp mismatch", "device relocation", "account sharing"]
}
```

### Hypothesis
```json
{
  "hypothesis_id": "HYP-001",
  "case_id": "CASE-001",
  "description": "Potential Data Exfiltration",
  "confidence": 0.78,
  "reliability": 0.75,
  "supporting_evidence": ["EV-031", "EV-044", "EV-078", "EV-091"],
  "contradicting_evidence": ["EV-105"],
  "missing_evidence": ["mail server logs", "destination IP"],
  "explanation": "string"
}
```

---

## Endpoints

### Cases
- `POST /cases` — create case. Body: `{ "name": "string", "investigator": "string", "description": "string" }` → returns `Case`
- `GET /cases` → list of `Case`
- `GET /cases/{case_id}` → single `Case`

### Evidence
- `POST /evidence/upload` — multipart form: `case_id`, `source`, `file` → returns `Evidence` (system computes hash, id, timestamp)
- `GET /evidence?case_id={id}` → list of `Evidence`
- `GET /evidence/{evidence_id}` → single `Evidence`
- `POST /evidence/{evidence_id}/analyze` — triggers processing pipeline → returns `{ "status": "queued|processing|done" }`
- `GET /evidence/{evidence_id}/provenance` → transformation_history + related evidence

### Events / Timeline
- `GET /cases/{case_id}/timeline` → list of `Event`, sorted by timestamp

### Graph
- `GET /cases/{case_id}/graph` → `{ "nodes": [...], "edges": [...] }`
  - node: `{ "id": "EV-031", "type": "person|device|file|network|email|archive", "label": "string" }`
  - edge: `{ "source": "id", "target": "id", "relation": "owns|accessed|compressed|sent_to|..." }`

### Correlation
- `GET /cases/{case_id}/correlations` → list of grouped event clusters (shared actor/device/time window)

### Contradictions
- `GET /cases/{case_id}/contradictions` → list of `Contradiction`

### Findings / Reliability
- `GET /findings/{finding_id}` → single `Finding`
- `GET /cases/{case_id}/findings` → list of `Finding`

### Hypotheses
- `GET /cases/{case_id}/hypotheses` → list of `Hypothesis`

### Report
- `GET /cases/{case_id}/report` → generates PDF/HTML, returns file or download URL

---

## Rules for changing this contract
1. Whoever needs the change edits this file and pings the other person before writing code.
2. Never silently change a field name/type in backend code without updating this doc.
3. Frontend should mock these exact shapes (see `frontend/src/api/mockData.js`) until the real endpoint exists.
