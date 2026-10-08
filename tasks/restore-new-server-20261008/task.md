# Task: restore-new-server-20261008

Goal: Restore the 8 October old-server backup onto new-server `examic.study`.

Environment: New-server `/home/ubuntu/frappe-bench`; old server read-only.

Approval: Owner approved target replacement and rollback backup in this session.

Base commit: 69f67ae; working tree initially clean.

Skills used: Repository lms-learning operating guidance; bench-ops unavailable locally.

Verification: Database gzip and rollback archives valid; migration exited 0;
11 selected table counts match source; 48 archived file/link entries match.
Verification artifact: `/home/ubuntu/restore-rollback-20261008/verification.json`.

Rollback: Database/files/config in `/home/ubuntu/restore-rollback-20261008`.

Status: done (restore).

Follow-up: Owner approved disabling maintenance; mode is now off and local/public
`/sqe` return HTTP 200. Verify authenticated learner pages in browser.
Old server unchanged.
