"""Render the signup form template with stand-ins for frappe, for the browser harness."""

import json
import pathlib
import sys

import jinja2

root = pathlib.Path(__file__).resolve().parents[2]
src = (root / "aimaticlearning/templates/lms_learning/examic_signup_form.html").read_text()
env = jinja2.Environment()
env.filters["tojson"] = lambda v: json.dumps(v)


class F:
	class db:
		@staticmethod
		def get_single_value(doctype, field):
			return {"user_category": 0, "custom_signup_content": "I agree to create a student account."}.get(field)

	class utils:
		nowdate = staticmethod(lambda: "2026-10-27")
		add_days = staticmethod(lambda d, n: "2026-11-27")
		formatdate = staticmethod(lambda d: "27 November 2026")


pathlib.Path(sys.argv[1]).write_text(env.from_string(src).render(frappe=F, _=lambda s: s))
