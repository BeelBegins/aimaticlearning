from __future__ import annotations

import frappe
from frappe import _

PREVIEW_ROLES = frozenset({"System Manager", "Course Creator"})


def has_preview_access(user: str | None = None) -> bool:
	user = user or frappe.session.user
	if user == "Guest":
		return False
	return bool(PREVIEW_ROLES & set(frappe.get_roles(user)))


def require_preview_access() -> None:
	if not has_preview_access():
		frappe.throw(
			_("This preview is restricted to Examic Study content reviewers."),
			frappe.PermissionError,
		)


def preview_roles() -> tuple[str, ...]:
	return tuple(sorted(PREVIEW_ROLES))
