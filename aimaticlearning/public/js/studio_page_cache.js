// Drop Desk's localStorage copy of Content Studio so dirty-guard fixes load.
try {
	const stamp = "studio-dirty-v3";
	if (localStorage.getItem("aimatic-studio-script") !== stamp) {
		localStorage.removeItem("_page:learning-content-console");
		localStorage.setItem("aimatic-studio-script", stamp);
	}
} catch (error) {
	/* ignore private-mode quota */
}
