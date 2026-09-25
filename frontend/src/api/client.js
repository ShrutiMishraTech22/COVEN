// Single place all API calls go through. Toggle USE_MOCK to false once
// a given backend endpoint is ready — swap function by function, not all at once.

import {
  mockCase, mockEvidence, mockTimeline, mockGraph,
  mockContradictions, mockFindings, mockHypotheses,
} from "./mockData";

const BASE_URL = "http://localhost:8000/api";
const USE_MOCK = true; // flip per-function below as backend endpoints go live

export async function getCase(caseId) {
  if (USE_MOCK) return mockCase;
  const res = await fetch(`${BASE_URL}/cases/${caseId}`);
  return res.json();
}

export async function getEvidence(caseId) {
  if (USE_MOCK) return mockEvidence;
  const res = await fetch(`${BASE_URL}/evidence?case_id=${caseId}`);
  return res.json();
}

export async function uploadEvidence(caseId, source, file) {
  if (USE_MOCK) return { ...mockEvidence[0], original_filename: file.name };
  const form = new FormData();
  form.append("case_id", caseId);
  form.append("source", source);
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/evidence/upload`, { method: "POST", body: form });
  return res.json();
}

export async function getTimeline(caseId) {
  if (USE_MOCK) return mockTimeline;
  const res = await fetch(`${BASE_URL}/cases/${caseId}/timeline`);
  return res.json();
}

export async function getGraph(caseId) {
  if (USE_MOCK) return mockGraph;
  const res = await fetch(`${BASE_URL}/cases/${caseId}/graph`);
  return res.json();
}

export async function getContradictions(caseId) {
  if (USE_MOCK) return mockContradictions;
  const res = await fetch(`${BASE_URL}/cases/${caseId}/contradictions`);
  return res.json();
}

export async function getFindings(caseId) {
  if (USE_MOCK) return mockFindings;
  const res = await fetch(`${BASE_URL}/cases/${caseId}/findings`);
  return res.json();
}

export async function getHypotheses(caseId) {
  if (USE_MOCK) return mockHypotheses;
  const res = await fetch(`${BASE_URL}/cases/${caseId}/hypotheses`);
  return res.json();
}
