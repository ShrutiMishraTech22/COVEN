// Single place all API calls go through. Toggle USE_MOCK to false once
// a given backend endpoint is ready — swap function by function, not all at once.

import {
  mockCase, mockEvidence, mockTimeline, mockGraph,
  mockContradictions, mockFindings, mockHypotheses,
} from "./mockData";

const BASE_URL = "http://localhost:8000/api";
const USE_MOCK = true; // flip per-function below as backend endpoints go live

export async function getCase(caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}`);

  if (!res.ok) {
    throw new Error(`Failed to load case: ${res.status}`);
  }

  return res.json();
}

export async function getCases() {
  const res = await fetch(`${BASE_URL}/cases`);

  if (!res.ok) {
    throw new Error(`Failed to load cases: ${res.status}`);
  }

  return res.json();
}

export async function getEvidence(caseId) {
  const res = await fetch(`${BASE_URL}/evidence?case_id=${caseId}`);

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Failed to load evidence");
  }

  return res.json();
}

export async function uploadEvidence(caseId, source, file) {
  const form = new FormData();

  form.append("case_id", caseId);
  form.append("source", source);
  form.append("file", file);

  const res = await fetch(`${BASE_URL}/evidence/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Evidence upload failed");
  }

  return res.json();
}

export async function getTimeline(caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/timeline`);

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Failed to load timeline");
  }

  return res.json();
}


export async function getGraph(caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/graph`);

  if (!res.ok) {
    throw new Error(`Failed to load graph: ${res.status}`);
  }

  return res.json();
}

export async function getContradictions(caseId) {
  const res = await fetch(
    `${BASE_URL}/cases/${caseId}/contradictions`
  );

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(
      errorText || "Failed to load contradictions"
    );
  }

  return res.json();
}

export async function getFindings(caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/findings`);

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Failed to load findings");
  }

  return res.json();
}

export async function getHypotheses(caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/hypotheses`);

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Failed to load hypotheses");
  }

  return res.json();
}
