# Synthetic Evidence Dataset

This is the backbone of your demo. Build it early (Sept 15-17), not late —
every downstream feature (correlation, contradiction, reliability, hypotheses)
is only as convincing as this data.

## What to build

A single coherent scenario: **corporate data exfiltration**, matching
blueprint section 37. Create files for each source below, using timestamps
that form a believable sequence.

### Required files (start here)
- `laptop_logs.json` — login, file access, archive creation events
- `usb_logs.json` — USB connect/disconnect events
- `network_logs.json` — outbound connections, IP addresses
- `email_logs.json` — sent emails with attachments
- `phone_gps.json` — GPS pings (deliberately conflicting location — see below)

### The story to encode (matches blueprint section 37/39)
```
09:42  laptop login          Mumbai
09:48  USB connected         Mumbai
09:51  confidential.pdf opened   Mumbai
09:54  multiple files accessed   Mumbai
09:58  archive.zip created       Mumbai
10:04  external network connection
10:08  email attachment added
10:09  email sent to external address
10:09  phone GPS ping        Delhi   <-- CONTRADICTION: same time, different city
```

### Rules for realism
- Every event needs a timestamp, actor, device, action, and location.
- Build in exactly 1-2 deliberate contradictions (location mismatch is the
  easiest to encode and matches the blueprint's "killer demo moment").
- Include a few decoy/normal events too (legitimate logins, routine file
  access) so correlation and contradiction detection look meaningful — an
  all-signal, no-noise dataset won't demo well.
- Keep field names identical to the `Event` schema in `docs/API_CONTRACT.md`
  so Person A's normalization code doesn't need special-casing your data.

## Format
Plain JSON arrays, one file per source. Example (`usb_logs.json`):
```json
[
  {
    "timestamp": "2026-09-10T09:48:00Z",
    "actor": "employee_a",
    "device": "laptop-01",
    "action": "usb_connect",
    "object": "usb-device-9",
    "location": "Mumbai"
  }
]
```
