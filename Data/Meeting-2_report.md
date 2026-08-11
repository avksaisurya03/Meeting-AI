# Executive Meeting Digest

---

## Executive Summary

Team discussed two urgent issues: (1) a critical memory bug in the Python ingestion worker causing Out-Of-Memory crashes on AWS ECS when processing 3D MRI scans over 500 MB, which crashes the API pod and drops user connections (causing broken pipe errors in the portal); and (2) a severe security/compliance risk where raw medical scans containing patient names and Aadhaar numbers are written to local disk without encryption, exposing the project to HIPAA and DPDP fines. The team agreed on an architectural change: stop processing DICOM on the API server — instead use frontend uploads to S3 via presigned URLs and process files in chunks with Celery background workers. Action items were assigned: Siddharth to refactor the DICOM parser and implement S3 streaming/Celery by Thursday 10 AM; Devansh to implement local AES-256 encryption for temporary worker files and submit a PR by Friday 12 PM; Meera to prepare a preliminary HIPAA audit report for Dr. Aris by Friday 4 PM. The security flaw must be resolved before the upcoming compliance audit next week.


## Action Items Matrix

| # | Task Title | Assigned (Role) | Priority | Effort | Timeline | Acceptance Criteria |
|---|------------|-----------------|----------|--------|----------|---------------------|
| 1 | **Refactor DICOM parser to use S3 presigned URLs and Celery workers (S3 streaming refactor)** | Siddharth | `High` | `Complex` | Thursday 10 AM | • DICOM files are no longer processed directly on the API server<br>• Frontend uploads use S3 presigned URLs for file transfer<br>• Celery background workers process DICOM files in chunks (streaming)<br>• No Out-Of-Memory container crashes when processing 3D MRI scans >500 MB<br>• API gateway performance remains responsive (no dropped connections during large uploads) |
| 2 | **Implement local AES-256 encryption for temporary worker files and submit PR** | Devansh | `High` | `Moderate` | Friday 12 PM | • Temporary worker files on local disk are encrypted using AES-256 before being written<br>• No plaintext patient-identifying information (e.g., patient names, Aadhaar numbers) is stored unencrypted on local disk<br>• A pull request implementing the encryption changes is submitted by the deadline |
| 3 | **Prepare preliminary HIPAA audit report addressing current security risk** | Meera | `High` | `Moderate` | Friday 4 PM | • Preliminary HIPAA audit report is delivered to Dr. Aris by the deadline<br>• Report identifies the unencrypted storage of raw medical scans as a compliance risk<br>• Report includes recommended remediation steps relevant to the identified risk (e.g., encryption, change in processing flow) |


## Architecture & Design Decisions

### Decision 1: Stop processing DICOM files on the API server; switch to frontend uploads to S3 using presigned URLs and process files in chunks with Celery background workers.
**Rationale:** This change prevents container Out-Of-Memory crashes when processing large 3D MRI scans (addressing the critical memory issue) and keeps the API gateway fast. It also aligns with the need to resolve storage/security risks before the upcoming compliance audit.

## Risk & Blocker Matrix

| # | Risk / Blocker | Impact Assessment |
|---|----------------|-------------------|
| 1 | **Python ingestion worker experiences Out-Of-Memory crashes on AWS ECS when processing 3D MRI scans over 500 MB.** | Container crashes the entire API pod instantly, dropping all active user connections and causing broken pipe errors on the web portal (demonstrated during a demo upload). |
| 2 | **Raw medical scans containing patient names and Aadhaar numbers are written to local disk without encryption.** | Severe regulatory exposure under HIPAA and DPDP; must be remediated before the upcoming compliance audit next week to avoid fines. |
| 3 | **Upcoming compliance audit next week.** | Time pressure to resolve security/compliance issues (encryption and processing flow changes) before the audit. |

