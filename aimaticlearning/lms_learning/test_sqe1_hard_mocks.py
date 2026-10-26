import unittest

from aimaticlearning.lms_learning.sqe1_hard_mocks import (
	FIRST_REUSE_MOCK,
	FLK1_COUNTS,
	FLK2_COUNTS,
	MAX_PAIRWISE_OVERLAP,
	UNIQUE_MOCKS,
	SHOW_ANSWERS,
	allocate,
	allocate_with_reuse,
	explain_gap,
	frontend_payload,
	hardness_key,
	is_eligible,
	report_lesson_body,
	session_rows,
	sitting_url,
	summarise,
	repeat_stats,
	take_striped,
	validate_reuse,
)


def _row(name, course="x", difficulty="Medium", question="A client asks which of the following is correct. " * 8):
	return {
		"name": name,
		"lms_course": course,
		"difficulty": difficulty,
		"question": question,
		"option_1": "a",
		"option_2": "b",
		"option_3": "c",
		"option_4": "d",
		"option_5": "e",
		"is_correct_1": 1,
		"is_correct_2": 0,
		"is_correct_3": 0,
		"is_correct_4": 0,
		"is_correct_5": 0,
		"ai_generated": 0,
		"concept": "",
		"chapter_title": "Chapter 1",
		"source_reference": "src",
	}


def _small_pools():
	pools = {
		"blp": [_row(f"blp{i}") for i in range(80)],
		"dr": [_row(f"dr{i}") for i in range(80)],
		"legal_services": [_row(f"ls{i}") for i in range(80)],
		"tort": [_row(f"tort{i}") for i in range(80)],
		"contract": [_row(f"con{i}") for i in range(80)],
		"legal_system": [_row(f"pub{i}") for i in range(80)],
		"wills": [_row(f"will{i}") for i in range(80)],
		"trusts": [_row(f"tr{i}") for i in range(80)],
		"land": [_row(f"land{i}") for i in range(80)],
		"property": [_row(f"pr{i}") for i in range(80)],
		"accounts": [_row(f"acc{i}", question="client account") for i in range(40)],
		"criminal_litigation": [_row(f"cr{i}") for i in range(90)],
		"criminal_law": [_row(f"cl{i}") for i in range(10)],
	}
	for row in pools["accounts"][:20]:
		row["chapter_title"] = "Chapter 8: Conveyancing Transactions"
	return pools


