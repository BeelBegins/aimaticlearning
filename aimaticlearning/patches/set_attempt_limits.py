import frappe

# Mocks: 10 attempts per session. MCQ module assessments: unlimited (0).
UNLIMITED_QUIZZES = ("blp-module-assessment-150-mcqs", "tort-law-module-assessment-108-mcqs")


def execute():
	"""Idempotent. Touches attempt limits and the lobby note only, never questions."""
	if "lms" not in frappe.get_installed_apps():
		return
	from aimaticlearning.lms_learning.exam_product import FORMAT_NOTE
	from aimaticlearning.lms_learning.sqe1_hard_mocks import COURSE_NAME, MAX_ATTEMPTS

	changes = []
	for quiz in frappe.get_all("LMS Quiz", filters={"course": COURSE_NAME}, fields=["name", "max_attempts"]):
		if quiz.max_attempts != MAX_ATTEMPTS:
			frappe.db.set_value("LMS Quiz", quiz.name, "max_attempts", MAX_ATTEMPTS, update_modified=False)
			changes.append((quiz.name, quiz.max_attempts, MAX_ATTEMPTS))

	for name in UNLIMITED_QUIZZES:
		current = frappe.db.get_value("LMS Quiz", name, "max_attempts")
		if current is not None and current != 0:
			frappe.db.set_value("LMS Quiz", name, "max_attempts", 0, update_modified=False)
			changes.append((name, current, 0))

	if frappe.db.exists("DocType", "Learning Mock Exam") and frappe.db.exists("Learning Mock Exam", COURSE_NAME):
		exam = frappe.db.get_value("Learning Mock Exam", COURSE_NAME, ["max_attempts", "format_note"], as_dict=True)
		if exam.max_attempts != MAX_ATTEMPTS or exam.format_note != FORMAT_NOTE:
			frappe.db.set_value(
				"Learning Mock Exam",
				COURSE_NAME,
				{"max_attempts": MAX_ATTEMPTS, "format_note": FORMAT_NOTE},
				update_modified=False,
			)
			changes.append((f"exam {COURSE_NAME}", exam.max_attempts, MAX_ATTEMPTS))

	for change in changes:
		print("attempt limit", change)
	return changes
