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
