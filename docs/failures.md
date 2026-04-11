# 🚩 Post-Mortems & System Failures

Learning from failure is critical. Every SEV1 incident requires a truthful post-mortem documented here.

---

## Incident: 2025-04-01 - PII Leak in Observability Logs

### 📅 Timeline
- **10:00 AM**: A human-in-the-loop reviewer noticed Social Security Numbers present in raw Langfuse logs.
- **10:15 AM**: Team confirmed the active PII Scrubber in `safety/guards/` was bypassing specific formatted texts.
- **10:30 AM**: API was temporarily degraded to safe-mode, halting complex RAG generation.
- **11:00 AM**: Emergency patch deployed tightening Presidio analyzer confidence bounds.

### 🔍 Root Cause
The `pii_scrubber.py` implementation was initialized with standard Presidio logic but failed to account for multiline block context when intercepting raw RAG document payloads. The RAG nodes sent giant chunked text strings that exceeded the regex batch boundary limit, parsing portions of the text unscrubbed into the observability tracer.

### 🛡️ Preventative Measures
1. **Added Chunked Scrubbing**: Scrubber now processes text at the sentence level rather than arbitrary large document blobs.
2. **Audit Pipeline Separation**: We added an assertion step (`evaluation/ci_cd/assert_pii.py`) in the deployment CI that runs massive adversarial PII payloads against the scrubber endpoint.
3. **Log Masking**: Added an edge-layer regex over the structured logger to catch any basic SSN/Credit Card patterns before they leave the VPC.
