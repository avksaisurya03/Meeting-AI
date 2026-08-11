# Meeting Analysis

## Summary

This standup focused on urgent integration issues in the DiagnosticAI EHR portal around patient portal uploads and medical image parsing. Two major problems were identified: a critical memory/OOM crash in the Python ingestion worker when processing 3D MRI scans >500 MB that brings down the API pod and drops user connections, and a severe security risk where raw medical scans (containing patient names and Aadhaar numbers) are written to local disk unencrypted. The team agreed on an architectural change: stop processing DICOM files on the API server; use frontend direct uploads to S3 via presigned URLs and have Celery background workers process files in chunks. Action items were assigned with short deadlines: Siddharth to refactor the DICOM parser for S3 streaming and Celery (due Thursday 10 AM), Devansh to implement local AES-256 encryption for temporary worker files and submit a PR (due Friday 12 PM), Meera to prepare a preliminary HIPAA audit report for Dr. Aris (due Friday 4 PM), and Siddharth will cover Elena's model validation tasks for the rest of the week. The security issue and OOM crashes are blocking progress and must be resolved before the upcoming compliance audit next week.

## Action Items

### Action Item 1

**Task Title:** Refactor DICOM parser to use S3 presigned URLs and Celery background workers (S3 streaming) to process large 3D MRI files

**Assigned:** Siddharth

**Priority:** High

**Effort:** Complex

**Timeline:** Thursday 10 AM

**Acceptance Criteria:**
- DICOM ingestion no longer processes files on the API server but instead uses frontend uploads via S3 presigned URLs
- Celery background workers process files in chunks from S3
- Processing 3D MRI scans >500 MB no longer causes Out-Of-Memory crashes or brings down the API pod

### Action Item 2

**Task Title:** Implement local AES-256 encryption for temporary worker files and submit PR

**Assigned:** Devansh

**Priority:** High

**Effort:** Moderate

**Timeline:** Friday 12 PM

**Acceptance Criteria:**
- Temporary worker files (raw medical scans) are encrypted on local disk using AES-256
- A PR implementing the AES-256 local encryption is submitted by Friday 12 PM

### Action Item 3

**Task Title:** Prepare preliminary HIPAA audit report (compliance review for current handling of medical scans)

**Assigned:** Meera

**Priority:** High

**Effort:** Moderate

**Timeline:** Friday 4 PM

**Acceptance Criteria:**
- Preliminary HIPAA audit report is delivered to Dr. Aris's inbox by Friday 4 PM

### Action Item 4

**Task Title:** Take over Elena's model validation tasks for the remainder of the week

**Assigned:** Siddharth

**Priority:** Medium

**Effort:** Moderate

**Timeline:** For the rest of the week

**Acceptance Criteria:**
- Siddharth performs and covers the model validation tasks that Elena was responsible for for the rest of the week

## Decisions

### Decision 1

**Decision:** Stop processing DICOM files directly on the API server; have the frontend upload files directly to S3 using presigned URLs and process them in chunks with Celery background workers.

**Rationale:** This architecture prevents the Python ingestion worker from running out of memory and crashing the API pod when handling large 3D MRI files, and keeps the API gateway fast. It also addresses the urgent need to remove sensitive raw scans from local API server storage ahead of the compliance audit.

## Blockers

### Blocker 1

**Blocker:** Python ingestion worker hits Out-Of-Memory when processing 3D MRI scans over 500 MB, causing container and entire API pod crashes.

**Impact:** Active user connections are dropped, the API pod crashes, and web portal uploads produce broken pipe errors (observed during a demo), blocking reliable image ingestion and uploads.

### Blocker 2

**Blocker:** Raw medical scans containing patient names and Aadhaar numbers are written to local disk without encryption on worker nodes.

**Impact:** Exposes the system to regulatory fines under HIPAA and DPDP if a node is compromised; this security risk must be resolved before the upcoming compliance audit next week.
