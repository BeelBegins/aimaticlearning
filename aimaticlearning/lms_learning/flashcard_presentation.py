from __future__ import annotations

from html import escape


def inline_flashcard_deck_html(learning_module: str, course_chapter: str) -> str:
	"""Return the shared learner markup for an inline chapter flashcard deck."""
	return (
		'<div class="aimatic-chapter-hub aimatic-flashcard-page" data-aimatic-flashcard-deck'
		f' data-learning-module="{escape(learning_module, quote=True)}"'
		f' data-course-chapter="{escape(course_chapter, quote=True)}">'
		'<header class="aimatic-topic-intro"><span>Flashcards</span>'
		'<p>Reveal each answer, then rate how confidently you recalled it.</p></header>'
		'<div class="aimatic-flashcard-loader" data-aimatic-flashcard-loader>'
		'<span aria-hidden="true"></span><strong>Loading flashcards...</strong></div></div>'
	)
