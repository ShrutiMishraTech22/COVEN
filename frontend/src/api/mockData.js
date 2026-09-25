// Mock data matching docs/API_CONTRACT.md exactly.
// Use this to build every screen BEFORE the real backend endpoint exists.
// Swap fetch calls from mock -> real API one endpoint at a time; don't
// change the shape here without updating the contract doc first.

export const mockCase = {
  case_id: "CASE-001",
  name: "Data Exfiltration Investigation",
  investigator: "Shruti",
  description: "Suspected confidential file transfer via USB + email",
  created_at: "2026-09-15T09:00:00Z",
};

export const mockEvidence = [
  {
    evidence_id: "EV-031",
    case_id: "CASE-001",
    source: "laptop",
    type: "file",
    original_filename: "confidential.pdf",
    timestamp: "2026-09-10T09:51:00Z",
    hash: "sha256:8d92abc...",
    metadata: { size_kb: 240 },
    acquisition_info: { collector: "system" },
    transformation_history: [],
    integrity_status: "verified",
  },
  {
    evidence_id: "EV-105",
    case_id: "CASE-001",
    source: "phone",
    type: "log",
    original_filename: "gps_log.json",
    timestamp: "2026-09-10T10:09:00Z",
    hash: "sha256:11ff22...",
    metadata: { location: "Delhi" },
    acquisition_info: { collector: "system" },
    transformation_history: [],
    integrity_status: "verified",
  },
];

export const mockTimeline = [
  { event_id: "EVT-001", evidence_id: "EV-031", case_id: "CASE-001", timestamp: "2026-09-10T09:42:00Z", actor: "employee_a", device: "laptop-01", action: "login", object: null, location: "Mumbai", source: "laptop", confidence: 1.0 },
  { event_id: "EVT-002", evidence_id: "EV-031", case_id: "CASE-001", timestamp: "2026-09-10T09:48:00Z", actor: "employee_a", device: "laptop-01", action: "usb_connect", object: "usb-device-9", location: "Mumbai", source: "usb", confidence: 1.0 },
  { event_id: "EVT-003", evidence_id: "EV-031", case_id: "CASE-001", timestamp: "2026-09-10T09:51:00Z", actor: "employee_a", device: "laptop-01", action: "file_access", object: "confidential.pdf", location: "Mumbai", source: "laptop", confidence: 1.0 },
  { event_id: "EVT-004", evidence_id: "EV-105", case_id: "CASE-001", timestamp: "2026-09-10T10:09:00Z", actor: "employee_a", device: "phone-01", action: "gps_ping", object: null, location: "Delhi", source: "phone", confidence: 1.0 },
];

export const mockGraph = {
  nodes: [
    { id: "employee_a", type: "person", label: "Employee A" },
    { id: "laptop-01", type: "device", label: "Laptop" },
    { id: "confidential.pdf", type: "file", label: "confidential.pdf" },
    { id: "archive.zip", type: "archive", label: "archive.zip" },
  ],
  edges: [
    { source: "employee_a", target: "laptop-01", relation: "owns" },
    { source: "laptop-01", target: "confidential.pdf", relation: "accessed" },
    { source: "confidential.pdf", target: "archive.zip", relation: "compressed" },
  ],
};

export const mockContradictions = [
  {
    contradiction_id: "CONTRA-001",
    case_id: "CASE-001",
    severity: "high",
    type: "location",
    evidence_ids: ["EV-031", "EV-105"],
    description: "Phone GPS shows Delhi while laptop login shows Mumbai at 10:09",
    possible_explanations: ["VPN", "timestamp mismatch", "device relocation", "account sharing"],
  },
];

export const mockFindings = [
  {
    finding_id: "FIND-001",
    case_id: "CASE-001",
    model: "rule-engine",
    model_version: "0.1",
    confidence: 0.87,
    supporting_evidence: ["EV-031"],
    contradicting_evidence: ["EV-105"],
    provenance: {},
    reliability: 0.78,
    reliability_breakdown: {
      model_confidence: 0.87,
      evidence_integrity: 1.0,
      source_reliability: 0.90,
      cross_source_agreement: 0.72,
      reproducibility: 0.95,
    },
    explanation: "Sequence of USB connect -> sensitive file access -> compression -> network activity matches exfiltration pattern.",
  },
];

export const mockHypotheses = [
  {
    hypothesis_id: "HYP-001",
    case_id: "CASE-001",
    description: "Potential Data Exfiltration",
    confidence: 0.78,
    reliability: 0.75,
    supporting_evidence: ["EV-031", "EV-044", "EV-078", "EV-091"],
    contradicting_evidence: ["EV-105"],
    missing_evidence: ["mail server logs", "destination IP"],
    explanation: "USB connect, sensitive file access, compression, and outbound network activity in sequence.",
  },
  {
    hypothesis_id: "HYP-002",
    case_id: "CASE-001",
    description: "Legitimate Backup",
    confidence: 0.42,
    reliability: 0.5,
    supporting_evidence: ["EV-044"],
    contradicting_evidence: ["EV-031"],
    missing_evidence: ["backup software logs"],
    explanation: "Known USB device and backup software signature detected, but immediately followed by external connection.",
  },
];
