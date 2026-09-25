# TrustGraph Build Timeline (target: Sept 25)

## Sept 15-17 — Foundation
- [ ] Lock API contract (docs/API_CONTRACT.md) — BOTH
- [ ] FastAPI + Postgres scaffold, ingestion endpoint (hash/metadata) — Person A
- [ ] React scaffold, case creation + upload UI wired to real API — Person B
- [ ] Synthetic dataset v1 (laptop/phone/network/email/usb, 1-2 contradictions, exfiltration pattern) — Person B
- [ ] Checkpoint: upload -> hash -> stored evidence, end to end

## Sept 18-20 — Core reasoning
- [ ] Normalization -> unified Event schema — Person A
- [ ] Correlation (group by entity/time window) — Person A
- [ ] Contradiction rules: location, temporal, identity mismatch (3 max) — Person A
- [ ] Evidence graph UI (React Flow) against mocks, then real data — Person B
- [ ] Timeline UI against mocks, then real data — Person B
- [ ] Checkpoint: correlation + contradictions visible on synthetic dataset

## Sept 21-22 — Reliability + hypotheses
- [ ] Reliability formula (weighted multiply, section 6 of blueprint) — Person A
- [ ] Hypothesis scoring (exfiltration/backup/sync templates) — Person A
- [ ] Contradiction + hypothesis panels — Person B
- [ ] Wire the "killer demo moment": AI confidence vs reliability score, click-to-explain — BOTH
- [ ] Checkpoint: full loop live — upload -> finding -> reliability -> contradiction -> hypotheses

## Sept 23 — Stretch (only if checkpoint above is solid)
- [ ] Report export (PDF/HTML)
- [ ] Basic OCR or NLP entity extraction
- [ ] Skip: Hindi/Hinglish, Neo4j, SHAP, audio/video

## Sept 24 — Freeze + polish
- [ ] No new features. Fix breakage only.
- [ ] Confirm demo dataset reliably triggers every feature

## Sept 25 — Pitch + submit
- [ ] Demo script (adapt blueprint section 57)
- [ ] Pitch deck (lean on blueprint sections 59-64)
- [ ] Dry run
- [ ] Submit
