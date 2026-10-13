(function () {
	"use strict";

	function learningDestination(link) {
		if (!document.body.classList.contains("aimatic-lms-student")) return null;
		const current = window.location.pathname.match(/^\/lms\/courses\/([^/]+)\/?$/);
		if (!current || !link.closest(".outline-lesson")) return null;
		const url = new URL(link.href, window.location.origin);
		const lesson = url.searchParams.get("editLesson");
		if (url.origin !== window.location.origin || url.pathname !== window.location.pathname ||
			url.hash !== "#editor" || !/^\d+-\d+$/.test(lesson || "")) return null;
		return "/lms/courses/" + current[1] + "/learn/" + lesson;
	}

	// A retained Course Instructor row can make LMS overview links point at
	// the editor after the user's staff role is removed. Follow the role-based
	// student marker from the server, while leaving real staff links intact.
	document.addEventListener("click", function (event) {
		const link = event.target.closest && event.target.closest("a");
		if (!link) return;
		const destination = learningDestination(link);
		if (!destination) return;
		event.preventDefault();
		event.stopImmediatePropagation();
		if (event.ctrlKey || event.metaKey || event.shiftKey || link.target === "_blank") {
			window.open(destination, "_blank", "noopener");
		} else {
			window.location.assign(destination);
		}
	}, true);
})();