class TestSqe1HardMocks(unittest.TestCase):
	def test_ineligible_without_fifth_option(self):
		row = _row("q1")
		row["option_5"] = ""
		self.assertFalse(is_eligible(row))

	def test_hard_ranks_before_medium(self):
		hard = _row("h", difficulty="Hard", question="short")
		medium = _row("m", difficulty="Medium", question="A client asks which of the following " * 20)
		self.assertLess(hardness_key(hard)[0], hardness_key(medium)[0])

	def test_stripe_spreads_hardest(self):
		pool = [_row(f"q{i}", question="x" * (200 - i)) for i in range(9)]
		buckets = take_striped(pool, [3, 3, 3])
		self.assertEqual([row["name"] for row in buckets[0]], ["q0", "q3", "q6"])
		self.assertEqual([row["name"] for row in buckets[1]], ["q1", "q4", "q7"])

	def test_allocate_unique_85_sessions(self):
		pools = {
			"blp": [_row(f"blp{i}") for i in range(160)],
			"dr": [_row(f"dr{i}") for i in range(120)],
			"legal_services": [_row(f"ls{i}") for i in range(120)],
			"tort": [_row(f"tort{i}") for i in range(140)],
			"contract": [_row(f"con{i}") for i in range(140)],
			"legal_system": [_row(f"pub{i}") for i in range(120)],
			"wills": [_row(f"will{i}") for i in range(120)],
			"trusts": [_row(f"tr{i}") for i in range(130)],
			"land": [_row(f"land{i}") for i in range(130)],
			"property": [_row(f"pr{i}") for i in range(120)],
			"accounts": [_row(f"acc{i}", question="client account") for i in range(130)],
			"criminal_litigation": [_row(f"cr{i}") for i in range(300)],
		}
		# Conveyancing-labelled accounts so property accounts can fill.
		for i, row in enumerate(pools["accounts"][:30]):
			row["chapter_title"] = "Chapter 8: Conveyancing Transactions"
		allocation = allocate(pools)
		summary = summarise(allocation)
		self.assertFalse(summary["duplicate"])
		self.assertEqual(summary["unique_questions"], UNIQUE_MOCKS * 340)
		for mock in summary["mocks"]:
			self.assertEqual(mock["sessions"]["flk1_s1"]["count"], 85)
			self.assertEqual(mock["sessions"]["flk1_s2"]["count"], 85)
			self.assertEqual(mock["sessions"]["flk2_s1"]["count"], 85)
			self.assertEqual(mock["sessions"]["flk2_s2"]["count"], 85)
		self.assertEqual(FLK1_COUNTS[0]["blp"], 33)
		names = [row["name"] for paper in allocation["papers"] for session in ("flk1_s1", "flk1_s2", "flk2_s1", "flk2_s2") for row in session_rows(paper, session)]
		self.assertEqual(len(names), len(set(names)))

	def test_counts_stay_inside_annex_4_and_sum_to_85(self):
		self.assertEqual(len(FLK1_COUNTS), len(FLK2_COUNTS))
		for c in FLK1_COUNTS:
			self.assertEqual(c["blp"] + c["dr"] + c["legal_services"], 85)
			self.assertEqual(c["tort"] + c["contract"] + c["legal_system"], 85)
			for key in ("blp", "dr", "tort", "contract", "legal_system"):
				self.assertTrue(24 <= c[key] <= 34, key)
			self.assertTrue(20 <= c["legal_services"] <= 27)
		for c in FLK2_COUNTS:
			self.assertEqual(c["wills"] + c["accounts_wills"] + c["trusts"] + c["land"], 85)
			self.assertEqual(
				c["property"] + c["accounts_property"] + c["criminal_liability"] + c["criminal_practice"], 85
			)
			self.assertTrue(24 <= c["wills"] + c["accounts_wills"] <= 34)
			self.assertTrue(24 <= c["property"] + c["accounts_property"] <= 34)

	def test_reuse_mocks_repeat_across_mocks_but_never_inside_one(self):
		pools = _small_pools()
		prior = {n: set() for n in range(1, UNIQUE_MOCKS + 1)}
		allocation = allocate_with_reuse(pools, [FIRST_REUSE_MOCK, FIRST_REUSE_MOCK + 1], prior)
		self.assertEqual(validate_reuse(allocation), [])
		for paper in allocation["papers"]:
			names = [r["name"] for s in ("flk1_s1", "flk1_s2", "flk2_s1", "flk2_s2") for r in session_rows(paper, s)]
			self.assertEqual(len(names), 340)
			self.assertEqual(len(names), len(set(names)))
		stats = repeat_stats(allocation["mock_sets"])
		self.assertGreater(stats[FIRST_REUSE_MOCK + 1]["repeated"], 0)

	def test_reuse_takes_unused_before_repeating(self):
		pools = _small_pools()
		first = allocate_with_reuse(pools, [FIRST_REUSE_MOCK], {})
		used = first["mock_sets"][FIRST_REUSE_MOCK]
		second = allocate_with_reuse(pools, [FIRST_REUSE_MOCK + 1], {FIRST_REUSE_MOCK: used})
		repeated = second["mock_sets"][FIRST_REUSE_MOCK + 1] & used
		# Every pool except accounts is larger than two mocks need, so only the
		# small accounts and criminal pools may repeat.
		self.assertLess(len(repeated), 60)

	def test_validate_flags_excess_overlap(self):
		pools = _small_pools()
		allocation = allocate_with_reuse(pools, [FIRST_REUSE_MOCK], {})
		names = allocation["mock_sets"][FIRST_REUSE_MOCK]
		allocation["mock_sets"][FIRST_REUSE_MOCK + 1] = set(names)
		self.assertGreater(repeat_stats(allocation["mock_sets"])[FIRST_REUSE_MOCK + 1]["max_pairwise_overlap"], MAX_PAIRWISE_OVERLAP)
		self.assertTrue(validate_reuse(allocation))

	def test_explain_gap_maps_known_bank_limits(self):
		self.assertEqual(explain_gap("Criminal Law has no 5-option bank")["id"], "criminal-liability")
		self.assertEqual(explain_gap("Eligible Hard tags are four-option")["id"], "hard-tags")
		self.assertEqual(explain_gap({"id": "custom", "title": "Kept", "detail": "x"})["title"], "Kept")

	def test_frontend_payload_omits_question_ids(self):
		summary = {
			"mocks": [
				{
					"mock": 1,
					"sessions": {
						"flk1_s1": {
							"count": 85,
							"areas": {"blp": 33, "dr": 25, "legal_services": 27},
							"difficulty": {"Medium": 85},
							"ethics_aml": 2,
							"tax": 1,
							"wales": 0,
						}
					},
				}
			],
			"gaps": ["Criminal Law has no 5-option bank"],
			"unique_questions": 1020,
			"duplicate": False,
			"published": 0,
		}
		payload = frontend_payload(summary, "now")
		self.assertEqual(payload["report_url"], "/learning-mock-report")
		self.assertEqual(payload["unique_questions"], 1020)
		self.assertEqual(payload["gaps"][0]["id"], "criminal-liability")
		self.assertEqual(payload["mocks"][0]["sessions"][0]["areas"][0]["label"], "Business Law and Practice")
		self.assertNotIn("name", payload["mocks"][0]["sessions"][0])
		body = report_lesson_body(payload)
		self.assertIn("/learning-mock-report", body)
		self.assertIn("Criminal Liability uses Criminal Litigation items", body)

	def test_sitting_url_and_closed_book(self):
		self.assertEqual(SHOW_ANSWERS, 0)
		self.assertEqual(sitting_url(1, 1), "/lms/courses/sqe1-hard-mocks/learn/1-1")
		self.assertEqual(sitting_url(3, 4), "/lms/courses/sqe1-hard-mocks/learn/3-4")
