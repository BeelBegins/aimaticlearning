# Examic architecture

Product code is this repository. Upstream Frappe LMS stays untouched.
Aimatic-owned behaviour is `aimaticlearning/lms_learning/`.

| Layer | Location |
|---|---|
| Frappe + LMS | bench apps `frappe`, `lms`, `payments` |
| Examic features | this app |
| Study Buddy AI | `lms_learning/nemotron_client.py` + `openrouter_api_key` |
| Site data | `sites/lms.aimatic.tech` on the shared bench until cutover |
| Public DNS | examic.study / www.examic.study → Caddy alias |

A shared bench does not make this product related to SZL retail.

SQE1 mock exams: working copy of the SRA specification (from 1 September 2026)
and the January 2027 paper format lives in [docs/sqe1/](sqe1/README.md).
Learner lobby: `/learning-mock-exam`. Staff coverage/gaps: `/learning-mock-report`.
